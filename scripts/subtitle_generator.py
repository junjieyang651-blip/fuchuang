#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
字幕文件生成工具
功能：根据文本内容生成 SRT 字幕文件
作者：诗韵长安项目组
"""

import os
import sys
from pathlib import Path
from datetime import timedelta


def seconds_to_srt_time(seconds):
    """
    将秒数转换为 SRT 时间格式 (HH:MM:SS,mmm)
    
    参数:
        seconds: 秒数
    返回:
        SRT 格式时间字符串
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def parse_text_to_subtitles(text, duration_per_line=3.0, start_time=0):
    """
    将文本解析为字幕条目
    
    参数:
        text: 文本内容（每行一句）
        duration_per_line: 每行默认持续时间（秒）
        start_time: 起始时间（秒）
    返回:
        字幕条目列表 [(index, start_time, end_time, text), ...]
    """
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    
    subtitles = []
    current_time = start_time
    
    for i, line in enumerate(lines, 1):
        # 根据标点符号估算持续时间
        # 中文标点：每个增加0.5秒
        punctuation_count = line.count('，') + line.count('。') + line.count('！') + line.count('？') + line.count('、')
        duration = duration_per_line + punctuation_count * 0.5
        
        # 根据字数调整（平均每字0.15秒）
        char_count = len(line.replace('，', '').replace('。', '').replace('！', '').replace('？', '').replace('、', ''))
        duration = max(duration, char_count * 0.15)
        
        end_time = current_time + duration
        
        subtitles.append((i, current_time, end_time, line))
        current_time = end_time + 0.3  # 添加0.3秒间隔
    
    return subtitles


def generate_srt(subtitles, output_path):
    """
    生成 SRT 字幕文件
    
    参数:
        subtitles: 字幕条目列表
        output_path: 输出文件路径
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for index, start, end, text in subtitles:
            f.write(f"{index}\n")
            f.write(f"{seconds_to_srt_time(start)} --> {seconds_to_srt_time(end)}\n")
            f.write(f"{text}\n")
            f.write("\n")


def generate_vtt(subtitles, output_path):
    """
    生成 WebVTT 字幕文件
    
    参数:
        subtitles: 字幕条目列表
        output_path: 输出文件路径
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("WEBVTT\n\n")
        for index, start, end, text in subtitles:
            # VTT使用点号代替逗号
            start_vtt = seconds_to_srt_time(start).replace(',', '.')
            end_vtt = seconds_to_srt_time(end).replace(',', '.')
            f.write(f"{index}\n")
            f.write(f"{start_vtt} --> {end_vtt}\n")
            f.write(f"{text}\n")
            f.write("\n")


def batch_generate_subtitles(text_file, output_dir, formats=['srt', 'vtt']):
    """
    从文本文件批量生成字幕
    
    参数:
        text_file: 文本文件路径
        output_dir: 输出目录
        formats: 输出格式列表
    """
    text_path = Path(text_file)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if not text_path.exists():
        print(f"❌ 文件不存在: {text_file}")
        return
    
    # 读取文本
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 解析字幕
    subtitles = parse_text_to_subtitles(text)
    
    if not subtitles:
        print("⚠️  文本内容为空")
        return
    
    print("=" * 50)
    print(f"📄 输入文件: {text_file}")
    print(f"📂 输出目录: {output_dir}")
    print(f"📝 字幕条目: {len(subtitles)} 条")
    print(f"⏱️  总时长: {seconds_to_srt_time(subtitles[-1][2])}")
    print("=" * 50)
    
    base_name = text_path.stem
    
    # 生成各种格式
    for fmt in formats:
        output_file = output_path / f"{base_name}.{fmt}"
        if fmt == 'srt':
            generate_srt(subtitles, output_file)
        elif fmt == 'vtt':
            generate_vtt(subtitles, output_file)
        print(f"✅ 已生成: {output_file}")
    
    print("\n" + "=" * 50)
    print("✅ 字幕生成完成")
    print("=" * 50)


def interactive_mode():
    """交互模式"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          📝  字幕文件生成工具  v1.0                        ║
║                                                           ║
║   功能：根据文本内容生成 SRT / VTT 字幕文件               ║
║   作者：诗韵长安项目组                                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    print("请选择操作模式：")
    print("1. 从文本文件生成字幕")
    print("2. 直接输入文本生成字幕")
    
    choice = input("\n请输入选项 (1/2): ").strip()
    
    if choice == "1":
        text_file = input("请输入文本文件路径: ").strip()
        output_dir = input("请输入输出目录 (默认 ./subtitles): ").strip() or "./subtitles"
        batch_generate_subtitles(text_file, output_dir)
        
    elif choice == "2":
        print("\n请输入字幕文本（每行一句，输入空行结束）：")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        
        if not lines:
            print("⚠️  未输入任何内容")
            return
        
        text = '\n'.join(lines)
        subtitles = parse_text_to_subtitles(text)
        
        output_file = input("\n请输入输出文件名 (默认 output.srt): ").strip() or "output.srt"
        
        if output_file.endswith('.srt'):
            generate_srt(subtitles, output_file)
        elif output_file.endswith('.vtt'):
            generate_vtt(subtitles, output_file)
        else:
            generate_srt(subtitles, output_file + '.srt')
        
        print(f"✅ 已生成: {output_file}")
        print(f"📝 字幕条目: {len(subtitles)} 条")
        print(f"⏱️  总时长: {seconds_to_srt_time(subtitles[-1][2])}")
    
    else:
        print("❌ 无效选项")


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 命令行模式
        text_file = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "./subtitles"
        batch_generate_subtitles(text_file, output_dir)
    else:
        # 交互模式
        interactive_mode()


if __name__ == "__main__":
    main()
