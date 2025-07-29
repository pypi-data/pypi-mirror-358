"""
美团TTS MCP服务器主文件
"""
import asyncio
import logging
import sys

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from src.config import config
from src.tools.manager import ToolManager  # 通过 __init__.py 导入

# 配置日志
logging.basicConfig(
    level=logging.WARNING,  # 提高日志级别，减少冗余输出
    format='%(levelname)s - %(message)s',  # 简化格式
    stream=sys.stderr
)

# 为本模块设置INFO级别，记录关键操作
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 初始化服务器和工具管理器
server = Server(config.SERVER_NAME)
tool_manager = ToolManager()


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """列出所有可用工具"""
    tools = tool_manager.get_all_tools()
    logger.info(f"提供 {len(tools)} 个工具: {[tool.name for tool in tools]}")
    return tools


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """处理工具调用请求"""
    logger.info(f"调用工具: {name}")
    try:
        result = await tool_manager.handle_tool_call(name, arguments or {})
        logger.info(f"工具 {name} 执行成功")
        return result
    except Exception as e:
        logger.error(f"工具 {name} 执行失败: {str(e)}")
        raise


async def main():
    """主函数"""
    logger.info(f"启动 {config.SERVER_NAME} v{config.SERVER_VERSION}")
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("MCP服务器已启动，等待连接...")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=config.SERVER_NAME,
                server_version=config.SERVER_VERSION,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def run_server():
    """命令行入口函数"""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
