#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量格式转换工具
功能：在 PNG / JPG / WebP 格式之间批量转换
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


# 支持的格式及其配置
FORMAT_CONFIG = {
    'jpg': {'mode': 'RGB', 'quality': 95},
    'jpeg': {'mode': 'RGB', 'quality': 95},
    'png': {'mode': 'RGBA', 'compress_level': 6},
    'webp': {'mode': 'RGBA', 'quality': 90},
}


def convert_image(input_path, output_path, target_format):
    """
    转换图片格式
    
    参数:
        input_path: 输入图片路径
        output_path: 输出图片路径
        target_format: 目标格式 (jpg, png, webp)
    """
    try:
        with Image.open(input_path) as img:
            config = FORMAT_CONFIG.get(target_format.lower(), {})
            
            # 处理颜色模式
            target_mode = config.get('mode', 'RGB')
            
            if target_format.lower() in ['jpg', 'jpeg']:
                # JPG不支持透明通道，需要转换
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (26, 20, 16))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
            
            # 保存参数
            save_kwargs = {}
            if 'quality' in config:
                save_kwargs['quality'] = config['quality']
            if 'compress_level' in config:
                save_kwargs['compress_level'] = config['compress_level']
            
            img.save(output_path, format=target_format.upper(), **save_kwargs, optimize=True)
            return True
            
    except Exception as e:
        print(f"❌ 转换失败 {input_path}: {e}")
        return False


def batch_convert(input_dir, output_dir, target_format, source_formats=None):
    """
    批量转换图片格式
    
    参数:
        input_dir: 输入目录
        output_dir: 输出目录
        target_format: 目标格式
        source_formats: 源格式列表，None表示所有支持格式
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 源格式
    if source_formats is None:
        source_formats = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    else:
        source_formats = {f'.{fmt.lower().lstrip(".")}' for fmt in source_formats}
    
    # 排除目标格式
    target_ext = f'.{target_format.lower().lstrip(".")}'
    source_formats.discard(target_ext)
    
    # 获取所有图片
    images = [f for f in input_path.iterdir() 
              if f.suffix.lower() in source_formats]
    
    if not images:
        print("⚠️  未找到符合要求的图片文件")
        return
    
    print("=" * 50)
    print(f"📂 输入目录: {input_dir}")
    print(f"📂 输出目录: {output_dir}")
    print(f"🔄 目标格式: {target_format.upper()}")
    print(f"🖼️  找到 {len(images)} 张图片")
    print("=" * 50)
    
    success_count = 0
    
    for i, img_file in enumerate(images, 1):
        print(f"\n[{i}/{len(images)}] 转换: {img_file.name}")
        
        # 生成输出文件名
        output_file = output_path / (img_file.stem + target_ext)
        
        if convert_image(img_file, output_file, target_format):
            print(f"   ✅ → {output_file.name}")
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ 转换完成: {success_count}/{len(images)} 张图片")
    print("=" * 50)


def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          🔄  批量格式转换工具  v1.0                        ║
║                                                           ║
║   支持：PNG ↔ JPG ↔ WebP 互相转换                         ║
║   作者：诗韵长安项目组                                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    # 获取用户输入
    print("请选择操作模式：")
    print("1. 转换当前目录下的图片")
    print("2. 指定输入/输出目录")
    
    choice = input("\n请输入选项 (1/2): ").strip()
    
    if choice == "1":
        input_dir = "."
        output_dir = "./converted"
    elif choice == "2":
        input_dir = input("请输入输入目录路径: ").strip()
        output_dir = input("请输入输出目录路径: ").strip()
    else:
        print("❌ 无效选项")
        return
    
    # 选择目标格式
    print("\n请选择目标格式：")
    print("1. JPG (适合照片，体积小)")
    print("2. PNG (支持透明，质量高)")
    print("3. WebP (现代格式，体积更小)")
    
    format_choice = input("\n请输入选项 (1/2/3): ").strip()
    
    format_map = {'1': 'jpg', '2': 'png', '3': 'webp'}
    target_format = format_map.get(format_choice)
    
    if not target_format:
        print("❌ 无效选项")
        return
    
    # 执行批量转换
    batch_convert(input_dir, output_dir, target_format)


if __name__ == "__main__":
    main()
