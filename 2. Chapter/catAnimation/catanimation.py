import pygame, sys
from pygame.locals import *

#constants
START_X = 1080
START_Y = 1080
MIDDLE_X = START_X/2
MIDDLE_Y = START_Y/2
MID_OFFSET_X = MIDDLE_X - (MIDDLE_X/2)
MID_OFFSET_Y = MIDDLE_Y - (MIDDLE_Y/2)

#game initialization
pygame.init()

#frames per second settings
FPS = 1_000
fpsClock = pygame.time.Clock()

#set up the window
DISPLAY_SURFACE = pygame.display.set_mode((START_X, START_Y), 0, 32)
pygame.display.set_caption('Animation')

#colour settings
WHITE = (255, 255, 255)
BLACK = (  0,   0,   0)
RED   = (255,   0,   0)
BLUE  = (  0,   0, 255)

#cat settings
catImg = pygame.image.load('cat.png')
cat_x = MID_OFFSET_X
cat_y = MID_OFFSET_Y
direction = 'right'
UPDATE = 5

while True: #the main game loop
    DISPLAY_SURFACE.fill(BLACK)

    pygame.draw.circle(DISPLAY_SURFACE, BLUE, (MIDDLE_X, MIDDLE_Y), MIDDLE_X-20)
    #pygame.draw.rect(DISPLAY_SURFACE, RED, (MID_OFFSET_X, MID_OFFSET_Y, MIDDLE_X, MIDDLE_Y))
    pygame.draw.rect(DISPLAY_SURFACE, RED, (MIDDLE_X-2, MIDDLE_Y-2, 3, 3))
    
    if direction == 'right':
        cat_X += UPDATE
        if cat_x == MIDDLE_X + MID_OFFSET_X - catImg.get_width()+30:
            direction = 'down'
    elif direction == 'down':
        cat_y += UPDATE
        if cat_y == MIDDLE_Y + MID_OFFSET_Y - catImg.get_width()+30:
            direction = 'left'
    elif direction == 'left':
        cat_x -= UPDATE
        if cat_x == MID_OFFSET_X:
            direction = 'up'
    elif direction == 'up':
        cat_y -= UPDATE
        if cat_y == MID_OFFSET_Y:
            direction = 'right'

    DISPLAY_SURFACE.blit(catImg, (cat_x, cat_y))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            
    pygame.display.update()
    fpsClock.tick(FPS)
