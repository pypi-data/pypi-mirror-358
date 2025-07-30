#!/bin/bash

# Claude Code Installation Script with Playwright Web Search

echo "🚀 Installing Claude Code with Playwright Web Search..."
echo "=================================================="

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Check Ollama
echo "🤖 Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
        echo "✅ Ollama is running"
    else
        echo "⚠️  Ollama is not running. Start it with: ollama serve"
    fi
    
    # Check for available models
    echo "📋 Available models:"
    ollama list
    
    # Suggest a model if none are available
    if ! ollama list | grep -q "llama3.2"; then
        echo "💡 Suggested: ollama pull llama3.2:latest"
    fi
else
    echo "❌ Ollama not found. Please install from: https://ollama.ai"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "🚀 To start Claude Code:"
echo "   python main.py"
echo ""
echo "📋 Prerequisites checklist:"
echo "   ✅ Python dependencies installed"
echo "   ✅ Playwright browsers installed"
echo "   $(if command -v ollama &> /dev/null; then echo '✅'; else echo '❌'; fi) Ollama installed"
echo "   $(if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then echo '✅'; else echo '❌'; fi) Ollama running"
echo ""
echo "🌐 Web Search Features:"
echo "   • Real-time Bing search with Playwright"
echo "   • Domain filtering (allow/block lists)"
echo "   • Clean result extraction and formatting"
echo "   • Integrated with Claude Code tool system"