#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图片批量重命名工具
功能：按照「英雄名-景点名-序号」规则批量重命名图片
作者：诗韵长安项目组
"""

import os
import sys
from pathlib import Path


# 英雄与景点的对应关系
HERO_LANDMARK_MAP = {
    '李白': '大唐不夜城',
    '上官婉儿': '大雁塔',
    '杨玉环': '华清宫',
    'liobai': '大唐不夜城',
    'shangguan': '大雁塔',
    'yangyuhuan': '华清宫',
}


def detect_hero_from_filename(filename):
    """
    从文件名中检测英雄名称
    
    参数:
        filename: 文件名
    返回:
        (英雄名, 景点名) 或 (None, None)
    """
    filename_lower = filename.lower()
    
    for hero, landmark in HERO_LANDMARK_MAP.items():
        if hero in filename_lower or hero.lower() in filename_lower:
            return hero, landmark
    
    return None, None


def batch_rename(input_dir, output_dir=None, dry_run=True, naming_rule='{hero}-{landmark}-{index}.{ext}'):
    """
    批量重命名图片
    
    参数:
        input_dir: 输入目录
        output_dir: 输出目录（None表示原地重命名）
        dry_run: 是否仅预览不执行
        naming_rule: 命名规则
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
    
    print("=" * 60)
    print(f"📂 输入目录: {input_dir}")
    print(f"🖼️  找到 {len(images)} 张图片")
    print("=" * 60)
    
    # 按英雄分组并排序
    hero_groups = {}
    ungrouped = []
    
    for img in sorted(images):
        hero, landmark = detect_hero_from_filename(img.name)
        if hero:
            if hero not in hero_groups:
                hero_groups[hero] = []
            hero_groups[hero].append((img, hero, landmark))
        else:
            ungrouped.append(img)
    
    # 生成新文件名
    rename_list = []
    
    for hero, items in hero_groups.items():
        landmark = HERO_LANDMARK_MAP.get(hero, '未知景点')
        for i, (img, _, _) in enumerate(items, 1):
            new_name = naming_rule.format(
                hero=hero,
                landmark=landmark,
                index=i,
                ext=img.suffix.lstrip('.')
            )
            rename_list.append((img, new_name, hero, landmark))
    
    # 显示预览
    print("\n📋 重命名预览：")
    print("-" * 60)
    
    for old_path, new_name, hero, landmark in rename_list:
        print(f"{old_path.name}")
        print(f"  → {new_name}")
        print(f"  英雄: {hero} | 景点: {landmark}")
        print()
    
    if ungrouped:
        print(f"\n⚠️  未能识别的图片 ({len(ungrouped)} 张)：")
        for img in ungrouped:
            print(f"  {img.name}")
    
    if dry_run:
        print("\n" + "=" * 60)
        print("🔍 这是预览模式，未实际执行重命名")
        print("要执行重命名，请添加 --execute 参数")
        print("=" * 60)
        return
    
    # 执行重命名
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = input_path
    
    success_count = 0
    
    for old_path, new_name, _, _ in rename_list:
        new_path = output_path / new_name
        
        try:
            if output_dir:
                # 复制到新目录
                import shutil
                shutil.copy2(old_path, new_path)
            else:
                # 原地重命名
                old_path.rename(new_path)
            success_count += 1
        except Exception as e:
            print(f"❌ 重命名失败: {old_path.name} → {new_name}: {e}")
    
    print("\n" + "=" * 60)
    print(f"✅ 重命名完成: {success_count}/{len(rename_list)} 张图片")
    print("=" * 60)


def interactive_mode():
    """交互模式"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          📝  图片批量重命名工具  v1.0                      ║
║                                                           ║
║   命名规则：英雄名-景点名-序号.扩展名                      ║
║   支持：李白、上官婉儿、杨玉环 三位英雄                    ║
║   作者：诗韵长安项目组                                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    input_dir = input("请输入图片目录路径: ").strip()
    
    if not input_dir:
        input_dir = "."
    
    output_dir = input("请输入输出目录路径（留空表示原地重命名）: ").strip() or None
    
    print("\n请选择操作：")
    print("1. 预览重命名结果（不执行）")
    print("2. 执行重命名")
    
    choice = input("\n请输入选项 (1/2): ").strip()
    
    dry_run = choice != "2"
    
    batch_rename(input_dir, output_dir, dry_run)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='图片批量重命名工具')
    parser.add_argument('input_dir', nargs='?', default='.', help='输入目录')
    parser.add_argument('-o', '--output', help='输出目录')
    parser.add_argument('-e', '--execute', action='store_true', help='执行重命名（默认仅预览）')
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        interactive_mode()
    else:
        batch_rename(args.input_dir, args.output, dry_run=not args.execute)


if __name__ == "__main__":
    main()
