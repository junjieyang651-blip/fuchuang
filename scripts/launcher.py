#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诗韵长安 · 工具集启动器
一键运行各种自动化工具
作者：诗韵长安项目组
"""

import os
import sys
import subprocess
from pathlib import Path


SCRIPTS = {
    '1': {
        'name': '批量图像尺寸调整',
        'script': 'batch_image_resize.py',
        'desc': '将图片调整为 1920×1080 或 1080×1920',
        'deps': ['Pillow']
    },
    '2': {
        'name': '批量格式转换',
        'script': 'batch_format_convert.py',
        'desc': '在 PNG/JPG/WebP 格式之间转换',
        'deps': ['Pillow']
    },
    '3': {
        'name': '字幕文件生成',
        'script': 'subtitle_generator.py',
        'desc': '根据文本生成 SRT/VTT 字幕',
        'deps': []
    },
    '4': {
        'name': '图片批量重命名',
        'script': 'batch_rename.py',
        'desc': '按「英雄名-景点名-序号」规则重命名',
        'deps': []
    },
    '5': {
        'name': '图片自动分类',
        'script': 'auto_classify.py',
        'desc': '根据英雄名自动归档到文件夹',
        'deps': []
    },
    '6': {
        'name': '视频片段拼接',
        'script': 'video_concat.py',
        'desc': '将多个视频片段拼接成完整视频',
        'deps': ['ffmpeg']
    },
}


def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ 需要 Python 3.7 或更高版本")
        return False
    return True


def check_pillow():
    """检查 Pillow 是否已安装"""
    try:
        import PIL
        return True
    except ImportError:
        return False


def check_ffmpeg():
    """检查 FFmpeg 是否已安装"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def install_pillow():
    """安装 Pillow"""
    print("\n正在安装 Pillow...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'Pillow'])


def run_script(script_name):
    """运行指定脚本"""
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"❌ 脚本不存在: {script_path}")
        return
    
    # 运行脚本
    subprocess.run([sys.executable, str(script_path)])


def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                                 ║
║          🏮  诗韵长安 · 工具集启动器  v1.0 🏮                  ║
║                                                                 ║
║     王者荣耀 × 西安盛唐文旅 融合创新项目                        ║
║     服务创新大赛 D04 数字文旅服务创新赛道                       ║
║                                                                 ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    # 检查 Python 版本
    if not check_python_version():
        return
    
    # 检查依赖
    pillow_ok = check_pillow()
    ffmpeg_ok = check_ffmpeg()
    
    print("📦 依赖状态：")
    print(f"   Pillow: {'✅ 已安装' if pillow_ok else '❌ 未安装'}")
    print(f"   FFmpeg: {'✅ 已安装' if ffmpeg_ok else '❌ 未安装 (视频拼接需要)'}")
    print()
    
    # 显示菜单
    print("=" * 60)
    print("请选择要运行的工具：")
    print("=" * 60)
    
    for key, info in SCRIPTS.items():
        status = "✅" if (info['script'] != 'video_concat.py' or ffmpeg_ok) else "⚠️"
        print(f"\n{key}. {status} {info['name']}")
        print(f"   {info['desc']}")
    
    print("\n0. 退出")
    print("\n" + "=" * 60)
    
    choice = input("\n请输入选项: ").strip()
    
    if choice == '0':
        print("\n👋 再见！")
        return
    
    if choice not in SCRIPTS:
        print("❌ 无效选项")
        return
    
    script_info = SCRIPTS[choice]
    
    # 检查 Pillow 依赖
    if 'Pillow' in script_info['deps'] and not pillow_ok:
        print("\n⚠️  此工具需要 Pillow 库")
        install = input("是否现在安装？ (y/n): ").strip().lower()
        if install == 'y':
            install_pillow()
        else:
            print("❌ 已取消")
            return
    
    # 检查 FFmpeg 依赖
    if 'ffmpeg' in script_info['deps'] and not ffmpeg_ok:
        print("\n❌ 此工具需要 FFmpeg")
        print("请先安装 FFmpeg：")
        print("  Windows: 从 https://ffmpeg.org 下载并添加到 PATH")
        print("  Mac: brew install ffmpeg")
        print("  Linux: sudo apt install ffmpeg")
        return
    
    print(f"\n🚀 启动: {script_info['name']}")
    print("=" * 60)
    
    run_script(script_info['script'])


if __name__ == "__main__":
    main()
