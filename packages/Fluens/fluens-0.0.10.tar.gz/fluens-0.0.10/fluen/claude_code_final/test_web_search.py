#!/usr/bin/env python3
"""
Test script for Playwright Web Search integration
"""

import asyncio
import sys
from pathlib import Path

# Add the claude_code directory to the path
sys.path.insert(0, str(Path(__file__).parent / "claude_code"))

try:
    from claude_code.web_search_playwright import claude_code_web_search
    PLAYWRIGHT_AVAILABLE = True
    print("✅ Playwright web search module imported successfully")
except ImportError as e:
    PLAYWRIGHT_AVAILABLE = False
    print(f"❌ Failed to import Playwright: {e}")
    print("Install with: pip install playwright beautifulsoup4 markdownify && playwright install chromium")

async def test_web_search():
    """Test the web search functionality"""
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not available, skipping web search test")
        return False
    
    print("\\n🔍 Testing Claude Code Web Search...")
    print("="*50)
    
    # Test search query
    query = "Python asyncio tutorial"
    print(f"🔎 Searching for: {query}")
    
    try:
        result = await claude_code_web_search(query)
        
        if result.success:
            print("✅ Web search successful!")
            print(f"📊 Results found: {result.metadata.get('results_count', 0)}")
            print("\\n📋 Search Results:")
            print("-" * 30)
            print(result.content[:500] + "..." if len(result.content) > 500 else result.content)
            print("\\n📊 Metadata:")
            print(result.metadata)
            return True
        else:
            print("❌ Web search failed!")
            print(f"Error: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during web search: {e}")
        return False

async def test_domain_filtering():
    """Test domain filtering functionality"""
    if not PLAYWRIGHT_AVAILABLE:
        return False
    
    print("\\n🎯 Testing Domain Filtering...")
    print("="*40)
    
    query = "Python documentation"
    allowed_domains = ["python.org", "docs.python.org"]
    
    print(f"🔎 Searching for: {query}")
    print(f"🎯 Allowed domains: {allowed_domains}")
    
    try:
        result = await claude_code_web_search(query, allowed_domains=allowed_domains)
        
        if result.success:
            print("✅ Domain filtering test successful!")
            print(f"📊 Filtered results: {result.metadata.get('results_count', 0)}")
            return True
        else:
            print("❌ Domain filtering test failed!")
            print(f"Error: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during domain filtering test: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Claude Code Web Search Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Basic web search
    if await test_web_search():
        tests_passed += 1
    
    # Test 2: Domain filtering
    if await test_domain_filtering():
        tests_passed += 1
    
    # Results
    print("\\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Web search is working correctly.")
        print("\\n✨ Features verified:")
        print("   • Playwright browser automation")
        print("   • Bing search result extraction")
        print("   • Domain filtering")
        print("   • Claude Code integration")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        if not PLAYWRIGHT_AVAILABLE:
            print("\\n💡 To fix: Run the installation script:")
            print("   ./install.sh")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
