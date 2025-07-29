"""
美团TTS客户端
"""

import uuid
from src.clients.base_client import MeituanBaseClient
from src.config import config
from src.utils.utils import HttpClient


class MeituanTTSClient(MeituanBaseClient):
    """美团文本转语音客户端"""

    def __init__(self):
        super().__init__(service_type="tts")

    async def synthesize(self, text: str, voice_name: str = "meishuyao",
                        speed: int = 50, volume: int = 50,
                        sample_rate: int = 24000, audio_format: str = "mp3") -> bytes:
        """
        文本转语音合成

        参数:
            text: 要合成的文本内容
            voice_name: 合成音色名称
            speed: 语速(0-100)
            volume: 音量(0-100)
            sample_rate: 采样率
            audio_format: 音频格式

        返回:
            音频数据字节

        异常:
            RuntimeError: TTS合成失败或返回非音频数据
        """
        token = await self.get_token()

        headers = {
            'Token': token,
            'SessionID': str(uuid.uuid4())
        }

        payload = {
            'text': text,
            'voice_name': voice_name,
            'speed': speed,
            'volume': volume,
            'sample_rate': sample_rate,
            'audio_format': audio_format
        }

        self.logger.info(f"TTS请求: 文本长度={len(text)}, 音色={voice_name}")

        response = await HttpClient.post_request(
            url=config.MEITUAN_TTS_API_URL,
            json_data=payload,
            headers=headers,
            timeout=15.0,
            expect_json=False
        )

        # 处理响应
        if isinstance(response, bytes):
            # 验证返回的是否为有效音频数据
            if len(response) == 0:
                raise RuntimeError("TTS服务返回空音频数据")

            # 简单的音频格式验证
            is_valid_audio = False

            if audio_format.lower() == 'mp3':
                # MP3文件通常以ID3标签开头或直接以MP3帧开头
                if response.startswith(b'ID3') or response.startswith(b'\xff\xfb') or response.startswith(b'\xff\xfa'):
                    is_valid_audio = True
            elif audio_format.lower() == 'wav':
                # WAV文件以RIFF头开始
                if response.startswith(b'RIFF') and b'WAVE' in response[:12]:
                    is_valid_audio = True
            elif audio_format.lower() == 'pcm':
                # PCM是原始音频数据，难以验证格式，只检查长度
                if len(response) > 100:  # 假设至少有100字节的音频数据
                    is_valid_audio = True
            elif audio_format.lower() == 'aac':
                # AAC文件可能以各种方式开头，简单检查长度
                if len(response) > 100:
                    is_valid_audio = True
            else:
                # 其他格式，简单检查长度
                if len(response) > 100:
                    is_valid_audio = True

            if not is_valid_audio:
                raise RuntimeError(f"TTS服务返回的数据不是有效的{audio_format}格式音频")

            self.logger.info(f"TTS合成成功: {len(response)} bytes")
            return response

        elif isinstance(response, dict):
            # 处理JSON错误响应
            error_code = response.get('errcode', -1)
            error_msg = response.get('errmsg', '未知错误')

            self.logger.error(f"TTS服务返回错误响应: code={error_code}, msg={error_msg}")

            # 提供详细的错误信息
            if error_code == 0:
                # 错误码为0但返回JSON，可能是配置问题
                raise RuntimeError("TTS服务配置错误：期望返回音频数据但收到JSON响应")
            else:
                raise RuntimeError(f"TTS合成失败: {error_msg} (错误码: {error_code})")

        else:
            # 其他类型的响应
            self.logger.error(f"TTS服务返回未知格式响应: {type(response)}")
            raise RuntimeError(f"TTS服务返回了无法识别的响应格式: {type(response).__name__}")
