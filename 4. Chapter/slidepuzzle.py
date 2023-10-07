# Slide Puzzle
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pyhame
# Creative Commons BY-NC-SA 3.0 US

import pygame, sys, random
from pygame.locals import *

# Create the constants (go ahead and experiment with different values)
BOARD_WIDTH = 4 #number of columns in the board
BOARD_HEIGHT = 4 #number of rows in the board
TILE_SIZE = 80
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
FPS = 30
BLANK = None

#                 R    G    B
BLACK =        (  0,   0,   0)
WHITE =        (255, 255, 255)
BRIGHT_BLUE =   (  0,  50, 255)
DARK_TUQUOISE = (  3,  54,  73)
GREEN =        (  0, 204,   0)

BG_COLOR = DARK_TUQUOISE
TILE_COLOR = GREEN
TEXT_COLOR = WHITE
BORDER_COLOR = BRIGHT_BLUE
BASIC_FONT_SIZE = 20

BUTTON_COLOR = WHITE
BUTTON_TEXT_COLOR = BLACK
MESSAGE_COLOR = WHITE

X_MARGIN = int( (WINDOW_WIDTH - (TILE_SIZE * BOARD_WIDTH + (BOARD_WIDTH - 1) )) / 2 )
Y_MARGIN = int( (WINDOW_HEIGHT - (TILE_SIZE * BOARD_HEIGHT + (BOARD_HEIGHT - 1) )) / 2 )

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

def main():
    global FPS_CLOCK, DISPLAY_SURFACE, BASIC_FONT, RESET_SURFACE, RESET_RECTANGLE, NEW_SURFACE, NEW_RECTANGLE, SOLVE_SURFACE, SOLVE_RECTANGLE
    
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Slide Puzzle')
    BASIC_FONT = pygame.font.Font('freesansbold.ttf', BASIC_FONT_SIZE)
    
    # Store the option buttons and their rectangles in OPTIONS
    RESET_SURFACE, RESET_RECTANGLE = makeText('Reset', TEXT_COLOR, TILE_COLOR, WINDOW_WIDTH - 120, WINDOW_HEIGHT - 90)
    NEW_SURFACE, NEW_RECTANGLE = makeText('New Game', TEXT_COLOR, TILE_COLOR, WINDOW_WIDTH - 120, WINDOW_HEIGHT - 60)
    SOLVE_SURFACE, SOLVE_RECTANGLE = makeText('Solve', TEXT_COLOR, TILE_COLOR, WINDOW_WIDTH - 120, WINDOW_HEIGHT - 30)
    
    mainBoard, solutionSequence = generateNewPuzzle(80)
    SOLVED_BOARD = getStartingBoard() #a solved board is the same as the board in a start state
    allMoves = [] #list of moves made from the solved configuration
    
    while True: #main game loop
        slideTo = None #the direction, if any, a tile should slide
        msg = '' #contains the message to show in the upper left corner
        if mainBoard == SOLVED_BOARD:
            msg = 'Solved!'
            
        drawBoard(mainBoard, msg)
        
        checkForQuit()
        for event in pygame.event.get(): #event handling loop
            if event.type == MOUSEBUTTONUP:
                spotX, spotY = getSpotClicked(mainBoard, event.pos[0], event.pos[1])
                
                if (spotX, spotY) == (None, None):
                    #check if the user clicked on an option button
                    if RESET_RECTANGLE.collidepoint(event.pos):
                        resetAnimation(mainBoard, allMoves) #clicked on Reset button
                        allMoves = []
                    elif NEW_RECTANGLE.collidepoint(event.pos):
                        mainBoard, solutionSequence = generateNewPuzzle(80) #clicked on New Game button
                        allMoves = []
                    elif SOLVE_RECTANGLE.collidepoint(event.pos):
                        resetAnimation(mainBoard, solutionSequence + allMoves) #clicked on Solve button
                        allMoves = []
                    else:
                        #check if the clicked tile was next to the blank spot
                
                        blankX, blankY = getBlankPosition(mainBoard)
                        if spotX == blankX + 1 and spotY == blankY:
                            slideTo = LEFT
                        elif spotX == blankX - 1 and spotY == blankY:
                            slideTo = RIGHT
                        elif spotX == blankX and spotY == blankY + 1:
                            slideTo = UP
                        elif spotX == blankX and spotY == blankY - 1:
                            slideTo = DOWN
                        
            elif event.type == KEYUP:
                #check if the user pressed a key to slide a tile
                if event.key in (K_LEFT, K_a) and isValidMove(mainBoard, LEFT):
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d) and isValidMove(mainBoard, RIGHT):
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w) and isValidMove(mainBoard, UP):
                    slideTo = UP
                elif event.key in (K_DOWN, K_s) and isValidMove(mainBoard, DOWN):
                    slideTo = DOWN
                    
        if slideTo:
            slideAnimation(mainBoard, slideTo, 'Click tile or press arrow keys to slide.', 8) #show slide on screen
            makeMove(mainBoard, slideTo)
            allMoves.append(slideTo) #record the slide
        pygame.display.update()
        FPS_CLOCK.tick(FPS)
        

def terminate():
    pygame.quit()
    sys.exit()


def checkForQuit():
    for event in pygame.event.get(QUIT): #get all the QUIT events
        terminate() #terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): #get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() #terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) #put the other KEYUP event objects back
        

def getStartingBoard():
    #Return a board data structure with tiles in the solved state.
    #For example. uf BOARD_WIDTH and BOARD_HEIGHT are both 3, this function
    #returns [[1, 4, 7], [2, 5, 8], [3, 6, None]]
    counter = 1
    board = []
    for x in range (BOARD_WIDTH):
        column = []
        for y in range (BOARD_HEIGHT):
            column.append(counter)
            counter += BOARD_WIDTH
        board.append(column)
        counter -= BOARD_WIDTH * (BOARD_HEIGHT - 1) + BOARD_WIDTH - 1
        
    board[BOARD_WIDTH-1][BOARD_HEIGHT-1] = None
    return board


def getBlankPosition(board):
    #Return the x and y of board coordinates of the blank space
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            if board[x][y] == None:
                return (x, y)


def makeMove(board, move):
    #This function does not check if the move is valid
    blankX, blankY = getBlankPosition(board)
    
    if move == UP:
        board[blankX][blankY], board[blankX][blankY + 1] = board[blankX][blankY + 1], board[blankX][blankY]
    elif move == DOWN:
        board[blankX][blankY], board[blankX][blankY - 1] = board[blankX][blankY - 1], board[blankX][blankY]
    elif move == LEFT:
        board[blankX][blankY], board[blankX + 1][blankY] = board[blankX + 1][blankY], board[blankX][blankY]
    elif move == RIGHT:
        board[blankX][blankY], board[blankX - 1][blankY] = board[blankX - 1][blankY], board[blankX][blankY]


def isValidMove(board, move):
    blankX, blankY = getBlankPosition(board)
    return (move == UP and blankY != len(board[0]) - 1) or \
        (move == DOWN and blankY != 0) or \
        (move == LEFT and blankX != len(board) - 1) or \
        (move == RIGHT and blankX != 0)


def getRandomMove(board, lastMove = None):
    #start with a full list of all four moves
    validMoves = [UP, DOWN, LEFT, RIGHT]
    
    #remove moves from the list as they are disqualified
    if lastMove == UP or not isValidMove(board, DOWN):
        validMoves.remove(DOWN)
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)
        
    #return a random move from the list of remaining moves
    return random.choice(validMoves)


def getLeftTopOfTile(tileX, tileY):
    left = X_MARGIN + (tileX * TILE_SIZE) + (tileX - 1)
    top = Y_MARGIN + (tileY * TILE_SIZE) + (tileY - 1)
    return (left, top)


def getSpotClicked(board, x, y):
    #from the x & y pixel coordinates, get the x & y board coordinates
    for tileX in range(len(board)):
        for tileY in range(len(board[0])):
            left, top = getLeftTopOfTile(tileX, tileY)
            tileRectangle = pygame.Rect(left, top, TILE_SIZE, TILE_SIZE)
            if tileRectangle.collidepoint(x, y):
                return (tileX, tileY)
    return (None, None)


def drawTile(tileX, tileY, number, adjacentX = 0, adjacentY = 0):
    #draw a tile at board coordinates tileX and tileY, optionally a few
    #pixels over (determined by adjacentX and adjacentY)
    left, top = getLeftTopOfTile(tileX, tileY)
    pygame.draw.rect(DISPLAY_SURFACE, TILE_COLOR, (left + adjacentX, top + adjacentY, TILE_SIZE, TILE_SIZE))
    textSurface = BASIC_FONT.render(str(number), True, TEXT_COLOR)
    textRectangle = textSurface.get_rect()
    textRectangle.center = left + int(TILE_SIZE / 2) + adjacentX, top + int(TILE_SIZE / 2) + adjacentY
    DISPLAY_SURFACE.blit(textSurface, textRectangle)


def makeText(text, color, bgColor, top, left):
    #create the Surface and Rect objects for some text.
    textSurface = BASIC_FONT.render(text, True, color, bgColor)
    textRectangle = textSurface.get_rect()
    textRectangle.topleft = (top, left)
    return (textSurface, textRectangle)


def drawBoard(board, message):
    DISPLAY_SURFACE.fill(BG_COLOR)
    if message:
        textSurface, textRectangle = makeText(message, MESSAGE_COLOR, BG_COLOR, 5, 5)
        DISPLAY_SURFACE.blit(textSurface, textRectangle)
        
    for tileX in range(len(board)):
        for tileY in range(len(board[0])):
            if board[tileX][tileY]:
                drawTile(tileX, tileY, board[tileX][tileY])
                
    left, top = getLeftTopOfTile(0, 0)
    width = BOARD_WIDTH * TILE_SIZE
    height = BOARD_HEIGHT * TILE_SIZE
    pygame.draw.rect(DISPLAY_SURFACE, BORDER_COLOR, (left - 5, top - 5, width + 11, height + 11), 4)
    
    DISPLAY_SURFACE.blit(RESET_SURFACE, RESET_RECTANGLE)
    DISPLAY_SURFACE.blit(NEW_SURFACE, NEW_RECTANGLE)
    DISPLAY_SURFACE.blit(SOLVE_SURFACE, SOLVE_RECTANGLE)


def slideAnimation(board, direction, message, animationSpeed):
    #Note: This function does not check if the move is valid
    
    blankX, blankY = getBlankPosition(board)
    if direction == UP:
        moveX = blankX
        moveY = blankY + 1
    elif direction == DOWN:
        moveX = blankX
        moveY = blankY - 1
    elif direction == LEFT:
        moveX = blankX + 1
        moveY = blankY
    elif direction == RIGHT:
        moveX = blankX - 1
        moveY = blankY
    
    #prepare the base surface
    drawBoard(board, message)
    baseSurface = DISPLAY_SURFACE.copy()
    #draw a blank space over the moving tile on the baseSurface Surface
    moveLeft, moveTop = getLeftTopOfTile(moveX, moveY)
    pygame.draw.rect(baseSurface, BG_COLOR, (moveLeft, moveTop, TILE_SIZE, TILE_SIZE))
    
    for i in range(0, TILE_SIZE, animationSpeed):
        #animate the tile sliding over
        checkForQuit()
        DISPLAY_SURFACE.blit(baseSurface, (0, 0))
        if direction == UP:
            drawTile(moveX, moveY, board[moveX][moveY], 0, -i)
        if direction == DOWN:
            drawTile(moveX, moveY, board[moveX][moveY], 0, i)
        if direction == LEFT:
            drawTile(moveX, moveY, board[moveX][moveY], -i, 0)
        if direction == RIGHT:
            drawTile(moveX, moveY, board[moveX][moveY], i, 0)
            
        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def generateNewPuzzle(numSlides):
    #From a starting configuration, make numSlides number of moves (and animate these moves)
    sequence = []
    board = getStartingBoard()
    drawBoard(board, '')
    pygame.display.update()
    pygame.time.wait(500) #pause 500 milliseconds for effect
    lastMove = None
    for i in range(numSlides):
        move = getRandomMove(board, lastMove)
        slideAnimation(board, move, 'Generating new puzzle...', int(TILE_SIZE / 3))
        makeMove(board, move)
        sequence.append(move)
        lastMove = move
    return (board, sequence)


def resetAnimation(board, allMoves):
    #make all of the moves in allMoves in reverse
    reverseAllMoves = allMoves[:] #gets a copy of the list
    reverseAllMoves.reverse()
    
    for move in reverseAllMoves:
        if move == UP:
            oppositeMove = DOWN
        elif move == DOWN:
            oppositeMove = UP
        elif move == RIGHT:
            oppositeMove = LEFT
        elif move == LEFT:
            oppositeMove = RIGHT
        slideAnimation(board, oppositeMove, '', int(TILE_SIZE / 2))
        makeMove(board, oppositeMove)


if __name__ == '__main__':
    main()