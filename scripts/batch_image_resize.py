#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量图像尺寸调整工具
功能：将图片批量调整为 1920×1080（横屏）或 1080×1920（竖屏）
作者：诗韵长安项目组
"""

import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("=" * 50)
    print("⚠️  缺少依赖库 Pillow")
    print("请运行以下命令安装：")
    print("pip install Pillow")
    print("=" * 50)
    sys.exit(1)


def get_image_orientation(width, height):
    """判断图片方向"""
    return "landscape" if width >= height else "portrait"


def resize_image(input_path, output_path, target_size, keep_aspect=True, bg_color=(26, 20, 16)):
    """
    调整图片尺寸
    
    参数:
        input_path: 输入图片路径
        output_path: 输出图片路径
        target_size: 目标尺寸 (width, height)
        keep_aspect: 是否保持宽高比
        bg_color: 填充背景色
    """
    try:
        with Image.open(input_path) as img:
            # 转换为RGB模式（处理PNG透明通道）
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, bg_color)
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            if keep_aspect:
                # 保持宽高比，居中填充
                img.thumbnail(target_size, Image.Resampling.LANCZOS)
                
                # 创建背景
                new_img = Image.new('RGB', target_size, bg_color)
                
                # 计算居中位置
                x = (target_size[0] - img.width) // 2
                y = (target_size[1] - img.height) // 2
                
                new_img.paste(img, (x, y))
                img = new_img
            else:
                # 直接拉伸
                img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            # 保存
            img.save(output_path, quality=95, optimize=True)
            return True
            
    except Exception as e:
        print(f"❌ 处理失败 {input_path}: {e}")
        return False


def batch_resize(input_dir, output_dir, landscape_size=(1920, 1080), portrait_size=(1080, 1920)):
    """
    批量调整图片尺寸
    
    参数:
        input_dir: 输入目录
        output_dir: 输出目录
        landscape_size: 横屏尺寸
        portrait_size: 竖屏尺寸
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 支持的图片格式
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    
    # 获取所有图片
    images = [f for f in input_path.iterdir() 
              if f.suffix.lower() in image_extensions]
    
    if not images:
        print("⚠️  未找到图片文件")
        return
    
    print("=" * 50)
    print(f"📂 输入目录: {input_dir}")
    print(f"📂 输出目录: {output_dir}")
    print(f"🖼️  找到 {len(images)} 张图片")
    print("=" * 50)
    
    success_count = 0
    
    for i, img_file in enumerate(images, 1):
        print(f"\n[{i}/{len(images)}] 处理: {img_file.name}")
        
        # 读取图片判断方向
        try:
            with Image.open(img_file) as img:
                width, height = img.size
                orientation = get_image_orientation(width, height)
                
                # 选择目标尺寸
                target_size = landscape_size if orientation == "landscape" else portrait_size
                
                print(f"   原始尺寸: {width}×{height} ({'横屏' if orientation == 'landscape' else '竖屏'})")
                print(f"   目标尺寸: {target_size[0]}×{target_size[1]}")
                
        except Exception as e:
            print(f"   ❌ 读取失败: {e}")
            continue
        
        # 处理图片
        output_file = output_path / img_file.name
        if resize_image(img_file, output_file, target_size):
            print(f"   ✅ 已保存")
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ 处理完成: {success_count}/{len(images)} 张图片")
    print("=" * 50)


def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          🖼️  批量图像尺寸调整工具  v1.0                   ║
║                                                           ║
║   功能：将图片批量调整为 1920×1080 或 1080×1920          ║
║   作者：诗韵长安项目组                                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    # 获取用户输入
    print("请选择操作模式：")
    print("1. 处理当前目录下的图片")
    print("2. 指定输入/输出目录")
    
    choice = input("\n请输入选项 (1/2): ").strip()
    
    if choice == "1":
        input_dir = "."
        output_dir = "./resized"
    elif choice == "2":
        input_dir = input("请输入输入目录路径: ").strip()
        output_dir = input("请输入输出目录路径: ").strip()
    else:
        print("❌ 无效选项")
        return
    
    # 执行批量处理
    batch_resize(input_dir, output_dir)


if __name__ == "__main__":
    main()
