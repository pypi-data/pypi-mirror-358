#!/usr/bin/env python3
"""
Claude Code Demo Script
Demonstrates the key features without requiring Ollama
"""

import asyncio
import tempfile
from pathlib import Path

from claude_code.tools import ClaudeCodeTools
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table


async def demo():
    """Demonstrate Claude Code features"""
    console = Console()
    
    # Welcome
    console.print(Panel(
        "🎉 [bold blue]Claude Code Demo[/bold blue]\\n"
        "Demonstrating core features without requiring Ollama",
        title="🚀 Demo",
        border_style="blue"
    ))
    console.print()
    
    # Create temporary workspace
    with tempfile.TemporaryDirectory() as temp_dir:
        tools = ClaudeCodeTools(temp_dir)
        
        console.print("📁 [bold]File Operations Demo[/bold]")
        
        # Demo 1: Create a Python file
        python_code = '''#!/usr/bin/env python3
"""
Example Python script for Claude Code demo
"""

def greet(name: str) -> str:
    """Greet someone politely"""
    return f"Hello, {name}! Welcome to Claude Code!"

def calculate_fibonacci(n: int) -> int:
    """Calculate fibonacci number"""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

if __name__ == "__main__":
    print(greet("Developer"))
    print(f"Fibonacci(10) = {calculate_fibonacci(10)}")
'''
        
        result = await tools.write("demo.py", python_code)
        console.print(f"✅ {result.content}")
        
        # Demo 2: Read and display with syntax highlighting
        result = await tools.read("demo.py")
        if result.success:
            syntax = Syntax(python_code, "python", theme="monokai", line_numbers=True)
            panel = Panel(syntax, title="📄 demo.py", border_style="green")
            console.print(panel)
        
        # Demo 3: Create more files
        await tools.write("config.json", '{"version": "1.0", "debug": true}')
        await tools.write("README.md", "# Demo Project\\n\\nThis is a demo.")
        await tools.write("requirements.txt", "requests>=2.0\\nrich>=13.0")
        
        # Demo 4: List files
        result = await tools.ls(".")
        console.print("\\n📂 [bold]Directory Listing:[/bold]")
        console.print(result.content)
        
        # Demo 5: Search for files
        result = await tools.glob("*.py")
        console.print("\\n🔍 [bold]Python files found:[/bold]")
        console.print(result.content)
        
        # Demo 6: Search in content
        result = await tools.grep("fibonacci", "*.py")
        console.print("\\n🔎 [bold]Files containing 'fibonacci':[/bold]")
        console.print(result.content)
        
        # Demo 7: Edit file
        result = await tools.edit("demo.py", "Developer", "Claude Code User")
        console.print(f"\\n✏️  {result.content}")
        
        # Demo 8: Execute command
        result = await tools.bash("python demo.py")
        console.print("\\n⚡ [bold]Command execution:[/bold]")
        console.print(result.content)
        
        # Demo 9: Todo management
        todos = [
            {"id": "1", "content": "Review the demo code", "status": "pending", "priority": "high"},
            {"id": "2", "content": "Test all features", "status": "in_progress", "priority": "medium"},
            {"id": "3", "content": "Deploy to production", "status": "pending", "priority": "low"}
        ]
        await tools.todo_write(todos)
        result = await tools.todo_read()
        console.print("\\n📋 [bold]Todo Management:[/bold]")
        console.print(result.content)
        
        await tools.close()
    
    # Command summary table
    console.print("\\n📚 [bold]Available Commands:[/bold]")
    table = Table(title="Claude Code Commands")
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Commands", style="white")
    table.add_column("Description", style="dim")
    
    table.add_row(
        "🤖 AI", 
        "ask, explain, fix, refactor, generate",
        "AI-powered coding assistance"
    )
    table.add_row(
        "📁 Files", 
        "read, write, edit, ls",
        "File operations with syntax highlighting"
    )
    table.add_row(
        "🔍 Search", 
        "find, search",
        "Find files and search content"
    )
    table.add_row(
        "⚡ System", 
        "run, bash",
        "Execute shell commands safely"
    )
    table.add_row(
        "📋 Tasks", 
        "todo",
        "Manage todos and tasks"
    )
    table.add_row(
        "🎮 Session", 
        "clear, reset, help, exit",
        "Session management"
    )
    
    console.print(table)
    
    # Final message
    console.print("\\n" + "="*60)
    console.print(Panel(
        "🎯 [bold green]Demo Complete![/bold green]\\n\\n"
        "To start Claude Code:\\n"
        "• [cyan]python main.py[/cyan] - Start interactive mode\\n"
        "• [cyan]./start.sh[/cyan] - Use startup script\\n\\n"
        "Features include:\\n"
        "• 🤖 AI assistance with Ollama\\n"
        "• 📁 Complete file operations\\n"
        "• 🔍 Advanced search capabilities\\n"
        "• ⚡ Safe command execution\\n"
        "• 🎨 Beautiful CLI interface\\n"
        "• ⌨️  Interactive features (Ctrl+C, tab completion)\\n"
        "• 📋 Todo management\\n"
        "• 🔄 Conversation history",
        title="🚀 Ready to Use",
        border_style="green"
    ))


if __name__ == "__main__":
    asyncio.run(demo())