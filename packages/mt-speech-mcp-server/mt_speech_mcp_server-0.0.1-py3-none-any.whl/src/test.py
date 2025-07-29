"""
测试音频信息获取功能
"""
import asyncio
import sys
import os
import logging

# 设置日志级别为 DEBUG
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # 输出到控制台
    ]
)

# 添加项目路径
sys.path.insert(0, '')

from tools.asr_tool import ASRToolHandler
from tools.tts_tool import TTSToolHandler


# 进行asr识别
async def test_asr_handle_request():
    """测试音频信息获取"""
    asr_handler = ASRToolHandler()

    params = {
        "audio_source": "/tmp/tts_output_31482f3f.mp3",
        "audio_format": "mp3",
        "sample_rate": 24000,
        "channel_num": 1,
        "source_type": "file"
    }

    try:
        asr_result = await asr_handler.handle_request(params)
        print(f"asr_result: {asr_result}")
    except  Exception as e:
        print(f"asr识别错误:{e}")


# 进行tts识别
async def test_tts_handle_request():
    """测试tts"""
    tts_handler = TTSToolHandler()

    try:
        tts_result = await tts_handler.handle_request({"text": "这是一段试听文本0623"})
        print(f"tts_result: {tts_result}")
    except  Exception as e:
        print(f"tts报错:{e}")


if __name__ == "__main__":
    # asyncio.run(test_asr_handle_request())
    asyncio.run(test_tts_handle_request())
