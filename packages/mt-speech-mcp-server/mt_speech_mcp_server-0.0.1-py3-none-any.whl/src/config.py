"""
配置管理模块
"""
import os
import tempfile
from pathlib import Path


class Config:
    """应用配置类"""

    # 美团TTS API配置
    MEITUAN_TTS_APP_KEY = os.environ.get(
        "MEITUAN_TTS_APP_KEY"
    )
    MEITUAN_TTS_SECRET_KEY = os.environ.get(
        "MEITUAN_TTS_SECRET_KEY"
    )

    # 美团ASR API配置
    MEITUAN_ASR_APP_KEY = os.environ.get(
        "MEITUAN_ASR_APP_KEY"
    )
    MEITUAN_ASR_SECRET_KEY = os.environ.get(
        "MEITUAN_ASR_SECRET_KEY"
    )

    # 使用固定的默认URL
    MEITUAN_TTS_API_URL = "https://aispeech.sankuai.com/tts/v1/synthesis"

    # 使用固定的默认URL
    MEITUAN_ASR_API_URL = "https://aispeech.sankuai.com/asr/v1/sentence_recognize"

    # 美团通用配置 - 使用固定的默认URL
    MEITUAN_AUTH_API_URL = "https://auth-ai.vip.sankuai.com/oauth/v2/token"

    # 音频信息接口 - 使用固定的默认URL
    MEITUAN_AUDIO_INFO_API_URL = "https://speech.sankuai.com/custom/web/v1/lm/audio_info"

    # 应用配置
    SERVER_NAME = "meituan_speech_mcp_server"
    SERVER_VERSION = "0.0.1"
    TEMP_DIR = Path(tempfile.gettempdir()) / "mcp_tts_cache"


config = Config()