#!/usr/bin/env python3
"""
Claude Code - Exact replica using Ollama
Entry point for the Claude Code CLI
"""

import asyncio
import sys
from .cli import main as async_main

def main():
    """Synchronous entry point for console scripts"""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()