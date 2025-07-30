# Claude Code - Python Implementation

A complete Claude Code CLI implementation in Python using Ollama, prompt_toolkit, and rich.

## Features

✨ **Complete Claude Code Experience**
- 🤖 AI-powered coding assistance with Ollama
- 📁 Full file operations (read, write, edit, multiedit)
- 🔍 Advanced search capabilities (glob, grep)
- ⚡ Shell command execution with safety checks
- 📋 Todo management system
- 🎨 Beautiful CLI interface with syntax highlighting
- ⌨️  Interactive features with Ctrl+C interrupt support
- 🔄 Conversation history and context management

## Installation

1. **Clone and setup:**
   ```bash
   cd claude_code_final
   pip install -r requirements.txt
   ```

2. **Install Ollama and pull a model:**
   ```bash
   # Install Ollama (visit https://ollama.ai for instructions)
   ollama pull llama3.2:latest
   # or any other model you prefer
   ```

3. **Run Claude Code:**
   ```bash
   python main.py
   ```

## Commands

### AI Commands
- `ask <question>` - Ask Claude anything
- `explain <file>` - Explain code in file
- `refactor <file>` - Refactor code with suggestions
- `fix <file>` - Find and fix bugs
- `generate <description>` - Generate code from description

### File Operations
- `read <file>` - Read file contents with syntax highlighting
- `write <file> <content>` - Write content to file
- `edit <file> <old> <new>` - Replace text in file
- `ls [path]` - List directory contents

### Search Operations
- `find <pattern>` - Find files matching pattern
- `search <pattern>` - Search file contents for pattern

### System Operations
- `run <command>` - Execute shell command safely
- `bash <command>` - Execute bash command
- `todo [list|add] [item]` - Manage todos

### Session Management
- `clear` - Clear screen
- `reset` - Reset conversation history
- `history` - Show conversation history
- `help [command]` - Show help
- `commands` - List all commands
- `exit` / `quit` - Exit Claude Code

## Interactive Features

- **Ctrl+C Interrupt**: Safely interrupt any operation
- **Tab Completion**: Auto-complete commands
- **Command History**: Navigate through previous commands
- **Syntax Highlighting**: Beautiful code display
- **Progress Indicators**: Visual feedback for operations
- **Confirmations**: Safety prompts for dangerous operations

## Configuration

By default, Claude Code connects to Ollama at `http://localhost:11434` using the `llama3.2:latest` model. You can modify these settings in `claude_code/llm_client.py`.

## Architecture

```
claude_code_final/
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── setup.py            # Package setup
└── claude_code/        # Main package
    ├── __init__.py     # Package init
    ├── cli.py          # Main CLI interface
    ├── llm_client.py   # Ollama LLM integration
    ├── tools.py        # All Claude Code tools
    └── prompts.py      # System prompts
```

## Safety Features

- Command validation and dangerous operation blocking
- File path sanitization and validation
- Timeout handling for long operations
- Graceful error handling and recovery
- User confirmation for destructive operations

## Dependencies

- `ollama` - LLM integration
- `prompt-toolkit` - Interactive CLI
- `rich` - Beautiful terminal formatting
- `click` - Command-line interface
- `aiofiles` - Async file operations
- `httpx` - HTTP client
- `halo` - Spinner animations

## License

MIT License - See LICENSE file for details.