"""
自动视频生成器

一个基于Python的自动化视频生成工具，支持文字转语音、字幕同步和视频合成。
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import generate_video, synthesize_and_get_durations
from .utils import get_voice_by_index, create_subtitle_image

__all__ = [
    "generate_video",
    "synthesize_and_get_durations", 
    "get_voice_by_index",
    "create_subtitle_image",
] 