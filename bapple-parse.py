import cv2
import numpy as np
import os


def rle_encode(arr):
    flat = arr.flatten()
    diffs = np.diff(flat)
    indices = np.where(diffs != 0)[0] + 1
    counts = np.diff(np.concatenate(([0], indices, [len(flat)])))
    values = flat[np.concatenate(([0], indices))]
    return list(zip(values.tolist(), counts.tolist()))


def save_rle_compact(rle, path):
    with open(path, "wb") as f:
        for value, count in rle:
            if value == 0:
                val_byte = 0
            elif value == 127:
                val_byte = 1
            else:
                val_byte = 2

            if count < 128:
                f.write(bytes([val_byte, count]))
            else:
                f.write(
                    bytes([val_byte | 0x80, count & 0xFF, (count >> 8) & 0xFF]))


def process_video(video_path, output_dir="./frames"):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    prev_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, bw = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        if prev_frame is None:
            delta = bw
            print(f"Encoded frame {frame_idx} (FULL FRAME)")
        else:
            delta = np.zeros_like(bw)
            changed_mask = (bw != prev_frame)

            white_changes = changed_mask & (bw == 255)
            delta[white_changes] = 255

            black_changes = changed_mask & (bw == 0)
            delta[black_changes] = 127

            changed_pixels = np.sum(changed_mask)
            total_pixels = bw.size
            change_percent = (changed_pixels / total_pixels) * 100
            print(
                f"Encoded frame {frame_idx} (DELTA: {changed_pixels}/{total_pixels} pixels changed, {change_percent:.1f}%)")

        rle = rle_encode(delta)
        out_path = os.path.join(output_dir, f"frame_{frame_idx:05d}.bin")
        save_rle_compact(rle, out_path)

        prev_frame = bw.copy()
        frame_idx += 1

    cap.release()
    print(f"Finished encoding {frame_idx} frames to {output_dir}/")


if __name__ == "__main__":
    process_video("bapple_nano.mp4", "./frames")
