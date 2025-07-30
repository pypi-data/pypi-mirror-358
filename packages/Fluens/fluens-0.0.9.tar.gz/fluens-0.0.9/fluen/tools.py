#!/usr/bin/env python3
"""
Claude Code Tools Implementation
All tools from the original Claude Code with comprehensive functionality
"""

import os
import re
import json
import glob
import shutil
import asyncio
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass
import aiofiles
import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify
import logging

logger = logging.getLogger(__name__)

@dataclass
class ToolResult:
    content: str
    error: Optional[str] = None
    metadata: Optional[Dict] = None

class ClaudeCodeTools:
    """Implementation of all Claude Code tools"""
    
    def __init__(self, workspace_root: str = None):
        self.workspace_root = Path(workspace_root or os.getcwd()).resolve()
        self.session_todos: List[Dict] = []
        self._http_client = httpx.AsyncClient()
    
    async def close(self):
        """Close HTTP client"""
        await self._http_client.aclose()
    
    # File Operations
    async def read(self, file_path: str, offset: int = 0, limit: int = 2000, explanation: str = "Read file contents with optional line offset and limit") -> ToolResult:
        """Read file from filesystem with line numbers"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.workspace_root / path
            
            if not path.exists():
                return ToolResult("", error=f"File does not exist: {file_path}")
            
            if path.is_dir():
                return ToolResult("", error=f"Path is a directory: {file_path}")
            
            # Handle binary files (images, etc.)
            if self._is_binary_file(path):
                return ToolResult(f"Binary file: {path}", metadata={"type": "binary", "size": path.stat().st_size})
            
            async with aiofiles.open(path, 'r', encoding='utf-8', errors='replace') as f:
                lines = await f.readlines()
            
            # Apply offset and limit
            if offset > 0:
                lines = lines[offset:]
            if limit > 0:
                lines = lines[:limit]
            
            # Format with line numbers (cat -n style)
            formatted_lines = []
            for i, line in enumerate(lines, start=offset + 1):
                # Truncate long lines
                if len(line) > 2000:
                    line = line[:2000] + "... [truncated]\\n"
                formatted_lines.append(f"{i:6d}\\t{line.rstrip()}")
            
            content = "\\n".join(formatted_lines)
            
            # Format content with explanation and tool info
            tool_info = f"Read({file_path})"
            if limit > 0 and len(lines) == limit:
                tool_info += f" - {limit} lines"
            
            final_content = f"{explanation}\\n{tool_info}\\n\\n{content}"
            
            # Add line count information at the end for UI display
            total_lines_read = len(lines)
            if total_lines_read > 0:
                final_content += f"\\n\\n└─ Read {total_lines_read} lines"
            
            content = final_content
            
            return ToolResult(content, metadata={"lines": len(lines), "total_lines": len(lines) + offset})
            
        except Exception as e:
            return ToolResult("", error=f"Error reading file: {str(e)}")
    
    async def write(self, file_path: str, content: str, explanation: str = "Write content to file, overwriting existing content") -> ToolResult:
        """Write content to file (overwrites existing)"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.workspace_root / path
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            result_content = f"{explanation}\\nWrite({path})\\n\\nFile written successfully: {path}"
            return ToolResult(result_content)
            
        except Exception as e:
            return ToolResult("", error=f"Error writing file: {str(e)}")
    
    async def edit(self, file_path: str, old_string: str, new_string: str, replace_all: bool = False, explanation: str = "Replace exact string in file with optional replace all flag") -> ToolResult:
        """Edit file with exact string replacement"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.workspace_root / path
            
            if not path.exists():
                return ToolResult("", error=f"File does not exist: {file_path}")
            
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            if old_string == new_string:
                return ToolResult("", error="old_string and new_string are identical")
            
            if replace_all:
                new_content = content.replace(old_string, new_string)
                replacements = content.count(old_string)
            else:
                if content.count(old_string) > 1:
                    return ToolResult("", error="old_string appears multiple times; use replace_all=true or provide more context")
                new_content = content.replace(old_string, new_string, 1)
                replacements = 1 if old_string in content else 0
            
            if replacements == 0:
                return ToolResult("", error="old_string not found in file")
            
            async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                await f.write(new_content)
            
            result_content = f"{explanation}\\nEdit({path})\\n\\nSuccessfully replaced {replacements} occurrence(s) in {path}"
            return ToolResult(result_content)
            
        except Exception as e:
            return ToolResult("", error=f"Error editing file: {str(e)}")
    
    async def multiedit(self, file_path: str, edits: List[Dict[str, Any]], explanation: str = "Apply multiple string replacements to file in single atomic operation") -> ToolResult:
        """Perform multiple edits atomically"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.workspace_root / path
            
            if not path.exists():
                return ToolResult("", error=f"File does not exist: {file_path}")
            
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            current_content = content
            applied_edits = 0
            
            for edit in edits:
                old_str = edit.get('old_string', '')
                new_str = edit.get('new_string', '')
                replace_all = edit.get('replace_all', False)
                
                if old_str == new_str:
                    return ToolResult("", error=f"Edit {applied_edits + 1}: old_string and new_string are identical")
                
                if replace_all:
                    if old_str in current_content:
                        current_content = current_content.replace(old_str, new_str)
                        applied_edits += 1
                    else:
                        return ToolResult("", error=f"Edit {applied_edits + 1}: old_string not found")
                else:
                    if current_content.count(old_str) > 1:
                        return ToolResult("", error=f"Edit {applied_edits + 1}: old_string appears multiple times")
                    elif old_str in current_content:
                        current_content = current_content.replace(old_str, new_str, 1)
                        applied_edits += 1
                    else:
                        return ToolResult("", error=f"Edit {applied_edits + 1}: old_string not found")
            
            async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                await f.write(current_content)
            
            result_content = f"{explanation}\\nMultiedit({path})\\n\\nSuccessfully applied {applied_edits} edits to {path}"
            return ToolResult(result_content)
            
        except Exception as e:
            return ToolResult("", error=f"Error in multiedit: {str(e)}")
    
    # Search & Discovery
    async def glob(self, pattern: str, path: str = None, explanation: str = "Find files matching glob pattern in specified directory") -> ToolResult:
        """Find files matching glob pattern"""
        try:
            search_path = Path(path) if path else self.workspace_root
            if not search_path.is_absolute():
                search_path = self.workspace_root / search_path
            
            # Use glob.glob for pattern matching
            full_pattern = str(search_path / pattern)
            matches = glob.glob(full_pattern, recursive=True)
            
            # Convert to relative paths and sort by modification time
            relative_matches = []
            for match in matches:
                rel_path = os.path.relpath(match, self.workspace_root)
                try:
                    mtime = os.path.getmtime(match)
                    relative_matches.append((rel_path, mtime))
                except OSError:
                    relative_matches.append((rel_path, 0))
            
            # Sort by modification time (newest first)
            relative_matches.sort(key=lambda x: x[1], reverse=True)
            result_paths = [path for path, _ in relative_matches]
            
            files_content = "\\n".join(result_paths) if result_paths else "No files found matching pattern"
            search_path_display = path or "."
            result_content = f"{explanation}\\nGlob({pattern}) in {search_path_display}\\n\\n{files_content}"
            return ToolResult(result_content, metadata={"count": len(result_paths)})
            
        except Exception as e:
            return ToolResult("", error=f"Error in glob search: {str(e)}")
    
    async def grep(self, pattern: str, include: str = None, path: str = None, explanation: str = "Search file contents for regex pattern with optional file filter") -> ToolResult:
        """Search file contents using regex"""
        try:
            search_path = Path(path) if path else self.workspace_root
            if not search_path.is_absolute():
                search_path = self.workspace_root / search_path
            
            matches = []
            regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            
            # Build file list based on include pattern
            if include:
                file_pattern = str(search_path / "**" / include)
                files_to_search = glob.glob(file_pattern, recursive=True)
            else:
                files_to_search = []
                for root, dirs, files in os.walk(search_path):
                    # Skip hidden directories
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    for file in files:
                        if not file.startswith('.'):
                            files_to_search.append(os.path.join(root, file))
            
            for file_path in files_to_search:
                if os.path.isfile(file_path) and not self._is_binary_file(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if regex.search(content):
                                rel_path = os.path.relpath(file_path, self.workspace_root)
                                mtime = os.path.getmtime(file_path)
                                matches.append((rel_path, mtime))
                    except Exception:
                        continue
            
            # Sort by modification time
            matches.sort(key=lambda x: x[1], reverse=True)
            result_paths = [path for path, _ in matches]
            
            files_content = "\\n".join(result_paths) if result_paths else "No files found containing pattern"
            search_path_display = path or "."
            include_display = f" ({include})" if include else ""
            result_content = f"{explanation}\\nGrep({pattern}){include_display} in {search_path_display}\\n\\n{files_content}"
            return ToolResult(result_content, metadata={"count": len(result_paths), "pattern": pattern})
            
        except Exception as e:
            return ToolResult("", error=f"Error in grep search: {str(e)}")
    
    async def ls(self, path: str, ignore: List[str] = None, explanation: str = "List files and directories with optional ignore patterns") -> ToolResult:
        """List files and directories"""
        try:
            target_path = Path(path)
            if not target_path.is_absolute():
                target_path = self.workspace_root / target_path
            
            if not target_path.exists():
                return ToolResult("", error=f"Path does not exist: {path}")
            
            if not target_path.is_dir():
                return ToolResult("", error=f"Path is not a directory: {path}")
            
            items = []
            ignore_patterns = ignore or []
            
            for item in sorted(target_path.iterdir()):
                # Check ignore patterns
                if any(item.match(pattern) for pattern in ignore_patterns):
                    continue
                
                if item.is_dir():
                    items.append(f"{item.name}/")
                else:
                    size = item.stat().st_size
                    items.append(f"{item.name} ({size} bytes)")
            
            files_content = "\\n".join(items) if items else "Directory is empty"
            result_content = f"{explanation}\\nLs({path})\\n\\n{files_content}"
            return ToolResult(result_content, metadata={"count": len(items)})
            
        except Exception as e:
            return ToolResult("", error=f"Error listing directory: {str(e)}")
    
    # Code Execution
    async def bash(self, command: str, timeout: int = 120, explanation: str = "Execute shell command with timeout in workspace directory") -> ToolResult:
        """Execute bash command"""
        try:
            # Security check - avoid dangerous commands
            dangerous_patterns = [
                r'rm\s+-rf\s+/',
                r'rm\s+-fr\s+/',
                r'dd\s+if=',
                r':\(\)\{.*;\}',  # Fork bomb
                r'mkfs\.',
                r'format\s+c:',
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    return ToolResult("", error="Command blocked for security reasons")
            
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=self.workspace_root
            )
            
            try:
                stdout, _ = await asyncio.wait_for(process.communicate(), timeout=timeout)
                output = stdout.decode('utf-8', errors='replace')
                
                # Truncate if too long
                if len(output) > 30000:
                    output = output[:30000] + "\\n... [output truncated]"
                
                result_content = f"{explanation}\\nBash({command})\\n\\n{output}"
                return ToolResult(result_content, metadata={"exit_code": process.returncode})
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ToolResult("", error=f"Command timed out after {timeout} seconds")
            
        except Exception as e:
            return ToolResult("", error=f"Error executing command: {str(e)}")
    
    # Web Operations
    async def web_fetch(self, url: str, prompt: str, explanation: str = "Fetch web page content and analyze with given prompt") -> ToolResult:
        """Fetch and analyze web content"""
        try:
            response = await self._http_client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            # Convert HTML to markdown
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for element in soup(["script", "style"]):
                element.decompose()
            
            # Convert to markdown
            markdown_content = markdownify(str(soup), heading_style="ATX")
            
            # Truncate if too long
            if len(markdown_content) > 10000:
                markdown_content = markdown_content[:10000] + "\\n... [content truncated]"
            
            # Simple analysis based on prompt (in a real implementation, this would use an LLM)
            analysis = f"{explanation}\\nWebfetch({url})\\n\\nContent fetched from {url}. Prompt: {prompt}\\n\\nContent:\\n{markdown_content}"
            
            return ToolResult(analysis, metadata={"url": url, "content_length": len(markdown_content)})
            
        except Exception as e:
            return ToolResult("", error=f"Error fetching web content: {str(e)}")
    
    async def web_search(self, query: str, allowed_domains: List[str] = None, 
                        blocked_domains: List[str] = None, explanation: str = "Search web with domain filtering options") -> ToolResult:
        """Search the web (placeholder implementation)"""
        # Note: This is a placeholder. In a real implementation, you'd integrate with a search API
        result_content = (
            f"{explanation}\\n"
            f"Websearch({query})\\n\\n"
            f"Web search results for: {query}\\n\\n"
            "Note: Web search functionality requires API integration with a search provider."
        )
        return ToolResult(result_content, metadata={"query": query})
    
    # Task Management
    async def todo_read(self, explanation: str = "Read current session todo list items") -> ToolResult:
        """Read current todo list"""
        todos_content = json.dumps(self.session_todos, indent=2) if self.session_todos else "[]"
        result_content = f"{explanation}\\nTodoread()\\n\\n{todos_content}"
        return ToolResult(result_content, metadata={"count": len(self.session_todos)})
    
    async def todo_write(self, todos: List[Dict[str, Any]], explanation: str = "Write or update session todo list with structured items") -> ToolResult:
        """Write/update todo list"""
        try:
            # Validate todo structure
            for todo in todos:
                required_fields = ["content", "status", "priority", "id"]
                if not all(field in todo for field in required_fields):
                    return ToolResult("", error=f"Todo missing required fields: {required_fields}")
                
                if todo["status"] not in ["pending", "in_progress", "completed", "cancelled"]:
                    return ToolResult("", error=f"Invalid status: {todo['status']}")
                
                if todo["priority"] not in ["high", "medium", "low"]:
                    return ToolResult("", error=f"Invalid priority: {todo['priority']}")
            
            self.session_todos = todos
            result_content = f"{explanation}\\nTodowrite()\\n\\nUpdated todo list with {len(todos)} items"
            return ToolResult(result_content)
            
        except Exception as e:
            return ToolResult("", error=f"Error updating todos: {str(e)}")
    
    # Task/Agent functionality
    async def task(self, description: str, prompt: str, explanation: str = "Launch autonomous agent to perform complex task") -> ToolResult:
        """Launch autonomous agent for complex tasks"""
        # This is a placeholder - in the real implementation, this would launch a sub-agent
        result_content = (
            f"{explanation}\\n"
            f"Task({description})\\n\\n"
            f"Task: {description}\\n\\nThis would launch an autonomous agent with the following prompt:\\n{prompt}\\n\\n"
            "Note: Task agent functionality would be implemented with full tool access."
        )
        return ToolResult(result_content, metadata={"description": description})
    
    # Utility methods
    def _is_binary_file(self, file_path: Union[str, Path]) -> bool:
        """Check if file is binary"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\\0' in chunk
        except:
            return True

# Tool registry for easy access
CLAUDE_TOOLS = {
    "read": "Read file contents with optional line offset and limit",
    "write": "Write content to file, overwriting existing content",
    "edit": "Replace exact string in file with optional replace all flag", 
    "multiedit": "Apply multiple string replacements to file in single atomic operation",
    "glob": "Find files matching glob pattern in specified directory",
    "grep": "Search file contents for regex pattern with optional file filter",
    "ls": "List files and directories with optional ignore patterns",
    "bash": "Execute shell command with timeout in workspace directory",
    "web_fetch": "Fetch web page content and analyze with given prompt",
    "web_search": "Search web with domain filtering options",
    "todo_read": "Read current session todo list items",
    "todo_write": "Write or update session todo list with structured items",
    "task": "Launch autonomous agent to perform complex task"
}
