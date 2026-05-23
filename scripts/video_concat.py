#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
视频片段自动拼接工具
功能：将多个视频片段拼接成完整视频
作者：诗韵长安项目组
"""

import os
import sys
import subprocess
from pathlib import Path


def check_ffmpeg():
    """检查 FFmpeg 是否已安装"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def get_video_info(video_path):
    """
    获取视频信息
    
    参数:
        video_path: 视频文件路径
    返回:
        dict: 视频信息
    """
    try:
        result = subprocess.run(
            [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_format', '-show_streams',
                str(video_path)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        import json
        info = json.loads(result.stdout)
        
        # 获取视频流信息
        video_stream = None
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break
        
        return {
            'width': video_stream.get('width', 0) if video_stream else 0,
            'height': video_stream.get('height', 0) if video_stream else 0,
            'duration': float(info.get('format', {}).get('duration', 0)),
            'fps': eval(video_stream.get('r_frame_rate', '0/1')) if video_stream else 0,
        }
    except Exception as e:
        print(f"⚠️  获取视频信息失败: {e}")
        return None


def concat_videos_ffmpeg(video_list, output_path, method='concat_demuxer'):
    """
    使用 FFmpeg 拼接视频
    
    参数:
        video_list: 视频文件路径列表
        output_path: 输出文件路径
        method: 拼接方法 ('concat_demuxer' 或 'filter_complex')
    """
    if not check_ffmpeg():
        print("=" * 60)
        print("❌ FFmpeg 未安装")
        print("\n请先安装 FFmpeg：")
        print("  Windows: 从 https://ffmpeg.org 下载并添加到 PATH")
        print("  Mac: brew install ffmpeg")
        print("  Linux: sudo apt install ffmpeg")
        print("=" * 60)
        return False
    
    # 创建临时文件列表
    temp_list_file = Path('./temp_video_list.txt')
    
    try:
        with open(temp_list_file, 'w', encoding='utf-8') as f:
            for video in video_list:
                # FFmpeg 需要 / 或转义 \
                video_path = str(video).replace('\\', '/')
                f.write(f"file '{video_path}'\n")
        
        # 构建 FFmpeg 命令
        if method == 'concat_demuxer':
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(temp_list_file),
                '-c', 'copy',
                str(output_path)
            ]
        else:
            # filter_complex 方法（需要重新编码）
            inputs = []
            filter_parts = []
            for i, video in enumerate(video_list):
                inputs.extend(['-i', str(video)])
                filter_parts.append(f'[{i}:v][{i}:a]')
            
            filter_complex = f"{''.join(filter_parts)}concat=n={len(video_list)}:v=1:a=1[outv][outa]"
            
            cmd = [
                'ffmpeg', '-y',
                *inputs,
                '-filter_complex', filter_complex,
                '-map', '[outv]',
                '-map', '[outa]',
                str(output_path)
            ]
        
        print(f"\n🎬 执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )
        
        if result.returncode == 0:
            return True
        else:
            print(f"❌ FFmpeg 错误: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 操作超时")
        return False
    except Exception as e:
        print(f"❌ 拼接失败: {e}")
        return False
    finally:
        # 清理临时文件
        if temp_list_file.exists():
            temp_list_file.unlink()


def batch_concat(video_dir, output_file, extensions=None, sort_by='name'):
    """
    批量拼接视频
    
    参数:
        video_dir: 视频目录
        output_file: 输出文件路径
        extensions: 视频格式列表
        sort_by: 排序方式 ('name', 'time', 'size')
    """
    video_path = Path(video_dir)
    
    if extensions is None:
        extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
    
    # 获取所有视频文件
    videos = [f for f in video_path.iterdir() 
              if f.suffix.lower() in extensions]
    
    if not videos:
        print("⚠️  未找到视频文件")
        return
    
    # 排序
    if sort_by == 'name':
        videos.sort(key=lambda x: x.name)
    elif sort_by == 'time':
        videos.sort(key=lambda x: x.stat().st_mtime)
    elif sort_by == 'size':
        videos.sort(key=lambda x: x.stat().st_size)
    
    print("=" * 60)
    print(f"📂 输入目录: {video_dir}")
    print(f"🎥 输出文件: {output_file}")
    print(f"📹 找到 {len(videos)} 个视频片段")
    print("=" * 60)
    
    # 显示视频列表
    print("\n📋 视频列表：")
    print("-" * 60)
    
    total_duration = 0
    for i, video in enumerate(videos, 1):
        info = get_video_info(video)
        duration = info['duration'] if info else 0
        total_duration += duration
        
        mins, secs = divmod(int(duration), 60)
        print(f"{i:2d}. {video.name}")
        print(f"    时长: {mins:02d}:{secs:02d}")
    
    mins, secs = divmod(int(total_duration), 60)
    print(f"\n总时长: {mins:02d}:{secs:02d}")
    
    # 执行拼接
    print("\n⏳ 正在拼接...")
    
    if concat_videos_ffmpeg(videos, output_file):
        output_size = Path(output_file).stat().st_size / (1024 * 1024)
        print("\n" + "=" * 60)
        print(f"✅ 拼接完成!")
        print(f"📄 输出文件: {output_file}")
        print(f"📦 文件大小: {output_size:.2f} MB")
        print("=" * 60)
    else:
        print("\n❌ 拼接失败")


def interactive_mode():
    """交互模式"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          🎬  视频片段自动拼接工具  v1.0                    ║
║                                                           ║
║   功能：将多个视频片段拼接成完整视频                       ║
║   依赖：需要安装 FFmpeg                                    ║
║   作者：诗韵长安项目组                                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    if not check_ffmpeg():
        print("❌ FFmpeg 未安装，请先安装 FFmpeg")
        print("\n安装方法：")
        print("  Windows: 从 https://ffmpeg.org 下载并添加到 PATH")
        print("  Mac: brew install ffmpeg")
        print("  Linux: sudo apt install ffmpeg")
        return
    
    video_dir = input("请输入视频目录路径: ").strip()
    
    if not video_dir:
        video_dir = "."
    
    output_file = input("请输入输出文件名 (默认 output.mp4): ").strip() or "output.mp4"
    
    print("\n请选择排序方式：")
    print("1. 按文件名排序")
    print("2. 按修改时间排序")
    print("3. 按文件大小排序")
    
    sort_choice = input("\n请输入选项 (1/2/3): ").strip()
    
    sort_map = {'1': 'name', '2': 'time', '3': 'size'}
    sort_by = sort_map.get(sort_choice, 'name')
    
    batch_concat(video_dir, output_file, sort_by=sort_by)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='视频片段自动拼接工具')
    parser.add_argument('input_dir', nargs='?', default='.', help='输入目录')
    parser.add_argument('-o', '--output', default='output.mp4', help='输出文件')
    parser.add_argument('-s', '--sort', choices=['name', 'time', 'size'], default='name', help='排序方式')
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        interactive_mode()
    else:
        batch_concat(args.input_dir, args.output, sort_by=args.sort)


if __name__ == "__main__":
    main()
