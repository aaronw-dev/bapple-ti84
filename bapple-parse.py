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


def write_frame_to_file(f, rle):
    frame_data = bytearray()
    for value, count in rle:
        if value == 0:
            val_byte = 0
        elif value == 127:
            val_byte = 1
        else:
            val_byte = 2

        if count < 128:
            frame_data.extend([val_byte, count])
        else:
            frame_data.extend(
                [val_byte | 0x80, count & 0xFF, (count >> 8) & 0xFF])

    frame_size = len(frame_data)
    f.write(frame_size.to_bytes(4, 'little'))
    f.write(frame_data)


def process_video(video_path, output_base="bapple_segment", segment_size=20*1024):
    """Process video and split into segments of specified size (default 20KB)."""
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    prev_frame = None
    segment_idx = 0
    current_segment_size = 0
    current_segment_frames = []
    all_frames_data = []

    print(f"Processing video with {segment_size} byte segments...")

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
            if frame_idx % 100 == 0:
                print(
                    f"Encoded frame {frame_idx} (DELTA: {changed_pixels}/{total_pixels} pixels changed, {change_percent:.1f}%)")

        rle = rle_encode(delta)

        # Encode frame data
        frame_data = bytearray()
        for value, count in rle:
            if value == 0:
                val_byte = 0
            elif value == 127:
                val_byte = 1
            else:
                val_byte = 2

            if count < 128:
                frame_data.extend([val_byte, count])
            else:
                frame_data.extend(
                    [val_byte | 0x80, count & 0xFF, (count >> 8) & 0xFF])

        frame_size = len(frame_data) + 4  # +4 for size header

        # Check if adding this frame would exceed segment size
        if current_segment_size + frame_size > segment_size and current_segment_frames:
            # Save current segment
            save_segment(output_base, segment_idx, current_segment_frames)
            segment_idx += 1
            current_segment_frames = []
            current_segment_size = 0

        # Add frame to current segment
        current_segment_frames.append((frame_idx, frame_data))
        current_segment_size += frame_size

        prev_frame = bw.copy()
        frame_idx += 1

    # Save final segment if it has frames
    if current_segment_frames:
        save_segment(output_base, segment_idx, current_segment_frames)
        segment_idx += 1

    cap.release()
    print(f"Finished encoding {frame_idx} frames into {segment_idx} segments")


def save_segment(output_base, segment_idx, frames):
    """Save a segment with its frames."""
    filename = f"{output_base}{segment_idx}.bin"
    with open(filename, "wb") as f:
        # Write frame count in this segment
        f.write(len(frames).to_bytes(4, 'little'))

        # Write each frame
        for frame_idx, frame_data in frames:
            f.write(len(frame_data).to_bytes(4, 'little'))
            f.write(frame_data)

    file_size = os.path.getsize(filename)
    start_frame = frames[0][0]
    end_frame = frames[-1][0]
    print(
        f"Saved segment {segment_idx}: frames {start_frame}-{end_frame} ({file_size} bytes)")


if __name__ == "__main__":
    process_video("bapple_atto.mp4", "SEGMENT",
                  20*1024)  # 20KB segments
