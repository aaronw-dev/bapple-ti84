import pygame
import time
import math


def pixelToCoords(pixel):
    return ((pixel % framew), math.floor(pixel/framew))


def drawlines(start, end, color):
    start_x, start_y = pixelToCoords(start)
    end_x, end_y = pixelToCoords(end - 1)

    if start_y == end_y:
        pygame.draw.line(screen, (color, color, color),
                         (start_x, start_y), (end_x, end_y))
    else:
        if start_x < framew - 1:
            pygame.draw.line(screen, (color, color, color),
                             (start_x, start_y), (framew - 1, start_y))

        for y in range(start_y + 1, end_y):
            pygame.draw.line(screen, (color, color, color),
                             (0, y), (framew - 1, y))

        if end_y > start_y and end_x >= 0:
            pygame.draw.line(screen, (color, color, color),
                             (0, end_y), (end_x, end_y))


def load_segment(segment_filename):
    """Load frames from a single segment file."""
    frames = []
    try:
        with open(segment_filename, "rb") as f:
            # Read frame count in this segment
            frame_count_bytes = f.read(4)
            if len(frame_count_bytes) != 4:
                return []
            frame_count = int.from_bytes(frame_count_bytes, 'little')

            # Read each frame
            for i in range(frame_count):
                size_bytes = f.read(4)
                if len(size_bytes) != 4:
                    break
                frame_size = int.from_bytes(size_bytes, 'little')

                frame_data = f.read(frame_size)
                if len(frame_data) != frame_size:
                    break
                frames.append(frame_data)

        print(f"Loaded {len(frames)} frames from {segment_filename}")
    except FileNotFoundError:
        print(f"Segment {segment_filename} not found!")
        return []

    return frames


class SimpleSegmentPlayer:
    def __init__(self, base_name):
        self.base_name = base_name
        self.current_segment_idx = -1
        self.current_segment_frames = []
        self.frames_loaded_so_far = 0

        print(f"Initialized simple segment player for {base_name}")

    def get_frame(self, global_frame_idx):
        """Get frame data for specified global frame index."""
        # Check if we need to load a new segment
        while global_frame_idx >= self.frames_loaded_so_far + len(self.current_segment_frames):
            # We need the next segment
            self.frames_loaded_so_far += len(self.current_segment_frames)
            self.current_segment_idx += 1

            segment_filename = f"{self.base_name}{self.current_segment_idx}.bin"
            self.current_segment_frames = load_segment(segment_filename)

            if not self.current_segment_frames:
                # No more segments
                return None

        # Calculate frame offset within current segment
        frame_offset = global_frame_idx - self.frames_loaded_so_far

        if 0 <= frame_offset < len(self.current_segment_frames):
            return self.current_segment_frames[frame_offset]

        return None


pygame.init()
pygame.display.set_caption("awdev's bapple - Segmented")
framew = 20
frameh = 16
screen = pygame.display.set_mode((framew, frameh))

clock = pygame.time.Clock()
running = True
last_frame_time = time.time()
targetfps = 5
frame_duration = 1/targetfps
curframe = 0

# Initialize simple segment player
player = SimpleSegmentPlayer("SEGMENT")
numframes = 99999  # We'll stop when no more segments are found

current_frame = [[0 for _ in range(framew)] for _ in range(frameh)]

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_time = time.time()
    if current_time - last_frame_time >= frame_duration:
        data = player.get_frame(curframe)
        if data is None:
            print(f"Animation finished at frame {curframe}")
            running = False
            continue

        startpixel = 0
        i = 0
        while i < len(data):
            val_byte = data[i]
            i += 1

            if val_byte & 0x80:
                val_code = val_byte & 0x7F
                if i + 1 < len(data):
                    count = data[i] | (data[i + 1] << 8)
                    i += 2
                else:
                    break
            else:
                val_code = val_byte
                if i < len(data):
                    count = data[i]
                    i += 1
                else:
                    break

            if val_code == 0:
                col = 0
            elif val_code == 1:
                col = 127
            else:
                col = 255

            for j in range(count):
                pixel_idx = startpixel + j
                if pixel_idx < framew * frameh:
                    x, y = pixelToCoords(pixel_idx)
                    if col == 255:
                        current_frame[y][x] = 255
                    elif col == 127:
                        current_frame[y][x] = 0
                    elif col == 0:
                        if curframe == 0:
                            current_frame[y][x] = 0

            startpixel += count

        for y in range(frameh):
            for x in range(framew):
                if current_frame[y][x] == 255:
                    screen.set_at((x, y), (255, 255, 255))
                else:
                    screen.set_at((x, y), (0, 0, 0))

        pygame.display.flip()
        curframe += 1
        last_frame_time = current_time

    clock.tick(targetfps)

pygame.quit()
