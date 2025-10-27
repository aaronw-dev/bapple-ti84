import pygame, time
import math
pygame.init()
framew = 320
frameh = 240
screen = pygame.display.set_mode((framew, frameh))
curframe = 0

def pixelToCoords(pixel):
    return ((pixel % framew), math.floor(pixel/framew))

def drawlines(start, end, color):
    linestart = pixelToCoords(start)
    lineend = pixelToCoords(end)
    y1 = linestart[1]
    y2 = lineend[1]

    for y in range(min(y1, y2), max(y1, y2) + 1):
        pygame.draw.line(screen, (color, color, color), (linestart[0], y), (lineend[0], y), width=1)

while True:
    with open(f"./frames/frame_{curframe:05d}.txt", "r") as file:
        rle = file.readlines()
    screen.fill((0, 0, 0))
    startpixel = 0
    for set in rle:
        splitset = set.split(":")
        col = int(splitset[0])
        length = int(splitset[1])
        endpixel = startpixel + length
        drawlines(startpixel, endpixel, col)
        startpixel = startpixel + length
    pygame.display.flip()
    time.sleep(1/30)
    curframe = curframe + 1
