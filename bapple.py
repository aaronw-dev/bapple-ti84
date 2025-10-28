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


pygame.init()
pygame.display.set_caption("awdev's bapple - Delta RLE")
framew = 160
frameh = 120
screen = pygame.display.set_mode((framew, frameh))

clock = pygame.time.Clock()
running = True
last_frame_time = time.time()
targetfps = 10
frame_duration = 1/targetfps
curframe = 0
numframes = 2193

'''print("preloading...")
dataframes = []
for i in range(numframes):
    with open(f"./frames/frame_{i:05d}.bin", "rb") as file:
        data = file.read()
        dataframes.append(data)
print("finished preloading.")'''

current_frame = [[0 for _ in range(framew)] for _ in range(frameh)]

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_time = time.time()
    if current_time - last_frame_time >= frame_duration:
        # data = dataframes[curframe]
        with open(f"./frames/frame_{curframe:05d}.bin", "rb") as file:
            data = file.read()

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

        screen.fill((0, 0, 0))

        for y in range(frameh):
            for x in range(framew):
                if current_frame[y][x] == 255:
                    screen.set_at((x, y), (255, 255, 255))

        pygame.display.flip()
        # print(f"Frame {curframe}")
        curframe += 1
        last_frame_time = current_time

    clock.tick(targetfps)

pygame.quit()
