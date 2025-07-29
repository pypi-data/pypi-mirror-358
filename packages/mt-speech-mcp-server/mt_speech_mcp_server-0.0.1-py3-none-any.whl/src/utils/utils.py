"""
工具函数模块
"""
import os
import httpx
from typing import Union, Dict, Any, Optional
from urllib.parse import urlparse


class HttpClient:
    """HTTP请求客户端工具类"""

    @staticmethod
    async def post_request(
            url: str,
            data: Optional[Dict[str, Any]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, Any]] = None,
            content: Optional[bytes] = None,
            timeout: float = 15.0,
            expect_json: bool = True,
            preserve_types: bool = False  # 新增参数
    ) -> Union[Dict[str, Any], bytes]:
        """
        发送POST请求

        参数:
            preserve_types: 是否保持数据类型（强制使用JSON格式）
        """
        async with httpx.AsyncClient(timeout=timeout) as client:
            request_kwargs = {
                'url': url,
                'headers': headers or {},
                'params': params or {}
            }

            # 设置请求体 - 优先使用JSON以保持类型
            if content is not None:
                request_kwargs['content'] = content
            elif json_data is not None:
                request_kwargs['json'] = json_data
            elif data is not None:
                if preserve_types:
                    # 强制使用JSON格式保持数据类型
                    request_kwargs['json'] = data
                else:
                    request_kwargs['data'] = data

            # 发送请求
            resp = await client.post(**request_kwargs)
            resp.raise_for_status()

            # 处理响应
            if expect_json:
                return resp.json()
            else:
                content_type = resp.headers.get('content-type', '')
                if content_type.startswith('audio/') or not expect_json:
                    return resp.content
                else:
                    return resp.json()

    @staticmethod
    async def get_request(
            url: str,
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, Any]] = None,
            timeout: float = 15.0
    ) -> Union[Dict[str, Any], bytes]:
        """
        发送GET请求

        参数:
            url: 请求URL
            headers: 请求头
            params: URL参数
            timeout: 超时时间（秒）

        返回:
            JSON响应数据或字节内容
        """
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(
                url=url,
                headers=headers or {},
                params=params or {}
            )
            resp.raise_for_status()

            # 尝试解析JSON，失败则返回字节内容
            try:
                return resp.json()
            except:
                return resp.content


def is_url(source: str) -> bool:
    """
    判断字符串是否为有效的URL

    参数:
        source: 待检查的字符串

    返回:
        bool: 如果是有效URL返回True，否则返回False
    """
    try:
        result = urlparse(source)
        return all([result.scheme, result.netloc])
    except:
        return False


def is_file_path(source: str) -> bool:
    """
    判断字符串是否为存在的本地文件路径

    参数:
        source: 待检查的字符串

    返回:
        bool: 如果是存在的文件路径返回True，否则返回False
    """
    return os.path.exists(source) and os.path.isfile(source)
