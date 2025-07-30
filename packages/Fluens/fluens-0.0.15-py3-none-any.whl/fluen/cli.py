"""
Claude Code CLI - Exact replica of the real Claude Code
"""

import asyncio
import sys
import signal
import argparse
from pathlib import Path
from typing import Optional, Dict, Any, List
import tempfile
import json

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.syntax import Syntax
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm

from .llm_client import OllamaLLMClient
from .tools import ClaudeCodeTools
from .tool_schemas import TOOL_SCHEMAS
from .web_search_playwright import claude_code_web_search
import datetime


class ClaudeCodeCLI:
    """Main Claude Code CLI interface - exact replica"""
    
    def __init__(self, workspace_root: str = None, think: bool = False):
        self.console = Console()
        self.workspace_root = Path(workspace_root or Path.cwd()).resolve()
        
        # Initialize components
        self.llm_client = OllamaLLMClient(host="http://192.168.170.76:11434",model='qwen3_14b_q6k:latest', think=think)
        self.tools = ClaudeCodeTools(str(self.workspace_root))
        
        # CLI state
        self.session = PromptSession(history=InMemoryHistory())
        self.interrupted = False
        self.running = False
        
        # Register all tools with LLM client
        self._register_tools()
        
        # Key bindings
        self.bindings = self._setup_key_bindings()
        
        # System prompt
        self.system_prompt = self._get_system_prompt()
        
    def _register_tools(self):
        """Register all tools with the LLM client"""
        tool_mapping = {
            "read": self.tools.read,
            "write": self.tools.write,
            "edit": self.tools.edit,
            "multiedit": self.tools.multiedit,
            "bash": self.tools.bash,
            "glob": self.tools.glob,
            "grep": self.tools.grep,
            "ls": self.tools.ls,
            "todo_read": self.tools.todo_read,
            "todo_write": self.tools.todo_write,
            "web_search": claude_code_web_search,
        }
        
        for schema in TOOL_SCHEMAS:
            tool_name = schema["name"]
            if tool_name in tool_mapping:
                self.llm_client.register_tool(
                    tool_name,
                    tool_mapping[tool_name],
                    schema
                )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for Claude Code"""
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        current_year = datetime.datetime.now().year
        return f"""You are Claude Code, Anthropic's official CLI for Claude.
You are an interactive CLI tool that helps users with software engineering tasks. Use the instructions below and the tools available to you to assist the user.

IMPORTANT: Assist with defensive security tasks only. Refuse to create, modify, or improve code that may be used maliciously. Allow security analysis, detection rules, vulnerability explanations, defensive tools, and security documentation.

Current date: {current_date}
Current year: {current_year}
Current working directory: {self.workspace_root}

You have access to these tools:
- read: Read file contents with line numbers
- write: Write content to files 
- edit: Edit files with exact string replacement
- multiedit: Perform multiple edits atomically
- bash: Execute shell commands safely
- glob: Find files matching patterns
- grep: Search file contents with regex
- ls: List directory contents
- todo_read: Read current session todos
- todo_write: Write/update session todos
- web_search: Search the web for current information with domain filtering

When the user asks you to do something:
1. Use the appropriate tools to complete the task
2. Be proactive and use multiple tools as needed
3. Provide clear, concise responses
4. Show your work by using tools transparently
5. For current events or recent information, use web_search tool

You should minimize output tokens while maintaining helpfulness and accuracy. Only address the specific query or task at hand.

Remember: You are running in an interactive CLI environment. The user expects you to actually perform actions using the available tools, not just explain what they should do."""

    def _setup_key_bindings(self):
        """Setup key bindings"""
        bindings = KeyBindings()
        
        @bindings.add('c-c')
        def _(event):
            """Handle Ctrl+C"""
            self.interrupted = True
            self.console.print("\\n🛑 Interrupted by user", style="yellow")
            event.app.exit(exception=KeyboardInterrupt)
            
        @bindings.add('c-d') 
        def _(event):
            """Handle Ctrl+D (EOF)"""
            event.app.exit()
            
        return bindings
    
    async def run(self):
        """Main CLI loop - exact Claude Code behavior"""
        self.running = True
        self._show_welcome()
        
        # Test LLM connection
        await self._test_llm_connection()
        
        while self.running:
            try:
                self.interrupted = False
                
                # Get user input with Claude Code style prompt
                user_input = await self._get_user_input()
                if not user_input.strip():
                    continue
                
                # Handle built-in commands
                if await self._handle_builtin_commands(user_input.strip()):
                    continue
                
                # Process with LLM and tools
                await self._process_with_llm(user_input.strip())
                
            except (KeyboardInterrupt, EOFError):
                if await self._confirm_exit():
                    break
            except Exception as e:
                self.console.print(f"❌ Error: {e}", style="red")
    
    def _show_welcome(self):
        """Show Claude Code welcome message"""
        welcome_text = Text()
        welcome_text.append("🤖 Claude Code ", style="bold blue")
        welcome_text.append("- Local Implementation with Ollama\\n", style="bold")
        welcome_text.append("Working directory: ", style="dim")
        welcome_text.append(str(self.workspace_root), style="bold cyan")
        welcome_text.append("\\n\\nI'm Claude, and I'm here to help with your code. I have access to tools that let me read, edit, and run code.\\n")
        welcome_text.append("You can ask me to do things like:\\n", style="dim")
        welcome_text.append("• Read and explain code files\\n", style="dim")
        welcome_text.append("• Make edits to fix bugs or add features\\n", style="dim") 
        welcome_text.append("• Run commands and tests\\n", style="dim")
        welcome_text.append("• Search for files and content\\n", style="dim")
        welcome_text.append("\\nPress Ctrl+C to interrupt any operation.\\n", style="dim yellow")
        
        panel = Panel(
            welcome_text,
            title="Welcome to Claude Code",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    async def _test_llm_connection(self):
        """Test LLM connection"""
        with self.console.status("🔗 Testing LLM connection..."):
            connected = await self.llm_client.test_connection()
            
        if connected:
            self.console.print("✅ Connected to LLM", style="green")
        else:
            self.console.print("⚠️  LLM connection failed - check if Ollama is running", style="yellow")
            self.console.print("   Start Ollama with: ollama serve", style="dim")
        self.console.print()
    
    async def _get_user_input(self) -> str:
        """Get user input with Claude Code style prompt"""
        return await self.session.prompt_async(
            HTML('<b>></b> '),
            key_bindings=self.bindings,
        )
    
    async def _handle_builtin_commands(self, user_input: str) -> bool:
        """Handle built-in commands that don't need LLM"""
        parts = user_input.split()
        if not parts:
            return False
            
        command = parts[0].lower()
        
        if command in ['exit', 'quit']:
            if await self._confirm_exit():
                self.running = False
            return True
            
        elif command == 'clear':
            self.console.clear()
            self._show_welcome()
            return True
            
        elif command == 'reset':
            self.llm_client.clear_history()
            self.console.print("🔄 Conversation history cleared", style="green")
            return True
            
        elif command == 'help':
            self._show_help()
            return True
            
        return False
    
    async def _process_with_llm(self, user_input: str):
        """Process user input with LLM and tools"""
        self.console.print()
        
        # Create a live display for streaming response
        with Live(self._create_thinking_display(), refresh_per_second=10) as live:
            response_text = ""
            
            try:
                async for chunk in self.llm_client.chat_with_tools(
                    user_input,
                    self.system_prompt,
                    TOOL_SCHEMAS
                ):
                    if self.interrupted:
                        break
                        
                    response_text += chunk
                    
                    # Update the live display with current response
                    live.update(self._create_response_display(response_text))
                    
            except KeyboardInterrupt:
                self.console.print("\\n🛑 Interrupted by user", style="yellow")
                return
            except Exception as e:
                live.update(Panel(f"❌ Error: {str(e)}", style="red"))
                return
        
        self.console.print()
    
    def _create_thinking_display(self):
        """Create thinking/processing display"""
        return Panel(
            "🤔 Thinking and processing your request...\\n[dim]Press Ctrl+C to interrupt[/dim]",
            title="Claude Code",
            border_style="blue"
        )
    
    def _create_response_display(self, text: str):
        """Create response display"""
        if not text.strip():
            return self._create_thinking_display()
            
        # Try to render as markdown if it looks like markdown
        if any(marker in text for marker in ['```', '##', '**', '- ', '1.']):
            try:
                markdown = Markdown(text)
                return Panel(
                    markdown,
                    title="Claude Code",
                    border_style="green"
                )
            except:
                pass
        
        return Panel(
            text,
            title="Claude Code", 
            border_style="green"
        )
    
    def _show_help(self):
        """Show help information"""
        help_text = Text()
        help_text.append("Claude Code Help\\n\\n", style="bold blue")
        help_text.append("I'm Claude, and I can help you with coding tasks. Here are some things you can ask me to do:\\n\\n", style="white")
        
        help_text.append("📁 File Operations:\\n", style="bold yellow")
        help_text.append("  • Read and explain code files\\n")
        help_text.append("  • Edit files to fix bugs or add features\\n")
        help_text.append("  • Create new files with specific content\\n")
        help_text.append("  • Search for files and content\\n\\n")
        
        help_text.append("⚡ Code Execution:\\n", style="bold green")
        help_text.append("  • Run shell commands and scripts\\n")
        help_text.append("  • Execute tests and builds\\n")
        help_text.append("  • Install dependencies\\n\\n")
        
        help_text.append("🔍 Analysis:\\n", style="bold cyan")
        help_text.append("  • Analyze code for bugs and improvements\\n")
        help_text.append("  • Review code quality and best practices\\n")
        help_text.append("  • Explain complex algorithms\\n\\n")
        
        help_text.append("📋 Task Management:\\n", style="bold magenta")
        help_text.append("  • Track todos and tasks\\n")
        help_text.append("  • Break down complex projects\\n\\n")
        
        help_text.append("Built-in Commands:\\n", style="bold red")
        help_text.append("  clear  - Clear the screen\\n")
        help_text.append("  reset  - Clear conversation history\\n") 
        help_text.append("  help   - Show this help\\n")
        help_text.append("  exit   - Exit Claude Code\\n\\n")
        
        help_text.append("Press Ctrl+C to interrupt any operation.\\n", style="dim yellow")
        
        panel = Panel(help_text, title="Help", border_style="blue")
        self.console.print(panel)
    
    async def _confirm_exit(self) -> bool:
        """Confirm exit"""
        try:
            return Confirm.ask("\\n🚪 Are you sure you want to exit?")
        except:
            return True
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.tools.close()
        self.console.print("👋 Goodbye!", style="bold blue")


async def main():
    """Main entry point for Claude Code"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Claude Code - Local Implementation with Ollama")
    parser.add_argument('--think', action='store_true', help='Enable thinking mode for LLM responses')
    args = parser.parse_args()
    
    cli = ClaudeCodeCLI(think=args.think)
    
    # Handle Ctrl+C gracefully
    def signal_handler(signum, frame):
        print("\\n\\n🛑 Interrupted by user")
        cli.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        await cli.run()
    except KeyboardInterrupt:
        print("\\n\\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        await cli.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
