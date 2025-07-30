"""
工具函数模块

包含各种辅助功能和工具函数。
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import opencc

def resource_path(relative_path):
    """兼容 PyInstaller 打包和源码运行的资源路径获取"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def get_voice_by_index(idx):
    """根据索引获取语音音色"""
    voices = [
        "zh-CN-XiaoxiaoNeural",  # 0 女
        "zh-CN-YunyangNeural",   # 1 男
        "zh-CN-XiaoyiNeural",    # 2 女
        "zh-CN-YunxiNeural",     # 3 女
        "zh-CN-YunjianNeural"    # 4 男
    ]
    if idx < 0 or idx >= len(voices):
        print(f"activeTimbre超出范围，使用默认音色: {voices[0]}")
        return voices[0]
    return voices[idx]

def create_subtitle_image(text, width, height, font_path, fontsize=40, color='black', bg_color=(0,0,0,0), margin_x=100, margin_bottom=50):
    """创建字幕图片"""
    # 繁体转简体
    converter = opencc.OpenCC('t2s')
    text = converter.convert(text)
    img = Image.new('RGBA', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, fontsize)
    max_text_width = width - 2 * margin_x
    avg_char_width = font.getlength('测')
    max_chars_per_line = max(int(max_text_width // avg_char_width), 1)
    # 只取第一行，超长截断
    if len(text) > max_chars_per_line:
        text = text[:max_chars_per_line] + '...'
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (width - w) // 2
    y = height - h - margin_bottom
    draw.text((x, y), text, font=font, fill=color)
    return np.array(img)

def split_timings(timing, max_chars=20):
    """
    智能分割timing，支持多种分割策略：
    1. 按句子分割（句号、问号、感叹号）
    2. 按逗号分割
    3. 按字符数分割
    4. 智能时长分配
    """
    new_timings = []
    
    for t in timing:
        txt = t['text'].strip()
        duration = t.get('duration', 0)
        delay = t.get('delay', 0)
        
        # 处理空白静默
        if txt == "" and (delay > 0 or duration > 0):
            new_timings.append({'text': txt, 'duration': duration, 'delay': delay})
            continue
            
        # 如果文本为空，跳过
        if not txt:
            continue
            
        # 策略1：按句子分割（句号、问号、感叹号）
        sentences = []
        current_sentence = ""
        for char in txt:
            current_sentence += char
            if char in '。？！.!?':
                sentences.append(current_sentence.strip())
                current_sentence = ""
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
            
        # 如果按句子分割后只有一句，尝试按逗号分割
        if len(sentences) <= 1:
            sentences = []
            current_sentence = ""
            for char in txt:
                current_sentence += char
                if char in '，,；;':
                    sentences.append(current_sentence.strip())
                    current_sentence = ""
            if current_sentence.strip():
                sentences.append(current_sentence.strip())
                
        # 如果按逗号分割后只有一句，按字符数分割
        if len(sentences) <= 1:
            sentences = [txt[i:i+max_chars] for i in range(0, len(txt), max_chars)]
            
        # 智能时长分配
        if len(sentences) == 1:
            new_timings.append({'text': txt, 'duration': duration, 'delay': delay})
        else:
            # 根据句子长度比例分配时长
            total_chars = sum(len(s) for s in sentences)
            for sentence in sentences:
                if total_chars > 0:
                    sentence_duration = (len(sentence) / total_chars) * duration
                else:
                    sentence_duration = duration / len(sentences)
                new_timings.append({
                    'text': sentence, 
                    'duration': sentence_duration,
                    'delay': 0  # 子句不设置delay
                })
    
    return new_timings

def auto_split_timing_by_duration(timing, target_duration_per_segment=3.0):
    """
    根据目标时长自动分割timing
    target_duration_per_segment: 每个片段的目标时长（秒）
    """
    new_timings = []
    current_segment = []
    current_duration = 0
    
    for t in timing:
        txt = t['text'].strip()
        duration = t.get('duration', 0)
        delay = t.get('delay', 0)
        
        # 处理空白静默
        if txt == "" and (delay > 0 or duration > 0):
            # 如果当前片段有内容，先保存
            if current_segment:
                new_timings.append({
                    'text': ' '.join(current_segment),
                    'duration': current_duration,
                    'delay': 0
                })
                current_segment = []
                current_duration = 0
            # 添加静默
            new_timings.append({'text': txt, 'duration': duration, 'delay': delay})
            continue
            
        # 如果文本为空，跳过
        if not txt:
            continue
            
        # 检查是否需要开始新片段
        if current_duration + duration > target_duration_per_segment and current_segment:
            # 保存当前片段
            new_timings.append({
                'text': ' '.join(current_segment),
                'duration': current_duration,
                'delay': 0
            })
            current_segment = []
            current_duration = 0
            
        # 添加到当前片段
        current_segment.append(txt)
        current_duration += duration
    
    # 保存最后一个片段
    if current_segment:
        new_timings.append({
            'text': ' '.join(current_segment),
            'duration': current_duration,
            'delay': 0
        })
    
    return new_timings

def to_seconds(t):
    """将时间字符串转换为秒数"""
    try:
        parts = t.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(float, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            minutes, seconds = map(float, parts)
            return minutes * 60 + seconds
        else:
            return float(t)
    except (ValueError, AttributeError):
        return None 