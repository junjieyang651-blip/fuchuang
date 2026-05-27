"""
诗韵长安・峡谷寻踪 —— 视频内容分析模块
========================================
使用 YOLOv8 对项目短视频进行逐帧目标检测与场景分析
技术栈: Python + Ultralytics YOLOv8 + OpenCV
辅助工具: CodeBuddy (AI编程助手)

功能说明:
1. 对短视频进行定间隔抽帧
2. 对每帧执行 YOLO 目标检测
3. 统计视频中出现的元素及时长分布
4. 输出关键帧标注图与分析报告

运行环境:
    pip install ultralytics opencv-python numpy

用法:
    python scripts/video_analysis.py --input video.mp4 --interval 30
"""

import os
import sys
import json
import argparse
from pathlib import Path

try:
    from ultralytics import YOLO
    import cv2
    import numpy as np
except ImportError:
    print("请先安装依赖: pip install ultralytics opencv-python numpy")
    sys.exit(1)


PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "video_analysis_results"
MODEL_NAME = "yolov8n.pt"


def analyze_video(video_path, frame_interval=30, conf_threshold=0.3):
    """对视频进行逐帧YOLO分析"""
    print("=" * 60)
    print("  诗韵长安 · 视频内容AI分析")
    print(f"  Model: YOLOv8n | 抽帧间隔: {frame_interval}帧")
    print("=" * 60)

    # 检查视频文件
    if not os.path.exists(video_path):
        print(f"  ✗ 视频文件不存在: {video_path}")
        return None

    # 加载模型
    print(f"\n[1/4] 加载模型...")
    model = YOLO(MODEL_NAME)
    print(f"  ✓ YOLOv8n 加载成功")

    # 打开视频
    print(f"\n[2/4] 读取视频信息...")
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps > 0 else 0

    print(f"  分辨率: {width}x{height}")
    print(f"  帧率: {fps:.1f} FPS")
    print(f"  总帧数: {total_frames}")
    print(f"  时长: {duration:.1f} 秒")
    print(f"  预计分析帧数: {total_frames // frame_interval}")

    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 逐帧分析
    print(f"\n[3/4] 开始逐帧检测...")
    frame_idx = 0
    analyzed_count = 0
    all_detections = {}
    class_timeline = {}  # 类别出现时间线

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_interval == 0:
            # YOLO推理
            results = model(frame, verbose=False, conf=conf_threshold)
            result = results[0]

            timestamp = frame_idx / fps if fps > 0 else 0
            frame_dets = []

            for box in result.boxes:
                cls_id = int(box.cls[0])
                cls_name = model.names[cls_id]
                conf = float(box.conf[0])
                frame_dets.append({
                    "class": cls_name,
                    "confidence": round(conf, 3),
                    "timestamp": round(timestamp, 2)
                })

                # 记录时间线
                if cls_name not in class_timeline:
                    class_timeline[cls_name] = []
                class_timeline[cls_name].append(timestamp)

            all_detections[frame_idx] = {
                "timestamp": round(timestamp, 2),
                "objects": frame_dets
            }

            # 保存关键帧（首次检测到新类别时）
            if len(frame_dets) > 0 and analyzed_count < 20:
                annotated = result.plot()
                kf_path = OUTPUT_DIR / f"keyframe_{frame_idx:06d}.jpg"
                cv2.imwrite(str(kf_path), annotated)

            analyzed_count += 1
            if analyzed_count % 10 == 0:
                print(f"  已分析 {analyzed_count} 帧 ({timestamp:.1f}s)...")

        frame_idx += 1

    cap.release()
    print(f"  ✓ 分析完成: 共处理 {analyzed_count} 帧")

    # 生成报告
    print(f"\n[4/4] 生成分析报告...")
    report = {
        "video_info": {
            "path": str(video_path),
            "resolution": f"{width}x{height}",
            "fps": fps,
            "duration_sec": round(duration, 1),
            "total_frames": total_frames
        },
        "analysis_config": {
            "model": MODEL_NAME,
            "frame_interval": frame_interval,
            "conf_threshold": conf_threshold,
            "frames_analyzed": analyzed_count
        },
        "class_summary": {},
        "detections": all_detections
    }

    # 类别统计
    total_det = 0
    for cls_name, timestamps in class_timeline.items():
        report["class_summary"][cls_name] = {
            "count": len(timestamps),
            "first_appear": min(timestamps),
            "last_appear": max(timestamps),
            "duration_coverage": round(max(timestamps) - min(timestamps), 2)
        }
        total_det += len(timestamps)

    # 保存报告
    report_path = OUTPUT_DIR / "video_analysis_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 打印摘要
    print(f"\n  {'─' * 40}")
    print(f"  视频时长: {duration:.1f}s | 分析帧数: {analyzed_count}")
    print(f"  总检出: {total_det} 个目标实例")
    print(f"\n  出现类别:")
    for cls, info in sorted(report["class_summary"].items(), key=lambda x: -x[1]["count"]):
        print(f"    {cls}: {info['count']}次 ({info['first_appear']:.1f}s - {info['last_appear']:.1f}s)")

    print(f"\n  ✓ 报告已保存: {report_path}")
    print(f"  ✓ 关键帧已保存: {OUTPUT_DIR}/")
    print(f"\n{'=' * 60}")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="诗韵长安 - 视频内容AI分析")
    parser.add_argument("--input", type=str, default="video.mp4", help="输入视频路径")
    parser.add_argument("--interval", type=int, default=30, help="抽帧间隔(默认30帧)")
    parser.add_argument("--conf", type=float, default=0.3, help="置信度阈值")
    args = parser.parse_args()

    analyze_video(args.input, args.interval, args.conf)
