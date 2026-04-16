"""
单条预览：合成 human_01/outfit_1/front 为 MP4，不删除 PNG。
用于在批量处理前验证画质/分辨率/帧率是否符合预期。
"""
import os
import sys
import glob
import cv2

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FPS = 30

# 要预览的单条序列
PNG_DIR = os.path.join(BASE_DIR, "human_01", "outfit_1", "front")
MP4_PATH = os.path.join(BASE_DIR, "human_01", "outfit_1", "front_preview.mp4")


def main():
    if not os.path.exists(PNG_DIR):
        print(f"错误：PNG 文件夹不存在 {PNG_DIR}")
        return

    frames = sorted(glob.glob(os.path.join(PNG_DIR, "*.png")))
    if not frames:
        print(f"错误：无 PNG 文件")
        return

    first = cv2.imread(frames[0])
    if first is None:
        print(f"错误：无法读取首帧 {frames[0]}")
        return

    h, w = first.shape[:2]
    print(f"帧数: {len(frames)}")
    print(f"分辨率: {w} x {h}")
    print(f"输出: {MP4_PATH}")
    print(f"合成中...")

    writer = cv2.VideoWriter(
        MP4_PATH,
        cv2.VideoWriter_fourcc(*"mp4v"),
        FPS,
        (w, h)
    )

    for i, frame_path in enumerate(frames):
        img = cv2.imread(frame_path)
        if img is not None:
            writer.write(img)
        if (i + 1) % 30 == 0:
            print(f"  {i + 1}/{len(frames)}")

    writer.release()

    size_mb = os.path.getsize(MP4_PATH) / (1024 * 1024)
    print(f"\n完成！")
    print(f"MP4 大小: {size_mb:.2f} MB")
    print(f"PNG 保留未删，确认画质 OK 后再运行 make_videos_batch.py")


if __name__ == "__main__":
    main()
