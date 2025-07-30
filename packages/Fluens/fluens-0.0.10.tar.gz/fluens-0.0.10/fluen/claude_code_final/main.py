#!/usr/bin/env python3
"""
Claude Code - Exact replica using Ollama
Entry point for the Claude Code CLI
"""

import asyncio
import sys
from .claude_code.cli import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)