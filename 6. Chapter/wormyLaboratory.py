# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys
from pygame.locals import *

FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the worm's head

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():
    
    #----------------------Worm 2----------------------
    global worm2Coords, direction2, worm2Alive
    start_time = pygame.time.get_ticks()
    #--------------------------------------------------
    
    # Set a random start point.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [{'x': startx,     'y': starty},
                {'x': startx - 1, 'y': starty},
                {'x': startx - 2, 'y': starty}]
    direction = RIGHT
    
    worm2Coords = [{'x': 0, 'y': 0},
                {'x': 0, 'y': 0},
                {'x': 0, 'y': 0}]
    direction2 = RIGHT
    worm2Alive = False

    # Start the apple in a random place.
    apple = getRandomLocation()

    while True: # main game loop
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        #----------------------Worm 2----------------------
        # Check if it's time to spawn the second worm
        current_time = pygame.time.get_ticks()
        if current_time - start_time > 20000 and not worm2Alive:  # 20 seconds
            spawnSecondWorm()
        
        # Move the second worm
        if worm2Alive:
            moveWorm(worm2Coords, getRandomDirection())
            
        # Check for collisions
        handleCollisions(wormCoords, worm2Coords)
        #--------------------------------------------------
        
        # check if the worm has hit itself or the edge
        if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or wormCoords[HEAD]['y'] == CELLHEIGHT:
            return # game over
        for wormBody in wormCoords[1:]:
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                return # game over

        # check if worm has eaten an apply
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            # don't remove worm's tail segment
            apple = getRandomLocation() # set a new apple somewhere
        else:
            del wormCoords[-1] # remove worm's tail segment

        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}
        wormCoords.insert(0, newHead)
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm1(wormCoords)
        if worm2Alive:
            drawWorm2(worm2Coords, RED)  # Draw the second worm in dark green
        drawApple(apple)
        drawScore(len(wormCoords) - 3 + len(worm2Coords) - 3)
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        
#----------------------Worm 2----------------------
def spawnSecondWorm():
    global worm2Coords, direction2, worm2Alive
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    worm2Coords = [{'x': startx, 'y': starty},
                   {'x': startx - 1, 'y': starty},
                   {'x': startx - 2, 'y': starty}]
    direction2 = RIGHT
    worm2Alive = True

def moveWorm(worm, direction):
    if direction == UP:
        newHead = {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y'] - 1}
    elif direction == DOWN:
        newHead = {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y'] + 1}
    elif direction == LEFT:
        newHead = {'x': worm[HEAD]['x'] - 1, 'y': worm[HEAD]['y']}
    elif direction == RIGHT:
        newHead = {'x': worm[HEAD]['x'] + 1, 'y': worm[HEAD]['y']}
    worm.insert(0, newHead)
    del worm[-1]

def handleCollisions(worm1, worm2):
    global worm2Alive
    # Check if the original worm collides with the second worm
    if worm1[HEAD] in worm2:
        # Grow the original worm's body without moving the head
        newBodySegment = {'x': worm1[HEAD]['x'], 'y': worm1[HEAD]['y']}
        worm1.insert(1, newBodySegment)

        # Kill the second worm only if it hits the edge
        if (worm2[HEAD]['x'] == -1 or worm2[HEAD]['x'] == CELLWIDTH or
                worm2[HEAD]['y'] == -1 or worm2[HEAD]['y'] == CELLHEIGHT):
            terminate()
        else:
            worm2Alive = False  # Kill the second worm

        return  # Avoid further processing if there's a collision

    # Check if the second worm collides with the original worm
    if worm2Alive and worm2[HEAD] in worm1:
        # Grow the second worm's body without moving the head
        newBodySegment = {'x': worm2[HEAD]['x'], 'y': worm2[HEAD]['y']}
        worm2.insert(1, newBodySegment)

def drawWorm2 (worm, color):
    for coord in worm:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, color, wormInnerSegmentRect)

def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}

def getRandomDirection():
    return random.choice([UP, DOWN, LEFT, RIGHT])
#--------------------------------------------------

def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue
    
    #--------------START/QUIT BUTTONS----------------
    # Draw "Start from the beginning" button
    startButtonSurf = BASICFONT.render('Start from the beginning', True, WHITE)
    startButtonRect = startButtonSurf.get_rect()
    startButtonRect.midtop = (WINDOWWIDTH / 2, overRect.height + 10 + 50)
    
    # Enlarge the button size
    startButtonRect.width += 20
    startButtonRect.height += 10
    
    # Create a black background for the button
    pygame.draw.rect(DISPLAYSURF, BLACK, (startButtonRect.left - 10, startButtonRect.top - 5, startButtonRect.width + 20, startButtonRect.height + 10))
    
    DISPLAYSURF.blit(startButtonSurf, startButtonRect)
    
    # Draw "Quit" button
    # Draw "Quit" button
    quitButtonSurf = BASICFONT.render('Quit', True, WHITE)
    quitButtonRect = quitButtonSurf.get_rect()
    quitButtonRect.midtop = (WINDOWWIDTH / 2, startButtonRect.height + startButtonRect.top + 10)
    
    # Enlarge the button size
    quitButtonRect.width += 20
    quitButtonRect.height += 10
    
    # Create a black background for the button
    pygame.draw.rect(DISPLAYSURF, BLACK, (quitButtonRect.left - 10, quitButtonRect.top - 5, quitButtonRect.width + 20, quitButtonRect.height + 10))
    
    DISPLAYSURF.blit(quitButtonSurf, quitButtonRect)

    pygame.display.update()
    #------------------------------------------------

    # while True:
    #     if checkForKeyPress():
    #         pygame.event.get() # clear event queue
    #         return
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
            elif event.type == MOUSEBUTTONUP:
                mouse_x, mouse_y = event.pos
                # Check if the mouse click is within the "Start from the beginning" button
                if startButtonRect.collidepoint(mouse_x, mouse_y):
                    runGame()
                    return
                # Check if the mouse click is within the "Quit" button
                elif quitButtonRect.collidepoint(mouse_x, mouse_y):
                    terminate()

def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm1(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()