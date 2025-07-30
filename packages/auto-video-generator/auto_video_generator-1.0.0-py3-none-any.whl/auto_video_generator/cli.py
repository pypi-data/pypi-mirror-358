"""
命令行接口模块

提供命令行参数解析和主程序入口。
"""

import json
import asyncio
import subprocess
import sys
import argparse
from .core import generate_video, synthesize_and_get_durations
from .utils import get_voice_by_index

def main():
    """主程序入口"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='自动生成带字幕视频工具')
    parser.add_argument('--video', '-v', help='输入视频文件名')
    parser.add_argument('--output', '-o', help='输出视频文件名')
    parser.add_argument('--timbre', '-t', type=int, choices=[0,1,2,3,4], help='语音音色 (0:女声小晓, 1:男声云扬, 2:女声小艺, 3:女声云希, 4:男声云健)')
    parser.add_argument('--font-size', type=int, help='字幕字体大小')
    parser.add_argument('--font-color', help='字幕字体颜色 (white/black/red/yellow等)')
    parser.add_argument('--bg-color', help='字幕背景颜色 (格式: R,G,B,A 例如: 0,0,0,128)')
    parser.add_argument('--margin-x', type=int, help='字幕左右边距')
    parser.add_argument('--margin-bottom', type=int, help='字幕底部边距')
    parser.add_argument('--subtitle-height', type=int, help='字幕区域高度')
    parser.add_argument('--auto-split', choices=['enable', 'disable'], help='是否启用智能分割')
    parser.add_argument('--split-strategy', choices=['smart', 'duration', 'none'], help='分割策略')
    parser.add_argument('--max-chars', type=int, help='每行最大字符数')
    parser.add_argument('--target-duration', type=float, help='目标时长(秒)')
    parser.add_argument('--segments-mode', choices=['keep', 'cut'], help='视频片段模式')
    parser.add_argument('--use-full-video', action='store_true', help='使用全部视频内容(设置segments为空)')
    parser.add_argument('--config', '-c', default='config.json', help='配置文件路径 (默认: config.json)')
    
    args = parser.parse_args()
    
    # 加载配置文件
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"错误：找不到配置文件 '{args.config}'")
        print("请确保配置文件存在，或使用 --config 参数指定正确的配置文件路径")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误：配置文件 '{args.config}' 格式不正确")
        print(f"JSON解析错误: {e}")
        sys.exit(1)
    
    # 使用命令行参数覆盖配置文件
    if args.video:
        config['video'] = args.video
        print(f"使用命令行参数设置视频文件: {args.video}")
    
    if args.output:
        config['output'] = args.output
        print(f"使用命令行参数设置输出文件: {args.output}")
    
    if args.timbre is not None:
        config['activeTimbre'] = args.timbre
        print(f"使用命令行参数设置语音音色: {args.timbre}")
    
    if args.use_full_video:
        config['segments'] = []
        print("使用命令行参数设置：使用全部视频内容")
    
    if args.segments_mode:
        config['segmentsMode'] = args.segments_mode
        print(f"使用命令行参数设置视频片段模式: {args.segments_mode}")
    
    # 覆盖字幕样式设置
    if any([args.font_size, args.font_color, args.bg_color, args.margin_x, args.margin_bottom, args.subtitle_height]):
        if 'subtitleStyle' not in config:
            config['subtitleStyle'] = {}
        
        if args.font_size:
            config['subtitleStyle']['fontSize'] = args.font_size
            print(f"使用命令行参数设置字体大小: {args.font_size}")
        
        if args.font_color:
            config['subtitleStyle']['color'] = args.font_color
            print(f"使用命令行参数设置字体颜色: {args.font_color}")
        
        if args.bg_color:
            try:
                bg_color = [int(x.strip()) for x in args.bg_color.split(',')]
                config['subtitleStyle']['bgColor'] = bg_color
                print(f"使用命令行参数设置背景颜色: {bg_color}")
            except ValueError:
                print(f"警告：背景颜色格式错误 '{args.bg_color}'，应为 R,G,B,A 格式")
        
        if args.margin_x:
            config['subtitleStyle']['marginX'] = args.margin_x
            print(f"使用命令行参数设置左右边距: {args.margin_x}")
        
        if args.margin_bottom:
            config['subtitleStyle']['marginBottom'] = args.margin_bottom
            print(f"使用命令行参数设置底部边距: {args.margin_bottom}")
        
        if args.subtitle_height:
            config['subtitleStyle']['height'] = args.subtitle_height
            print(f"使用命令行参数设置字幕区域高度: {args.subtitle_height}")
    
    # 覆盖智能分割设置
    if any([args.auto_split, args.split_strategy, args.max_chars, args.target_duration]):
        if 'autoSplit' not in config:
            config['autoSplit'] = {}
        
        if args.auto_split:
            config['autoSplit']['enable'] = (args.auto_split == 'enable')
            print(f"使用命令行参数设置智能分割: {'启用' if args.auto_split == 'enable' else '禁用'}")
        
        if args.split_strategy:
            config['autoSplit']['strategy'] = args.split_strategy
            print(f"使用命令行参数设置分割策略: {args.split_strategy}")
        
        if args.max_chars:
            config['autoSplit']['maxChars'] = args.max_chars
            print(f"使用命令行参数设置最大字符数: {args.max_chars}")
        
        if args.target_duration:
            config['autoSplit']['targetDuration'] = args.target_duration
            print(f"使用命令行参数设置目标时长: {args.target_duration}秒")
    
    # 检查必要的配置项
    if 'video' not in config:
        print("错误：配置文件中缺少 'video' 字段")
        print("请在配置文件中设置视频文件名，或使用 --video 参数指定")
        sys.exit(1)
    
    if 'timing' not in config:
        print("错误：配置文件中缺少 'timing' 字段")
        print("请在配置文件中设置字幕内容")
        sys.exit(1)
    
    # 设置默认值
    if 'output' not in config:
        config['output'] = 'output1.mp4'
    
    if 'activeTimbre' not in config:
        config['activeTimbre'] = 0
    
    print(f"\n=== 配置信息 ===")
    print(f"输入视频: {config['video']}")
    print(f"输出视频: {config['output']}")
    print(f"语音音色: {config['activeTimbre']}")
    print(f"字幕条数: {len(config['timing'])}")
    print(f"视频片段: {'使用全部视频' if not config.get('segments') else f'{len(config.get('segments', []))}个片段'}")
    print("=" * 20 + "\n")
    
    # 安装依赖
    import importlib.util
    if importlib.util.find_spec('pydub') is None:
        print('正在安装pydub...')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pydub'])
    
    # 执行主流程
    active_timbre = config.get('activeTimbre', 0)
    timing = config['timing']
    voice = get_voice_by_index(active_timbre)
    
    # 合成音频并获取每条字幕的朗读时长
    durations = asyncio.run(synthesize_and_get_durations(timing, voice))
    
    # 直接调用视频生成逻辑
    generate_video(config, timing)
    print("全部流程已完成，只保留最终视频！")

if __name__ == "__main__":
    main() 