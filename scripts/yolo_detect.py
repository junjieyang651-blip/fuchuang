"""
诗韵长安・峡谷寻踪 —— AI目标检测模块
========================================
使用 YOLOv8 对项目国风插画进行多目标检测与分析
技术栈: Python + Ultralytics YOLOv8 + OpenCV
辅助工具: CodeBuddy (AI编程助手)

功能说明:
1. 对9幅AI生成国风插画执行目标检测
2. 输出检测结果(类别、置信度、边界框)
3. 生成标注后的可视化图像
4. 统计各类目标分布情况

运行环境:
    pip install ultralytics opencv-python numpy

用法:
    python scripts/yolo_detect.py
"""

import os
import json
import sys
from pathlib import Path

try:
    from ultralytics import YOLO
    import cv2
    import numpy as np
except ImportError:
    print("请先安装依赖: pip install ultralytics opencv-python numpy")
    sys.exit(1)


# ===== 配置 =====
PROJECT_ROOT = Path(__file__).parent.parent
IMAGE_DIR = PROJECT_ROOT
OUTPUT_DIR = PROJECT_ROOT / "detection_results"
MODEL_NAME = "yolov8n.pt"  # YOLOv8 Nano (轻量级，适合快速推理)

# 9幅插画文件名
ARTWORKS = [
    "李白-大唐不夜城-1.jpg",
    "李白-大唐不夜城-2.jpg",
    "李白-大唐不夜城-3.jpg",
    "上官婉儿-大雁塔-1.jpg",
    "上官婉儿-大雁塔-2.jpg",
    "上官婉儿-大雁塔-3.jpg",
    "杨玉环-华清宫-1.jpg",
    "杨玉环-华清宫-2.jpg",
    "杨玉环-华清宫-3.jpg",
]

# COCO类别中文映射（与网页端保持一致）
CLASS_NAME_CN = {
    'person': '人物', 'sword': '长剑', 'knife': '利刃',
    'cup': '酒杯', 'bowl': '碗', 'vase': '花瓶',
    'book': '书卷', 'umbrella': '伞', 'bottle': '酒壶',
    'wine glass': '酒盏', 'chair': '座椅', 'dining table': '案几',
    'potted plant': '盆景', 'bird': '飞鸟', 'horse': '骏马',
    'backpack': '行囊', 'kite': '风筝',
}


def detect_artworks():
    """对所有插画执行YOLO目标检测"""
    print("=" * 60)
    print("  诗韵长安 · AI目标检测分析")
    print("  Model: YOLOv8n | Framework: Ultralytics")
    print("=" * 60)

    # 加载模型
    print(f"\n[1/3] 加载 YOLOv8 模型: {MODEL_NAME}")
    model = YOLO(MODEL_NAME)
    print(f"  ✓ 模型加载成功 (参数量: {sum(p.numel() for p in model.model.parameters())/1e6:.1f}M)")

    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 执行检测
    print(f"\n[2/3] 开始检测 {len(ARTWORKS)} 幅插画...")
    all_results = {}
    total_objects = 0

    for i, filename in enumerate(ARTWORKS, 1):
        img_path = IMAGE_DIR / filename
        if not img_path.exists():
            print(f"  [{i}/9] ⚠ 文件不存在: {filename}")
            continue

        # 推理
        results = model(str(img_path), verbose=False, conf=0.25)
        result = results[0]

        # 解析检测结果
        detections = []
        for box in result.boxes:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].cpu().numpy().tolist()

            detections.append({
                "class": cls_name,
                "class_cn": CLASS_NAME_CN.get(cls_name, cls_name),
                "confidence": round(conf, 4),
                "bbox_xyxy": [round(x, 1) for x in xyxy],
            })

        total_objects += len(detections)
        all_results[filename] = detections

        # 保存标注图
        annotated = result.plot()
        output_path = OUTPUT_DIR / f"detected_{filename}"
        cv2.imwrite(str(output_path), annotated)

        print(f"  [{i}/9] {filename}: 检出 {len(detections)} 个目标")
        for det in detections:
            print(f"         → {det['class_cn']}({det['class']}) conf={det['confidence']:.2f}")

    # 保存JSON结果
    json_path = OUTPUT_DIR / "detection_results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # 统计分析
    print(f"\n[3/3] 检测统计")
    print(f"  {'─' * 40}")
    print(f"  总检出目标数: {total_objects}")
    print(f"  平均每幅: {total_objects / max(len(all_results), 1):.1f} 个")

    # 类别分布
    class_count = {}
    for dets in all_results.values():
        for d in dets:
            cn = d['class_cn']
            class_count[cn] = class_count.get(cn, 0) + 1

    if class_count:
        print(f"\n  类别分布:")
        for cls, cnt in sorted(class_count.items(), key=lambda x: -x[1]):
            print(f"    {cls}: {cnt} 次")

    print(f"\n  ✓ 标注图已保存至: {OUTPUT_DIR}/")
    print(f"  ✓ JSON结果已保存至: {json_path}")
    print(f"\n{'=' * 60}")
    return all_results


def generate_webpage_data(results):
    """将检测结果转换为网页可用的JS数据格式"""
    js_data = {}
    for i, filename in enumerate(ARTWORKS):
        if filename not in results:
            continue
        dets = results[filename]
        js_data[i] = [{
            "label": f"{d['class_cn']}({d['class']})",
            "conf": d['confidence'],
            "bbox": d['bbox_xyxy']
        } for d in dets]

    output_path = OUTPUT_DIR / "web_detect_data.js"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("// 由 yolo_detect.py 自动生成的真实检测数据\n")
        f.write(f"const YOLO_DETECT_RESULTS = {json.dumps(js_data, ensure_ascii=False, indent=2)};\n")

    print(f"\n  ✓ 网页数据已生成: {output_path}")


if __name__ == "__main__":
    results = detect_artworks()
    if results:
        generate_webpage_data(results)
