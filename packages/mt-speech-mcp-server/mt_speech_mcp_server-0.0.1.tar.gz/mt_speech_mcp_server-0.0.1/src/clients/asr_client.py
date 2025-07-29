"""
美团ASR客户端
"""
import base64
import json
import uuid

from src.clients.base_client import MeituanBaseClient
from src.config import config
from src.utils.utils import HttpClient


class MeituanASRClient(MeituanBaseClient):
    """美团语音识别客户端"""

    def __init__(self):
        super().__init__(service_type="asr")

    async def recognize_from_url(self, audio_url: str, audio_format: str,
                                 sample_rate: int, channel_num: int = 1) -> str:
        """
        通过URL进行语音识别

        参数:
            audio_url: 音频文件URL
            audio_format: 音频格式 (pcm, wav, mp3, aac, amr等)
            sample_rate: 采样率
            channel_num: 声道数 (1:单声道, 2:双声道)

        返回:
            识别结果文本
        """
        token = await self.get_token()

        # 构建ASR参数
        asr_params = {
            "audio_format": audio_format,
            "sample_rate": sample_rate,
            "channel_num": channel_num,
            "data_type": "url",
            "data": audio_url
        }

        headers = {
            'Token': token,
            'SessionID': str(uuid.uuid4()),
            'Content-Type': 'application/json'
        }

        # 发送请求
        response = await HttpClient.post_request(
            url=config.MEITUAN_ASR_API_URL,
            headers=headers,
            json_data=asr_params,
            timeout=30.0
        )

        result = response['data']
        self.logger.info(f"ASR识别成功: {result[:50]}...")
        return result

    async def recognize_from_binary(self, audio_data: bytes, audio_format: str,
                                    sample_rate: int, channel_num: int = 1) -> str:
        """
        通过二进制数据进行语音识别

        参数:
            audio_data: 音频二进制数据
            audio_format: 音频格式 (pcm, wav, mp3, aac, amr等)
            sample_rate: 采样率
            channel_num: 声道数 (1:单声道, 2:双声道)

        返回:
            识别结果文本
        """
        self.logger.info(f"ASR识别: 格式={audio_format}, 采样率={sample_rate}, 声道={channel_num}")
        token = await self.get_token()

        # 构建ASR参数
        asr_params = {
            "audio_format": audio_format,
            "sample_rate": sample_rate,
            "channel_num": channel_num,
            "data_type": "binary"
        }

        # Base64编码参数
        asr_params_json = json.dumps(asr_params)
        asr_params_b64 = base64.b64encode(asr_params_json.encode('utf-8')).decode('utf-8')

        headers = {
            'Token': token,
            'SessionID': str(uuid.uuid4()),
            'Set': 'asr',
            'Content-Type': 'application/octet-stream',
            'Asr-Params': asr_params_b64
        }

        # 发送请求，音频数据作为body
        response = await HttpClient.post_request(
            url=config.MEITUAN_ASR_API_URL,
            content=audio_data,
            headers=headers,
            timeout=30.0
        )

        # 检查响应数据类型并转换为JSON字符串
        if isinstance(response['data'], dict):
            self.logger.info(f"ASR识别成功: {response['data']}")
            return json.dumps(response['data'])
        else:
            return response['data']
