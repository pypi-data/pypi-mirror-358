import sys
import os
import platform
from datetime import datetime
from llm import OllamaClient
from tools import ClaudeCodeTools


class ChatManager:
    def __init__(self, model_name="llama3.2", num_ctx=None, host="http://192.168.170.76:11434"):
        self.conversation_history = []
        self.ollama_client = OllamaClient(host=host, model=model_name)
        self.processing = False
        self.tools = ClaudeCodeTools()
        self.available_functions = self._setup_tool_functions()
        self.tool_definitions = self._setup_tool_definitions()
        self.conversation_display = []  # Simple text-based conversation
    
    def _setup_tool_functions(self):
        """Map tool names to their corresponding methods"""
        return {
            'read': self.tools.read,
            'write': self.tools.write,
            'edit': self.tools.edit,
            'multiedit': self.tools.multiedit,
            'glob': self.tools.glob,
            'grep': self.tools.grep,
            'ls': self.tools.ls,
            'bash': self.tools.bash,
            'web_fetch': self.tools.web_fetch,
            'web_search': self.tools.web_search,
            'todo_read': self.tools.todo_read,
            'todo_write': self.tools.todo_write,
            'task': self.tools.task
        }
    
    def _setup_tool_definitions(self):
        """Create Ollama-compatible tool definitions"""
        return [
            {
                'type': 'function',
                'function': {
                    'name': 'read',
                    'description': 'Read file contents with optional line offset and limit',
                    'parameters': {
                        'type': 'object',
                        'required': ['file_path', 'explanation'],
                        'properties': {
                            'file_path': {'type': 'string', 'description': 'Absolute path to the file to read'},
                            'offset': {'type': 'integer', 'description': 'Line number to start reading from'},
                            'limit': {'type': 'integer', 'description': 'Number of lines to read'},
                            'explanation': {'type': 'string', 'description': 'Read file contents with optional line offset and limit'}
                        }
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'write',
                    'description': 'Write content to file, overwriting existing content',
                    'parameters': {
                        'type': 'object',
                        'required': ['file_path', 'content', 'explanation'],
                        'properties': {
                            'file_path': {'type': 'string', 'description': 'Absolute path to the file to write'},
                            'content': {'type': 'string', 'description': 'Content to write to the file'},
                            'explanation': {'type': 'string', 'description': 'Write content to file, overwriting existing content'}
                        }
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'edit',
                    'description': 'Replace exact string in file with optional replace all flag',
                    'parameters': {
                        'type': 'object',
                        'required': ['file_path', 'old_string', 'new_string', 'explanation'],
                        'properties': {
                            'file_path': {'type': 'string', 'description': 'Absolute path to the file to edit'},
                            'old_string': {'type': 'string', 'description': 'Text to replace'},
                            'new_string': {'type': 'string', 'description': 'Replacement text'},
                            'replace_all': {'type': 'boolean', 'description': 'Replace all occurrences (default false)'},
                            'explanation': {'type': 'string', 'description': 'Replace exact string in file with optional replace all flag'}
                        }
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'multiedit',
                    'description': 'Apply multiple string replacements to file in single atomic operation',
                    'parameters': {
                        'type': 'object',
                        'required': ['file_path', 'edits', 'explanation'],
                        'properties': {
                            'file_path': {'type': 'string', 'description': 'Absolute path to the file to edit'},
                            'edits': {'type': 'array', 'description': 'List of edit operations with old_string, new_string, and optional replace_all'},
                            'explanation': {'type': 'string', 'description': 'Apply multiple string replacements to file in single atomic operation'}
                        }
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'glob',
                    'description': 'Find files matching glob pattern in specified directory',
                    'parameters': {
                        'type': 'object',
                        'required': ['pattern', 'explanation'],
                        'properties': {
                            'pattern': {'type': 'string', 'description': 'Glob pattern to match files'},
                            'path': {'type': 'string', 'description': 'Directory to search in'},
                            'explanation': {'type': 'string', 'description': 'Find files matching glob pattern in specified directory'}
                        }
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'grep',
                    'description': 'Search file contents for regex pattern with optional file filter',
                    'parameters': {
                        'type': 'object',
                        'required': ['pattern', 'explanation'],
                        'properties': {
                            'pattern': {'type': 'string', 'description': 'Regex pattern to search for'},
                            'include': {'type': 'string', 'description': 'File pattern to include (e.g. "*.py")'},
                            'path': {'type': 'string', 'description': 'Directory to search in'},
                            'explanation': {'type': 'string', 'description': 'Search file contents for regex pattern with optional file filter'}
                        }
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'ls',
                    'description': 'List files and directories with optional ignore patterns',
                    'parameters': {
                        'type': 'object',
                        'required': ['path', 'explanation'],
                        'properties': {
                            'path': {'type': 'string', 'description': 'Absolute path to directory to list'},
                            'ignore': {'type': 'array', 'description': 'List of glob patterns to ignore'},
                            'explanation': {'type': 'string', 'description': 'List files and directories with optional ignore patterns'}
                        }
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'bash',
                    'description': 'Execute shell command with timeout in workspace directory',
                    'parameters': {
                        'type': 'object',
                        'required': ['command', 'explanation'],
                        'properties': {
                            'command': {'type': 'string', 'description': 'The bash command to execute'},
                            'timeout': {'type': 'integer', 'description': 'Timeout in seconds (default 120)'},
                            'explanation': {'type': 'string', 'description': 'Execute shell command with timeout in workspace directory'}
                        }
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'web_fetch',
                    'description': 'Fetch web page content and analyze with given prompt',
                    'parameters': {
                        'type': 'object',
                        'required': ['url', 'prompt', 'explanation'],
                        'properties': {
                            'url': {'type': 'string', 'description': 'URL to fetch content from'},
                            'prompt': {'type': 'string', 'description': 'Prompt to analyze the fetched content'},
                            'explanation': {'type': 'string', 'description': 'Fetch web page content and analyze with given prompt'}
                        }
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'web_search',
                    'description': 'Search web with domain filtering options',
                    'parameters': {
                        'type': 'object',
                        'required': ['query', 'explanation'],
                        'properties': {
                            'query': {'type': 'string', 'description': 'Search query'},
                            'allowed_domains': {'type': 'array', 'description': 'List of allowed domains'},
                            'blocked_domains': {'type': 'array', 'description': 'List of blocked domains'},
                            'explanation': {'type': 'string', 'description': 'Search web with domain filtering options'}
                        }
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'todo_read',
                    'description': 'Read current session todo list items',
                    'parameters': {
                        'type': 'object',
                        'required': ['explanation'],
                        'properties': {
                            'explanation': {'type': 'string', 'description': 'Read current session todo list items'}
                        }
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'todo_write',
                    'description': 'Write or update session todo list with structured items',
                    'parameters': {
                        'type': 'object',
                        'required': ['todos', 'explanation'],
                        'properties': {
                            'todos': {'type': 'array', 'description': 'List of todo items with content, status, priority, and id'},
                            'explanation': {'type': 'string', 'description': 'Write or update session todo list with structured items'}
                        }
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'task',
                    'description': 'Launch autonomous agent to perform complex task',
                    'parameters': {
                        'type': 'object',
                        'required': ['description', 'prompt', 'explanation'],
                        'properties': {
                            'description': {'type': 'string', 'description': 'Short description of the task'},
                            'prompt': {'type': 'string', 'description': 'Detailed prompt for the agent'},
                            'explanation': {'type': 'string', 'description': 'Launch autonomous agent to perform complex task'}
                        }
                    }
                }
            }
        ]

    def add_user_message(self, content: str):
        self.conversation_history.append({"type": "user", "content": content})
        self.conversation_display.append(f"> {content}")

    def add_assistant_message(self, content: str):
        self.conversation_history.append({"type": "assistant", "content": content})
        self.conversation_display.append(f"● {content}")
    
    def add_tool_call(self, tool_name: str, arguments: dict):
        self.conversation_history.append({
            "type": "tool_call", 
            "tool_name": tool_name, 
            "arguments": arguments
        })
        # Show initial tool call line like Claude Code style
        first_arg = str(list(arguments.values())[0]) if arguments else ""
        explanation = arguments.get('explanation',"")
        capitalized_tool_name = tool_name.replace('_', ' ').title().replace(' ', '')
        # Initial line showing the tool starting
        initial_line = f"🟢 {capitalized_tool_name}({first_arg})"
        if explanation:
            self.conversation_display.append(f"●  {explanation}")
        initial_line = f"🟢 {capitalized_tool_name}({first_arg})"
        self.conversation_display.append(initial_line)
        
        # Trigger UI refresh to show tool starting
        if hasattr(self, 'ui_refresh_callback') and self.ui_refresh_callback:
            self.ui_refresh_callback()
            
        return len(self.conversation_display) - 1
    
    def add_tool_result(self, content: str, widget_id: int = None, error: str = None):
        self.conversation_history.append({"type": "tool_result", "content": content})
        tool_name = self.conversation_history[-2]['tool_name']
        capitalized_tool_name = tool_name.replace('_', ' ').title().replace(' ', '')
        # Count actual lines in content, not characters
        line_count = len(content.splitlines()) if content else 0
        self.conversation_display.append(f"\u00A0\u00A0\u00A0└─ {capitalized_tool_name} completed ({line_count} lines)")
        

    def get_conversation_text(self) -> str:
        """Get simple text conversation"""
        return "\n\n".join(self.conversation_display)
    

    def _get_system_context(self):
        """Generate system context with current working directory and system info"""
        cwd = os.getcwd()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        system_context = f"""You are Claude Code, an AI coding assistant. Here is important context about the current environment:

Current Working Directory: {cwd}
Operating System: {platform.system()}
Platform: {platform.platform()}
Python Version: {platform.python_version()}
Current Date/Time: {current_time}

You have access to various tools to help with coding tasks. Always be aware of the current working directory when working with file paths. /no_think"""
        
        return system_context

    def _convert_history_to_messages(self):
        messages = []
        
        # Add system message with context at the beginning
        system_context = self._get_system_context()
        messages.append({"role": "system", "content": system_context})
        
        for message in self.conversation_history:
            if message["type"] == "user":
                messages.append({"role": "user", "content": message["content"]})
            elif message["type"] == "assistant":
                messages.append({"role": "assistant", "content": message["content"]})
        return messages

    async def get_assistant_response(self, user_text: str) -> str:
        self.processing = True
        try:
            messages = self._convert_history_to_messages()
            
            # Get initial response from model with tools
            response = self.ollama_client.chat(messages, tools=self.tool_definitions)
            
            # Check if model wants to use tools
            if response.message.tool_calls:
                tool_outputs = []
                
                # Execute tool calls
                for tool in response.message.tool_calls:
                    # Add tool call to conversation and get widget ID
                    widget_id = self.add_tool_call(tool.function.name, tool.function.arguments)
                    
                    if function_to_call := self.available_functions.get(tool.function.name):
                        print(f'Executing tool: {tool.function.name}')
                        print(f'Arguments: {tool.function.arguments}')
                        
                        # Execute the tool function
                        try:
                            # Convert arguments and call function
                            result = await function_to_call(**tool.function.arguments)
                            output = result.content if hasattr(result, 'content') else str(result)
                            error = result.error if hasattr(result, 'error') else None
                            
                            if error:
                                output = f"Error: {error}"
                        except Exception as e:
                            output = f"Tool execution error: {str(e)}"
                            error = str(e)
                        
                        # Add tool result and trigger display update
                        self.add_tool_result(output, widget_id, error)
                        tool_outputs.append(output)
                        
                        # Trigger UI refresh if callback is set
                        if hasattr(self, 'ui_refresh_callback') and self.ui_refresh_callback:
                            self.ui_refresh_callback()
                        
                        print(f'Tool output: {output[:200]}...' if len(output) > 200 else f'Tool output: {output}')
                    else:
                        output = f'Function {tool.function.name} not found'
                        self.add_tool_result(output, widget_id, "Function not found")
                        tool_outputs.append(output)
                
                # Add function response to messages and get final response
                messages.append({'role': 'assistant', 'content': response.message.content or '', 'tool_calls': response.message.tool_calls})
                
                # Use the last tool output for the model (or combine them)
                combined_output = "\n".join(tool_outputs) if len(tool_outputs) > 1 else (tool_outputs[0] if tool_outputs else "")
                messages.append({'role': 'tool', 'content': combined_output, 'name': tool.function.name})
                
                # Get final response from model with function outputs
                final_response = self.ollama_client.chat(messages)
                return final_response.message.content
            else:
                # No tool calls, return direct response
                return response.message.content
                
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            self.processing = False

    def is_processing(self) -> bool:
        return self.processing

    def stop_processing(self):
        self.processing = False

    def get_conversation_history(self):
        return self.conversation_history.copy()

    def clear_conversation(self):
        self.conversation_history.clear()
    
    async def execute_tool(self, tool_name: str, **kwargs):
        """Execute a tool and return the result"""
        if hasattr(self.tools, tool_name):
            tool_method = getattr(self.tools, tool_name)
            return await tool_method(**kwargs)
        else:
            return f"Tool '{tool_name}' not found"
    
    def get_available_tools(self):
        """Get list of available tools"""
        from tools import CLAUDE_TOOLS
        return CLAUDE_TOOLS
    
    
    
    
    def clear_conversation(self):
        """Clear conversation"""
        self.conversation_history.clear()
        self.conversation_display.clear()
