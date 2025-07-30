"""
Complete Tool Schemas for Claude Code - ALL tools included
"""

COMPLETE_TOOL_SCHEMAS = [
    # ==================== CORE FILE OPERATIONS ====================
    {
        "name": "read",
        "description": "Reads a file from the local filesystem with line numbers using exact Claude Code format",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The absolute path to the file to read"
                },
                "offset": {
                    "type": "integer", 
                    "description": "The line number to start reading from (optional, 0-indexed)",
                    "default": 0
                },
                "limit": {
                    "type": "integer",
                    "description": "The number of lines to read (optional, default 2000)",
                    "default": 2000
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "write", 
        "description": "Writes a file to the local filesystem, overwriting existing content",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The absolute path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "edit",
        "description": "Performs exact string replacements in files with Claude Code validation",
        "parameters": {
            "type": "object", 
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The absolute path to the file to modify"
                },
                "old_string": {
                    "type": "string",
                    "description": "The exact text to replace"
                },
                "new_string": {
                    "type": "string", 
                    "description": "The text to replace it with (must be different from old_string)"
                },
                "replace_all": {
                    "type": "boolean",
                    "description": "Replace all occurrences of old_string (default false)",
                    "default": false
                }
            },
            "required": ["file_path", "old_string", "new_string"]
        }
    },
    {
        "name": "multiedit",
        "description": "Performs multiple edits to a single file in one atomic operation",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string", 
                    "description": "The absolute path to the file to modify"
                },
                "edits": {
                    "type": "array",
                    "description": "Array of edit operations to perform sequentially",
                    "items": {
                        "type": "object",
                        "properties": {
                            "old_string": {
                                "type": "string",
                                "description": "The exact text to replace"
                            },
                            "new_string": {
                                "type": "string",
                                "description": "The text to replace it with"
                            },
                            "replace_all": {
                                "type": "boolean", 
                                "description": "Replace all occurrences (default false)",
                                "default": false
                            }
                        },
                        "required": ["old_string", "new_string"]
                    }
                }
            },
            "required": ["file_path", "edits"]
        }
    },
    
    # ==================== DIRECTORY AND SEARCH ====================
    {
        "name": "ls",
        "description": "Lists files and directories in a given path with Claude Code formatting",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The absolute path to the directory to list"
                },
                "ignore": {
                    "type": "array",
                    "description": "List of glob patterns to ignore (optional)",
                    "items": {"type": "string"}
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "glob",
        "description": "Fast file pattern matching tool that works with any codebase size",
        "parameters": {
            "type": "object", 
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The glob pattern to match files against (supports ** for recursive)"
                },
                "path": {
                    "type": "string",
                    "description": "The directory to search in (optional, defaults to workspace root)"
                }
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "grep",
        "description": "Fast content search tool using regular expressions",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string", 
                    "description": "The regular expression pattern to search for in file contents"
                },
                "include": {
                    "type": "string",
                    "description": "File pattern to include in search (e.g. '*.js', '*.{ts,tsx}') (optional)"
                },
                "path": {
                    "type": "string",
                    "description": "The directory to search in (optional, defaults to workspace root)"
                }
            },
            "required": ["pattern"]
        }
    },
    
    # ==================== COMMAND EXECUTION ====================
    {
        "name": "bash",
        "description": "Executes a bash command with security checks and timeout",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to execute"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Optional timeout in seconds (default 120, max 600)",
                    "default": 120
                }
            },
            "required": ["command"]
        }
    },
    
    # ==================== TASK MANAGEMENT ====================
    {
        "name": "todo_read",
        "description": "Read the current to-do list for the session",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "todo_write",
        "description": "Create and manage a structured task list for the current session",
        "parameters": {
            "type": "object",
            "properties": {
                "todos": {
                    "type": "array",
                    "description": "The updated todo list",
                    "items": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Task description (required, non-empty)"
                            },
                            "status": {
                                "type": "string", 
                                "enum": ["pending", "in_progress", "completed"],
                                "description": "Task status (required)"
                            },
                            "priority": {
                                "type": "string", 
                                "enum": ["high", "medium", "low"],
                                "description": "Task priority (required)"
                            },
                            "id": {
                                "type": "string",
                                "description": "Unique task identifier (required, non-empty)"
                            }
                        },
                        "required": ["content", "status", "priority", "id"]
                    }
                }
            },
            "required": ["todos"]
        }
    },
    
    # ==================== NOTEBOOK OPERATIONS ====================
    {
        "name": "notebook_read",
        "description": "Reads a Jupyter notebook (.ipynb file) and returns all cells with their outputs",
        "parameters": {
            "type": "object",
            "properties": {
                "notebook_path": {
                    "type": "string",
                    "description": "The absolute path to the Jupyter notebook file to read"
                },
                "cell_id": {
                    "type": "string",
                    "description": "The ID of a specific cell to read (optional, if not provided all cells are read)"
                }
            },
            "required": ["notebook_path"]
        }
    },
    {
        "name": "notebook_edit",
        "description": "Completely replaces the contents of a specific cell in a Jupyter notebook",
        "parameters": {
            "type": "object",
            "properties": {
                "notebook_path": {
                    "type": "string",
                    "description": "The absolute path to the Jupyter notebook file to edit"
                },
                "new_source": {
                    "type": "string",
                    "description": "The new source for the cell"
                },
                "cell_id": {
                    "type": "string",
                    "description": "The ID of the cell to edit (optional for insert mode)"
                },
                "cell_type": {
                    "type": "string",
                    "enum": ["code", "markdown"],
                    "description": "The type of the cell (required for insert mode)"
                },
                "edit_mode": {
                    "type": "string",
                    "enum": ["replace", "insert", "delete"],
                    "description": "The type of edit to make (default replace)",
                    "default": "replace"
                }
            },
            "required": ["notebook_path", "new_source"]
        }
    },
    
    # ==================== WEB OPERATIONS ====================
    {
        "name": "web_fetch",
        "description": "Fetches content from a specified URL and processes it",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to fetch content from (must be a valid HTTP/HTTPS URL)"
                },
                "prompt": {
                    "type": "string", 
                    "description": "The prompt describing what information to extract from the page"
                }
            },
            "required": ["url", "prompt"]
        }
    },
    {
        "name": "web_search", 
        "description": "Search the web with domain filtering options",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to use (minimum 2 characters)"
                },
                "allowed_domains": {
                    "type": "array",
                    "description": "Only include search results from these domains (optional)",
                    "items": {"type": "string"}
                },
                "blocked_domains": {
                    "type": "array", 
                    "description": "Never include search results from these domains (optional)",
                    "items": {"type": "string"}
                }
            },
            "required": ["query"]
        }
    },
    
    # ==================== ADVANCED TASK SYSTEM ====================
    {
        "name": "task",
        "description": "Launch an autonomous agent to perform complex tasks with full tool access",
        "parameters": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "A short (3-5 word) description of the task"
                },
                "prompt": {
                    "type": "string",
                    "description": "Detailed instructions for the autonomous agent to perform"
                }
            },
            "required": ["description", "prompt"]
        }
    },
    {
        "name": "exit_plan_mode",
        "description": "Exit plan mode and present the plan for user approval",
        "parameters": {
            "type": "object",
            "properties": {
                "plan": {
                    "type": "string",
                    "description": "The plan you came up with that you want to run by the user for approval"
                }
            },
            "required": ["plan"]
        }
    },
    
    # ==================== ENHANCED WORKFLOW TOOLS ====================
    {
        "name": "analyze_codebase",
        "description": "Perform comprehensive codebase analysis with autonomous agent",
        "parameters": {
            "type": "object",
            "properties": {
                "focus": {
                    "type": "string",
                    "description": "Specific area to focus analysis on (optional, e.g. 'security', 'performance', 'architecture')"
                }
            },
            "required": []
        }
    },
    {
        "name": "implement_feature",
        "description": "Implement a new feature using autonomous agent with full development workflow",
        "parameters": {
            "type": "object",
            "properties": {
                "feature_description": {
                    "type": "string",
                    "description": "Detailed description of the feature to implement"
                }
            },
            "required": ["feature_description"]
        }
    },
    {
        "name": "debug_issue",
        "description": "Debug and fix an issue using autonomous agent with systematic approach",
        "parameters": {
            "type": "object",
            "properties": {
                "issue_description": {
                    "type": "string",
                    "description": "Description of the issue or bug to debug and fix"
                }
            },
            "required": ["issue_description"]
        }
    },
    {
        "name": "smart_search",
        "description": "Perform intelligent search combining multiple search methods",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to find in files and content"
                },
                "search_type": {
                    "type": "string",
                    "enum": ["hybrid", "files", "content"],
                    "description": "Type of search to perform (default hybrid)",
                    "default": "hybrid"
                }
            },
            "required": ["query"]
        }
    }
]

# Tool categories for organization
TOOL_CATEGORIES = {
    "file_operations": ["read", "write", "edit", "multiedit"],
    "directory_search": ["ls", "glob", "grep", "smart_search"],
    "execution": ["bash"],
    "task_management": ["todo_read", "todo_write"],
    "notebooks": ["notebook_read", "notebook_edit"],
    "web": ["web_fetch", "web_search"], 
    "autonomous": ["task", "exit_plan_mode"],
    "workflows": ["analyze_codebase", "implement_feature", "debug_issue"]
}

# Get all tool names
ALL_TOOL_NAMES = [schema["name"] for schema in COMPLETE_TOOL_SCHEMAS]