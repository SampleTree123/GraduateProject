import os
import glob
import cv2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMERAS = ["front", "back", "left", "right"]
FPS = 30

for camera in CAMERAS:
    input_dir = os.path.join(BASE_DIR, camera)
    output_file = os.path.join(BASE_DIR, f"{camera}.mp4")

    if not os.path.exists(input_dir):
        print(f"跳过 {camera}：文件夹不存在")
        continue

    frames = sorted(glob.glob(os.path.join(input_dir, "*.png")))
    if not frames:
        print(f"跳过 {camera}：没有找到 PNG 文件")
        continue

    # 读取第一帧获取分辨率
    first = cv2.imread(frames[0])
    h, w = first.shape[:2]

    writer = cv2.VideoWriter(
        output_file,
        cv2.VideoWriter_fourcc(*"mp4v"),
        FPS,
        (w, h)
    )

    print(f"合成 {camera}：{len(frames)} 帧，分辨率 {w}x{h} -> {output_file}")

    for frame_path in frames:
        img = cv2.imread(frame_path)
        writer.write(img)

    writer.release()
    print(f"完成：{output_file}")

print("=== 所有视频合成完成 ===")
