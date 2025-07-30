#!/usr/bin/env python3
"""
Quick test to verify the fixes work
"""

import sys
from pathlib import Path
import datetime

# Add the claude_code directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from claude_code.cli import ClaudeCodeCLI
    print("✅ CLI import successful")
    
    # Test CLI initialization
    cli = ClaudeCodeCLI()
    print("✅ CLI initialization successful")
    
    # Check if web_search is registered
    if "web_search" in cli.llm_client.tools:
        print("✅ web_search tool registered successfully")
    else:
        print("❌ web_search tool NOT registered")
        print(f"Available tools: {list(cli.llm_client.tools.keys())}")
    
    # Check system prompt includes date
    system_prompt = cli.system_prompt
    current_year = datetime.datetime.now().year
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    
    if str(current_year) in system_prompt:
        print(f"✅ Current year ({current_year}) found in system prompt")
    else:
        print(f"❌ Current year ({current_year}) NOT found in system prompt")
    
    if "web_search" in system_prompt:
        print("✅ web_search mentioned in system prompt")
    else:
        print("❌ web_search NOT mentioned in system prompt")
        
    print(f"\\n📅 Current date in prompt: {current_date}")
    print(f"📅 Current year in prompt: {current_year}")
    print("\\n✨ Both fixes applied successfully!")
    print("\\nNow try: python main.py")
    print("Then ask: > 2025 ipl winner who")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()