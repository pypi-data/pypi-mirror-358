"""
工具处理器基类
"""
import mcp.types as types
from abc import ABC, abstractmethod
from typing import List


class BaseToolHandler(ABC):
    """工具处理器基类"""
    
    @staticmethod
    @abstractmethod
    def get_tool_definition() -> types.Tool:
        """获取工具定义"""
        pass
    
    @abstractmethod
    async def handle_request(self, arguments: dict) -> List[types.TextContent]:
        """处理请求"""
        pass