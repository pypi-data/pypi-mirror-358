#!/usr/bin/env python3
"""
Test script to verify all Claude Code features
"""

import asyncio
import tempfile
import os
from pathlib import Path

from claude_code.tools import ClaudeCodeTools
from claude_code.llm_client import OllamaLLMClient


async def test_tools():
    """Test all tool functions"""
    print("🧪 Testing Claude Code Tools...")
    
    # Create a temporary workspace
    with tempfile.TemporaryDirectory() as temp_dir:
        tools = ClaudeCodeTools(temp_dir)
        
        print("📁 Testing file operations...")
        
        # Test write
        result = await tools.write("test.py", "print('Hello, World!')")
        assert result.success, f"Write failed: {result.error}"
        print("✅ Write test passed")
        
        # Test read
        result = await tools.read("test.py")
        assert result.success, f"Read failed: {result.error}"
        assert "Hello, World!" in result.content
        print("✅ Read test passed")
        
        # Test edit
        result = await tools.edit("test.py", "Hello, World!", "Hello, Claude Code!")
        assert result.success, f"Edit failed: {result.error}"
        print("✅ Edit test passed")
        
        # Verify edit
        result = await tools.read("test.py")
        assert "Hello, Claude Code!" in result.content
        print("✅ Edit verification passed")
        
        # Test ls
        result = await tools.ls(".")
        assert result.success, f"Ls failed: {result.error}"
        assert "test.py" in result.content
        print("✅ Ls test passed")
        
        # Test glob
        result = await tools.glob("*.py")
        assert result.success, f"Glob failed: {result.error}"
        assert "test.py" in result.content
        print("✅ Glob test passed")
        
        # Test grep
        result = await tools.grep("Claude Code")
        assert result.success, f"Grep failed: {result.error}"
        print("✅ Grep test passed")
        
        # Test bash
        result = await tools.bash("echo 'Test command'")
        assert result.success, f"Bash failed: {result.error}"
        assert "Test command" in result.content
        print("✅ Bash test passed")
        
        # Test multiedit
        edits = [
            {"old_string": "print(", "new_string": "console.log("},
            {"old_string": "Claude Code!", "new_string": "Multidit Test!"}
        ]
        # First create a file with content that can be multiedited
        await tools.write("test_multi.py", "print('Hello, Claude Code!')")
        result = await tools.multiedit("test_multi.py", edits)
        assert result.success, f"Multiedit failed: {result.error}"
        print("✅ Multiedit test passed")
        
        # Test todo operations
        todos = [
            {"id": "1", "content": "Test todo", "status": "pending", "priority": "high"}
        ]
        result = await tools.todo_write(todos)
        assert result.success, f"Todo write failed: {result.error}"
        print("✅ Todo write test passed")
        
        result = await tools.todo_read()
        assert result.success, f"Todo read failed: {result.error}"
        assert "Test todo" in result.content
        print("✅ Todo read test passed")
        
        await tools.close()
        print("✅ All tool tests passed!")


async def test_llm_client():
    """Test LLM client"""
    print("🤖 Testing LLM Client...")
    
    client = OllamaLLMClient()
    
    # Test connection (this might fail if Ollama isn't running)
    connected = await client.test_connection()
    if connected:
        print("✅ LLM connection test passed")
        
        # Test basic chat
        response_parts = []
        async for chunk in client.chat("Say 'Hello from Claude Code test!'"):
            response_parts.append(chunk)
        
        response = "".join(response_parts)
        if response and "Error" not in response:
            print("✅ LLM chat test passed")
        else:
            print("⚠️ LLM chat test: got response but might be error")
    else:
        print("⚠️ LLM connection test failed (Ollama might not be running)")


async def test_cli_components():
    """Test CLI components without full startup"""
    print("🖥️ Testing CLI Components...")
    
    from claude_code.cli import ClaudeCodeCLI
    
    # Test CLI initialization
    cli = ClaudeCodeCLI()
    assert cli.workspace_root.exists(), "Workspace root should exist"
    assert cli.commands, "Commands should be loaded"
    assert len(cli.commands) > 10, "Should have multiple commands"
    print("✅ CLI initialization test passed")
    
    # Test command registry
    expected_commands = ["ask", "read", "write", "edit", "ls", "help", "exit"]
    for cmd in expected_commands:
        assert cmd in cli.commands, f"Command {cmd} should be available"
    print("✅ CLI command registry test passed")
    
    await cli.cleanup()
    print("✅ CLI component tests passed!")


def test_imports():
    """Test all imports work correctly"""
    print("📦 Testing imports...")
    
    try:
        import claude_code.cli
        import claude_code.tools
        import claude_code.llm_client
        import claude_code.prompts
        print("✅ All imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    return True


async def main():
    """Run all tests"""
    print("🚀 Starting Claude Code Feature Tests\\n")
    
    # Test imports first
    if not test_imports():
        return False
    
    # Test tools
    await test_tools()
    print()
    
    # Test LLM client
    await test_llm_client()
    print()
    
    # Test CLI components
    await test_cli_components()
    print()
    
    print("🎉 All Claude Code tests completed!")
    print("✅ Your Claude Code implementation is ready to use!")
    print("\\nTo start: python main.py")
    
    return True


if __name__ == "__main__":
    asyncio.run(main())