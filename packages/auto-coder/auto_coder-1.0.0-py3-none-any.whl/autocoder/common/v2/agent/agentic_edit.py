import json
import os
import time
import byzerllm
from typing import List, Dict, Any, Union, Optional, Tuple
from autocoder.common.printer import Printer

from autocoder.common import AutoCoderArgs, git_utils, SourceCodeList
from autocoder.common.global_cancel import global_cancel
from autocoder.common import detect_env
from autocoder.common import shells
from loguru import logger
from autocoder.utils.auto_project_type import ProjectTypeAnalyzer

from autocoder.common.mcp_server import get_mcp_server, McpServerInfoRequest
from autocoder.common import SourceCodeList
from autocoder.common.utils_code_auto_generate import stream_chat_with_continue  # Added import
import re
import xml.sax.saxutils
import time  # Added for sleep
from typing import Union, Type, Generator
from autocoder.events.event_manager_singleton import get_event_manager
from autocoder.events.event_types import EventMetadata
from autocoder.memory.active_context_manager import ActiveContextManager
from autocoder.events import event_content as EventContentCreator
from autocoder.common.action_yml_file_manager import ActionYmlFileManager
from autocoder.common.auto_coder_lang import get_message
from autocoder.common.save_formatted_log import save_formatted_log
from autocoder.common.v2.agent.agentic_edit_types import FileChangeEntry
from autocoder.utils.llms import get_single_llm

from autocoder.common.file_checkpoint.manager import FileChangeManager as CheckpointFileChangeManager
from autocoder.linters.normal_linter import NormalLinter
from autocoder.compilers.normal_compiler import NormalCompiler
from autocoder.common.v2.agent.agentic_edit_tools import (  # Import specific resolvers
    BaseToolResolver,
    ExecuteCommandToolResolver, ReadFileToolResolver, WriteToFileToolResolver,
    ReplaceInFileToolResolver, SearchFilesToolResolver, ListFilesToolResolver,
    ListCodeDefinitionNamesToolResolver, AskFollowupQuestionToolResolver,
    AttemptCompletionToolResolver, PlanModeRespondToolResolver, UseMcpToolResolver,
    UseRAGToolResolver, ACModReadToolResolver, ACModWriteToolResolver, TodoReadToolResolver,
    TodoWriteToolResolver
)
from autocoder.common.llm_friendly_package import LLMFriendlyPackageManager
from autocoder.common.rulefiles.autocoderrules_utils import get_rules,auto_select_rules,get_required_and_index_rules
from autocoder.common.v2.agent.agentic_edit_types import (AgenticEditRequest, ToolResult,
                                                          MemoryConfig, CommandConfig, BaseTool,
                                                          ExecuteCommandTool, ReadFileTool,
                                                          WriteToFileTool,
                                                          ReplaceInFileTool,
                                                          SearchFilesTool,
                                                          ListFilesTool,
                                                          ListCodeDefinitionNamesTool, AskFollowupQuestionTool,
                                                          AttemptCompletionTool, PlanModeRespondTool, UseMcpTool,
                                                          UseRAGTool, ACModReadTool, ACModWriteTool, TodoReadTool,
                                                          TodoWriteTool,
                                                          TOOL_MODEL_MAP,
                                                          # Event Types
                                                          LLMOutputEvent, LLMThinkingEvent, ToolCallEvent,
                                                          ToolResultEvent, CompletionEvent, PlanModeRespondEvent, ErrorEvent, TokenUsageEvent,
                                                          WindowLengthChangeEvent,
                                                          ConversationIdEvent,
                                                          # Import specific tool types for display mapping
                                                          ReadFileTool, WriteToFileTool, ReplaceInFileTool, ExecuteCommandTool,
                                                          ListFilesTool, SearchFilesTool, ListCodeDefinitionNamesTool,
                                                          AskFollowupQuestionTool, UseMcpTool, AttemptCompletionTool,
                                                          AgenticEditConversationConfig
                                                          )
from autocoder.common.rag_manager import RAGManager
from autocoder.rag.token_counter import count_tokens

# Map Pydantic Tool Models to their Resolver Classes
TOOL_RESOLVER_MAP: Dict[Type[BaseTool], Type[BaseToolResolver]] = {
    ExecuteCommandTool: ExecuteCommandToolResolver,
    ReadFileTool: ReadFileToolResolver,
    WriteToFileTool: WriteToFileToolResolver,
    ReplaceInFileTool: ReplaceInFileToolResolver,
    SearchFilesTool: SearchFilesToolResolver,
    ListFilesTool: ListFilesToolResolver,
    ListCodeDefinitionNamesTool: ListCodeDefinitionNamesToolResolver,
    ACModReadTool: ACModReadToolResolver,
    ACModWriteTool: ACModWriteToolResolver,
    AskFollowupQuestionTool: AskFollowupQuestionToolResolver,
    AttemptCompletionTool: AttemptCompletionToolResolver,  # Will stop the loop anyway
    PlanModeRespondTool: PlanModeRespondToolResolver,
    UseMcpTool: UseMcpToolResolver,
    UseRAGTool: UseRAGToolResolver,
    TodoReadTool: TodoReadToolResolver,
    TodoWriteTool: TodoWriteToolResolver
}
from autocoder.common.conversations.get_conversation_manager import get_conversation_manager 
from autocoder.common.pull_requests import create_pull_request
from autocoder.common.auto_coder_lang import get_message, get_message_with_format
from autocoder.common.pruner.agentic_conversation_pruner import AgenticConversationPruner
from copy import deepcopy


# --- Tool Display Customization is now handled by agentic_tool_display.py ---


class AgenticEdit:
    def __init__(
        self,
        llm: Union[byzerllm.ByzerLLM, byzerllm.SimpleByzerLLM],
        conversation_history: List[Dict[str, Any]],
        files: SourceCodeList,
        args: AutoCoderArgs,
        memory_config: MemoryConfig,
        command_config: Optional[CommandConfig] = None,
        conversation_name:Optional[str] = "current",
        conversation_config:Optional[AgenticEditConversationConfig] = None
    ):
        self.llm = llm
        self.context_prune_llm = get_single_llm(args.context_prune_model or args.model,product_mode=args.product_mode) 
        self.args = args
        self.printer = Printer()
        # Removed self.tools and self.result_manager
        self.files = files
        # Removed self.max_iterations
        # Note: This might need updating based on the new flow
        self.conversation_history = conversation_history                    

        self.current_conversations = []
        self.memory_config = memory_config
        self.command_config = command_config  # Note: command_config might be unused now
        self.project_type_analyzer = ProjectTypeAnalyzer(
            args=args, llm=self.llm)
        self.base_persist_dir = os.path.join(args.source_dir, ".auto-coder", "plugins", "chat-auto-coder")        

        # self.shadow_manager = ShadowManager(
        #     args.source_dir, args.event_file, args.ignore_clean_shadows)
        self.shadow_manager = None
        # self.shadow_linter = ShadowLinter(self.shadow_manager, verbose=False)
        self.shadow_compiler = None
        # self.shadow_compiler = ShadowCompiler(self.shadow_manager, verbose=False)
        self.shadow_linter = None

        self.checkpoint_manager = CheckpointFileChangeManager(
            project_dir=args.source_dir,
            backup_dir=os.path.join(args.source_dir,".auto-coder","checkpoint"),
            store_dir=os.path.join(args.source_dir,".auto-coder","checkpoint_store"),
            max_history=50)
        self.linter = NormalLinter(args.source_dir,verbose=False)
        self.compiler = NormalCompiler(args.source_dir,verbose=False)        
            

        self.mcp_server_info = ""
        try:
            self.mcp_server = get_mcp_server()
            mcp_server_info_response = self.mcp_server.send_request(
                McpServerInfoRequest(
                    model=args.inference_model or args.model,
                    product_mode=args.product_mode,
                )
            )
            self.mcp_server_info = mcp_server_info_response.result
        except Exception as e:
            logger.error(f"Error getting MCP server info: {str(e)}")

        # 初始化 RAG 管理器并获取服务器信息
        self.rag_server_info = ""
        try:
            self.rag_manager = RAGManager(args)
            if self.rag_manager.has_configs():
                self.rag_server_info = self.rag_manager.get_config_info()
                logger.info(f"RAG manager initialized with {len(self.rag_manager.get_all_configs())} configurations")
            else:
                logger.info("No RAG configurations found")
        except Exception as e:
            logger.error(f"Error initializing RAG manager: {str(e)}")
            self.rag_manager = None

        # 变更跟踪信息
        # 格式: { file_path: FileChangeEntry(...) }
        self.file_changes: Dict[str, FileChangeEntry] = {}

        # 对话管理器
        self.conversation_config =conversation_config
        self.conversation_manager = get_conversation_manager()
        
        # Agentic 对话修剪器
        self.agentic_pruner = AgenticConversationPruner(args=args, llm=self.context_prune_llm)

        if self.conversation_config.action == "new":
            conversation_id = self.conversation_manager.create_conversation(name=self.conversation_config.query or "New Conversation",
                                                                            description=self.conversation_config.query or "New Conversation")
            self.conversation_manager.set_current_conversation(conversation_id)

        if self.conversation_config.action == "resume" and self.conversation_config.conversation_id:
            self.conversation_manager.set_current_conversation(self.conversation_config.conversation_id)
            

    @byzerllm.prompt()
    def generate_library_docs_prompt(self, libraries_with_paths: List[Dict[str, str]], docs_content: str) -> Dict[str, Any]:
        """
        ====

        THIRD-PARTY LIBRARY DOCUMENTATION

        The following documentation is for third-party libraries that are available in this project. Use this information to understand the capabilities and APIs of these libraries when they are relevant to the user's task.

        Libraries included: {{ libraries_list }}

        <library_documentation>
        {{ combined_docs }}
        </library_documentation>

        You should reference this documentation when:
        1. The user asks about functionality that might be provided by these libraries
        2. You need to implement features that could leverage these library capabilities  
        3. You want to suggest using library functions instead of implementing from scratch
        4. You need to understand the API or usage patterns of these libraries
        ====
        """
        # 格式化库列表，包含名称和路径
        libraries_list = []
        for lib_info in libraries_with_paths:
            name = lib_info.get('name', '')
            path = lib_info.get('path', 'Path not found')
            libraries_list.append(f"{name} (路径: {path})")
        
        return {
            "libraries_list": ", ".join(libraries_list),
            "combined_docs": docs_content
        }

    def record_file_change(self, file_path: str, change_type: str, diff: Optional[str] = None, content: Optional[str] = None):
        """
        记录单个文件的变更信息。

        Args:
            file_path: 相对路径
            change_type: 'added' 或 'modified'
            diff: 对于 replace_in_file，传入 diff 内容
            content: 最新文件内容（可选，通常用于 write_to_file）
        """
        entry = self.file_changes.get(file_path)
        if entry is None:
            entry = FileChangeEntry(
                type=change_type, diffs=[], content=content)
            self.file_changes[file_path] = entry
        else:
            # 文件已经存在，可能之前是 added，现在又被 modified，或者多次 modified
            # 简单起见，type 用 added 优先，否则为 modified
            if entry.type != "added":
                entry.type = change_type

            # content 以最新为准
            if content is not None:
                entry.content = content

        if diff:
            entry.diffs.append(diff)

    def get_all_file_changes(self) -> Dict[str, FileChangeEntry]:
        """
        获取当前记录的所有文件变更信息。

        Returns:
            字典，key 为文件路径，value 为变更详情
        """
        return self.file_changes

    def get_changed_files_from_shadow(self) -> List[str]:
        """
        获取影子系统当前有哪些文件被修改或新增。

        Returns:
            变更的文件路径列表
        """
        changed_files = []
        shadow_root = self.shadow_manager.shadows_dir
        for root, dirs, files in os.walk(shadow_root):
            for fname in files:
                shadow_file_path = os.path.join(root, fname)
                try:
                    project_file_path = self.shadow_manager.from_shadow_path(
                        shadow_file_path)
                    rel_path = os.path.relpath(
                        project_file_path, self.args.source_dir)
                    changed_files.append(rel_path)
                except Exception:
                    # 非映射关系，忽略
                    continue
        return changed_files

    @byzerllm.prompt()
    def _analyze(self, request: AgenticEditRequest) -> str:
        """        
        You are a highly skilled software engineer with extensive knowledge in many programming languages, frameworks, design patterns, and best practices.        

        ====        

        TOOL USE

        You have access to a set of tools that are executed upon the user's approval. You can use one tool per message, and will receive the result of that tool use in the user's response. You use tools step-by-step to accomplish a given task, with each tool use informed by the result of the previous tool use.

        # Tool Use Formatting

        Tool use is formatted using XML-style tags. The tool name is enclosed in opening and closing tags, and each parameter is similarly enclosed within its own set of tags. Here's the structure:

        <tool_name>
        <parameter1_name>value1</parameter1_name>
        <parameter2_name>value2</parameter2_name>
        ...
        </tool_name>

        For example:

        <read_file>
        <path>src/main.js</path>
        </read_file>

        Always adhere to this format for the tool use to ensure proper parsing and execution.


        # Tools

        ## execute_command
        Description: Request to execute a CLI command on the system. Use this when you need to perform system operations or run specific commands to accomplish any step in the user's task. You must tailor your command to the user's system and provide a clear explanation of what the command does. For command chaining, use the appropriate chaining syntax for the user's shell. Prefer to execute complex CLI commands over creating executable scripts, as they are more flexible and easier to run. Commands will be executed in the current working directory: {{current_project}}
        Parameters:
        - command: (required) The CLI command to execute. This should be valid for the current operating system. Ensure the command is properly formatted and does not contain any harmful instructions.
        - requires_approval: (required) A boolean indicating whether this command requires explicit user approval before execution in case the user has auto-approve mode enabled. Set to 'true' for potentially impactful operations like installing/uninstalling packages, deleting/overwriting files, system configuration changes, network operations, or any commands that could have unintended side effects. Set to 'false' for safe operations like reading files/directories, running development servers, building projects, and other non-destructive operations.
        Usage:
        <execute_command>
        <command>Your command here</command>
        <requires_approval>true or false</requires_approval>
        </execute_command>

        ## ac_mod_read
        Description: Request to retrieve information about an AC Module - a language-agnostic module containing a .ac.mod.md file that provides complete functionality and can be used as an API. The .ac.mod.md file contains usage examples, core components, component dependencies, references to other AC modules, and testing information. It accepts a directory path (absolute or relative to the current project).
        Parameters:
        - path: (required) The AC Module directory path (directory containing .ac.mod.md file).
        Usage:
        <ac_mod_read>
        <path>relative/or/absolute/ac/module/path</path>
        </ac_mod_read>

        ## ac_mod_write
        Description: Request to create or update an AC Module's .ac.mod.md file. This tool allows you to define a new AC Module or modify an existing one by writing to its .ac.mod.md file. The file contains usage examples, core components, component dependencies, references to other AC modules, and testing information.
        Parameters:
        - path: (required) The AC Module directory path (directory where .ac.mod.md file should be created or updated).
        - diff: (required) One or more SEARCH/REPLACE blocks following this exact format:
        ```
        <<<<<<< SEARCH
        [exact content to find]
        =======
        [new content to replace with]
        >>>>>>> REPLACE

        This tool have the same usage as the replace_in_file tool, but it is used to update the AC Module's .ac.mod.md file.
        
        Usage:
        
        <ac_mod_write>
        <path>relative/or/absolute/ac/module/path</path>
        <diff>
        Search and replace blocks here
        </diff>
        </ac_mod_write>

        ## read_file
        Description: Request to read the contents of a file at the specified path. Use this when you need to examine the contents of an existing file you do not know the contents of, for example to analyze code, review text files, or extract information from configuration files. Automatically extracts raw text from PDF and DOCX files. May not be suitable for other types of binary files, as it returns the raw content as a string.
        Parameters:
        - path: (required) The path of the file to read (relative to the current working directory {{ current_project }})
        Usage:
        <read_file>
        <path>File path here</path>
        </read_file>

        ## write_to_file
        Description: Request to write content to a file at the specified path. If the file exists, it will be overwritten with the provided content. If the file doesn't exist, it will be created. This tool will automatically create any directories needed to write the file.
        Parameters:
        - path: (required) The path of the file to write to (relative to the current working directory {{ current_project }})
        - content: (required) The content to write to the file. ALWAYS provide the COMPLETE intended content of the file, without any truncation or omissions. You MUST include ALL parts of the file, even if they haven't been modified.
        Usage:
        <write_to_file>
        <path>File path here</path>
        <content>
        Your file content here
        </content>
        </write_to_file>

        ## replace_in_file
        Description: Request to replace sections of content in an existing file using SEARCH/REPLACE blocks that define exact changes to specific parts of the file. This tool should be used when you need to make targeted changes to specific parts of a file.
        Parameters:
        - path: (required) The path of the file to modify (relative to the current working directory {{ current_project }})
        - diff: (required) One or more SEARCH/REPLACE blocks following this exact format:
        ```
        <<<<<<< SEARCH
        [exact content to find]
        =======
        [new content to replace with]
        >>>>>>> REPLACE
        ```
        Critical rules:
        1. SEARCH content must match the associated file section to find EXACTLY:
            * Match character-for-character including whitespace, indentation, line endings
            * Include all comments, docstrings, etc.
        2. SEARCH/REPLACE blocks will ONLY replace the first match occurrence.
            * Including multiple unique SEARCH/REPLACE blocks if you need to make multiple changes.
            * Include *just* enough lines in each SEARCH section to uniquely match each set of lines that need to change.
            * When using multiple SEARCH/REPLACE blocks, list them in the order they appear in the file.
        3. Keep SEARCH/REPLACE blocks concise:
            * Break large SEARCH/REPLACE blocks into a series of smaller blocks that each change a small portion of the file.
            * Include just the changing lines, and a few surrounding lines if needed for uniqueness.
            * Do not include long runs of unchanging lines in SEARCH/REPLACE blocks.
            * Each line must be complete. Never truncate lines mid-way through as this can cause matching failures.
        4. Special operations:
            * To move code: Use two SEARCH/REPLACE blocks (one to delete from original + one to insert at new location)
            * To delete code: Use empty REPLACE section
        Usage:
        <replace_in_file>
        <path>File path here</path>
        <diff>
        Search and replace blocks here
        </diff>
        </replace_in_file>

        ## search_files
        Description: Request to perform a regex search across files in a specified directory, providing context-rich results. This tool searches for patterns or specific content across multiple files, displaying each match with encapsulating context.
        Parameters:
        - path: (required) The path of the directory to search in (relative to the current working directory {{ current_project }}). This directory will be recursively searched.
        - regex: (required) The regular expression pattern to search for. Uses Rust regex syntax.
        - file_pattern: (optional) Glob pattern to filter files (e.g., '*.ts' for TypeScript files). If not provided, it will search all files (*).
        Usage:
        <search_files>
        <path>Directory path here</path>
        <regex>Your regex pattern here</regex>
        <file_pattern>file pattern here (optional)</file_pattern>
        </search_files>

        ## list_files
        Description: Request to list files and directories within the specified directory. If recursive is true, it will list all files and directories recursively. If recursive is false or not provided, it will only list the top-level contents. Do not use this tool to confirm the existence of files you may have created, as the user will let you know if the files were created successfully or not.
        Parameters:
        - path: (required) The path of the directory to list contents for (relative to the current working directory {{ current_project }})
        - recursive: (optional) Whether to list files recursively. Use true for recursive listing, false or omit for top-level only.
        Usage:
        <list_files>
        <path>Directory path here</path>
        <recursive>true or false (optional)</recursive>
        </list_files>

        ## list_code_definition_names
        Description: Request to list definition names (classes, functions, methods, etc.) used in source code files at the top level of the specified directory. This tool provides insights into the codebase structure and important constructs, encapsulating high-level concepts and relationships that are crucial for understanding the overall architecture.
        Parameters:
        - path: (required) The path of the directory (relative to the current working directory {{ current_project }}) to list top level source code definitions for.
        Usage:
        <list_code_definition_names>
        <path>Directory path here</path>
        </list_code_definition_names>
                
        ## ask_followup_question
        Description: Ask the user a question to gather additional information needed to complete the task. This tool should be used when you encounter ambiguities, need clarification, or require more details to proceed effectively. It allows for interactive problem-solving by enabling direct communication with the user. Use this tool judiciously to maintain a balance between gathering necessary information and avoiding excessive back-and-forth.
        Parameters:
        - question: (required) The question to ask the user. This should be a clear, specific question that addresses the information you need.
        - options: (optional) An array of 2-5 options for the user to choose from. Each option should be a string describing a possible answer. You may not always need to provide options, but it may be helpful in many cases where it can save the user from having to type out a response manually. IMPORTANT: NEVER include an option to toggle to Act mode, as this would be something you need to direct the user to do manually themselves if needed.
        Usage:
        <ask_followup_question>
        <question>Your question here</question>
        <options>
        Array of options here (optional), e.g. ["Option 1", "Option 2", "Option 3"]
        </options>
        </ask_followup_question>    

        ## todo_read
        Description: Request to read the current todo list for the session. This tool helps you track progress, organize complex tasks, and understand the current status of ongoing work. Use this tool proactively to stay aware of task progress and demonstrate thoroughness.
        Parameters:
        - No parameters required
        Usage:
        <todo_read>
        </todo_read>

        ## todo_write
        Description: Request to create and manage a structured task list for your current coding session. This helps you track progress, organize complex tasks, and demonstrate thoroughness to the user. It also helps the user understand the progress of the task and overall progress of their request. Use this tool proactively for complex multi-step tasks, when explicitly requested by the user, or when you need to organize multiple operations.
        Parameters:
        - action: (required) The action to perform: 'create' (create new todo list), 'add_task' (add single task), 'update' (update existing task), 'mark_progress' (mark task as in progress), 'mark_completed' (mark task as completed)
        - task_id: (optional) The ID of the task to update (required for update, mark_progress, mark_completed actions)
        - content: (optional) The task content or description (required for create, add_task actions)
        - priority: (optional) Task priority level: 'high', 'medium', 'low' (default: 'medium')
        - status: (optional) Task status: 'pending', 'in_progress', 'completed' (default: 'pending')
        - notes: (optional) Additional notes or details about the task
        Usage:
        <todo_write>
        <action>create</action>
        <content> 
        <task>Read the configuration file</task>
        <task>Update the database settings</task>
        <task>Test the connection</task>
        <task>Deploy the changes</task>
        </content>
        <priority>high</priority>
        </todo_write>           

        ## attempt_completion
        Description: After each tool use, the user will respond with the result of that tool use, i.e. if it succeeded or failed, along with any reasons for failure. Once you've received the results of tool uses and can confirm that the task is complete, use this tool to present the result of your work to the user. Optionally you may provide a CLI command to showcase the result of your work. The user may respond with feedback if they are not satisfied with the result, which you can use to make improvements and try again.
        IMPORTANT NOTE: This tool CANNOT be used until you've confirmed from the user that any previous tool uses were successful. Failure to do so will result in code corruption and system failure. Before using this tool, you must ask yourself in <thinking></thinking> tags if you've confirmed from the user that any previous tool uses were successful. If not, then DO NOT use this tool.
        Parameters:
        - result: (required) The result of the task. Formulate this result in a way that is final and does not require further input from the user. Don't end your result with questions or offers for further assistance.
        - command: (optional) A CLI command to execute to show a live demo of the result to the user. For example, use \`open index.html\` to display a created html website, or \`open localhost:3000\` to display a locally running development server. But DO NOT use commands like \`echo\` or \`cat\` that merely print text. This command should be valid for the current operating system. Ensure the command is properly formatted and does not contain any harmful instructions.
        Usage:
        <attempt_completion>
        <result>
        Your final result description here
        </result>
        <command>Command to demonstrate result (optional)</command>
        </attempt_completion>        

        ## mcp_tool
        Description: Request to execute a tool via the Model Context Protocol (MCP) server. Use this when you need to execute a tool that is not natively supported by the agentic edit tools.
        Parameters:
        - server_name: (optional) The name of the MCP server to use. If not provided, the tool will automatically choose the best server based on the query.
        - tool_name: (optional) The name of the tool to execute. If not provided, the tool will automatically choose the best tool in the selected server based on the query.
        - query: (required) The query to pass to the tool.
        Usage:
        <use_mcp_tool>
        <server_name>xxx</server_name>
        <tool_name>xxxx</tool_name>
        <query>
        Your query here
        </query>
        </use_mcp_tool> 

        {%if mcp_server_info %}
        ### MCP_SERVER_LIST
        {{mcp_server_info}}
        {%endif%}

        ## rag_tool
        Description: Request to query the RAG server for information. Use this when you need to query the RAG server for information.
        Parameters:
        - server_name: (required) The url of the RAG server to use.
        - query: (required) The query to pass to the tool.
        Usage:
        <use_rag_tool>
        <server_name>xxx</server_name>
        <query>Your query here</query>
        </use_rag_tool>

        {%if rag_server_info %}
        ### RAG_SERVER_LIST
        {{rag_server_info}}
        {%endif%}        

        # Tool Use Examples

        ## Example 1: Requesting to execute a command

        <execute_command>
        <command>npm run dev</command>
        <requires_approval>false</requires_approval>
        </execute_command>

        ## Example 2: Requesting to create a new file

        <write_to_file>
        <path>src/frontend-config.json</path>
        <content>
        {
        "apiEndpoint": "https://api.example.com",
        "theme": {
            "primaryColor": "#007bff",
            "secondaryColor": "#6c757d",
            "fontFamily": "Arial, sans-serif"
        },
        "features": {
            "darkMode": true,
            "notifications": true,
            "analytics": false
        },
        "version": "1.0.0"
        }
        </content>
        </write_to_file>

        ## Example 3: Requesting to make targeted edits to a file

        <replace_in_file>
        <path>src/components/App.tsx</path>
        <diff>
        <<<<<<< SEARCH
        import React from 'react';
        =======
        import React, { useState } from 'react';
        >>>>>>> REPLACE

        <<<<<<< SEARCH
        function handleSubmit() {
        saveData();
        setLoading(false);
        }

        =======
        >>>>>>> REPLACE

        <<<<<<< SEARCH
        return (
        <div>
        =======
        function handleSubmit() {
        saveData();
        setLoading(false);
        }

        return (
        <div>
        >>>>>>> REPLACE
        </diff>
        </replace_in_file>

        ## Example 4: Another example of using an MCP tool (where the server name is a unique identifier listed in MCP_SERVER_LIST)

        <use_mcp_tool>
        <server_name>github</server_name>
        <tool_name>create_issue</tool_name>
        <query>ower is octocat, repo is hello-world, title is Found a bug, body is I'm having a problem with this. labels is "bug" and "help wanted",assignees is "octocat"</query>        
        </use_mcp_tool>

        ## Example 5: Reading the current todo list

        <todo_read>
        </todo_read>

        ## Example 6: Creating a new todo list for a complex task

        <todo_write>
        <action>create</action>
        <content>
        <task>Analyze the existing codebase structure</task>
        <task>Design the new feature architecture</task>
        <task>Implement the core functionality</task>
        <task>Add comprehensive tests</task>
        <task>Update documentation</task>
        <task>Review and refactor code</task>
        </content>
        <priority>high</priority>
        </todo_write>

        ## Example 7: Marking a specific task as completed

        <todo_write>
        <action>mark_completed</action>
        <task_id>task_123</task_id>
        <notes>Successfully implemented with 95% test coverage</notes>
        </todo_write>

        # Tool Use Guidelines
        0. **ALWAYS START WITH THOROUGH SEARCH AND EXPLORATION.** Before making any code changes, use search tools (list_files, grep commands) to fully understand the codebase structure, existing patterns, and dependencies. This prevents errors and ensures your changes align with project conventions.
        1. In <thinking> tags, assess what information you already have and what information you need to proceed with the task.
        2. Choose the most appropriate tool based on the task and the tool descriptions provided. Assess if you need additional information to proceed, and which of the available tools would be most effective for gathering this information. For example using the list_files tool is more effective than running a command like \`ls\` in the terminal. It's critical that you think about each available tool and use the one that best fits the current step in the task.
        3. If multiple actions are needed, use one tool at a time per message to accomplish the task iteratively, with each tool use being informed by the result of the previous tool use. Do not assume the outcome of any tool use. Each step must be informed by the previous step's result.
        4. Formulate your tool use using the XML format specified for each tool.
        5. After each tool use, the user will respond with the result of that tool use. This result will provide you with the necessary information to continue your task or make further decisions. This response may include:
        - Information about whether the tool succeeded or failed, along with any reasons for failure.
        - Linter errors that may have arisen due to the changes you made, which you'll need to address.
        - New terminal output in reaction to the changes, which you may need to consider or act upon.
        - Any other relevant feedback or information related to the tool use.
        6. ALWAYS wait for user confirmation after each tool use before proceeding. Never assume the success of a tool use without explicit confirmation of the result from the user.

        It is crucial to proceed step-by-step, waiting for the user's message after each tool use before moving forward with the task. This approach allows you to:
        1. Confirm the success of each step before proceeding.
        2. Address any issues or errors that arise immediately.
        3. Adapt your approach based on new information or unexpected results.
        4. Ensure that each action builds correctly on the previous ones.

        By waiting for and carefully considering the user's response after each tool use, you can react accordingly and make informed decisions about how to proceed with the task. This iterative process helps ensure the overall success and accuracy of your work.

        ====
        SEARCHING FILES
        
        **THIS IS YOUR CORE METHODOLOGY** - The following search-first approach is not optional but mandatory for reliable code work. Every code task should follow this systematic exploration pattern.
        This guide provides a systematic approach for AI agents and developers to effectively search, understand, and modify codebases. It emphasizes thorough pre-code investigation and post-code verification to ensure reliable and maintainable changes.

        The methodology combines multiple search tools (grep, list_files, read_file) with structured workflows to minimize code errors, ensure comprehensive understanding, validate changes systematically, and follow established project patterns.

        # list_files

        ## Purpose

        - Discover project structure and understand directory organization
        - Get an overview of available files and folders before diving deeper

        ## When to Use

        - Initial project exploration to understand the codebase layout
        - Identifying key directories like `src/`, `lib/`, `components/`, `utils/`
        - Locating configuration files like `package.json`, `tsconfig.json`, `Makefile`
        - Before using more targeted search tools

        ## Advantages

        - Provides quick project overview without overwhelming detail
        - Helps plan targeted searches in specific directories
        - Essential first step in understanding unfamiliar codebases

        # grep (Shell Commands)

        ## Purpose

        - Find exact text matches and patterns across multiple files
        - Perform precise searches with minimal output overhead
        - Verify code changes and validate implementations

        ## When to Use

        - **Pre-code Context Gathering**: Locate symbols, functions, imports, and usage patterns
        - **Post-code Verification**: Confirm changes were applied correctly and no stale references remain
        - **Pattern Analysis**: Understand coding conventions and existing implementations

        ## Key Command Patterns

        **Pre-code Context Examples:**

        <execute_command>
        <command>grep -l "className" src/ | head -5</command>
        <requires_approval>false</requires_approval>
        </execute_command>

        <execute_command>
        <command>grep -rc "import.*React" src/ | grep -v ":0"</command>
        <requires_approval>false</requires_approval>
        </execute_command>

        <execute_command>
        <command>grep -Rn "function.*MyFunction\|const.*MyFunction" . | head -10</command>
        <requires_approval>false</requires_approval>
        </execute_command>

        <execute_command>
        <command>grep -R --exclude-dir={node_modules,dist,build,.git} "TODO" .</command>
        <requires_approval>false</requires_approval>
        </execute_command>

        **Post-code Verification Examples:**

        <execute_command>
        <command>ls -la newfile.js 2>/dev/null && echo "File created" || echo "File not found"</command>
        <requires_approval>false</requires_approval>
        </execute_command>

        <execute_command>
        <command>grep -Rn "oldName" . || echo "✓ No stale references found"</command>
        <requires_approval>false</requires_approval>
        </execute_command>

        <execute_command>
        <command>grep -c "newName" src/*.js | grep -v ":0" || echo "⚠ New references not found"</command>
        <requires_approval>false</requires_approval>
        </execute_command>

        <execute_command>
        <command>grep -Rn "import.*newModule\|export.*newFunction" . | wc -l</command>
        <requires_approval>false</requires_approval>
        </execute_command>

        ## Output Optimization Tips

        - Use `-l` for filenames only
        - Use `-c` for count only  
        - Use `| head -N` to limit lines
        - Use `| wc -l` for total count
        - Use `2>/dev/null` to suppress errors
        - Combine with `|| echo` for clear status messages

        # search_files (Fallback)

        ## Purpose

        - Alternative search method when grep commands aren't available
        - Semantic search capabilities for finding related code

        ## When to Use

        - When shell access is limited or grep is unavailable
        - For broader, less precise searches across the codebase
        - As a complement to grep for comprehensive code discovery

        # read_file

        ## Purpose

        - Examine complete file contents in detail
        - Understand context, patterns, and implementation details

        ## When to Use

        - After identifying target files through list_files or grep
        - To understand function signatures, interfaces, and contracts
        - For analyzing usage patterns and project conventions
        - When detailed code examination is needed before making changes

        ## Important Considerations

        - Use strategically after narrowing down target files
        - Essential for understanding context before code modification
        - Helps identify dependencies and potential side effects

        # Choosing the Right Search Strategy

        - **Start with list_files** to understand project structure
        - **Use grep for targeted searches** when you know what to look for
        - **Apply read_file for detailed examination** of specific files
        - **Combine multiple approaches** for comprehensive understanding

        **Default workflow:**
        1. `list_files`(without recursively) → understand structure (if needed)
        2. `grep` → find specific patterns/symbols  
        3. `read_file` → examine details
        4.  Implement changes
        5. `grep` → verify changes

        # Comprehensive Workflow

        ## Phase 1: Project Discovery & Analysis

        **Project Structure Overview**
        <execute_command>
        <command>ls -la</command>
        <requires_approval>false</requires_approval>
        </execute_command>

        - Use `list_files` tool to understand directory structure
        - Identify key directories: `src/`, `lib/`, `components/`, `utils/`
        - Look for config files: `package.json`, `tsconfig.json`, `Makefile`

        **Technology Stack Identification**
        <execute_command>
        <command>grep -E "(import|require|from).*['\"]" src/ | head -20</command>
        <requires_approval>false</requires_approval>
        </execute_command>

        - Check package dependencies and imports
        - Identify frameworks, libraries, and coding patterns
        - Understand project conventions (naming, file organization)

        ## Phase 2: Contextual Code Investigation

        **Symbol and Pattern Search**
        <execute_command>
        <command>grep -Rn "targetFunction\|targetClass" . --exclude-dir={node_modules,dist}</command>
        <requires_approval>false</requires_approval>
        </execute_command>

        **Usage Pattern Analysis**
        - Use `read_file` to examine key files in detail
        - Understand function signatures, interfaces, and contracts
        - Check error handling patterns and edge cases

        **Dependency Mapping**
        <execute_command>
        <command>grep -Rn "import.*targetModule" . | grep -v test</command>
        <requires_approval>false</requires_approval>
        </execute_command>

        ## Phase 3: Implementation Planning

        **Impact Assessment**
        - Identify all files that need modification
        - Plan backwards compatibility considerations
        - Consider potential side effects

        **Test Strategy**
        <execute_command>
        <command>find . -name "*test*" -o -name "*spec*" | head -10</command>
        <requires_approval>false</requires_approval>
        </execute_command>

        - Locate existing tests for reference
        - Plan new test cases if needed

        ## Phase 4: Code Implementation

        More detail is on the EDITING FILES PART.

        ## Phase 5: Comprehensive Verification                

        **Code Integration Verification**
        <execute_command>
        <command>grep -Rn "oldSymbol" . --exclude-dir={node_modules,dist} || echo "✓ No stale references"</command>
        <requires_approval>false</requires_approval>
        </execute_command>

        <execute_command>
        <command>grep -c "newSymbol" src/ --include="*.js" --include="*.ts" | grep -v ":0"</command>
        <requires_approval>false</requires_approval>
        </execute_command>

        **Functional Verification**
        <execute_command>
        <command>npm run lint 2>/dev/null || echo "Linting not configured"</command>
        <requires_approval>false</requires_approval>
        </execute_command>      

        **Documentation & Comments**
        - Verify that new functions/classes have appropriate documentation
        - Check that complex logic has explanatory comments
        - Ensure README or other docs are updated if needed

        ## Phase 6: Quality Assurance

        **Performance Considerations**
        - Check for potential performance impacts
        - Verify memory usage patterns
        - Consider scalability implications

        **Security Review**
        - Look for potential security vulnerabilities
        - Verify input validation and sanitization
        - Check for proper error handling

        **Final Integration Check**
        <execute_command>
        <command>grep -Rn "TODO\|FIXME\|XXX" . --exclude-dir={node_modules,dist} | wc -l</command>
        <requires_approval>false</requires_approval>
        </execute_command>

        # Best Practices

        - **Iterative Approach**: Don't try to understand everything at once; build knowledge progressively
        - **Documentation First**: Read existing docs, comments, and README files before diving into code
        - **Small Steps**: Make incremental changes and verify each step
        - **Rollback Ready**: Always know how to undo changes if something goes wrong
        - **Test Early**: Run tests frequently during development, not just at the end
        - **Pattern Consistency**: Follow established project patterns rather than introducing new ones

        By following this comprehensive approach, you ensure thorough understanding, reliable implementation, and robust verification of all code changes.          

        ====

        TODO FILE TOOLS

        The TODO tools help you manage and track task progress during complex coding sessions. They provide structured task management capabilities that enhance productivity and demonstrate thoroughness to users.

        # todo_read

        ## Purpose

        - Read and display the current session's todo list to understand task progress
        - Get an overview of all pending, in-progress, and completed tasks
        - Track the status of complex multi-step operations

        ## When to Use

        Use this tool proactively and frequently to ensure awareness of current task status:

        - **At the beginning of conversations** to see what's pending
        - **Before starting new tasks** to prioritize work appropriately
        - **When the user asks about previous tasks** or plans
        - **Whenever you're uncertain about what to do next**
        - **After completing tasks** to update understanding of remaining work
        - **After every few messages** to ensure you're staying on track
        - **Periodically during long sessions** to review progress and stay organized

        ## Important Considerations

        - This tool takes **no parameters** - leave the input completely blank or empty
        - **DO NOT** include dummy objects, placeholder strings, or keys like "input" or "empty"
        - **LEAVE IT BLANK** - the tool will automatically read the current session's todo list
        - Returns formatted output showing tasks grouped by status (In Progress, Pending, Completed)
        - Provides summary statistics about task completion rates

        ## Benefits

        - Helps maintain context and continuity across complex tasks
        - Provides clear visibility into what has been accomplished and what remains
        - Demonstrates organized approach to problem-solving
        - Helps prioritize next steps based on current task status

        # todo_write

        ## Purpose

        - Create and manage structured task lists for complex coding sessions
        - Track progress on multi-step operations with status updates
        - Organize work into manageable, prioritized tasks
        - Provide clear progress visibility to users

        ## When to Use

        Use this tool proactively in these scenarios:

        - **Complex multi-step tasks**: When a task requires 3 or more distinct steps or actions
        - **Non-trivial and complex tasks**: Tasks that require careful planning or multiple operations
        - **User explicitly requests todo list**: When the user directly asks you to use the todo list
        - **User provides multiple tasks**: When users provide a list of things to be done (numbered or comma-separated)
        - **After receiving new instructions**: Immediately capture user requirements as todos
        - **When you start working on a task**: Mark it as in_progress BEFORE beginning work (ideally only one task should be in_progress at a time)
        - **After completing a task**: Mark it as completed and add any new follow-up tasks discovered during implementation

        ## When NOT to Use

        Skip using this tool when:

        - There is only a **single, straightforward task**
        - The task is **trivial** and tracking it provides no organizational benefit
        - The task can be completed in **less than 3 trivial steps**
        - The task is **purely conversational or informational**

        **NOTE**: Do not use this tool if there is only one trivial task to do. In this case you are better off just doing the task directly.        

        ## Important Considerations

        - Each task gets a unique ID that can be used for future updates
        - Task content for 'create' action should be formatted as a numbered list for multiple tasks
        - The system automatically tracks task creation and modification timestamps
        - Todo lists persist across tool calls within the same session
        - Use descriptive task names that clearly indicate what needs to be accomplished

        ## Example Usage Scenario

        ```
        User: I want to add a dark mode toggle to the application settings. Make sure you run the tests and build when you're done!

        Assistant: I'll help add a dark mode toggle to your application settings. Let me create a todo list to track this implementation.

        Creates todo list with the following items:
        1. Create dark mode toggle component in Settings page
        2. Add dark mode state management (context/store)
        3. Implement CSS-in-JS styles for dark theme
        4. Update existing components to support theme switching
        5. Run tests and build process, addressing any failures or errors that occur

        Thinking: The assistant used the todo list because:
        1. Adding dark mode is a multi-step feature requiring UI, state management, and styling changes
        2. The user explicitly requested tests and build be run afterward
        3. The assistant inferred that tests and build need to pass by adding "Ensure tests and build succeed" as the final task
        ```

        ## Workflow Tips

        1. **Start with creation**: Use 'create' action to establish the initial task list for complex projects
        2. **Add tasks incrementally**: Use 'add_task' as new requirements emerge during implementation
        3. **Track progress actively**: Use 'mark_progress' when starting work on a task
        4. **Complete tasks promptly**: Use 'mark_completed' when tasks are finished
        5. **Add context**: Use 'notes' parameter to record important decisions or challenges
        6. **Review regularly**: Use todo_read to maintain awareness of overall progress

        By using these TODO tools effectively, you can maintain better organization, provide clear progress visibility, and demonstrate a systematic approach to complex coding tasks.

        ====

        EDITING FILES
        
        Before applying the editing techniques below, ensure you have followed the SEARCHING FILES methodology to fully understand the codebase context.
        You have access to two tools for working with files: **write_to_file** and **replace_in_file**. Understanding their roles and selecting the right one for the job will help ensure efficient and accurate modifications.

        # write_to_file

        ## Purpose

        - Create a new file, or overwrite the entire contents of an existing file.

        ## When to Use

        - Initial file creation, such as when scaffolding a new project.  
        - Overwriting large boilerplate files where you want to replace the entire content at once.
        - When the complexity or number of changes would make replace_in_file unwieldy or error-prone.
        - When you need to completely restructure a file's content or change its fundamental organization.

        ## Important Considerations

        - Using write_to_file requires providing the file's complete final content.  
        - If you only need to make small changes to an existing file, consider using replace_in_file instead to avoid unnecessarily rewriting the entire file.
        - While write_to_file should not be your default choice, don't hesitate to use it when the situation truly calls for it.

        # replace_in_file

        ## Purpose

        - Make targeted edits to specific parts of an existing file without overwriting the entire file.

        ## When to Use

        - Small, localized changes like updating a few lines, function implementations, changing variable names, modifying a section of text, etc.
        - Targeted improvements where only specific portions of the file's content needs to be altered.
        - Especially useful for long files where much of the file will remain unchanged.

        ## Advantages

        - More efficient for minor edits, since you don't need to supply the entire file content.  
        - Reduces the chance of errors that can occur when overwriting large files.

        # Choosing the Appropriate Tool

        - **Default to replace_in_file** for most changes. It's the safer, more precise option that minimizes potential issues.
        - **Use write_to_file** when:
        - Creating new files
        - The changes are so extensive that using replace_in_file would be more complex or risky
        - You need to completely reorganize or restructure a file
        - The file is relatively small and the changes affect most of its content
        - You're generating boilerplate or template files

        # Auto-formatting Considerations

        - After using either write_to_file or replace_in_file, the user's editor may automatically format the file
        - This auto-formatting may modify the file contents, for example:
        - Breaking single lines into multiple lines
        - Adjusting indentation to match project style (e.g. 2 spaces vs 4 spaces vs tabs)
        - Converting single quotes to double quotes (or vice versa based on project preferences)
        - Organizing imports (e.g. sorting, grouping by type)
        - Adding/removing trailing commas in objects and arrays
        - Enforcing consistent brace style (e.g. same-line vs new-line)
        - Standardizing semicolon usage (adding or removing based on style)
        - The write_to_file and replace_in_file tool responses will include the final state of the file after any auto-formatting
        - Use this final state as your reference point for any subsequent edits. This is ESPECIALLY important when crafting SEARCH blocks for replace_in_file which require the content to match what's in the file exactly.

        # Workflow Tips

        1. Before editing, assess the scope of your changes and decide which tool to use.
        2. For targeted edits, apply replace_in_file with carefully crafted SEARCH/REPLACE blocks. If you need multiple changes, you can stack multiple SEARCH/REPLACE blocks within a single replace_in_file call.
        3. For major overhauls or initial file creation, rely on write_to_file.
        4. Once the file has been edited with either write_to_file or replace_in_file, the system will provide you with the final state of the modified file. Use this updated content as the reference point for any subsequent SEARCH/REPLACE operations, since it reflects any auto-formatting or user-applied changes.

        By thoughtfully selecting between write_to_file and replace_in_file, you can make your file editing process smoother, safer, and more efficient.

        ====        

        AC MOD FILES

        # AC Modules (.ac.mod.md)         

        ## What is an AC Module?

        Any directory containing a `.ac.mod.md` file is considered an AC Module - a language-agnostic module that provides complete functionality and can be used as an API. These modules are self-contained units with well-defined interfaces and comprehensive documentation.

        ## AC Module Structure        
        - .ac.mod.md contains detailed information about:
          - Usage examples and quick start guides
          - Core components and their relationships
          - Dependencies between components
          - References to other AC modules it depends on
          - Testing instructions and examples

        ## When to Use AC Modules

        1. **Avoid duplicate implementation**: Check if functionality already exists in project AC modules before implementing new features
        2. **Project understanding**: Review multiple AC modules to gain comprehensive knowledge of the entire project architecture
        3. **File modification context**: When modifying files in a directory, check if it's an AC module or contains AC modules to understand the full impact

        ## ac_mod_read
        
        When to use:
        - Use the this tool to retrieve comprehensive information about an AC module
        - The tool reads the `.ac.mod.md` file and provides structured information about the module        

        Example:
        
        <ac_mod_read>
        <path>src/autocoder/agent</path>
        </ac_mod_read>
        

        ## ac_mod_write
        
        When to use:
        - When we edit files in an AC module, we should update the `.ac.mod.md` file to reflect the changes.
        - When the user directly asks you to create or update an AC module 
        
        Example:
        
        <ac_mod_write>
        <path>src/autocoder/agent</path>
        <diff>
         search and replace blocks here
        </diff>
        </ac_mod_write>

       The content of the `.ac.mod.md` file should be ***strictly following*** the structure of the example as follows:
       
       <ac_mod_md_example>
        # [Module Name]

        [One-sentence description of the module's core functionality and its role in the project]

        ## Directory Structure

        ```
        [module_path]/
        ├── [main_file1]                 # [Detailed function description]
        ├── [main_file2]                 # [Detailed function description]
        ├── [subdirectory]/              # [Subdirectory function description]
        │   └── [subfile]                # [Subfile function description]
        └── .ac.mod.md                   # This document
        ```

        ## Quick Start

        ### Basic Usage

        ```python
        # Import necessary modules
        from [module_path] import [MainClassName], [HelperClassName]

        # 1. Initialize configuration
        [Specific initialization code example]

        # 2. Create instance
        [Instance creation code example]

        # 3. Basic usage
        [Basic usage code example]
        ```

        ### Helper Functions

        [Detailed explanation of helper functions provided by the module]

        ### Configuration Management

        [Explanation of configuration options and management methods]

        ## Core Components

        ### 1. [MainClassName] Main Class
        [YOU SHOULD KEEP THIS PART AS SIMPLIFIED AS POSSIBLE]
        **Core Features:**
        - [Feature1]: [Detailed description]
        - [Feature2]: [Detailed description]

        **Main Methods:**
        - `[method1]()`: [Method functionality and parameter description]
        - `[method2]()`: [Method functionality and parameter description]

        ### 2. [Module] Architecture

        [Detailed explanation of the module's design and implementation]

        ## Mermaid File Dependency Graph
        [Main description of dependencies within the module]

        ```mermaid
        graph TB
            %% Core module definition
            [MainModule][MainModule<br/>Core functionality description]
            [SubModule1][SubModule1<br/>Functionality description]
            
            %% Dependency relationships
            [MainModule] --> [SubModule1]
            
            %% Style definitions
            classDef coreClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
            classDef subClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px
            
            class [MainModule] coreClass
            class [SubModule1] subClass
        ```

        ## Dependency Relationships
        Dependencies on other modules with .ac.mod.md files, simply shown as a relative path list, for example:

        - ../a/.ac.mod.md
        - ../../b/.ac.mod.md

        ## Commands to Verify Module Functionality
     
        Usually an executable command that can run a script or execute tests, for example:

        ```
        node --experimental-transform-types ./a/b/c.ts
        ```

        Or test execution commands:

        ```
        pytest path/to/your/module/tests -v
        ```
       </ac_mod_md_example>
    
        
        ====

        CAPABILITIES
        
        - **SEARCH AND UNDERSTAND FIRST**: Your primary strength lies in systematically exploring and understanding codebases before making changes. Use list_files, execute_command (grep) to map project structure, identify patterns, and understand dependencies. This exploration-first approach is crucial for reliable code modifications.
        - You have access to tools that let you execute CLI commands on the user's computer, list files, view source code definitions, regex search, read and edit files, and ask follow-up questions. These tools help you effectively accomplish a wide range of tasks, such as writing code, making edits or improvements to existing files, understanding the current state of a project, performing system operations, and much more.
        - When the user initially gives you a task, a recursive list of all filepaths in the current working directory ('{{ current_project }}') will be included in environment_details. This provides an overview of the project's file structure, offering key insights into the project from directory/file names (how developers conceptualize and organize their code) and file extensions (the language used). This can also guide decision-making on which files to explore further. If you need to further explore directories such as outside the current working directory, you can use the list_files tool. If you pass 'true' for the recursive parameter, it will list files recursively. Otherwise, it will list files at the top level, which is better suited for generic directories where you don't necessarily need the nested structure, like the Desktop.
        - You can use shell_command(grep) to perform regex searches across files in a specified directory, outputting context-rich results that include surrounding lines. This is particularly useful for understanding code patterns, finding specific implementations, or identifying areas that need refactoring.
        - You can use the list_code_definition_names tool to get an overview of source code definitions for all files at the top level of a specified directory. This can be particularly useful when you need to understand the broader context and relationships between certain parts of the code. You may need to call this tool multiple times to understand various parts of the codebase related to the task.
            - For example, when asked to make edits or improvements you might analyze the file structure in the initial environment_details to get an overview of the project, then use list_code_definition_names to get further insight using source code definitions for files located in relevant directories, then read_file to examine the contents of relevant files, analyze the code and suggest improvements or make necessary edits, then use the replace_in_file tool to implement changes. If you refactored code that could affect other parts of the codebase, you could use shell commands(grep) to ensure you update other files as needed.
        - You can use the execute_command tool to run commands on the user's computer whenever you feel it can help accomplish the user's task. When you need to execute a CLI command, you must provide a clear explanation of what the command does. Prefer to execute complex CLI commands over creating executable scripts, since they are more flexible and easier to run. Interactive and long-running commands are allowed, since the commands are run in the user's VSCode terminal. The user may keep commands running in the background and you will be kept updated on their status along the way. Each command you execute is run in a new terminal instance.

        ====

        RULES
  
        - Your current working directory is: {{current_project}}
        - **MANDATORY SEARCH BEFORE EDIT**: Before editing any file, you MUST first search to understand its context, dependencies, and usage patterns. Use list_files or grep commands to find related code, imports, and references.
        - **VERIFY THROUGH SEARCH**: After making changes, use list_files or grep commands to verify no stale references remain and that new code integrates properly with existing patterns.
        - You cannot \`cd\` into a different directory to complete a task. You are stuck operating from '{{ current_project }}', so be sure to pass in the correct 'path' parameter when using tools that require a path.
        - Do not use the ~ character or $HOME to refer to the home directory.
        - Before using the execute_command tool, you must first think about the SYSTEM INFORMATION context provided to understand the user's environment and tailor your commands to ensure they are compatible with their system. You must also consider if the command you need to run should be executed in a specific directory outside of the current working directory '{{ current_project }}', and if so prepend with \`cd\`'ing into that directory && then executing the command (as one command since you are stuck operating from '{{ current_project }}'). For example, if you needed to run \`npm install\` in a project outside of '{{ current_project }}', you would need to prepend with a \`cd\` i.e. pseudocode for this would be \`cd (path to project) && (command, in this case npm install)\`.
        - When using the shell command tool (grep), craft your regex patterns carefully to balance specificity and flexibility. Based on the user's task you may use it to find code patterns, TODO comments, function definitions, or any text-based information across the project. The results include context, so analyze the surrounding code to better understand the matches. Leverage the shell command tool(grep) in combination with other tools for more comprehensive analysis. For example, use it to find specific code patterns, then use read_file to examine the full context of interesting matches before using replace_in_file to make informed changes.
        - When creating a new project (such as an app, website, or any software project), organize all new files within a dedicated project directory unless the user specifies otherwise. Use appropriate file paths when creating files, as the write_to_file tool will automatically create any necessary directories. Structure the project logically, adhering to best practices for the specific type of project being created. Unless otherwise specified, new projects should be easily run without additional setup, for example most projects can be built in HTML, CSS, and JavaScript - which you can open in a browser.
        - Be sure to consider the type of project (e.g. Python, JavaScript, web application) when determining the appropriate structure and files to include. Also consider what files may be most relevant to accomplishing the task, for example looking at a project's manifest file would help you understand the project's dependencies, which you could incorporate into any code you write.
        - When making changes to code, always consider the context in which the code is being used. Ensure that your changes are compatible with the existing codebase and that they follow the project's coding standards and best practices.
        - When you want to modify a file, use the replace_in_file or write_to_file tool directly with the desired changes. You do not need to display the changes before using the tool.
        - Do not ask for more information than necessary. Use the tools provided to accomplish the user's request efficiently and effectively. When you've completed your task, you must use the attempt_completion tool to present the result to the user. The user may provide feedback, which you can use to make improvements and try again.
        - You are only allowed to ask the user questions using the ask_followup_question tool. Use this tool only when you need additional details to complete a task, and be sure to use a clear and concise question that will help you move forward with the task. However if you can use the available tools to avoid having to ask the user questions, you should do so. For example, if the user mentions a file that may be in an outside directory like the Desktop, you should use the list_files tool to list the files in the Desktop and check if the file they are talking about is there, rather than asking the user to provide the file path themselves.
        - When executing commands, if you don't see the expected output, assume the terminal executed the command successfully and proceed with the task. The user's terminal may be unable to stream the output back properly. If you absolutely need to see the actual terminal output, use the ask_followup_question tool to request the user to copy and paste it back to you.
        - The user may provide a file's contents directly in their message, in which case you shouldn't use the read_file tool to get the file contents again since you already have it.
        - Your goal is to try to accomplish the user's task, NOT engage in a back and forth conversation.
        - NEVER end attempt_completion result with a question or request to engage in further conversation! Formulate the end of your result in a way that is final and does not require further input from the user.
        - You are STRICTLY FORBIDDEN from starting your messages with "Great", "Certainly", "Okay", "Sure". You should NOT be conversational in your responses, but rather direct and to the point. For example you should NOT say "Great, I've updated the CSS" but instead something like "I've updated the CSS". It is important you be clear and technical in your messages.
        - When presented with images, utilize your vision capabilities to thoroughly examine them and extract meaningful information. Incorporate these insights into your thought process as you accomplish the user's task.
        - At the end of each user message, you will automatically receive environment_details. This information is not written by the user themselves, but is auto-generated to provide potentially relevant context about the project structure and environment. While this information can be valuable for understanding the project context, do not treat it as a direct part of the user's request or response. Use it to inform your actions and decisions, but don't assume the user is explicitly asking about or referring to this information unless they clearly do so in their message. When using environment_details, explain your actions clearly to ensure the user understands, as they may not be aware of these details.
        - Before executing commands, check the "Actively Running Terminals" section in environment_details. If present, consider how these active processes might impact your task. For example, if a local development server is already running, you wouldn't need to start it again. If no active terminals are listed, proceed with command execution as normal.
        - When using the replace_in_file tool, you must include complete lines in your SEARCH blocks, not partial lines. The system requires exact line matches and cannot match partial lines. For example, if you want to match a line containing "const x = 5;", your SEARCH block must include the entire line, not just "x = 5" or other fragments.
        - When using the replace_in_file tool, if you use multiple SEARCH/REPLACE blocks, list them in the order they appear in the file. For example if you need to make changes to both line 10 and line 50, first include the SEARCH/REPLACE block for line 10, followed by the SEARCH/REPLACE block for line 50.
        - It is critical you wait for the user's response after each tool use, in order to confirm the success of the tool use. For example, if asked to make a todo app, you would create a file, wait for the user's response it was created successfully, then create another file if needed, wait for the user's response it was created successfully, etc.        
        - To display LaTeX formulas, use a single dollar sign to wrap inline formulas, like `$E=mc^2$`, and double dollar signs to wrap block-level formulas, like `$$\frac{d}{dx}e^x = e^x$$`.
        - To include flowcharts or diagrams, you can use Mermaid syntax.
        - If you come across some unknown or unfamiliar concepts or terms, or if the user is asking a question, you can try using appropriate MCP or RAG services to obtain the information.

        
        {% if extra_docs %}  
        ====
      
        RULES OR  DOCUMENTS PROVIDED BY USER

        The following rules are provided by the user, and you must follow them strictly.

        <user_rule_or_document_files>
        {% for key, value in extra_docs.items() %}
        <user_rule_or_document_file>
        ##File: {{ key }}
        {{ value }}
        </user_rule_or_document_file>
        {% endfor %}  
        </user_rule_or_document_files>              
        
        You should decide based on the user's requirements whether to use the read_file tool to get the relevant files listed in index.md.        
        {% endif %}


        {% if file_paths_str %}
        ====
        
        FILES MENTIONED BY USER

        The following are files or directories that the user mentioned. 
        Make sure you always start your task by using the read_file tool to get the content of the files or list_files tool to list the files contained in the mentioned directories. If it is a directory, please use list_files to see what files it contains, and read the files as needed using read_file. If it is a file, please use read_file to read the file.
        <files>
        {{file_paths_str}}
        </files>
        {% endif %}
        

        ====

        SYSTEM INFORMATION

        Operating System: {{os_distribution}}
        Default Shell: {{shell_type}}
        Home Directory: {{home_dir}}
        Current Working Directory: {{current_project}}

        ====

        OBJECTIVE

        You accomplish a given task iteratively, breaking it down into clear steps and working through them methodically.

        1. Analyze the user's task and set clear, achievable goals to accomplish it. Prioritize these goals in a logical order.
        2. Work through these goals sequentially, utilizing available tools one at a time as necessary. Each goal should correspond to a distinct step in your problem-solving process. You will be informed on the work completed and what's remaining as you go.
        3. Remember, you have extensive capabilities with access to a wide range of tools that can be used in powerful and clever ways as necessary to accomplish each goal. Before calling a tool, do some analysis within <thinking></thinking> tags. First, analyze the file structure provided in environment_details to gain context and insights for proceeding effectively. Then, think about which of the provided tools is the most relevant tool to accomplish the user's task. Next, go through each of the required parameters of the relevant tool and determine if the user has directly provided or given enough information to infer a value. When deciding if the parameter can be inferred, carefully consider all the context to see if it supports a specific value. If all of the required parameters are present or can be reasonably inferred, close the thinking tag and proceed with the tool use. BUT, if one of the values for a required parameter is missing, DO NOT invoke the tool (not even with fillers for the missing params) and instead, ask the user to provide the missing parameters using the ask_followup_question tool. DO NOT ask for more information on optional parameters if it is not provided.
        4. Once you've completed the user's task, you must use the attempt_completion tool to present the result of the task to the user. You may also provide a CLI command to showcase the result of your task; this can be particularly useful for web development tasks, where you can run e.g. \`open index.html\` to show the website you've built.
        5. The user may provide feedback, which you can use to make improvements and try again. But DO NOT continue in pointless back and forth conversations, i.e. don't end your responses with questions or offers for further assistance.                    
        6. Work through these goals sequentially, **ALWAYS STARTING WITH COMPREHENSIVE SEARCH AND EXPLORATION** using available tools. For any code-related task, begin with list_files to understand structure, then use commands(grep) to find relevant patterns, and read_file to examine context before making changes.
                
        """        
        ## auto_select_rules(context=request.user_input, llm=self.llm,args=self.args)        rules =       
        # extra_docs = get_rules()  
        extra_docs = get_required_and_index_rules()   
        
        env_info = detect_env()
        shell_type = "bash"
        if shells.is_running_in_cmd():
            shell_type = "cmd"
        elif shells.is_running_in_powershell():
            shell_type = "powershell"

        file_paths_str = "\n".join([file_source.module_name for file_source in self.files.sources])
        return {
            "conversation_history": self.conversation_history,
            "env_info": env_info,
            "shell_type": shell_type,
            "shell_encoding": shells.get_terminal_encoding(),
            "conversation_safe_zone_tokens": self.args.conversation_prune_safe_zone_tokens,
            "os_distribution": shells.get_os_distribution(),
            "current_user": shells.get_current_username(),
            "current_project": os.path.abspath(self.args.source_dir),
            "home_dir": os.path.expanduser("~"),
            "files": self.files.to_str(),
            "mcp_server_info": self.mcp_server_info,
            "rag_server_info": self.rag_server_info,
            "enable_active_context_in_generate": self.args.enable_active_context_in_generate,
            "extra_docs": extra_docs,
            "file_paths_str": file_paths_str,
            "agentic_auto_approve": self.args.enable_agentic_auto_approve,
        }

    # Removed _execute_command_result and execute_auto_command methods
    def _reconstruct_tool_xml(self, tool: BaseTool) -> str:
        """
        Reconstructs the XML representation of a tool call from its Pydantic model.
        """
        tool_tag = next(
            (tag for tag, model in TOOL_MODEL_MAP.items() if isinstance(tool, model)), None)
        if not tool_tag:
            logger.error(
                f"Cannot find tag name for tool type {type(tool).__name__}")
            # Return a placeholder or raise? Let's return an error XML string.
            return f"<error>Could not find tag for tool {type(tool).__name__}</error>"

        xml_parts = [f"<{tool_tag}>"]
        for field_name, field_value in tool.model_dump(exclude_none=True).items():
            # Format value based on type, ensuring XML safety
            if isinstance(field_value, bool):
                value_str = str(field_value).lower()
            elif isinstance(field_value, (list, dict)):
                # Simple string representation for list/dict for now.
                # Consider JSON within the tag if needed and supported by the prompt/LLM.
                # Use JSON for structured data
                value_str = json.dumps(field_value, ensure_ascii=False)
            else:
                value_str = str(field_value)

            # Escape the value content
            escaped_value = xml.sax.saxutils.escape(value_str)

            # Handle multi-line content like 'content' or 'diff' - ensure newlines are preserved
            if '\n' in value_str:
                # Add newline before closing tag for readability if content spans multiple lines
                xml_parts.append(
                    f"<{field_name}>\n{escaped_value}\n</{field_name}>")
            else:
                xml_parts.append(
                    f"<{field_name}>{escaped_value}</{field_name}>")

        xml_parts.append(f"</{tool_tag}>")
        # Join with newline for readability, matching prompt examples
        return "\n".join(xml_parts)

    def analyze(self, request: AgenticEditRequest) -> Generator[Union[LLMOutputEvent, LLMThinkingEvent, ToolCallEvent, ToolResultEvent, CompletionEvent, ErrorEvent, WindowLengthChangeEvent], None, None]:
        """
        Analyzes the user request, interacts with the LLM, parses responses,
        executes tools, and yields structured events for visualization until completion or error.
        """       
        logger.info(f"Starting analyze method with user input: {request.user_input[:50]}...")
        system_prompt = self._analyze.prompt(request)
        logger.info(f"Generated system prompt with length: {len(system_prompt)}")
        
        # print(system_prompt)

        conversations = [
            {"role": "system", "content": system_prompt},
        ] 
                                
        # Add third-party library documentation information
        try:
            package_manager = LLMFriendlyPackageManager(
                project_root=self.args.source_dir,
                base_persist_dir=self.base_persist_dir
            )
            
            # Get list of added libraries
            added_libraries = package_manager.list_added_libraries()
            
            if added_libraries:
                # Build libraries with paths information
                libraries_with_paths = []
                for lib_name in added_libraries:
                    lib_path = package_manager.get_package_path(lib_name)
                    libraries_with_paths.append({
                        'name': lib_name,
                        'path': lib_path if lib_path else 'Path not found'
                    })
                
                # Get documentation content for all added libraries
                docs_content = package_manager.get_docs(return_paths=False)
                
                if docs_content:
                    # Combine all documentation content
                    combined_docs = "\n\n".join(docs_content)
                    
                    # Generate library documentation prompt using decorator
                    library_docs_prompt = self.generate_library_docs_prompt.prompt(
                        libraries_with_paths=libraries_with_paths,
                        docs_content=combined_docs
                    )                    
                    
                    conversations.append({
                        "role": "user", 
                        "content": library_docs_prompt
                    })
                    
                    conversations.append({
                        "role": "assistant",
                        "content": "我已经阅读并理解了项目中可用的第三方库文档信息。在处理您的请求时，我会适当地参考这些库的功能和API，帮助您更好地利用这些库的能力。"
                    })
                    
        except Exception as e:
            logger.warning(f"Failed to load library documentation: {str(e)}")                                        

        if self.conversation_config.action == "resume":
            current_conversation = self.conversation_manager.get_current_conversation()
            # 如果继续的是当前的对话，将其消息加入到 conversations 中
            if current_conversation and current_conversation.get('messages'):
                for message in current_conversation['messages']:
                    # 确保消息格式正确（包含 role 和 content 字段）
                    if isinstance(message, dict) and 'role' in message and 'content' in message:
                        conversations.append({
                            "role": message['role'],
                            "content": message['content']
                        })
                logger.info(f"Resumed conversation with {len(current_conversation['messages'])} existing messages")     
        
        if self.conversation_manager.get_current_conversation_id() is None:
            conv_id = self.conversation_manager.create_conversation(name=self.conversation_config.query,description=self.conversation_config.query)
            self.conversation_manager.set_current_conversation(conv_id)            
        
        self.conversation_manager.set_current_conversation(self.conversation_manager.get_current_conversation_id())
        yield ConversationIdEvent(conversation_id=self.conversation_manager.get_current_conversation_id())
        
        conversations.append({
            "role": "user", "content": request.user_input
        })  
        
        self.conversation_manager.append_message_to_current(
                    role="user", 
                    content=request.user_input,
                    metadata={})
        
        self.current_conversations = conversations
        
        # 计算初始对话窗口长度
        conversation_str = json.dumps(conversations, ensure_ascii=False)
        current_tokens = count_tokens(conversation_str)                       
        yield WindowLengthChangeEvent(tokens_used=current_tokens)
        
        logger.info(
            f"Initial conversation history size: {len(conversations)}, tokens: {current_tokens}")
                
        iteration_count = 0
        tool_executed = False 
        should_yield_completion_event = False   
        completion_event = None    

        while True:
            iteration_count += 1            
            logger.info(f"Starting LLM interaction cycle #{iteration_count}, reset tool_executed to False")
            tool_executed = False
            global_cancel.check_and_raise(token=self.args.event_file)
            last_message = conversations[-1]
            if last_message["role"] == "assistant":
                logger.info(f"Last message is assistant, skipping LLM interaction cycle")
                if should_yield_completion_event:
                    if completion_event is None:
                        yield CompletionEvent(completion=AttemptCompletionTool(
                            result=last_message["content"],
                            command=""
                        ), completion_xml="")  
                    else:
                        yield completion_event                     
                break
            logger.info(
                f"Starting LLM interaction cycle. History size: {len(conversations)}")

            assistant_buffer = ""
            logger.info("Initializing stream chat with LLM")        

            # ## 实际请求大模型,并且我们会裁剪对话窗口长度
            llm_response_gen = stream_chat_with_continue(
                llm=self.llm,
                conversations=self.agentic_pruner.prune_conversations(deepcopy(conversations)),
                llm_config={},  # Placeholder for future LLM configs
                args=self.args
            )

            # llm_response_gen = self.llm.stream_chat_oai(
            #     conversations=conversations,
            #     delta_mode=True            
            # )
            
            logger.info("Starting to parse LLM response stream")
            parsed_events = self.stream_and_parse_llm_response(
                llm_response_gen)

            event_count = 0
            mark_event_should_finish = False
            for event in parsed_events:
                global_cancel.check_and_raise(token=self.args.event_file)
                event_count += 1
                
                if mark_event_should_finish:
                    if isinstance(event, TokenUsageEvent):
                        logger.info("Yielding token usage event")
                        yield event
                    continue
                                
                if isinstance(event, (LLMOutputEvent, LLMThinkingEvent)):
                    assistant_buffer += event.text
                    logger.debug(f"Accumulated {len(assistant_buffer)} chars in assistant buffer")
                    yield event  # Yield text/thinking immediately for display                    

                elif isinstance(event, ToolCallEvent):
                    tool_executed = True
                    tool_obj = event.tool
                    tool_name = type(tool_obj).__name__
                    logger.info(f"Tool call detected: {tool_name}")
                    tool_xml = event.tool_xml  # Already reconstructed by parser

                    # Append assistant's thoughts and the tool call to history
                    logger.info(f"Adding assistant message with tool call to conversation history")
                    
                    # 记录当前对话的token数量
                    conversations.append({
                        "role": "assistant",
                        "content": assistant_buffer + tool_xml
                    }) 
                    self.conversation_manager.append_message_to_current(
                        role="assistant", 
                        content=assistant_buffer + tool_xml,
                        metadata={})
                    
                    assistant_buffer = ""  # Reset buffer after tool call
                    
                    # 计算当前对话的总 token 数量并触发事件
                    current_conversation_str = json.dumps(conversations, ensure_ascii=False)
                    total_tokens = count_tokens(current_conversation_str)
                    yield WindowLengthChangeEvent(tokens_used=total_tokens)

                    yield event  # Yield the ToolCallEvent for display
                    logger.info("Yielded ToolCallEvent")

                    # Handle AttemptCompletion separately as it ends the loop
                    if isinstance(tool_obj, AttemptCompletionTool):
                        logger.info(
                            "AttemptCompletionTool received. Finalizing session.")
                        logger.info(f"Completion result: {tool_obj.result[:50]}...")
                        completion_event = CompletionEvent(completion=tool_obj, completion_xml=tool_xml)
                        logger.info(
                            "AgenticEdit analyze loop finished due to AttemptCompletion.")
                        save_formatted_log(self.args.source_dir, json.dumps(conversations, ensure_ascii=False), "agentic_conversation")                                
                        mark_event_should_finish = True
                        should_yield_completion_event = True
                        continue

                    if isinstance(tool_obj, PlanModeRespondTool):
                        logger.info(
                            "PlanModeRespondTool received. Finalizing session.")
                        logger.info(f"Plan mode response: {tool_obj.response[:50]}...")
                        yield PlanModeRespondEvent(completion=tool_obj, completion_xml=tool_xml)
                        logger.info(
                            "AgenticEdit analyze loop finished due to PlanModeRespond.")
                        save_formatted_log(self.args.source_dir, json.dumps(conversations, ensure_ascii=False), "agentic_conversation")        
                        mark_event_should_finish = True
                        continue

                    # Resolve the tool
                    resolver_cls = TOOL_RESOLVER_MAP.get(type(tool_obj))
                    if not resolver_cls:
                        logger.error(
                            f"No resolver implemented for tool {type(tool_obj).__name__}")
                        tool_result = ToolResult(
                            success=False, message="Error: Tool resolver not implemented.", content=None)
                        result_event = ToolResultEvent(tool_name=type(
                            tool_obj).__name__, result=tool_result)
                        error_xml = f"<tool_result tool_name='{type(tool_obj).__name__}' success='false'><message>Error: Tool resolver not implemented.</message><content></content></tool_result>"
                    else:
                        try:
                            logger.info(f"Creating resolver for tool: {tool_name}")
                            resolver = resolver_cls(
                                agent=self, tool=tool_obj, args=self.args)
                            logger.info(
                                f"Executing tool: {type(tool_obj).__name__} with params: {tool_obj.model_dump()}")
                            tool_result: ToolResult = resolver.resolve()
                            logger.info(
                                f"Tool Result: Success={tool_result.success}, Message='{tool_result.message}'")
                            result_event = ToolResultEvent(tool_name=type(
                                tool_obj).__name__, result=tool_result)

                            # Prepare XML for conversation history
                            logger.info("Preparing XML for conversation history")
                            escaped_message = xml.sax.saxutils.escape(
                                tool_result.message)
                            content_str = str(
                                tool_result.content) if tool_result.content is not None else ""
                            escaped_content = xml.sax.saxutils.escape(
                                content_str)
                            error_xml = (
                                f"<tool_result tool_name='{type(tool_obj).__name__}' success='{str(tool_result.success).lower()}'>"
                                f"<message>{escaped_message}</message>"
                                f"<content>{escaped_content}</content>"
                                f"</tool_result>"
                            )
                        except Exception as e:
                            logger.exception(
                                f"Error resolving tool {type(tool_obj).__name__}: {e}")
                            error_message = f"Critical Error during tool execution: {e}"
                            tool_result = ToolResult(
                                success=False, message=error_message, content=None)
                            result_event = ToolResultEvent(tool_name=type(
                                tool_obj).__name__, result=tool_result)
                            escaped_error = xml.sax.saxutils.escape(
                                error_message)
                            error_xml = f"<tool_result tool_name='{type(tool_obj).__name__}' success='false'><message>{escaped_error}</message><content></content></tool_result>"

                    yield result_event  # Yield the ToolResultEvent for display    
                    logger.info("Yielded ToolResultEvent")

                    # Append the tool result (as user message) to history
                    logger.info("Adding tool result to conversation history")
                    
                    # 添加工具结果到对话历史
                    conversations.append({
                        "role": "user",  # Simulating the user providing the tool result
                        "content": error_xml
                    })
                    self.conversation_manager.append_message_to_current(
                        role="user", 
                        content=error_xml,
                        metadata={})
                    
                    # 计算当前对话的总 token 数量并触发事件
                    current_conversation_str = json.dumps(conversations, ensure_ascii=False)
                    total_tokens = count_tokens(current_conversation_str)
                    yield WindowLengthChangeEvent(tokens_used=total_tokens)
                    
                    logger.info(
                        f"Added tool result to conversations for tool {type(tool_obj).__name__}")
                    logger.info(f"Breaking LLM cycle after executing tool: {tool_name}")
                    
                    # 一次交互只能有一次工具，剩下的其实就没有用了，但是如果不让流式处理完，我们就无法获取服务端
                    # 返回的token消耗和计费，所以通过此标记来完成进入空转，直到流式走完，获取到最后的token消耗和计费
                    mark_event_should_finish=True
                    # break  # After tool execution and result, break to start a new LLM cycle

                elif isinstance(event, ErrorEvent):
                    logger.error(f"Error event occurred: {event.message}")
                    yield event  # Pass through errors
                    # Optionally stop the process on parsing errors
                    # logger.error("Stopping analyze loop due to parsing error.")
                    # return
                elif isinstance(event, TokenUsageEvent):
                    logger.info("Yielding token usage event")
                    yield event    
                
            
            if not tool_executed:
                # No tool executed in this LLM response cycle
                logger.info("LLM response finished without executing a tool.")                
                # Append any remaining assistant buffer to history if it wasn't followed by a tool
                if assistant_buffer:
                    logger.info(f"Appending assistant buffer to history: {len(assistant_buffer)} chars")
                    
                    last_message = conversations[-1]
                    if last_message["role"] != "assistant":
                        logger.info("Adding new assistant message")
                        conversations.append(
                            {"role": "assistant", "content": assistant_buffer})
                        self.conversation_manager.append_message_to_current(
                            role="assistant", content=assistant_buffer,metadata={})
                        
                    elif last_message["role"] == "assistant":
                        logger.info("Appending to existing assistant message")
                        last_message["content"] += assistant_buffer
                        
                    # 计算当前对话的总 token 数量并触发事件
                    current_conversation_str = json.dumps(conversations, ensure_ascii=False)
                    total_tokens = count_tokens(current_conversation_str)
                    yield WindowLengthChangeEvent(tokens_used=total_tokens)
                
                # 添加系统提示，要求LLM必须使用工具或明确结束，而不是直接退出
                logger.info("Adding system reminder to use tools or attempt completion")
                
                conversations.append({
                    "role": "user",
                    "content": "NOTE: You must use an appropriate tool (such as read_file, write_to_file, execute_command, etc.) or explicitly complete the task (using attempt_completion). Do not provide text responses without taking concrete actions. Please select a suitable tool to continue based on the user's task."
                })

                self.conversation_manager.append_message_to_current(
                    role="user", 
                    content="NOTE: You must use an appropriate tool (such as read_file, write_to_file, execute_command, etc.) or explicitly complete the task (using attempt_completion). Do not provide text responses without taking concrete actions. Please select a suitable tool to continue based on the user's task.",
                    metadata={})
                
                # 计算当前对话的总 token 数量并触发事件
                current_conversation_str = json.dumps(conversations, ensure_ascii=False)
                total_tokens = count_tokens(current_conversation_str)
                yield WindowLengthChangeEvent(tokens_used=total_tokens)
                # 继续循环，让 LLM 再思考，而不是 break
                logger.info("Continuing the LLM interaction loop without breaking")
                continue
            
        logger.info(f"AgenticEdit analyze loop finished after {iteration_count} iterations.")
        save_formatted_log(self.args.source_dir, json.dumps(conversations, ensure_ascii=False), "agentic_conversation")    

    def stream_and_parse_llm_response(
        self, generator: Generator[Tuple[str, Any], None, None]
    ) -> Generator[Union[LLMOutputEvent, LLMThinkingEvent, ToolCallEvent, ErrorEvent], None, None]:
        """
        Streamingly parses the LLM response generator, distinguishing between
        plain text, thinking blocks, and tool usage blocks, yielding corresponding Event models.

        Args:
            generator: An iterator yielding (content, metadata) tuples from the LLM stream.

        Yields:
            Union[LLMOutputEvent, LLMThinkingEvent, ToolCallEvent, ErrorEvent]: Events representing
            different parts of the LLM's response.
        """
        buffer = ""
        in_tool_block = False
        in_thinking_block = False
        current_tool_tag = None
        tool_start_pattern = re.compile(
            r"<([a-zA-Z0-9_]+)>")  # Matches tool tags
        thinking_start_tag = "<thinking>"
        thinking_end_tag = "</thinking>"

        def parse_tool_xml(tool_xml: str, tool_tag: str) -> Optional[BaseTool]:
            """Minimal parser for tool XML string."""
            params = {}
            try:
                # Find content between <tool_tag> and </tool_tag>
                inner_xml_match = re.search(
                    rf"<{tool_tag}>(.*?)</{tool_tag}>", tool_xml, re.DOTALL)
                if not inner_xml_match:
                    logger.error(
                        f"Could not find content within <{tool_tag}>...</{tool_tag}>")
                    return None
                inner_xml = inner_xml_match.group(1).strip()

                # Find <param>value</param> pairs within the inner content
                pattern = re.compile(r"<([a-zA-Z0-9_]+)>(.*?)</\1>", re.DOTALL)
                for m in pattern.finditer(inner_xml):
                    key = m.group(1)
                    # Basic unescaping (might need more robust unescaping if complex values are used)
                    val = xml.sax.saxutils.unescape(m.group(2))
                    params[key] = val

                tool_cls = TOOL_MODEL_MAP.get(tool_tag)
                if tool_cls:
                    # Attempt to handle boolean conversion specifically for requires_approval
                    if 'requires_approval' in params:
                        params['requires_approval'] = params['requires_approval'].lower(
                        ) == 'true'
                    # Attempt to handle JSON parsing for ask_followup_question_tool
                    if tool_tag == 'ask_followup_question' and 'options' in params:
                        try:
                            params['options'] = json.loads(
                                params['options'])
                        except json.JSONDecodeError:
                            logger.warning(
                                f"Could not decode JSON options for ask_followup_question_tool: {params['options']}")
                            # Keep as string or handle error? Let's keep as string for now.
                            pass
                    if tool_tag == 'plan_mode_respond' and 'options' in params:
                        try:
                            params['options'] = json.loads(
                                params['options'])
                        except json.JSONDecodeError:
                            logger.warning(
                                f"Could not decode JSON options for plan_mode_respond_tool: {params['options']}")
                    # Handle recursive for list_files
                    if tool_tag == 'list_files' and 'recursive' in params:
                        params['recursive'] = params['recursive'].lower() == 'true'
                    return tool_cls(**params)
                else:
                    logger.error(f"Tool class not found for tag: {tool_tag}")
                    return None
            except Exception as e:
                logger.exception(
                    f"Failed to parse tool XML for <{tool_tag}>: {e}\nXML:\n{tool_xml}")
                return None

        last_metadata = None        
        for content_chunk, metadata in generator:            
            global_cancel.check_and_raise(token=self.args.event_file)                      
            if not content_chunk:
                last_metadata = metadata                
                continue
            
            last_metadata = metadata
            buffer += content_chunk            

            while True:
                # Check for transitions: thinking -> text, tool -> text, text -> thinking, text -> tool
                next_event_pos = len(buffer)
                found_event = False

                # 1. Check for </thinking> if inside thinking block
                if in_thinking_block:
                    end_think_pos = buffer.find(thinking_end_tag)
                    if end_think_pos != -1:
                        thinking_content = buffer[:end_think_pos]
                        yield LLMThinkingEvent(text=thinking_content)
                        buffer = buffer[end_think_pos + len(thinking_end_tag):]
                        in_thinking_block = False
                        found_event = True
                        continue  # Restart loop with updated buffer/state
                    else:
                        # Need more data to close thinking block
                        break

                # 2. Check for </tool_tag> if inside tool block
                elif in_tool_block:
                    end_tag = f"</{current_tool_tag}>"
                    end_tool_pos = buffer.find(end_tag)
                    if end_tool_pos != -1:
                        tool_block_end_index = end_tool_pos + len(end_tag)
                        tool_xml = buffer[:tool_block_end_index]
                        tool_obj = parse_tool_xml(tool_xml, current_tool_tag)

                        if tool_obj:
                            # Reconstruct the XML accurately here AFTER successful parsing
                            # This ensures the XML yielded matches what was parsed.
                            reconstructed_xml = self._reconstruct_tool_xml(
                                tool_obj)
                            if reconstructed_xml.startswith("<error>"):
                                yield ErrorEvent(message=f"Failed to reconstruct XML for tool {current_tool_tag}")
                            else:
                                yield ToolCallEvent(tool=tool_obj, tool_xml=reconstructed_xml)
                        else:
                            # yield ErrorEvent(message=f"Failed to parse tool: <{current_tool_tag}>")
                            # Optionally yield the raw XML as plain text?
                            yield LLMOutputEvent(text=f"Failed to parse tool: <{current_tool_tag}> {tool_xml}")

                        buffer = buffer[tool_block_end_index:]
                        in_tool_block = False
                        current_tool_tag = None
                        found_event = True
                        continue  # Restart loop
                    else:
                        # Need more data to close tool block
                        break

                # 3. Check for <thinking> or <tool_tag> if in plain text state
                else:
                    start_think_pos = buffer.find(thinking_start_tag)
                    tool_match = tool_start_pattern.search(buffer)
                    start_tool_pos = tool_match.start() if tool_match else -1
                    tool_name = tool_match.group(1) if tool_match else None

                    # Determine which tag comes first (if any)
                    first_tag_pos = -1
                    is_thinking = False
                    is_tool = False

                    if start_think_pos != -1 and (start_tool_pos == -1 or start_think_pos < start_tool_pos):
                        first_tag_pos = start_think_pos
                        is_thinking = True
                    elif start_tool_pos != -1 and (start_think_pos == -1 or start_tool_pos < start_think_pos):
                        # Check if it's a known tool
                        if tool_name in TOOL_MODEL_MAP:
                            first_tag_pos = start_tool_pos
                            is_tool = True
                        else:
                            # Unknown tag, treat as text for now, let buffer grow
                            pass

                    if first_tag_pos != -1:  # Found either <thinking> or a known <tool>
                        # Yield preceding text if any
                        preceding_text = buffer[:first_tag_pos]
                        if preceding_text:
                            yield LLMOutputEvent(text=preceding_text)

                        # Transition state
                        if is_thinking:
                            buffer = buffer[first_tag_pos +
                                            len(thinking_start_tag):]
                            in_thinking_block = True
                        elif is_tool:
                            # Keep the starting tag
                            buffer = buffer[first_tag_pos:]
                            in_tool_block = True
                            current_tool_tag = tool_name

                        found_event = True
                        continue  # Restart loop

                    else:
                        # No tags found, or only unknown tags found. Need more data or end of stream.
                        # Yield text chunk but keep some buffer for potential tag start
                        # Keep last 100 chars
                        split_point = max(0, len(buffer) - 100)
                        text_to_yield = buffer[:split_point]
                        if text_to_yield:
                            yield LLMOutputEvent(text=text_to_yield)
                            buffer = buffer[split_point:]
                        break  # Need more data

                # If no event was processed in this iteration, break inner loop
                if not found_event:
                    break                

        # After generator exhausted, yield any remaining content
        if in_thinking_block:
            # Unterminated thinking block
            yield ErrorEvent(message="Stream ended with unterminated <thinking> block.")
            if buffer:
                # Yield remaining as thinking
                yield LLMThinkingEvent(text=buffer)
        elif in_tool_block:
            # Unterminated tool block
            yield ErrorEvent(message=f"Stream ended with unterminated <{current_tool_tag}> block.")
            if buffer:
                yield LLMOutputEvent(text=buffer)  # Yield remaining as text
        elif buffer:
            # Yield remaining plain text
            yield LLMOutputEvent(text=buffer)

        # 这个要放在最后，防止其他关联的多个事件的信息中断        
        yield TokenUsageEvent(usage=last_metadata)            
    

    def apply_pre_changes(self):
        # get the file name
        file_name = os.path.basename(self.args.file)
        if not self.args.skip_commit:
            try:
                commit_result = git_utils.commit_changes(
                    self.args.source_dir, f"auto_coder_pre_{file_name}")
                get_event_manager(self.args.event_file).write_result(
                    EventContentCreator.create_result(
                        content={
                            "have_commit":commit_result.success,
                            "commit_hash":commit_result.commit_hash,
                            "diff_file_num":len(commit_result.changed_files),
                            "event_file":self.args.event_file
                        }), metadata=EventMetadata(
                        action_file=self.args.file,
                        is_streaming=False,
                        path="/agent/edit/apply_pre_changes",
                        stream_out_type="/agent/edit").to_dict())
                
            except Exception as e:
                self.printer.print_in_terminal("git_init_required",
                                               source_dir=self.args.source_dir, error=str(e))
                return

    def get_available_checkpoints(self) -> List[Dict[str, Any]]:
        """
        获取可用的检查点列表
        
        Returns:
            List[Dict[str, Any]]: 检查点信息列表
        """
        if not self.checkpoint_manager:
            return []
        
        return self.checkpoint_manager.get_available_checkpoints()
    
    def rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """
        回滚到指定的检查点，恢复文件状态和对话状态
        
        Args:
            checkpoint_id: 检查点ID
            
        Returns:
            bool: 是否成功回滚
        """
        if not self.checkpoint_manager:
            logger.error("无法回滚：检查点管理器未初始化")
            return False
        
        try:
            # 回滚文件变更
            undo_result, checkpoint = self.checkpoint_manager.undo_change_group_with_conversation(checkpoint_id)
            if not undo_result.success:
                logger.error(f"回滚文件变更失败: {undo_result.errors}")
                return False
            
            # 恢复对话状态
            if checkpoint:
                self.current_conversations = checkpoint.conversations
                logger.info(f"已恢复对话状态，包含 {len(checkpoint.conversations)} 条消息")
                return True
            else:
                logger.warning(f"未找到关联的对话检查点: {checkpoint_id}，只回滚了文件变更")
                return undo_result.success
        except Exception as e:
            logger.exception(f"回滚到检查点 {checkpoint_id} 失败: {str(e)}")
            return False
    
    def handle_rollback_command(self, command: str) -> str:
        """
        处理回滚相关的命令
        
        Args:
            command: 命令字符串，如 "rollback list", "rollback to <id>", "rollback info <id>"
            
        Returns:
            str: 命令执行结果
        """
        if command == "rollback list":
            # 列出可用的检查点
            checkpoints = self.get_available_checkpoints()
            if not checkpoints:
                return "没有可用的检查点。"
            
            result = "可用的检查点列表：\n"
            for i, cp in enumerate(checkpoints):
                time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cp["timestamp"]))
                result += f"{i+1}. ID: {cp['id'][:8]}... | 时间: {time_str} | 变更文件数: {cp['changes_count']}"
                result += f" | {'包含对话状态' if cp['has_conversation'] else '不包含对话状态'}\n"
            
            return result
        
        elif command.startswith("rollback info "):
            # 显示检查点详情
            cp_id = command[len("rollback info "):].strip()
            
            # 查找检查点
            checkpoints = self.get_available_checkpoints()
            target_cp = None
            
            # 支持通过序号或ID查询
            if cp_id.isdigit() and 1 <= int(cp_id) <= len(checkpoints):
                target_cp = checkpoints[int(cp_id) - 1]
            else:
                for cp in checkpoints:
                    if cp["id"].startswith(cp_id):
                        target_cp = cp
                        break
            
            if not target_cp:
                return f"未找到ID为 {cp_id} 的检查点。"
            
            # 获取检查点详细信息
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(target_cp["timestamp"]))
            
            # 获取变更文件列表
            changes = self.checkpoint_manager.get_changes_by_group(target_cp["id"])
            changed_files = [change.file_path for change in changes]
            
            # 获取对话状态信息
            conversation_info = "无对话状态信息"
            if target_cp["has_conversation"] and hasattr(self.checkpoint_manager, 'conversation_store'):
                checkpoint = self.checkpoint_manager.conversation_store.get_checkpoint(target_cp["id"])
                if checkpoint and checkpoint.conversations:
                    conversation_info = f"包含 {len(checkpoint.conversations)} 条对话消息"
            
            result = f"检查点详情：\n"
            result += f"ID: {target_cp['id']}\n"
            result += f"创建时间: {time_str}\n"
            result += f"变更文件数: {target_cp['changes_count']}\n"
            result += f"对话状态: {conversation_info}\n\n"
            
            if changed_files:
                result += "变更文件列表：\n"
                for i, file_path in enumerate(changed_files):
                    result += f"{i+1}. {file_path}\n"
            
            return result
        
        elif command.startswith("rollback to "):
            # 回滚到指定检查点
            cp_id = command[len("rollback to "):].strip()
            
            # 查找检查点
            checkpoints = self.get_available_checkpoints()
            target_cp = None
            
            # 支持通过序号或ID回滚
            if cp_id.isdigit() and 1 <= int(cp_id) <= len(checkpoints):
                target_cp = checkpoints[int(cp_id) - 1]
            else:
                for cp in checkpoints:
                    if cp["id"].startswith(cp_id):
                        target_cp = cp
                        break
            
            if not target_cp:
                return f"未找到ID为 {cp_id} 的检查点。"
            
            # 执行回滚
            success = self.rollback_to_checkpoint(target_cp["id"])
            
            if success:
                # 获取变更文件列表
                changes = self.checkpoint_manager.get_changes_by_group(target_cp["id"])
                changed_files = [change.file_path for change in changes]
                
                result = f"成功回滚到检查点 {target_cp['id'][:8]}...\n"
                result += f"恢复了 {len(changed_files)} 个文件的状态"
                
                if target_cp["has_conversation"]:
                    result += f"\n同时恢复了对话状态"
                
                return result
            else:
                return f"回滚到检查点 {target_cp['id'][:8]}... 失败。"
        
        return "未知命令。可用命令：rollback list, rollback info <id>, rollback to <id>"
    
    def apply_changes(self):
        """
        Apply all tracked file changes to the original project directory.
        """                            
        if not self.args.skip_commit:
            try:
                file_name = os.path.basename(self.args.file)
                commit_result = git_utils.commit_changes(
                    self.args.source_dir,
                    f"{self.args.query}\nauto_coder_{file_name}",
                )
                
                get_event_manager(self.args.event_file).write_result(
                    EventContentCreator.create_result(
                        content={
                            "have_commit":commit_result.success,
                            "commit_hash":commit_result.commit_hash,
                            "diff_file_num":len(commit_result.changed_files),
                            "event_file":self.args.event_file                                
                        }), metadata=EventMetadata(
                        action_file=self.args.file,
                        is_streaming=False,
                        path="/agent/edit/apply_changes",
                        stream_out_type="/agent/edit").to_dict())
                
                action_yml_file_manager = ActionYmlFileManager(
                    self.args.source_dir)
                action_file_name = os.path.basename(self.args.file)
                add_updated_urls = []
                commit_result.changed_files
                for file in commit_result.changed_files:
                    add_updated_urls.append(
                        os.path.join(self.args.source_dir, file))

                self.args.add_updated_urls = add_updated_urls
                update_yaml_success = action_yml_file_manager.update_yaml_field(
                    action_file_name, "add_updated_urls", add_updated_urls)
                if not update_yaml_success:
                    self.printer.print_in_terminal(
                        "yaml_save_error", style="red", yaml_file=action_file_name)

                if self.args.enable_active_context:
                    active_context_manager = ActiveContextManager(
                        self.llm, self.args.source_dir)
                    task_id = active_context_manager.process_changes(
                        self.args)
                    self.printer.print_in_terminal("active_context_background_task",
                                                    style="blue",
                                                    task_id=task_id)
                git_utils.print_commit_info(commit_result=commit_result)
                
                # 检查是否需要创建 Pull Request
                if self.conversation_config and self.conversation_config.pull_request:
                    self._create_pull_request(commit_result)
                    
            except Exception as e:                
                self.printer.print_str_in_terminal(
                    str(e),
                    style="red"
                )        
            
    def _create_pull_request(self, commit_result):
        """
        创建 Pull Request（如果配置启用）
        
        Args:
            commit_result: Git commit 结果对象
        """
        try:
            # 获取当前分支名
            current_branch = git_utils.get_current_branch(self.args.source_dir)
            if not current_branch:
                logger.warning(get_message("/agent/edit/pull_request/branch_name_failed"))
                return                        
            
            # 准备 PR 标题和描述
            query = self.args.query or get_message("/agent/edit/pull_request/default_query")
            pr_title = get_message_with_format("/agent/edit/pull_request/title", query="{query[0:40]}...")
            
            # 构建 PR 描述
            file_list = ""
            if commit_result.changed_files:
                for file_path in commit_result.changed_files:
                    file_list += f"- `{file_path}`\n"
            
            pr_description = get_message_with_format(
                "/agent/edit/pull_request/description",
                query=query,
                file_count=len(commit_result.changed_files or []),
                commit_hash=commit_result.commit_hash,
                file_list=file_list.strip(),
                source_branch=current_branch,
                target_branch="main",
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
            )

            # 创建 Pull Request
            logger.info(get_message_with_format("/agent/edit/pull_request/creating", title=pr_title))
            
            result = create_pull_request(
                repo_path=self.args.source_dir,
                title=pr_title,                
                description=pr_description,                
            )
            
            if result.success:
                logger.info(get_message("/agent/edit/pull_request/success"))
                logger.info(f"PR URL: {result.pr_url}")
                logger.info(f"PR 编号: {result.pr_number}")
                
                # 打印成功信息到终端
                self.printer.print_str_in_terminal(
                    get_message("/agent/edit/pull_request/success"),
                    style="green"
                )
                self.printer.print_str_in_terminal(f"PR URL: {result.pr_url}")
                self.printer.print_str_in_terminal(f"PR 编号: {result.pr_number}")
                
                # 写入事件日志
                get_event_manager(self.args.event_file).write_result(
                    EventContentCreator.create_result(
                        content={
                            "success": True,
                            "pr_url": result.pr_url,
                            "pr_number": result.pr_number,
                            "source_branch": current_branch,
                            "target_branch": "main",
                            "platform": result.platform.value if result.platform else "unknown"
                        }), 
                    metadata=EventMetadata(
                        action_file=self.args.file,
                        is_streaming=False,
                        path="/agent/edit/pull_request_created",
                        stream_out_type="/agent/edit"
                    ).to_dict()
                )
                
            else:
                error_msg = get_message_with_format("/agent/edit/pull_request/failed", error=result.error_message)
                logger.error(error_msg)
                
                # 打印错误信息到终端
                self.printer.print_str_in_terminal(error_msg, style="red")
                
                # 写入错误事件日志
                get_event_manager(self.args.event_file).write_error(
                    EventContentCreator.create_error(
                        error_code="PR_CREATION_FAILED",
                        error_message=result.error_message,
                        details={
                            "source_branch": current_branch,
                            "target_branch": "main"
                        }
                    ).to_dict(),
                    metadata=EventMetadata(
                        action_file=self.args.file,
                        is_streaming=False,
                        path="/agent/edit/pull_request_error",
                        stream_out_type="/agent/edit"
                    ).to_dict()
                )
                
        except Exception as e:
            error_msg = get_message_with_format("/agent/edit/pull_request/exception", error=str(e))
            logger.exception(error_msg)
            
            # 打印异常信息到终端
            self.printer.print_str_in_terminal(error_msg, style="red")
            
            # 写入异常事件日志
            get_event_manager(self.args.event_file).write_error(
                EventContentCreator.create_error(
                    error_code="PR_CREATION_EXCEPTION",
                    error_message=get_message_with_format("/agent/edit/pull_request/exception", error=str(e)),
                    details={"exception_type": type(e).__name__}
                ).to_dict(),
                metadata=EventMetadata(
                    action_file=self.args.file,
                    is_streaming=False,
                    path="/agent/edit/pull_request_exception",
                    stream_out_type="/agent/edit"
                ).to_dict()
            )    
