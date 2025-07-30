# Claude Code - Usage Guide

## 🚀 Quick Start

1. **Start Ollama:**
   ```bash
   ollama serve
   # In another terminal:
   ollama pull llama3.2:latest  # or your preferred model
   ```

2. **Start Claude Code:**
   ```bash
   python main.py
   ```

3. **Start coding!**
   ```
   > read main.py
   > help me fix the bug in this file
   > create a new file called utils.py with helper functions
   > run the tests
   ```

## 💬 How to Use

### Just talk to Claude naturally:

```
> I need to create a web scraper for news articles
> Read the config.json file and explain what each setting does  
> There's a bug in user.py line 45, can you fix it?
> Run the tests and fix any failures
> Create a README for this project
```

### Key Features:

**🤖 AI-Powered**: 
- Uses your local Ollama model
- Understands natural language requests
- Maintains conversation context

**📁 File Operations**:
- Reads/writes files with syntax highlighting
- Makes precise edits to fix bugs
- Creates new files with content

**⚡ Command Execution**:
- Runs shell commands safely
- Executes tests and builds
- Installs dependencies

**🔍 Smart Search**:
- Finds files by patterns
- Searches content with regex
- Analyzes code structure

**📋 Task Management**:
- Tracks todos automatically
- Breaks down complex tasks
- Shows progress

## 🎯 Examples

### Debugging Code
```
> There's an error when I run python app.py, can you help?
```
Claude will:
1. Read the app.py file
2. Run it to see the error
3. Identify the issue
4. Fix the code
5. Test the fix

### Creating New Features
```
> Add a login system to my Flask app with password hashing
```
Claude will:
1. Examine your existing Flask code
2. Create authentication routes
3. Add password hashing
4. Update templates
5. Test the implementation

### Code Review
```
> Review my code for security issues and best practices
```
Claude will:
1. Read all your code files
2. Identify security vulnerabilities
3. Suggest improvements
4. Make the fixes
5. Document the changes

## ⌨️ Interactive Features

- **Ctrl+C**: Interrupt any operation
- **Tab**: Auto-complete (when available)
- **↑/↓**: Navigate command history
- **clear**: Clear screen
- **reset**: Clear conversation history
- **help**: Show help
- **exit**: Quit Claude Code

## 🔧 Configuration

Edit `claude_code/llm_client.py` to customize:

```python
class OllamaLLMClient:
    def __init__(
        self,
        host: str = "http://localhost:11434",  # Your Ollama server
        model: str = "llama3.2:latest",        # Your preferred model
        stream: bool = True                    # Enable streaming
    ):
```

## 🛠️ Troubleshooting

**"LLM connection failed"**:
- Ensure Ollama is running: `ollama serve`
- Check if model is available: `ollama list`
- Verify the host/port in configuration

**"Command blocked for security"**:
- Some dangerous commands are blocked
- Claude Code protects against destructive operations

**Tool execution errors**:
- Check file permissions
- Ensure you're in the correct directory
- Verify file paths are correct

## 🎨 Tips for Best Results

1. **Be specific**: "Fix the bug in line 45" vs "fix this code"
2. **Provide context**: "I'm building a web API" helps Claude understand
3. **Use natural language**: Talk to Claude like a colleague
4. **Let Claude work**: It will use multiple tools to complete tasks
5. **Ask follow-ups**: "Can you also add error handling?"

## 🔒 Security

Claude Code includes safety features:
- Blocks dangerous shell commands
- Validates file paths
- Asks for confirmation on destructive operations
- Sandboxes operations to your workspace

You have complete control - Claude only does what you ask!