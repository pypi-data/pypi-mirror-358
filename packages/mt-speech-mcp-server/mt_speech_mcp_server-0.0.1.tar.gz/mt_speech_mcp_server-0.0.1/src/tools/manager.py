"""
工具管理器
"""
import mcp.types as types
from typing import List, Dict
from src.tools.base import BaseToolHandler
from src.tools.tts_tool import TTSToolHandler
from src.tools.asr_tool import ASRToolHandler


class ToolManager:
    """工具管理器"""
    
    def __init__(self):
        self.tts_handler = TTSToolHandler()
        self.asr_handler = ASRToolHandler()
        self.tools: Dict[str, BaseToolHandler] = {
            "text_to_audio": self.tts_handler,
            "audio_to_text": self.asr_handler
        }
    
    def get_all_tools(self) -> List[types.Tool]:
        """获取所有工具定义"""
        return [
            TTSToolHandler.get_tool_definition(),
            ASRToolHandler.get_tool_definition()
        ]
    
    async def handle_tool_call(self, name: str, arguments: dict) -> List[types.TextContent]:
        """处理工具调用"""
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")
        
        if not arguments:
            raise ValueError("Missing arguments")
        
        handler = self.tools[name]
        return await handler.handle_request(arguments)