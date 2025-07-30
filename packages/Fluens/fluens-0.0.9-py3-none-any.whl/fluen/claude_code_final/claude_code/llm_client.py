"""
LLM Client using Ollama - Exact Claude Code replica
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, Callable, AsyncGenerator
from ollama import AsyncClient
import logging

logger = logging.getLogger(__name__)


class OllamaLLMClient:
    """Ollama-based LLM client that mimics Claude Code exactly"""
    
    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "llama3.2:latest",
        stream: bool = True,
        think: bool = False
    ):
        self.client = AsyncClient(host=host)
        self.model = model
        self.stream = stream
        self.think = think
        self.conversation_history: List[Dict[str, str]] = []
        self.tools = {}
        
    def register_tool(self, name: str, func: Callable, schema: Dict):
        """Register a tool function"""
        self.tools[name] = {
            "function": func,
            "schema": schema
        }
        
    async def chat_with_tools(
        self,
        message: str,
        system_prompt: str,
        tool_schemas: List[Dict] = None
    ) -> AsyncGenerator[str, None]:
        """Chat with tool calling capability - exact Claude Code behavior"""
        
        # Add /no_think suffix for Qwen models
        if "qwen" in self.model.lower():
            system_prompt = system_prompt + "/no_think"
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": message})
        
        try:
            # First get the LLM response
            response_content = ""
            tool_calls = []
            
            if tool_schemas:
                # Format tools for Ollama
                tools = []
                for schema in tool_schemas:
                    tools.append({
                        "type": "function",
                        "function": schema
                    })
                
                # Get response with tools
                async for chunk in await self.client.chat(
                    model=self.model,
                    messages=messages,
                    stream=self.stream,
                    tools=tools,
                    think=self.think
                ):
                    if chunk.get('message'):
                        msg = chunk['message']
                        
                        # Handle content
                        if msg.get('content'):
                            content = msg['content']
                            response_content += content
                            
                            # Skip think tokens and empty content when think is False
                            if not self.think:
                                if '<think>' in content or '</think>' in content or content.strip() == '':
                                    continue
                            
                            yield content
                        
                        # Handle tool calls
                        if msg.get('tool_calls'):
                            tool_calls.extend(msg['tool_calls'])
                
                # Execute tool calls if any
                if tool_calls:
                    yield "\n\n"
                    for tool_call in tool_calls:
                        if tool_call.get('function'):
                            func_name = tool_call['function']['name']
                            func_args = tool_call['function'].get('arguments', {})
                            
                            yield f"🔧 Using {func_name}({', '.join(f'{k}={v}' for k, v in func_args.items())})\n"
                            
                            if func_name in self.tools:
                                try:
                                    # Execute the tool
                                    tool_func = self.tools[func_name]["function"]
                                    if asyncio.iscoroutinefunction(tool_func):
                                        result = await tool_func(**func_args)
                                    else:
                                        result = tool_func(**func_args)
                                    
                                    # Display result
                                    if hasattr(result, 'content'):
                                        yield f"{result.content}\n"
                                        if result.error:
                                            yield f"❌ Error: {result.error}\n"
                                    else:
                                        yield f"{str(result)}\n"
                                        
                                except Exception as e:
                                    yield f"❌ Error executing {func_name}: {str(e)}\n"
                            else:
                                yield f"❌ Unknown tool: {func_name}\n"
                    
                    # Continue conversation with tool results
                    messages.append({"role": "assistant", "content": response_content})
                    
                    # Add tool results to messages
                    for tool_call in tool_calls:
                        if tool_call.get('function'):
                            func_name = tool_call['function']['name']
                            if func_name in self.tools:
                                messages.append({
                                    "role": "tool",
                                    "name": func_name,
                                    "content": "Tool executed successfully"
                                })
                    
                    # Get follow-up response if needed
                    follow_up_content = ""
                    async for chunk in await self.client.chat(
                        model=self.model,
                        messages=messages,
                        stream=self.stream,
                        think=self.think
                    ):
                        if chunk.get('message') and chunk['message'].get('content'):
                            content = chunk['message']['content']
                            follow_up_content += content
                            
                            # Skip think tokens and empty content when think is False
                            if not self.think:
                                if '<think>' in content or '</think>' in content or content.strip() == '':
                                    continue
                            
                            yield content
                    
                    # Update conversation history
                    self.conversation_history.extend([
                        {"role": "user", "content": message},
                        {"role": "assistant", "content": response_content + follow_up_content}
                    ])
                else:
                    # No tool calls, just add to history
                    self.conversation_history.extend([
                        {"role": "user", "content": message},
                        {"role": "assistant", "content": response_content}
                    ])
            else:
                # No tools available, regular chat
                async for chunk in await self.client.chat(
                    model=self.model,
                    messages=messages,
                    stream=self.stream,
                    think=self.think
                ):
                    if chunk.get('message') and chunk['message'].get('content'):
                        content = chunk['message']['content']
                        response_content += content
                        
                        # Skip think tokens when think is False
                        if not self.think and ('<think>' in content or '</think>' in content):
                            continue
                        
                        yield content
                
                # Add to history
                self.conversation_history.extend([
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": response_content}
                ])
                        
        except Exception as e:
            error_msg = f"❌ Error communicating with LLM: {str(e)}"
            logger.error(error_msg)
            yield error_msg
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    async def test_connection(self) -> bool:
        """Test if the LLM is accessible"""
        try:
            response = await self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                stream=False,
                think=self.think
            )
            return bool(response.get('message'))
        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            return False