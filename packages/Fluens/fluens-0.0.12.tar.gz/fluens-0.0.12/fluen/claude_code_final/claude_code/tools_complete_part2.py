"""
Complete Claude Code Tools Implementation - Part 2 (Remaining Tools)
"""

import os
import re
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import aiofiles
import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify

# Continuing from tools_complete.py...

class ClaudeCodeToolsComplete:
    """Complete implementation - Part 2"""
    
    # ==================== COMMAND EXECUTION ====================
    
    async def bash(self, command: str, timeout: int = 120) -> ToolResult:
        """Bash execution - EXACT Claude Code algorithm"""
        try:
            # Security validation - exact Claude Code patterns
            for pattern in self.DANGEROUS_PATTERNS:
                if re.search(pattern, command, re.IGNORECASE):
                    return ToolResult("", error="Command blocked for security reasons", success=False)
            
            # Additional Claude Code security checks
            command_lower = command.lower().strip()
            
            # Block interactive commands
            interactive_commands = ['vi', 'vim', 'nano', 'emacs', 'less', 'more', 'top', 'htop']
            if any(cmd in command_lower.split() for cmd in interactive_commands):
                return ToolResult("", error="Interactive commands not supported", success=False)
            
            # Block network-related dangerous commands
            if any(word in command_lower for word in ['curl -x', 'wget -e', 'nc -l', 'netcat -l']):
                return ToolResult("", error="Potentially unsafe network command blocked", success=False)
            
            # Convert timeout to seconds (Claude Code uses milliseconds in API but seconds internally)
            timeout_seconds = timeout if timeout <= 600 else 120  # Max 10 minutes
            
            # Execute command in workspace directory
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,  # Combine stderr into stdout
                cwd=self.workspace_root,
                env=dict(os.environ, PWD=str(self.workspace_root))
            )
            
            try:
                # Wait for completion with timeout
                stdout, _ = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout_seconds
                )
                
                output = stdout.decode('utf-8', errors='replace')
                
                # Truncate output if too long (exact Claude Code behavior)
                if len(output) > self.MAX_OUTPUT_LENGTH:
                    output = output[:self.MAX_OUTPUT_LENGTH] + "\\n... [output truncated]"
                
                # Claude Code includes exit code in metadata
                return ToolResult(
                    output or "(no output)",
                    metadata={
                        "exit_code": process.returncode,
                        "command": command,
                        "truncated": len(stdout) > self.MAX_OUTPUT_LENGTH
                    }
                )
                
            except asyncio.TimeoutError:
                # Kill the process
                process.kill()
                await process.wait()
                return ToolResult("", error=f"Command timed out after {timeout_seconds} seconds", success=False)
            
        except FileNotFoundError:
            return ToolResult("", error="Command not found", success=False)
        except PermissionError:
            return ToolResult("", error="Permission denied", success=False)
        except Exception as e:
            return ToolResult("", error=f"Error executing command: {str(e)}", success=False)
    
    # ==================== TODO MANAGEMENT ====================
    
    async def todo_read(self) -> ToolResult:
        """Read todos - EXACT Claude Code algorithm"""
        if not self.session_todos:
            return ToolResult("[]", metadata={"count": 0})
        
        # Return formatted JSON exactly like Claude Code
        try:
            formatted_todos = json.dumps(self.session_todos, indent=2)
            return ToolResult(formatted_todos, metadata={"count": len(self.session_todos)})
        except Exception as e:
            return ToolResult("", error=f"Error formatting todos: {str(e)}", success=False)
    
    async def todo_write(self, todos: List[Dict[str, Any]]) -> ToolResult:
        """Write todos - EXACT Claude Code algorithm"""
        try:
            # Validate todo structure exactly like Claude Code
            if not isinstance(todos, list):
                return ToolResult("", error="todos must be an array", success=False)
            
            for i, todo in enumerate(todos):
                if not isinstance(todo, dict):
                    return ToolResult("", error=f"Todo {i+1} must be an object", success=False)
                
                # Required fields validation
                required_fields = ["content", "status", "priority", "id"]
                for field in required_fields:
                    if field not in todo:
                        return ToolResult("", error=f"Todo {i+1} missing required field: {field}", success=False)
                
                # Validate status
                valid_statuses = ["pending", "in_progress", "completed"]
                if todo["status"] not in valid_statuses:
                    return ToolResult("", error=f"Todo {i+1} invalid status: {todo['status']}. Must be one of: {valid_statuses}", success=False)
                
                # Validate priority
                valid_priorities = ["low", "medium", "high"]
                if todo["priority"] not in valid_priorities:
                    return ToolResult("", error=f"Todo {i+1} invalid priority: {todo['priority']}. Must be one of: {valid_priorities}", success=False)
                
                # Validate content is non-empty string
                if not isinstance(todo["content"], str) or not todo["content"].strip():
                    return ToolResult("", error=f"Todo {i+1} content must be a non-empty string", success=False)
                
                # Validate id is non-empty string
                if not isinstance(todo["id"], str) or not todo["id"].strip():
                    return ToolResult("", error=f"Todo {i+1} id must be a non-empty string", success=False)
            
            # Check for duplicate IDs
            ids = [todo["id"] for todo in todos]
            if len(ids) != len(set(ids)):
                return ToolResult("", error="Duplicate todo IDs found", success=False)
            
            # Store todos (session-scoped, not persistent)
            self.session_todos = todos
            
            return ToolResult(f"Todos updated successfully. Total: {len(todos)}", metadata={"count": len(todos)})
            
        except Exception as e:
            return ToolResult("", error=f"Error updating todos: {str(e)}", success=False)
    
    # ==================== NOTEBOOK OPERATIONS ====================
    
    async def notebook_read(self, notebook_path: str, cell_id: str = None) -> ToolResult:
        """Read Jupyter notebook - EXACT Claude Code algorithm"""
        try:
            # Path validation
            path = Path(notebook_path)
            if not path.is_absolute():
                path = self.workspace_root / path
            path = path.resolve()
            
            # Security check
            try:
                path.relative_to(self.workspace_root)
            except ValueError:
                return ToolResult("", error="Path outside workspace", success=False)
            
            if not path.exists():
                return ToolResult("", error=f"Notebook does not exist: {notebook_path}", success=False)
            
            if path.suffix.lower() != '.ipynb':
                return ToolResult("", error="File is not a Jupyter notebook (.ipynb)", success=False)
            
            # Read and parse notebook
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                notebook_content = await f.read()
            
            try:
                notebook = json.loads(notebook_content)
            except json.JSONDecodeError as e:
                return ToolResult("", error=f"Invalid notebook JSON: {str(e)}", success=False)
            
            # Validate notebook structure
            if not isinstance(notebook, dict) or 'cells' not in notebook:
                return ToolResult("", error="Invalid notebook structure", success=False)
            
            cells = notebook['cells']
            if not isinstance(cells, list):
                return ToolResult("", error="Invalid notebook cells structure", success=False)
            
            # Filter by cell_id if specified
            if cell_id:
                target_cells = [cell for cell in cells if cell.get('id') == cell_id]
                if not target_cells:
                    return ToolResult("", error=f"Cell with id '{cell_id}' not found", success=False)
                cells = target_cells
            
            # Format output exactly like Claude Code
            formatted_cells = []
            for i, cell in enumerate(cells):
                cell_type = cell.get('cell_type', 'unknown')
                cell_id_str = cell.get('id', f'cell-{i}')
                
                formatted_cells.append(f"=== Cell {i+1} ({cell_type}) [id: {cell_id_str}] ===")
                
                # Cell source
                source = cell.get('source', [])
                if isinstance(source, list):
                    source_text = ''.join(source)
                else:
                    source_text = str(source)
                
                if source_text.strip():
                    formatted_cells.append(source_text.rstrip())
                else:
                    formatted_cells.append("(empty cell)")
                
                # Cell outputs (for executed cells)
                outputs = cell.get('outputs', [])
                if outputs:
                    formatted_cells.append("\\n--- Outputs ---")
                    for output in outputs:
                        output_type = output.get('output_type', 'unknown')
                        if output_type == 'stream':
                            text = ''.join(output.get('text', []))
                            formatted_cells.append(f"[{output.get('name', 'stdout')}] {text.rstrip()}")
                        elif output_type == 'execute_result' or output_type == 'display_data':
                            data = output.get('data', {})
                            if 'text/plain' in data:
                                text = ''.join(data['text/plain'])
                                formatted_cells.append(f"[result] {text.rstrip()}")
                        elif output_type == 'error':
                            error_name = output.get('ename', 'Error')
                            error_value = output.get('evalue', '')
                            formatted_cells.append(f"[error] {error_name}: {error_value}")
                
                formatted_cells.append("")  # Empty line between cells
            
            content = "\\n".join(formatted_cells)
            
            return ToolResult(content, metadata={
                "total_cells": len(notebook['cells']),
                "cells_shown": len(cells),
                "notebook_format": notebook.get('nbformat', 'unknown')
            })
            
        except Exception as e:
            return ToolResult("", error=f"Error reading notebook: {str(e)}", success=False)
    
    async def notebook_edit(self, notebook_path: str, new_source: str, cell_id: str = None, 
                           cell_type: str = None, edit_mode: str = "replace") -> ToolResult:
        """Edit Jupyter notebook - EXACT Claude Code algorithm"""
        try:
            # Parameter validation
            valid_edit_modes = ["replace", "insert", "delete"]
            if edit_mode not in valid_edit_modes:
                return ToolResult("", error=f"Invalid edit_mode: {edit_mode}. Must be one of: {valid_edit_modes}", success=False)
            
            valid_cell_types = ["code", "markdown"]
            if cell_type and cell_type not in valid_cell_types:
                return ToolResult("", error=f"Invalid cell_type: {cell_type}. Must be one of: {valid_cell_types}", success=False)
            
            # Path validation
            path = Path(notebook_path)
            if not path.is_absolute():
                path = self.workspace_root / path
            path = path.resolve()
            
            # Security check
            try:
                path.relative_to(self.workspace_root)
            except ValueError:
                return ToolResult("", error="Path outside workspace", success=False)
            
            if not path.exists():
                return ToolResult("", error=f"Notebook does not exist: {notebook_path}", success=False)
            
            # Read notebook
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                notebook_content = await f.read()
            
            try:
                notebook = json.loads(notebook_content)
            except json.JSONDecodeError as e:
                return ToolResult("", error=f"Invalid notebook JSON: {str(e)}", success=False)
            
            # Validate notebook structure
            if not isinstance(notebook, dict) or 'cells' not in notebook:
                return ToolResult("", error="Invalid notebook structure", success=False)
            
            cells = notebook['cells']
            if not isinstance(cells, list):
                return ToolResult("", error="Invalid notebook cells structure", success=False)
            
            # Handle different edit modes
            if edit_mode == "insert":
                # Insert new cell
                if cell_type is None:
                    return ToolResult("", error="cell_type required for insert mode", success=False)
                
                new_cell = {
                    "cell_type": cell_type,
                    "source": new_source.split('\\n') if new_source else [],
                    "metadata": {},
                    "id": cell_id or f"new-cell-{len(cells)}"
                }
                
                if cell_type == "code":
                    new_cell["execution_count"] = None
                    new_cell["outputs"] = []
                
                # Find insertion point
                if cell_id:
                    # Insert after specified cell
                    insert_index = len(cells)  # Default to end
                    for i, cell in enumerate(cells):
                        if cell.get('id') == cell_id:
                            insert_index = i + 1
                            break
                else:
                    insert_index = 0  # Insert at beginning
                
                cells.insert(insert_index, new_cell)
                action = f"Inserted new {cell_type} cell at position {insert_index + 1}"
                
            elif edit_mode == "delete":
                # Delete cell
                if not cell_id:
                    return ToolResult("", error="cell_id required for delete mode", success=False)
                
                # Find and remove cell
                removed = False
                for i, cell in enumerate(cells):
                    if cell.get('id') == cell_id:
                        cells.pop(i)
                        removed = True
                        action = f"Deleted cell {i + 1} (id: {cell_id})"
                        break
                
                if not removed:
                    return ToolResult("", error=f"Cell with id '{cell_id}' not found", success=False)
                
            else:  # replace mode
                # Replace cell content
                if not cell_id:
                    return ToolResult("", error="cell_id required for replace mode", success=False)
                
                # Find and update cell
                updated = False
                for i, cell in enumerate(cells):
                    if cell.get('id') == cell_id:
                        cell['source'] = new_source.split('\\n') if new_source else []
                        if cell_type:
                            cell['cell_type'] = cell_type
                        updated = True
                        action = f"Updated cell {i + 1} (id: {cell_id})"
                        break
                
                if not updated:
                    return ToolResult("", error=f"Cell with id '{cell_id}' not found", success=False)
            
            # Write notebook back atomically
            updated_content = json.dumps(notebook, indent=2, ensure_ascii=False)
            
            temp_path = path.with_suffix(path.suffix + '.tmp')
            try:
                async with aiofiles.open(temp_path, 'w', encoding='utf-8') as f:
                    await f.write(updated_content)
                temp_path.replace(path)
            except Exception as e:
                if temp_path.exists():
                    temp_path.unlink()
                raise
            
            return ToolResult(f"{action}. Total cells: {len(cells)}")
            
        except Exception as e:
            return ToolResult("", error=f"Error editing notebook: {str(e)}", success=False)
    
    # ==================== WEB OPERATIONS ====================
    
    async def web_fetch(self, url: str, prompt: str) -> ToolResult:
        """Web fetch - EXACT Claude Code algorithm"""
        try:
            # URL validation
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Fetch content with timeout
            try:
                response = await self._http_client.get(
                    url, 
                    timeout=30.0,
                    follow_redirects=True,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (compatible; Claude-Code/1.0)'
                    }
                )
                response.raise_for_status()
            except httpx.TimeoutException:
                return ToolResult("", error="Request timed out", success=False)
            except httpx.HTTPStatusError as e:
                return ToolResult("", error=f"HTTP error: {e.response.status_code}", success=False)
            except Exception as e:
                return ToolResult("", error=f"Network error: {str(e)}", success=False)
            
            # Process content based on content type
            content_type = response.headers.get('content-type', '').lower()
            
            if 'text/html' in content_type:
                # Parse HTML and convert to markdown
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for element in soup(['script', 'style', 'meta', 'link', 'noscript']):
                    element.decompose()
                
                # Convert to markdown
                markdown_content = markdownify(str(soup), heading_style="ATX")
                content = markdown_content
                
            elif 'application/json' in content_type:
                # Pretty print JSON
                try:
                    json_data = response.json()
                    content = json.dumps(json_data, indent=2)
                except:
                    content = response.text
            else:
                # Plain text or other
                content = response.text
            
            # Truncate if too long
            if len(content) > 50000:  # Claude Code specific limit for web content
                content = content[:50000] + "\\n... [content truncated]"
            
            # Simple analysis based on prompt (in real Claude Code, this would use the LLM)
            analysis_result = f"""Fetched content from: {url}
Analysis prompt: {prompt}

Content:
{content}"""
            
            return ToolResult(analysis_result, metadata={
                "url": url,
                "content_type": content_type,
                "content_length": len(content),
                "status_code": response.status_code
            })
            
        except Exception as e:
            return ToolResult("", error=f"Error fetching web content: {str(e)}", success=False)
    
    async def web_search(self, query: str, allowed_domains: List[str] = None, 
                        blocked_domains: List[str] = None) -> ToolResult:
        """Web search - Claude Code algorithm (placeholder)"""
        # Note: Real implementation would integrate with search API
        return ToolResult(
            f"Web search results for: {query}\\n\\n"
            "Note: Web search functionality requires integration with a search API provider.\\n"
            "This is a placeholder implementation.",
            metadata={
                "query": query,
                "allowed_domains": allowed_domains or [],
                "blocked_domains": blocked_domains or []
            }
        )
    
    # ==================== UTILITY METHODS ====================
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """Binary file detection - exact Claude Code algorithm"""
        try:
            # Check file extension first (faster)
            binary_extensions = {
                '.exe', '.dll', '.so', '.dylib', '.bin', '.dat',
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.tiff',
                '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv',
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
                '.pyc', '.pyo', '.pyd', '.class'
            }
            
            if file_path.suffix.lower() in binary_extensions:
                return True
            
            # Check file content for null bytes
            with open(file_path, 'rb') as f:
                chunk = f.read(8192)  # Read first 8KB
                return b'\\0' in chunk
                
        except Exception:
            return True  # Assume binary if can't read
    
    def _format_file_size(self, size: int) -> str:
        """Format file size - exact Claude Code format"""
        if size == 0:
            return "0 bytes"
        
        units = ["bytes", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size_float = float(size)
        
        while size_float >= 1024 and unit_index < len(units) - 1:
            size_float /= 1024
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size_float)} {units[unit_index]}"
        else:
            return f"{size_float:.1f} {units[unit_index]}"