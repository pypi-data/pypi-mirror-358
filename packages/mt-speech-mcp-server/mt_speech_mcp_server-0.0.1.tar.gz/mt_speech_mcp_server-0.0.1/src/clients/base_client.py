"""
美团AI服务基础客户端模块
"""
import time
from typing import Optional

import httpx

from src.config import config
import logging

class MeituanBaseClient:
    """美团AI服务基础客户端 - 负责令牌管理"""

    def __init__(self, service_type: str = "tts"):
        """
        初始化客户端
        Args:
            service_type: 服务类型，"tts" 或 "asr"
        """
        self.service_type = service_type
        self._token: Optional[str] = None
        self._token_expire_time: int = 0
        # 为每个客户端实例创建专用的logger
        self.logger = logging.getLogger(f"meituan.{service_type}.client")

    def _validate_config(self):
        """验证必要的配置项 - 仅在实际使用时调用"""
        app_key, secret_key = self._get_credentials()
        if not app_key or not secret_key:
            raise ValueError(f"缺少必要的配置: {self.service_type.upper()}_APP_KEY 和 {self.service_type.upper()}_SECRET_KEY 必须设置")

    def _get_credentials(self):
        """根据服务类型获取对应的密钥"""
        if self.service_type == "asr":
            return config.MEITUAN_ASR_APP_KEY, config.MEITUAN_ASR_SECRET_KEY
        else:  # 默认为 tts
            return config.MEITUAN_TTS_APP_KEY, config.MEITUAN_TTS_SECRET_KEY

    async def _fetch_token(self):
        """获取访问令牌"""
        app_key, secret_key = self._get_credentials()
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    config.MEITUAN_AUTH_API_URL,
                    data={
                        'grant_type': 'client_credentials',
                        'client_id': app_key,
                        'client_secret': secret_key
                    },
                    timeout=10.0  # 增加超时时间
                )
                resp.raise_for_status()
                data = resp.json()

                if data.get('errcode') != 0:
                    error_msg = f"Token获取失败: {data.get('errmsg', '未知错误')}"
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)

                access_token = data['data']['access_token']
                expires_in = int(data['data']['expires_in'])
                self._token = access_token
                self._token_expire_time = int(time.time()) + expires_in
                self.logger.info("Token获取成功")

        except httpx.TimeoutException:
            error_msg = "Token获取超时"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        except httpx.HTTPError as e:
            error_msg = f"Token获取网络错误: {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Token获取未知错误: {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    async def get_token(self) -> str:
        """智能令牌管理 - 自动刷新过期令牌"""
        # 验证配置
        self._validate_config()

        now = int(time.time())
        TOKEN_EXPIRE_MARGIN = 60  # 提前60秒刷新令牌
        if not self._token or now > self._token_expire_time - TOKEN_EXPIRE_MARGIN:
            await self._fetch_token()
        return self._token

