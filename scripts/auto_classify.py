#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图片自动分类工具
功能：根据英雄名称自动将图片归档到对应文件夹
作者：诗韵长安项目组
"""

import os
import sys
import shutil
from pathlib import Path


# 英雄关键词配置
HERO_KEYWORDS = {
    '李白': ['李白', 'libai', 'liobai'],
    '上官婉儿': ['上官婉儿', '婉儿', 'shangguan', 'wanger'],
    '杨玉环': ['杨玉环', '玉环', 'yangyuhuan', 'yuhuan'],
}


def detect_hero(filename):
    """
    从文件名中检测英雄
    
    参数:
        filename: 文件名
    返回:
        英雄名称或 None
    """
    filename_lower = filename.lower()
    
    for hero, keywords in HERO_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in filename_lower:
                return hero
    
    return None


def auto_classify(input_dir, output_dir=None, copy_mode=True, dry_run=True):
    """
    自动分类图片
    
    参数:
        input_dir: 输入目录
        output_dir: 输出目录（None表示在输入目录下创建分类文件夹）
        copy_mode: True=复制，False=移动
        dry_run: 是否仅预览不执行
    """
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"❌ 目录不存在: {input_dir}")
        return
    
    # 支持的图片格式
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    
    # 获取所有图片
    images = [f for f in input_path.iterdir() 
              if f.suffix.lower() in image_extensions]
    
    if not images:
        print("⚠️  未找到图片文件")
        return
    
    # 设置输出目录
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = input_path
    
    print("=" * 60)
    print(f"📂 输入目录: {input_dir}")
    print(f"📂 输出目录: {output_path}")
    print(f"🖼️  找到 {len(images)} 张图片")
    print(f"📋 操作模式: {'复制' if copy_mode else '移动'}")
    print("=" * 60)
    
    # 分类统计
    classified = {}
    unclassified = []
    
    for img in images:
        hero = detect_hero(img.name)
        if hero:
            if hero not in classified:
                classified[hero] = []
            classified[hero].append(img)
        else:
            unclassified.append(img)
    
    # 显示分类结果
    print("\n📊 分类统计：")
    print("-" * 60)
    
    for hero, files in classified.items():
        print(f"  {hero}: {len(files)} 张")
        for f in files:
            print(f"    • {f.name}")
    
    if unclassified:
        print(f"\n  未识别: {len(unclassified)} 张")
        for f in unclassified:
            print(f"    • {f.name}")
    
    if dry_run:
        print("\n" + "=" * 60)
        print("🔍 这是预览模式，未实际执行分类")
        print("要执行分类，请添加 --execute 参数")
        print("=" * 60)
        return
    
    # 执行分类
    success_count = 0
    
    for hero, files in classified.items():
        # 创建英雄文件夹
        hero_dir = output_path / hero
        hero_dir.mkdir(parents=True, exist_ok=True)
        
        for img in files:
            dest = hero_dir / img.name
            
            try:
                if copy_mode:
                    shutil.copy2(img, dest)
                else:
                    shutil.move(str(img), dest)
                success_count += 1
                print(f"✅ {img.name} → {hero}/")
            except Exception as e:
                print(f"❌ 处理失败 {img.name}: {e}")
    
    print("\n" + "=" * 60)
    print(f"✅ 分类完成: {success_count}/{sum(len(v) for v in classified.values())} 张图片")
    print("=" * 60)


def interactive_mode():
    """交互模式"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          📂  图片自动分类工具  v1.0                        ║
║                                                           ║
║   功能：根据英雄名称自动将图片归档到对应文件夹             ║
║   支持：李白、上官婉儿、杨玉环 三位英雄                    ║
║   作者：诗韵长安项目组                                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    input_dir = input("请输入图片目录路径: ").strip()
    
    if not input_dir:
        input_dir = "."
    
    output_dir = input("请输入输出目录路径（留空表示在原目录下创建分类文件夹）: ").strip() or None
    
    print("\n请选择操作模式：")
    print("1. 复制文件到分类文件夹")
    print("2. 移动文件到分类文件夹")
    
    mode_choice = input("\n请输入选项 (1/2): ").strip()
    copy_mode = mode_choice != "2"
    
    print("\n请选择执行模式：")
    print("1. 预览分类结果（不执行）")
    print("2. 执行分类")
    
    exec_choice = input("\n请输入选项 (1/2): ").strip()
    dry_run = exec_choice != "2"
    
    auto_classify(input_dir, output_dir, copy_mode, dry_run)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='图片自动分类工具')
    parser.add_argument('input_dir', nargs='?', default='.', help='输入目录')
    parser.add_argument('-o', '--output', help='输出目录')
    parser.add_argument('-m', '--move', action='store_true', help='移动文件（默认复制）')
    parser.add_argument('-e', '--execute', action='store_true', help='执行分类（默认仅预览）')
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        interactive_mode()
    else:
        auto_classify(
            args.input_dir, 
            args.output, 
            copy_mode=not args.move, 
            dry_run=not args.execute
        )


if __name__ == "__main__":
    main()
