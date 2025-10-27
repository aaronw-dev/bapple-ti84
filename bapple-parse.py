import cv2
import numpy as np
import os

def rle_encode(arr):
    """Run-length encode a 1D array of 0s and 255s."""
    flat = arr.flatten()
    diffs = np.diff(flat)
    indices = np.where(diffs != 0)[0] + 1
    counts = np.diff(np.concatenate(([0], indices, [len(flat)])))
    values = flat[np.concatenate(([0], indices))]
    return list(zip(values.tolist(), counts.tolist()))

def save_rle_to_txt(rle, path):
    """Save RLE data to a text file."""
    with open(path, "w") as f:
        for value, count in rle:
            f.write(f"{value}:{count}\n")

def process_video(video_path, output_dir="./frames"):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Threshold to pure black (0) or white (255)
        _, bw = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        # Encode and save
        rle = rle_encode(bw)
        out_path = os.path.join(output_dir, f"frame_{frame_idx:05d}.txt")
        save_rle_to_txt(rle, out_path)
        print(f"Encoded frame {frame_idx}")
        frame_idx += 1

    cap.release()
    print(f"Finished encoding {frame_idx} frames to {output_dir}/")

# --- Example usage ---
if __name__ == "__main__":
    process_video("bapple-comp.mp4", "./frames")