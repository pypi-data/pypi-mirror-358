"""
Playwright-based Web Search for Claude Code
Copied and adapted from OpenCursor code_agent
"""

import asyncio
import os
import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from .tools_complete import ToolResult


class PlaywrightBrowser:
    """A simplified browser interaction manager using Playwright"""

    def __init__(self, headless=False):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.headless = headless

    async def initialize(self):
        """Initialize the browser if not already done"""
        if self.page is not None:
            return

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.page = await self.context.new_page()

    async def navigate_to(self, url: str):
        """Navigate to a URL"""
        await self.initialize()
        try:
            await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception as e:
            print(f"Navigation error: {str(e)}")

    async def get_page_html(self):
        """Get the HTML content of the current page"""
        return await self.page.content()

    async def close(self):
        """Close browser and clean up resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


class PlaywrightSearch:
    """Web search implementation using Playwright"""

    def __init__(self, search_provider: str = 'bing', headless: bool = False):
        """Initialize the search agent"""
        self.browser = PlaywrightBrowser(headless=headless)
        self.search_provider = search_provider

    async def search(self, query: str, num_results: int = 10) -> List[Dict[str, str]]:
        """Perform a web search and return results"""
        try:
            # Navigate to search engine
            search_url = f'https://www.{self.search_provider}.com/search?q={query}'
            await self.browser.navigate_to(search_url)
            
            # Get the HTML content
            html = await self.browser.get_page_html()
            
            # Extract search results
            if self.search_provider == 'bing':
                search_results = self._extract_bing_results(html, num_results)
            elif self.search_provider == 'duckduckgo':
                search_results = self._extract_duckduckgo_results(html, num_results)
            else:
                search_results = []
                
            return search_results
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []
        finally:
            await self.browser.close()

    def _extract_bing_results(self, html: str, max_results: int = 10) -> List[Dict[str, str]]:
        """Extract search results from Bing HTML content"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []

        # Process Bing search results
        result_elements = soup.find_all('li', class_='b_algo')

        for result_element in result_elements:
            if len(results) >= max_results:
                break

            title = None
            url = None
            description = None

            # Find title and URL
            title_header = result_element.find('h2')
            if title_header:
                title_link = title_header.find('a')
                if title_link and title_link.get('href'):
                    url = title_link['href']
                    title = title_link.get_text(strip=True)

            # Find description
            caption_div = result_element.find('div', class_='b_caption')
            if caption_div:
                p_tag = caption_div.find('p')
                if p_tag:
                    description = p_tag.get_text(strip=True)

            # Add valid results
            if url and title:
                results.append({
                    "url": url,
                    "title": title,
                    "description": description or ""
                })

        return results

    def _extract_duckduckgo_results(self, html_content: str, max_results: int = 10) -> List[Dict[str, str]]:
        """Extract search results from DuckDuckGo HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []

        # Find all result containers
        result_elements = soup.find_all('article', {'data-testid': 'result'})

        for result_element in result_elements:
            if len(results) >= max_results:
                break
                
            # URL
            url_element = result_element.find('a', {'data-testid': 'result-extras-url-link'})
            url = url_element['href'] if url_element else None

            # Title
            title_element = result_element.find('a', {'data-testid': 'result-title-a'})
            title = title_element.get_text(strip=True) if title_element else None

            # Description (Snippet)
            description_element = result_element.find('div', {'data-result': 'snippet'})
            if description_element:
                # Remove date spans if present
                date_span = description_element.find('span', class_=re.compile(r'MILR5XIV'))
                if date_span:
                    date_span.decompose()
                description = description_element.get_text(strip=True)
            else:
                description = None

            if url and title:
                results.append({
                    "url": url,
                    "title": title,
                    "description": description or ""
                })

        return results


class ClaudeCodeWebSearch:
    """Claude Code web search using Playwright - exact integration"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
    
    async def web_search(self, query: str, allowed_domains: List[str] = None, 
                        blocked_domains: List[str] = None, max_results: int = 10) -> ToolResult:
        """
        Web search with domain filtering - EXACT Claude Code algorithm
        """
        try:
            if not query or len(query.strip()) < 2:
                return ToolResult("", error="Search query must be at least 2 characters", success=False)
            
            # Initialize search
            search_agent = PlaywrightSearch(search_provider="bing", headless=self.headless)
            
            # Perform search
            results = await search_agent.search(query.strip(), num_results=max_results)
            
            if not results:
                return ToolResult(f"No search results found for: {query}", metadata={
                    "query": query,
                    "results_count": 0
                })
            
            # Apply domain filtering
            filtered_results = []
            for result in results:
                url = result.get('url', '')
                
                # Check blocked domains
                if blocked_domains:
                    if any(blocked_domain in url for blocked_domain in blocked_domains):
                        continue
                
                # Check allowed domains
                if allowed_domains:
                    if not any(allowed_domain in url for allowed_domain in allowed_domains):
                        continue
                
                filtered_results.append(result)
            
            # Format results exactly like Claude Code
            if not filtered_results:
                return ToolResult(f"No results found after domain filtering for: {query}", metadata={
                    "query": query,
                    "results_count": 0,
                    "filtered_count": len(results)
                })
            
            # Claude Code format for search results
            formatted_results = f"🔍 Web search results for: {query}\n\n"
            
            for i, result in enumerate(filtered_results, 1):
                formatted_results += f"{i}. **{result['title']}**\n"
                formatted_results += f"   {result['url']}\n"
                if result.get('description'):
                    # Truncate description if too long
                    description = result['description']
                    if len(description) > 200:
                        description = description[:200] + "..."
                    formatted_results += f"   {description}\n"
                formatted_results += "\n"
            
            return ToolResult(formatted_results, metadata={
                "query": query,
                "results_count": len(filtered_results),
                "total_found": len(results),
                "allowed_domains": allowed_domains or [],
                "blocked_domains": blocked_domains or []
            })
            
        except Exception as e:
            return ToolResult("", error=f"Error performing web search: {str(e)}", success=False)


# Integration function for Claude Code tools
async def claude_code_web_search(query: str, allowed_domains: List[str] = None, 
                                blocked_domains: List[str] = None) -> ToolResult:
    """
    Claude Code web search tool using Playwright
    
    Args:
        query: The search query to use
        allowed_domains: Only include search results from these domains (optional)
        blocked_domains: Never include search results from these domains (optional)
    
    Returns:
        ToolResult: Formatted search results with metadata
    """
    search_tool = ClaudeCodeWebSearch(headless=False)
    return await search_tool.web_search(query, allowed_domains, blocked_domains)


# Test function
async def test_web_search():
    """Test the web search functionality"""
    print("Testing Claude Code Web Search...")
    
    result = await claude_code_web_search("Python programming tutorials")
    
    if result.success:
        print("✅ Search successful!")
        print(result.content)
        print(f"Metadata: {result.metadata}")
    else:
        print("❌ Search failed!")
        print(f"Error: {result.error}")


if __name__ == "__main__":
    asyncio.run(test_web_search())
