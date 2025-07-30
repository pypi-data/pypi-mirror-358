#!/usr/bin/env python3
"""
Widget System for Claude Code Terminal
Provides modular, extensible widgets for different content types
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from textual.widgets import Markdown, Static, Collapsible
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult
from textual import events
import json

def to_camel_case(text):
    words = text.split('_')
    return ''.join(word.capitalize() for word in words)

class BaseWidget(ABC):
    """Base class for all terminal widgets"""
    
    def __init__(self, widget_id: str, data: Any = None, metadata: Dict = None):
        self.widget_id = widget_id
        self.data = data
        self.metadata = metadata or {}
        self.expanded = True
        self.visible = True
    
    @abstractmethod
    def render(self) -> str:
        """Render widget content as markdown string"""
        pass
    
    def toggle_expansion(self):
        """Toggle widget expansion state"""
        self.expanded = not self.expanded
    
    def set_visibility(self, visible: bool):
        """Set widget visibility"""
        self.visible = visible


class MarkdownWidget(BaseWidget):
    """Widget for rendering markdown content"""
    
    def __init__(self, widget_id: str, content: str, title: str = None, **kwargs):
        super().__init__(widget_id, content, kwargs)
        self.content = content
        self.title = title
    
    def render(self) -> str:
        if not self.visible:
            return ""
        
        if self.title:
            return f"### {self.title}\n\n{self.content}\n\n"
        return f"{self.content}\n\n"


class ToolWidget(BaseWidget):
    """Widget for displaying tool calls and results"""
    
    def __init__(self, widget_id: str, tool_name: str, arguments: Dict, 
                 result: str = None, error: str = None, **kwargs):
        super().__init__(widget_id, {"tool_name": tool_name, "arguments": arguments}, kwargs)
        self.tool_name = tool_name
        self.arguments = arguments
        self.result = result
        self.error = error
        self.expanded = False  # Tools start collapsed
    
    def set_result(self, result: str, error: str = None):
        """Set tool execution result"""
        self.result = result
        self.error = error
    
    def render(self) -> str:
        if not self.visible:
            return ""
        
        # Format arguments
        args_str = ", ".join([f"{k}={v}" for k, v in self.arguments.items()])
        args_str_first = str(self.arguments.values()[0])
        
        # Expansion indicator
        expand_indicator = "▼" if self.expanded else "▶"
        
        # Tool call header
        header = f"🟢 **{to_camel_case(self.tool_name)}**({args_str_first}) {expand_indicator}"
        
        if not self.expanded:
            return f"{header}\n\n"
        
        # Show result if expanded
        content = [header, ""]
        
        if self.error:
            content.append(f"❌ **Error:** {self.error}")
        elif self.result:
            # Truncate long results
            result_content = self.result
            lines = result_content.split('\n')
            if len(lines) > 10:
                preview = '\n'.join(lines[:3]) + f'\n... ({len(lines)} lines total)'
                content.append(f"```\n{preview}\n```")
            else:
                content.append(f"```\n{result_content}\n```")
        else:
            content.append("⏳ Executing...")
        
        return "\n".join(content) + "\n\n"


class MessageWidget(BaseWidget):
    """Widget for user and assistant messages"""
    
    def __init__(self, widget_id: str, content: str, message_type: str, **kwargs):
        super().__init__(widget_id, content, kwargs)
        self.content = content
        self.message_type = message_type  # 'user' or 'assistant'
    
    def render(self) -> str:
        if not self.visible:
            return ""
        
        if self.message_type == "user":
            return f"> {self.content}\n\n"
        else:  # assistant
            return f"● {self.content}\n\n"


class StatusWidget(BaseWidget):
    """Widget for status updates and system messages"""
    
    def __init__(self, widget_id: str, status: str, status_type: str = "info", **kwargs):
        super().__init__(widget_id, status, kwargs)
        self.status = status
        self.status_type = status_type  # 'info', 'warning', 'error', 'success'
    
    def render(self) -> str:
        if not self.visible:
            return ""
        
        icons = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'success': '✅'
        }
        
        icon = icons.get(self.status_type, 'ℹ️')
        return f"{icon} {self.status}\n\n"


class WidgetManager:
    """Manages all widgets in the terminal display"""
    
    def __init__(self):
        self.widgets: List[BaseWidget] = []
        self.widget_map: Dict[str, BaseWidget] = {}
        self._widget_counter = 0
    
    def _generate_widget_id(self, prefix: str = "widget") -> str:
        """Generate unique widget ID"""
        self._widget_counter += 1
        return f"{prefix}_{self._widget_counter}"
    
    def add_widget(self, widget: BaseWidget) -> str:
        """Add widget to manager"""
        self.widgets.append(widget)
        self.widget_map[widget.widget_id] = widget
        return widget.widget_id
    
    def remove_widget(self, widget_id: str) -> bool:
        """Remove widget by ID"""
        if widget_id in self.widget_map:
            widget = self.widget_map[widget_id]
            self.widgets.remove(widget)
            del self.widget_map[widget_id]
            return True
        return False
    
    def get_widget(self, widget_id: str) -> Optional[BaseWidget]:
        """Get widget by ID"""
        return self.widget_map.get(widget_id)
    
    def clear(self):
        """Clear all widgets"""
        self.widgets.clear()
        self.widget_map.clear()
    
    def add_message(self, content: str, message_type: str) -> str:
        """Add message widget"""
        widget_id = self._generate_widget_id("msg")
        widget = MessageWidget(widget_id, content, message_type)
        return self.add_widget(widget)
    
    def add_tool_call(self, tool_name: str, arguments: Dict) -> str:
        """Add tool call widget"""
        widget_id = self._generate_widget_id("tool")
        widget = ToolWidget(widget_id, tool_name, arguments)
        return self.add_widget(widget)
    
    def update_tool_result(self, widget_id: str, result: str, error: str = None):
        """Update tool widget with result"""
        widget = self.get_widget(widget_id)
        if isinstance(widget, ToolWidget):
            widget.set_result(result, error)
    
    def add_markdown(self, content: str, title: str = None) -> str:
        """Add markdown widget"""
        widget_id = self._generate_widget_id("md")
        widget = MarkdownWidget(widget_id, content, title)
        return self.add_widget(widget)
    
    def add_status(self, status: str, status_type: str = "info") -> str:
        """Add status widget"""
        widget_id = self._generate_widget_id("status")
        widget = StatusWidget(widget_id, status, status_type)
        return self.add_widget(widget)
    
    def toggle_widget_expansion(self, widget_id: str):
        """Toggle widget expansion"""
        widget = self.get_widget(widget_id)
        if widget:
            widget.toggle_expansion()
    
    def render_all(self) -> str:
        """Render all widgets as markdown"""
        rendered_parts = []
        for widget in self.widgets:
            if widget.visible:
                rendered_parts.append(widget.render())
        
        return "".join(rendered_parts)
    
    def get_tool_widgets(self) -> List[ToolWidget]:
        """Get all tool widgets"""
        return [w for w in self.widgets if isinstance(w, ToolWidget)]
    
    def find_widgets_by_type(self, widget_type: type) -> List[BaseWidget]:
        """Find widgets by type"""
        return [w for w in self.widgets if isinstance(w, widget_type)]
