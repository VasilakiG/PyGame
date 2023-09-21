# Memory Puzzle
# By Al Sweigart al@inventwithpython
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys
from pygame.locals import *

FPS = 30 #frames per second
WINDOW_WIDTH = 640 #size of window's width in pixels
WINDOW_HEIGHT = 480 #size of window's height in pixels
REVEAL_SPEED = 8 #speed boxes' sliding reveals and covers
BOX_SIZE = 40 #size of box height & width in pixels
GAP_SIZE = 10 #size of gap between boxes in pixels
BOARD_WIDTH = 10 #number of columns of icons
BOARD_HEIGHT = 7 #number of rows of icons
assert (BOARD_WIDTH * BOARD_HEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.'
X_MARGIN = int((WINDOW_WIDTH - (BOARD_WIDTH * (BOX_SIZE + GAP_SIZE))) / 2)
Y_MARGIN = int((WINDOW_HEIGHT - (BOARD_HEIGHT * (BOX_SIZE + GAP_SIZE))) / 2)

#            R    G    B
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)

BG_COLOR = NAVYBLUE
LIGHT_BG_COLOR = GRAY
BOX_COLOR = WHITE
HIGHLIGHT_COLOR = BLUE

DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

ALL_COLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALL_SHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL)
assert len(ALL_COLORS) * len(ALL_SHAPES) * 2 >= BOARD_WIDTH * BOARD_HEIGHT, 'Board is too big for the number of shapes/colors defined.'

def main():
    global FPS_CLOCK, DISPLAY_SURFACE
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    mouse_x = 0 #used to store x coordinate of mouse event
    mouse_y = 0 #used to store y coordinate of mouse event
    pygame.display.set_caption('Memory Game')
    
    main_board = getRandomizedBoard()
    revealed_boxes = generateRevealedBoxesData(False)
    
    first_selection = None #stores the (x, y) of the first box clicked
    
    DISPLAY_SURFACE.fill(BG_COLOR)
    startGameAnimation(main_board)
    
    while True: #main game loop
        mouse_clicked = False
        
        DISPLAY_SURFACE.fill(BG_COLOR) #drawing the window
        drawBoard(main_board, revealed_boxes)
        
        for event in pygame.event.get(): #event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mouse_x, mouse_y = event.pos
            elif event.type == MOUSEBUTTONUP:
                mouse_x, mouse_y = event.pos
                mouse_clicked = True
                
        box_x, box_y = getBoxAtPixel(mouse_x, mouse_y)
        if box_x != None and box_y != None:
            #The mouse is currently over a box
            if not revealed_boxes[box_x][box_y]:
                drawHighlightBox(box_x, box_y)
            if not revealed_boxes[box_x][box_y] and mouse_clicked:
                revealBoxesAnimation(main_board, [(box_x, box_y)])
                revealed_boxes[box_x][box_y] = True #set the box as "revealed"
                if first_selection == None: # the current box was the first box clicked
                    first_selection = (box_x, box_y)
                else: #the current box was the second box clicked
                    #Check if there is a match between the two icons
                    icon1shape, icon1color = getShapeAndColor(main_board, first_selection[0], first_selection[1])
                    icon2shape, icon2color = getShapeAndColor(main_board, box_x, box_y)
                    
                    if icon1shape != icon2shape or icon1color != icon2color:
                        #Icons don't match. Re-cover up both selections
                        pygame.time.wait(1000) #1000 milliseconds = 1
                        coverBoxesAnimation(main_board, [(first_selection[0], first_selection[1]), (box_x, box_y)])
                        revealed_boxes[first_selection[0]][first_selection[1]] = False
                        revealed_boxes[box_x][box_y] = False
                    elif hasWon(revealed_boxes): #check if all pairs found
                        gameWonAnimation(main_board)
                        pygame.time.wait(2000)
                        
                        #Reset the board
                        main_board = getRandomizedBoard()
                        revealed_boxes = generateRevealedBoxesData(False)
                        
                        #Show the fully unrevealed board for a second
                        drawBoard(main_board, revealed_boxes)
                        pygame.display.update()
                        pygame.time.wait(1000)
                        
                        #Replay the start game animation
                        startGameAnimation(main_board)
                    first_selection = None #reset first_selection variable
                        
        #Redraw the screen and wait a clock tick
        pygame.display.update()
        FPS_CLOCK.tick(FPS)
        
        
def generateRevealedBoxesData(val):
    revealed_boxes = []
    for i in range (BOARD_WIDTH):
        revealed_boxes.append([val] * BOARD_HEIGHT)
    return revealed_boxes


def getRandomizedBoard():
    #Get a list of every possible shape in every possible color
    icons = []
    for color in ALL_COLORS:
        for shape in ALL_SHAPES:
            icons.append( (shape, color) )
            
    random.shuffle(icons) #randomize the order of the icons list
    numIconsUsed = int(BOARD_WIDTH * BOARD_HEIGHT / 2) #calculate how many icons are needed
    icons = icons[:numIconsUsed] * 2 #make two of each
    random.shuffle(icons)
    
    #Create the board data structure, with randomly placed icons
    board = []
    for x in range(BOARD_WIDTH):
        column = []
        for y in range(BOARD_HEIGHT):
            column.append(icons[0])
            del icons[0] #remove the icons as we assign them
        board.append(column)
    return board


def splitIntoGroupsOf(group_size, the_list):
    #splits a list into a list of lists, where the inner lists have at most group_size number of items
    result = []
    for i in range(0, len(the_list), group_size):
        result.append(the_list[i:i + group_size])
    return result


def leftTopCoordsOfBox(box_x, box_y):
    #Convert board coordinates to pixel coordinates
    left = box_x * (BOX_SIZE + GAP_SIZE) + X_MARGIN
    top = box_y * (BOX_SIZE + GAP_SIZE) + Y_MARGIN
    return (left, top)


def getBoxAtPixel(x, y):
    for box_x in range(BOARD_WIDTH):
        for box_y in range (BOARD_HEIGHT):
            left, top = leftTopCoordsOfBox(box_x, box_y)
            box_rect = pygame.Rect(left, top, BOX_SIZE, BOX_SIZE)
            if box_rect.collidepoint(x, y):
                return (box_x, box_y)
    return (None, None)


def drawIcon(shape, color, box_x, box_y):
    quarter = int(BOX_SIZE * 0.25) #syntactic sugar
    half    = int(BOX_SIZE * 0.5) #syntactic sugar
    
    left, top = leftTopCoordsOfBox(box_x, box_y) #get pixel coords from board coords
    #Draw the shapes
    if shape == DONUT:
        pygame.draw.circle(DISPLAY_SURFACE, color, (left + half, top + half), half - 5)
        pygame.draw.circle(DISPLAY_SURFACE, BG_COLOR, (left + half, top + half), quarter - 5)
    elif shape  == SQUARE:
        pygame.draw.rect(DISPLAY_SURFACE, color, (left + quarter, top + quarter, BOX_SIZE - half, BOX_SIZE - half))
    elif shape == DIAMOND:
        pygame.draw.polygon(DISPLAY_SURFACE, color, ((left + half, top), (left + BOX_SIZE - 1, top + half), (left + half, top + BOX_SIZE - 1), (left, top + half)))
    elif shape == LINES:
        for i in range(0, BOX_SIZE, 4):
            pygame.draw.line(DISPLAY_SURFACE, color, (left, top + i), (left + i, top))
            pygame.draw.line(DISPLAY_SURFACE, color, (left + i, top + BOX_SIZE - 1), (left + BOX_SIZE - 1, top + i))
    elif shape == OVAL:
        pygame.draw.ellipse(DISPLAY_SURFACE, color, (left, top + quarter, BOX_SIZE, half))
        
        
def getShapeAndColor(board, box_x, box_y):
    #shape value for x, y spot is stored in board[x][y][0]
    #color value for x, y spot is stored in board[x][y][1]
    return board[box_x][box_y][0], board[box_x][box_y][1]


def drawBoxCovers(board, boxes, coverage):
    #Draws boxes being covererd/revealed. "boxes" is a list of two-item lists, which have the x & y spot of the box
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAY_SURFACE, BG_COLOR, (left, top, BOX_SIZE, BOX_SIZE))
        shape, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(shape, color, box[0], box[1])
        if coverage > 0: #only draw the cover if there is an coverage
            pygame.draw.rect(DISPLAY_SURFACE, BOX_COLOR, (left, top, coverage, BOX_SIZE))
    pygame.display.update()
    FPS_CLOCK.tick(FPS)


def revealBoxesAnimation(board, boxesToReveal):
    #Do the "box reveal" animation
    for coverage in range(BOX_SIZE, (-REVEAL_SPEED) - 1, -REVEAL_SPEED):
        drawBoxCovers(board, boxesToReveal, coverage)


def coverBoxesAnimation(board, boxesToCover):
    #Do the "box cover" animation
    for coverage in range(0, BOX_SIZE + REVEAL_SPEED, REVEAL_SPEED):
        drawBoxCovers(board, boxesToCover, coverage)


def drawBoard(board, revealed):
    #Draws all of the boxes in their covered or revealed state
    for box_x in range(BOARD_WIDTH):
        for box_y in range(BOARD_HEIGHT):
            left, top = leftTopCoordsOfBox(box_x, box_y)
            if not revealed[box_x][box_y]:
                #Draw a covered box
                pygame.draw.rect(DISPLAY_SURFACE, BOX_COLOR, (left, top, BOX_SIZE, BOX_SIZE))
            else:
                #Draw the (revealed) icon
                shape, color = getShapeAndColor(board, box_x, box_y)
                drawIcon(shape, color, box_x, box_y)


def drawHighlightBox(box_x, box_y):
    left, top = leftTopCoordsOfBox(box_x, box_y)
    pygame.draw.rect(DISPLAY_SURFACE, HIGHLIGHT_COLOR, (left - 5, top - 5, BOX_SIZE + 10, BOX_SIZE + 10), 4)
    
    
def startGameAnimation(board):
    #Randomly reveal the boxes 8 at a time
    covered_boxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            boxes.append( (x, y) )
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8, boxes)
    
    drawBoard(board, covered_boxes)
    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)


def gameWonAnimation(board):
    #flash the background color when the player has won
    
    covered_boxes = generateRevealedBoxesData(True)
    color1 = LIGHT_BG_COLOR
    color2 = BG_COLOR
    
    for i in range(13):
        color1, color2 = color2, color1 #swap colors
        DISPLAY_SURFACE.fill(color1)
        drawBoard(board, covered_boxes)
        pygame.display.update()
        pygame.time.wait(300)
        
        
def hasWon(revealedBoxes):
    #Returns True if all the boxes have been revealed, otherwise False
    for i in revealedBoxes:
        if False in i:
            return False #return False if any boxes are covered
    return True


if __name__ == '__main__':
    main()