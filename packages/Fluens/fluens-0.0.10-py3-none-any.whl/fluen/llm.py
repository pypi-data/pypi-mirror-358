from ollama import Client, ChatResponse
from typing import List, Dict, Any, Optional, Callable


class OllamaClient:
    def __init__(
        self,
        host: str = "http://192.168.170.76:11434",
        model: str = "qwen2.5:7b-instruct",
        stream: bool = False
    ):
        self.client = Client(host=host)
        self.model = model
        self.stream = stream
        self.available_functions = {}

    def chat(
        self,
        messages: List[Dict[str, str]],
        think: bool = False,
        tools: Optional[List[Any]] = None,
        stream: Optional[bool] = None
    ) -> ChatResponse:
        """Simple, elegant chat interface"""
        
        response = self.client.chat(
            self.model,
            messages=messages,
            think=think,
            tools=tools,
            stream=stream or self.stream
        )
        
        if tools and response.message.tool_calls:
            self._handle_tool_calls(response, messages)
            
        return response

    def add_tool(self, func: Callable, name: Optional[str] = None):
        """Add a function as a tool"""
        tool_name = name or func.__name__
        self.available_functions[tool_name] = func
        return self

    def think_and_respond(self, message: str) -> ChatResponse:
        """Quick thinking interface"""
        messages = [{"role": "user", "content": message}]
        response = self.client.chat(messages, think=True)
        
        if hasattr(response.message, 'thinking'):
            print('Thinking:\n========\n\n' + response.message.thinking)
            print('\nResponse:\n========\n\n' + response.message.content)
            
        return response

    def _handle_tool_calls(self, response: ChatResponse, messages: List[Dict]):
        """Handle tool calls elegantly"""
        for tool in response.message.tool_calls:
            if function_to_call := self.available_functions.get(tool.function.name):
                output = function_to_call(**tool.function.arguments)
                messages.extend([
                    response.message,
                    {"role": "tool", "content": str(output), "name": tool.function.name}
                ])
