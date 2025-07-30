#!/bin/bash

# Claude Code Startup Script

echo "🚀 Starting Claude Code..."
echo "📁 Working directory: $(pwd)"
echo "🔗 Checking dependencies..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running at localhost:11434"
    echo "   Please start Ollama first: ollama serve"
    echo "   Or update the host in claude_code/llm_client.py"
fi

echo "✅ Starting Claude Code CLI..."
python3 main.py