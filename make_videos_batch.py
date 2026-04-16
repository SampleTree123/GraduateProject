"""
批量将 PNG 序列合成为 MP4 视频，合成成功后立即删除 PNG 以节省磁盘空间。

目录结构：
    MovieRenders/
      human_01/
        outfit_1/
          front/    (PNG 序列)
          back/
          left/
          right/
        outfit_2/
        ...
      human_02/
      ...

输出：每个 camera 文件夹转换成同名 MP4，放在其父目录下
    human_01/outfit_1/front.mp4
    human_01/outfit_1/back.mp4
    ...
"""
import os
import sys
import glob
import shutil
import cv2

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHARACTERS = [f"human_{i:02d}" for i in [1, 2, 3, 4, 6, 7, 8, 9, 10, 11]]
OUTFIT_COUNT = 10
CAMERAS = ["front", "back", "left", "right"]
FPS = 30

# 最小合理文件大小（MB）- 低于此值认为合成失败
MIN_MP4_SIZE_MB = 0.1


def convert_png_to_mp4(png_dir, mp4_path):
    """将 PNG 序列合成为 MP4，返回是否成功"""
    frames = sorted(glob.glob(os.path.join(png_dir, "*.png")))
    if not frames:
        print(f"  跳过：无 PNG 文件")
        return False

    first = cv2.imread(frames[0])
    if first is None:
        print(f"  跳过：无法读取首帧 {frames[0]}")
        return False

    h, w = first.shape[:2]

    writer = cv2.VideoWriter(
        mp4_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        FPS,
        (w, h)
    )

    for frame_path in frames:
        img = cv2.imread(frame_path)
        if img is not None:
            writer.write(img)

    writer.release()

    # 检查输出文件是否合理
    if not os.path.exists(mp4_path):
        return False
    size_mb = os.path.getsize(mp4_path) / (1024 * 1024)
    if size_mb < MIN_MP4_SIZE_MB:
        print(f"  警告：MP4 过小 {size_mb:.2f}MB，可能合成失败")
        return False

    return True


def main():
    total = len(CHARACTERS) * OUTFIT_COUNT * len(CAMERAS)
    done = 0
    failed = []

    for character in CHARACTERS:
        char_dir = os.path.join(BASE_DIR, character)
        if not os.path.exists(char_dir):
            print(f"跳过角色 {character}：文件夹不存在")
            done += OUTFIT_COUNT * len(CAMERAS)
            continue

        for outfit_num in range(1, OUTFIT_COUNT + 1):
            outfit_dir = os.path.join(char_dir, f"outfit_{outfit_num}")
            if not os.path.exists(outfit_dir):
                print(f"跳过 {character}/outfit_{outfit_num}：文件夹不存在")
                done += len(CAMERAS)
                continue

            for camera in CAMERAS:
                done += 1
                png_dir = os.path.join(outfit_dir, camera)
                mp4_path = os.path.join(outfit_dir, f"{camera}.mp4")

                tag = f"[{done}/{total}] {character}/outfit_{outfit_num}/{camera}"

                if not os.path.exists(png_dir):
                    print(f"{tag} 跳过：PNG 文件夹不存在")
                    continue

                # 如果已经有 MP4 且 PNG 文件夹还在，清理后继续
                if os.path.exists(mp4_path) and os.path.getsize(mp4_path) / (1024 * 1024) >= MIN_MP4_SIZE_MB:
                    print(f"{tag} MP4 已存在，清理 PNG")
                    shutil.rmtree(png_dir)
                    continue

                print(f"{tag} 合成中...")
                success = convert_png_to_mp4(png_dir, mp4_path)

                if success:
                    # 合成成功，删除 PNG 释放空间
                    shutil.rmtree(png_dir)
                    mp4_size_mb = os.path.getsize(mp4_path) / (1024 * 1024)
                    print(f"{tag} 完成 ({mp4_size_mb:.1f}MB)，PNG 已删除")
                else:
                    print(f"{tag} 失败！保留 PNG")
                    failed.append(f"{character}/outfit_{outfit_num}/{camera}")

    print("\n" + "=" * 50)
    print(f"全部处理完成：成功 {total - len(failed)}/{total}")
    if failed:
        print(f"失败列表（PNG 已保留）：")
        for f in failed:
            print(f"  - {f}")
    print("=" * 50)


if __name__ == "__main__":
    main()
