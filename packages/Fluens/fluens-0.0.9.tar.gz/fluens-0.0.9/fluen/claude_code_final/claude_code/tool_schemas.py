"""
Tool schemas for Claude Code - exact replica of Claude Code tools
"""

TOOL_SCHEMAS = [
    {
        "name": "read",
        "description": "Reads a file from the local filesystem with line numbers",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The absolute path to the file to read"
                },
                "offset": {
                    "type": "integer", 
                    "description": "The line number to start reading from (optional)"
                },
                "limit": {
                    "type": "integer",
                    "description": "The number of lines to read (optional)"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "write",
        "description": "Writes a file to the local filesystem",
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
        "description": "Performs exact string replacements in files",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The absolute path to the file to modify"
                },
                "old_string": {
                    "type": "string",
                    "description": "The text to replace"
                },
                "new_string": {
                    "type": "string", 
                    "description": "The text to replace it with"
                },
                "replace_all": {
                    "type": "boolean",
                    "description": "Replace all occurrences (default false)"
                }
            },
            "required": ["file_path", "old_string", "new_string"]
        }
    },
    {
        "name": "multiedit",
        "description": "Performs multiple edits to a single file in one operation",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The absolute path to the file to modify"
                },
                "edits": {
                    "type": "array",
                    "description": "Array of edit operations",
                    "items": {
                        "type": "object",
                        "properties": {
                            "old_string": {"type": "string"},
                            "new_string": {"type": "string"},
                            "replace_all": {"type": "boolean", "default": False}
                        },
                        "required": ["old_string", "new_string"]
                    }
                }
            },
            "required": ["file_path", "edits"]
        }
    },
    {
        "name": "bash",
        "description": "Executes a bash command in a persistent shell session",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to execute"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Optional timeout in seconds (default 120)"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "glob",
        "description": "Fast file pattern matching tool",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The glob pattern to match files against"
                },
                "path": {
                    "type": "string",
                    "description": "The directory to search in (optional)"
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
                    "description": "The regular expression pattern to search for"
                },
                "include": {
                    "type": "string",
                    "description": "File pattern to include in search (optional)"
                },
                "path": {
                    "type": "string",
                    "description": "The directory to search in (optional)"
                }
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "ls",
        "description": "Lists files and directories in a given path",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The absolute path to the directory to list"
                },
                "ignore": {
                    "type": "array",
                    "description": "List of glob patterns to ignore",
                    "items": {"type": "string"}
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "todo_read",
        "description": "Use this tool to read the current to-do list for the session",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "todo_write", 
        "description": "Use this tool to create and manage a structured task list",
        "parameters": {
            "type": "object",
            "properties": {
                "todos": {
                    "type": "array",
                    "description": "The updated todo list",
                    "items": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                            "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                            "id": {"type": "string"}
                        },
                        "required": ["content", "status", "priority", "id"]
                    }
                }
            },
            "required": ["todos"]
        }
    },
    {
        "name": "web_search",
        "description": "Search the web for current information and real-time data",
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
    }
]