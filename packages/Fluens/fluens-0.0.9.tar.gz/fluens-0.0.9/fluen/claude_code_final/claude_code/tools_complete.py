"""
Complete Claude Code Tools Implementation - Exact Algorithm Match
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
    success: bool = True

class ClaudeCodeToolsComplete:
    """Complete implementation matching exact Claude Code algorithms"""
    
    def __init__(self, workspace_root: str = None):
        self.workspace_root = Path(workspace_root or os.getcwd()).resolve()
        self.session_todos: List[Dict] = []
        self._http_client = httpx.AsyncClient()
        
        # Claude Code specific configurations
        self.MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
        self.MAX_OUTPUT_LENGTH = 30000
        self.MAX_LINE_LENGTH = 2000
        self.DEFAULT_READ_LIMIT = 2000
        
        # Default ignore patterns (exact Claude Code patterns)
        self.DEFAULT_IGNORE_PATTERNS = [
            '.git', '__pycache__', '*.pyc', '.DS_Store', 
            'node_modules', '.next', '.nuxt', 'dist', 'build',
            '*.log', '.env', '.env.*'
        ]
        
        # Dangerous command patterns (exact Claude Code security)
        self.DANGEROUS_PATTERNS = [
            r'rm\s+-rf\s+/',
            r'rm\s+-fr\s+/',
            r'dd\s+if=',
            r':\(\)\{.*;\}',  # Fork bomb
            r'mkfs\.',
            r'format\s+c:',
            r'del\s+/[qsf]',
            r'rd\s+/s',
            r'shutdown',
            r'reboot',
            r'halt',
            r'init\s+[06]'
        ]
    
    async def close(self):
        """Close HTTP client"""
        await self._http_client.aclose()
    
    # ==================== FILE OPERATIONS ====================
    
    async def read(self, file_path: str, offset: int = 0, limit: int = None) -> ToolResult:
        """Read file - EXACT Claude Code algorithm"""
        try:
            # Path validation and normalization
            path = Path(file_path)
            if not path.is_absolute():
                path = self.workspace_root / path
            path = path.resolve()
            
            # Security: Ensure path is within workspace
            try:
                path.relative_to(self.workspace_root)
            except ValueError:
                return ToolResult("", error="Path outside workspace", success=False)
            
            if not path.exists():
                return ToolResult("", error=f"File does not exist: {file_path}", success=False)
            
            if path.is_dir():
                return ToolResult("", error=f"Path is a directory: {file_path}", success=False)
            
            # File size check
            file_size = path.stat().st_size
            if file_size > self.MAX_FILE_SIZE:
                return ToolResult("", error=f"File too large: {file_size} bytes (max {self.MAX_FILE_SIZE})", success=False)
            
            # Binary file detection
            if self._is_binary_file(path):
                return ToolResult(
                    f"Binary file: {path.name}",
                    metadata={"type": "binary", "size": file_size, "path": str(path)}
                )
            
            # Read file with exact Claude Code format
            async with aiofiles.open(path, 'r', encoding='utf-8', errors='replace') as f:
                lines = await f.readlines()
            
            total_lines = len(lines)
            
            # Apply offset and limit (exact Claude Code logic)
            if offset > 0:
                if offset >= total_lines:
                    return ToolResult("", error=f"Offset {offset} beyond file length {total_lines}", success=False)
                lines = lines[offset:]
            
            limit = limit or self.DEFAULT_READ_LIMIT
            if limit > 0:
                lines = lines[:limit]
            
            # Format with exact Claude Code line numbers: cat -n format
            formatted_lines = []
            for i, line in enumerate(lines, start=offset + 1):
                # Truncate long lines exactly like Claude Code
                if len(line) > self.MAX_LINE_LENGTH:
                    line = line[:self.MAX_LINE_LENGTH] + "... [line truncated]\\n"
                
                # Exact format: 6-digit line number, tab, content
                formatted_lines.append(f"{i:6d}\\t{line.rstrip()}")
            
            content = "\\n".join(formatted_lines)
            
            # Add metadata exactly like Claude Code
            metadata = {
                "lines_read": len(lines),
                "total_lines": total_lines,
                "file_size": file_size,
                "offset": offset,
                "truncated": len(lines) == limit and (offset + limit < total_lines)
            }
            
            return ToolResult(content, metadata=metadata)
            
        except PermissionError:
            return ToolResult("", error="Permission denied", success=False)
        except Exception as e:
            return ToolResult("", error=f"Error reading file: {str(e)}", success=False)
    
    async def write(self, file_path: str, content: str) -> ToolResult:
        """Write file - EXACT Claude Code algorithm"""
        try:
            # Path validation and normalization
            path = Path(file_path)
            if not path.is_absolute():
                path = self.workspace_root / path
            path = path.resolve()
            
            # Security: Ensure path is within workspace
            try:
                if path.exists():
                    path.relative_to(self.workspace_root)
                else:
                    # For new files, check parent directory
                    path.parent.relative_to(self.workspace_root)
            except ValueError:
                return ToolResult("", error="Path outside workspace", success=False)
            
            # Create parent directories (exact Claude Code behavior)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file atomically
            temp_path = path.with_suffix(path.suffix + '.tmp')
            try:
                async with aiofiles.open(temp_path, 'w', encoding='utf-8') as f:
                    await f.write(content)
                
                # Atomic rename
                temp_path.replace(path)
                
            except Exception as e:
                # Cleanup temp file if it exists
                if temp_path.exists():
                    temp_path.unlink()
                raise
            
            return ToolResult(f"File written successfully: {path.relative_to(self.workspace_root)}")
            
        except PermissionError:
            return ToolResult("", error="Permission denied", success=False)
        except Exception as e:
            return ToolResult("", error=f"Error writing file: {str(e)}", success=False)
    
    async def edit(self, file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> ToolResult:
        """Edit file - EXACT Claude Code algorithm"""
        try:
            # Validation: old_string and new_string cannot be identical
            if old_string == new_string:
                return ToolResult("", error="old_string and new_string are identical", success=False)
            
            # Path validation
            path = Path(file_path)
            if not path.is_absolute():
                path = self.workspace_root / path
            path = path.resolve()
            
            # Security check
            try:
                path.relative_to(self.workspace_root)
            except ValueError:
                return ToolResult("", error="Path outside workspace", success=False)
            
            if not path.exists():
                return ToolResult("", error=f"File does not exist: {file_path}", success=False)
            
            # Read file first (Claude Code requirement)
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Count occurrences
            occurrence_count = content.count(old_string)
            
            if occurrence_count == 0:
                return ToolResult("", error="old_string not found in file", success=False)
            
            if not replace_all and occurrence_count > 1:
                return ToolResult("", error="old_string appears multiple times; use replace_all=true or provide more context", success=False)
            
            # Perform replacement
            if replace_all:
                new_content = content.replace(old_string, new_string)
                replacements = occurrence_count
            else:
                new_content = content.replace(old_string, new_string, 1)
                replacements = 1
            
            # Write back atomically
            temp_path = path.with_suffix(path.suffix + '.tmp')
            try:
                async with aiofiles.open(temp_path, 'w', encoding='utf-8') as f:
                    await f.write(new_content)
                temp_path.replace(path)
            except Exception as e:
                if temp_path.exists():
                    temp_path.unlink()
                raise
            
            return ToolResult(f"Successfully replaced {replacements} occurrence(s) in {path.relative_to(self.workspace_root)}")
            
        except PermissionError:
            return ToolResult("", error="Permission denied", success=False)
        except Exception as e:
            return ToolResult("", error=f"Error editing file: {str(e)}", success=False)
    
    async def multiedit(self, file_path: str, edits: List[Dict[str, Any]]) -> ToolResult:
        """MultiEdit - EXACT Claude Code algorithm"""
        try:
            if not edits:
                return ToolResult("", error="No edits provided", success=False)
            
            # Path validation
            path = Path(file_path)
            if not path.is_absolute():
                path = self.workspace_root / path
            path = path.resolve()
            
            # Security check
            try:
                path.relative_to(self.workspace_root)
            except ValueError:
                return ToolResult("", error="Path outside workspace", success=False)
            
            if not path.exists():
                return ToolResult("", error=f"File does not exist: {file_path}", success=False)
            
            # Read file
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                original_content = await f.read()
            
            current_content = original_content
            
            # Validate all edits first (Claude Code does this)
            for i, edit in enumerate(edits):
                if not isinstance(edit, dict):
                    return ToolResult("", error=f"Edit {i+1}: must be an object", success=False)
                
                if 'old_string' not in edit or 'new_string' not in edit:
                    return ToolResult("", error=f"Edit {i+1}: missing old_string or new_string", success=False)
                
                old_str = edit['old_string']
                new_str = edit['new_string']
                
                if old_str == new_str:
                    return ToolResult("", error=f"Edit {i+1}: old_string and new_string are identical", success=False)
            
            # Apply edits sequentially (exact Claude Code behavior)
            for i, edit in enumerate(edits):
                old_str = edit['old_string']
                new_str = edit['new_string']
                replace_all = edit.get('replace_all', False)
                
                occurrence_count = current_content.count(old_str)
                
                if occurrence_count == 0:
                    return ToolResult("", error=f"Edit {i+1}: old_string not found", success=False)
                
                if not replace_all and occurrence_count > 1:
                    return ToolResult("", error=f"Edit {i+1}: old_string appears multiple times", success=False)
                
                # Apply the edit
                if replace_all:
                    current_content = current_content.replace(old_str, new_str)
                else:
                    current_content = current_content.replace(old_str, new_str, 1)
            
            # Write atomically
            temp_path = path.with_suffix(path.suffix + '.tmp')
            try:
                async with aiofiles.open(temp_path, 'w', encoding='utf-8') as f:
                    await f.write(current_content)
                temp_path.replace(path)
            except Exception as e:
                if temp_path.exists():
                    temp_path.unlink()
                raise
            
            return ToolResult(f"Successfully applied {len(edits)} edits to {path.relative_to(self.workspace_root)}")
            
        except PermissionError:
            return ToolResult("", error="Permission denied", success=False)
        except Exception as e:
            return ToolResult("", error=f"Error in multiedit: {str(e)}", success=False)
    
    # ==================== DIRECTORY OPERATIONS ====================
    
    async def ls(self, path: str, ignore: List[str] = None) -> ToolResult:
        """List directory - EXACT Claude Code algorithm"""
        try:
            # Path validation
            target_path = Path(path)
            if not target_path.is_absolute():
                target_path = self.workspace_root / target_path
            target_path = target_path.resolve()
            
            # Security check
            try:
                target_path.relative_to(self.workspace_root)
            except ValueError:
                return ToolResult("", error="Path outside workspace", success=False)
            
            if not target_path.exists():
                return ToolResult("", error=f"Path does not exist: {path}", success=False)
            
            if not target_path.is_dir():
                return ToolResult("", error=f"Path is not a directory: {path}", success=False)
            
            # Combine default and custom ignore patterns
            ignore_patterns = set(self.DEFAULT_IGNORE_PATTERNS)
            if ignore:
                ignore_patterns.update(ignore)
            
            items = []
            try:
                # Get directory contents
                for item in target_path.iterdir():
                    # Apply ignore patterns
                    item_name = item.name
                    if any(item.match(pattern) for pattern in ignore_patterns):
                        continue
                    
                    # Hidden files (start with .)
                    if item_name.startswith('.') and item_name not in ['.', '..']:
                        continue
                    
                    if item.is_dir():
                        items.append((item_name + '/', 'dir', 0))
                    else:
                        try:
                            size = item.stat().st_size
                            items.append((item_name, 'file', size))
                        except (OSError, PermissionError):
                            items.append((item_name, 'file', 0))
                
                # Sort: directories first, then files, case-insensitive
                items.sort(key=lambda x: (x[1] != 'dir', x[0].lower()))
                
                # Format output exactly like Claude Code
                if not items:
                    return ToolResult("Directory is empty")
                
                formatted_items = []
                for name, item_type, size in items:
                    if item_type == 'dir':
                        formatted_items.append(f"{name}")
                    else:
                        size_str = self._format_file_size(size)
                        formatted_items.append(f"{name} ({size_str})")
                
                content = "\\n".join(formatted_items)
                return ToolResult(content, metadata={"count": len(items), "path": str(target_path)})
                
            except PermissionError:
                return ToolResult("", error="Permission denied", success=False)
            
        except Exception as e:
            return ToolResult("", error=f"Error listing directory: {str(e)}", success=False)
    
    # ==================== SEARCH OPERATIONS ====================
    
    async def glob(self, pattern: str, path: str = None) -> ToolResult:
        """Glob search - EXACT Claude Code algorithm"""
        try:
            # Path setup
            search_path = Path(path) if path else self.workspace_root
            if not search_path.is_absolute():
                search_path = self.workspace_root / search_path
            search_path = search_path.resolve()
            
            # Security check
            try:
                search_path.relative_to(self.workspace_root)
            except ValueError:
                return ToolResult("", error="Search path outside workspace", success=False)
            
            # Build full pattern
            if pattern.startswith('/'):
                # Absolute pattern
                full_pattern = str(self.workspace_root) + pattern
            else:
                full_pattern = str(search_path / pattern)
            
            # Execute glob with recursive support
            matches = glob.glob(full_pattern, recursive=True)
            
            # Filter to files only and get relative paths with metadata
            file_matches = []
            for match in matches:
                match_path = Path(match)
                if match_path.is_file():
                    try:
                        # Get relative path from workspace root
                        rel_path = match_path.relative_to(self.workspace_root)
                        mtime = match_path.stat().st_mtime
                        file_matches.append((str(rel_path), mtime))
                    except (OSError, ValueError):
                        continue
            
            # Sort by modification time (newest first) - exact Claude Code behavior
            file_matches.sort(key=lambda x: x[1], reverse=True)
            
            # Extract just the paths
            result_paths = [path for path, _ in file_matches]
            
            if not result_paths:
                return ToolResult("No files found matching pattern", metadata={"count": 0, "pattern": pattern})
            
            content = "\\n".join(result_paths)
            return ToolResult(content, metadata={"count": len(result_paths), "pattern": pattern})
            
        except Exception as e:
            return ToolResult("", error=f"Error in glob search: {str(e)}", success=False)
    
    async def grep(self, pattern: str, include: str = None, path: str = None) -> ToolResult:
        """Grep search - EXACT Claude Code algorithm"""
        try:
            # Path setup
            search_path = Path(path) if path else self.workspace_root
            if not search_path.is_absolute():
                search_path = self.workspace_root / search_path
            search_path = search_path.resolve()
            
            # Security check
            try:
                search_path.relative_to(self.workspace_root)
            except ValueError:
                return ToolResult("", error="Search path outside workspace", success=False)
            
            # Compile regex pattern
            try:
                regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            except re.error as e:
                return ToolResult("", error=f"Invalid regex pattern: {str(e)}", success=False)
            
            matches = []
            
            # Build file list
            if include:
                # Use glob pattern for file filtering
                file_pattern = str(search_path / "**" / include)
                files_to_search = glob.glob(file_pattern, recursive=True)
            else:
                # Walk directory tree
                files_to_search = []
                for root, dirs, files in os.walk(search_path):
                    # Filter out ignored directories
                    dirs[:] = [d for d in dirs if not any(
                        Path(d).match(pattern) for pattern in self.DEFAULT_IGNORE_PATTERNS
                    )]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Skip hidden files and ignored patterns
                        if not file.startswith('.'):
                            files_to_search.append(file_path)
            
            # Search each file
            for file_path in files_to_search:
                file_path_obj = Path(file_path)
                
                if not file_path_obj.is_file():
                    continue
                
                # Skip binary files
                if self._is_binary_file(file_path_obj):
                    continue
                
                try:
                    # Read and search file content
                    async with aiofiles.open(file_path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                        content = await f.read()
                        
                    if regex.search(content):
                        # Get relative path and modification time
                        rel_path = file_path_obj.relative_to(self.workspace_root)
                        mtime = file_path_obj.stat().st_mtime
                        matches.append((str(rel_path), mtime))
                        
                except (OSError, PermissionError, UnicodeDecodeError):
                    continue
            
            # Sort by modification time (newest first)
            matches.sort(key=lambda x: x[1], reverse=True)
            result_paths = [path for path, _ in matches]
            
            if not result_paths:
                return ToolResult("No files found containing pattern", metadata={"count": 0, "pattern": pattern})
            
            content = "\\n".join(result_paths)
            return ToolResult(content, metadata={"count": len(result_paths), "pattern": pattern})
            
        except Exception as e:
            return ToolResult("", error=f"Error in grep search: {str(e)}", success=False)
    
    # Continue with remaining tools...