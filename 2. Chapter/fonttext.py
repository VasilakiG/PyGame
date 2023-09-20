import pygame, sys
from pygame.locals import *

pygame.init()
DISPLAY_SURFACE = pygame.display.set_mode((400, 300))
pygame.display.set_caption('Hello World!')

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)

fontObject = pygame.font.Font('freesansbold.ttf', 32)
textSurfaceObject = fontObject.render('Hello World!', True, BLACK, WHITE)
textRectObject = textSurfaceObject.get_rect()
textRectObject.center = (200, 150)

#main game loop
while True:
    DISPLAY_SURFACE.fill(WHITE)
    DISPLAY_SURFACE.blit(textSurfaceObject, textRectObject)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
