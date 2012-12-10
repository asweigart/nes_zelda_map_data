import pygame, sys, os, pprint, time, pyganim
from pygame.locals import *

"""
world is 16 x 8 rooms, 256 x 88 tiles (including half tiles), 4096 x 1344 pixels
rooms are 16 x 10.5 tiles, 256 x 168 pixels
tiles are 16 x 16 pixels (except bottom row which is 16 x 8)

World map colors:
['(32, 56, 236, 255)',      # blue
 '(252, 252, 252, 255)',    # white
 '(200, 76, 12, 255)',      # brown
 '(0, 168, 0, 255)',        # green
 '(116, 116, 116, 255)',    # gray
 '(252, 216, 168, 255)',    # tan
 '(0, 0, 0, 255)']          # black
"""

pygame.init()


mainClock = pygame.time.Clock()

ROOM_WIDTH = 256 # size of a single "room" in pixels
ROOM_HEIGHT = 168

WINDOW_MAGNIFICATION = 3 # each pixel will be enlarged by this many times before being drawn on the screen (must be an int)

LEFT, RIGHT, UP, DOWN = 'left right up down'.split() # constants
WALKRATE = 3 # how many pixels to move while walking per frame
ANIMRATE = 0.15 # how many seconds each frame of link's walking animation lasts

WINDOW_WIDTH, WINDOW_HEIGHT = ROOM_WIDTH * WINDOW_MAGNIFICATION, ROOM_HEIGHT * WINDOW_MAGNIFICATION

DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('NES Zelda Walking Tour')

CAMERA_LEFT, CAMERA_TOP = ROOM_WIDTH * 7, ROOM_HEIGHT * 7 # Where on the map the left, top of the camera is. Starts at the (7, 7) room.
LINK_LEFT, LINK_TOP = CAMERA_LEFT + (7*16 + 8), CAMERA_TOP + (5*16) # link's current (left, top) position in map pixels
LINK_WIDTH, LINK_HEIGHT = 16, 16 # constants

# Set up Link walking animation:
# load each image for the animation frames
down1 = pygame.image.load('link_down1.png')
down2 = pygame.image.load('link_down2.png')
up1   = pygame.image.load('link_up1.png')
up2   = pygame.image.load('link_up2.png')
left1 = pygame.image.load('link_left1.png')
left2 = pygame.image.load('link_left2.png')

# creating the PygAnimation objects for walking in all directions
walkingAnim = {}
walkingAnim[DOWN] = pyganim.PygAnimation(((down1, ANIMRATE), (down2, ANIMRATE)))
walkingAnim[UP]   = pyganim.PygAnimation(((up1, ANIMRATE), (up2, ANIMRATE)))
walkingAnim[LEFT] = pyganim.PygAnimation(((left1, ANIMRATE), (left2, ANIMRATE)))

# create the right-facing sprites by copying and flipping the left-facing sprites
walkingAnim[RIGHT] = walkingAnim[LEFT].getCopy()
walkingAnim[RIGHT].flip(True, False)
walkingAnim[RIGHT].makeTransformsPermanent()

# resize the Link images to match the window's magnification
for i in (UP, DOWN, LEFT, RIGHT):
    walkingAnim[i].scale((LINK_WIDTH * WINDOW_MAGNIFICATION, LINK_HEIGHT * WINDOW_MAGNIFICATION))
    walkingAnim[i].makeTransformsPermanent()

# The PygConductor object keeps the animations of each direction in sync
animConductor = pyganim.PygConductor(walkingAnim)


def loadOverworldTiles():
    # Create individual tiles for each tile in overworldtiles.png
    # The returned dictionary has keys of two-digit hex numbers.

    """
    The overworldtiles.png file's hex keys looks like this:
    00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f 10 11
    12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f 20 21 22 23
    24 25 26 27 28 29 2a 2b 2c 2d 2e 2f 30 31 32 33 34 35
    36 37 38 39 3a 3b 3c 3d 3e 3f 40 41 42 43 44 45 46 47
    48 49 4a 4b 4c 4d 4e 4f 50 51 52 53 54 55 56 57 58 59
    5a 5b 5c 5d 5e 5f 60 61 62 63 64 65 66 67 68 69 6a 6b
    6c 6d 6e 6f 70 71 72 73 74 75 76 77 78 79 7a 7b 7c 7d
    7e 7f 80 81 82 83 84 85 86 87 88 89 8a 8b 8c 8d 8e 8f

    So tile 00 is the brown stairs at the top left of overworldtiles.png and
    tile 1f is the white gravestone tile.

    So the allOverworldTiles dict will be like:
    {'00': <pygame Surface of brown stairs tile>,
     '01': <pygame Surface of brow rock tile>,
     etc.
    }
    """
    tilesImg = pygame.image.load(os.path.join('overworld_map', 'overworldtiles.png'))
    allOverworldTiles = {}
    i = 0 # the first tile number is 0
    for top in range(0, 8*17, 17):
        for left in range(0, 20*17, 17):
            tileSurf = pygame.Surface((16, 16))
            tileSurf.blit(tilesImg, (0,0), (left + 1, top + 1, 16, 16))
            allOverworldTiles[hex(i)[2:].rjust(2, '0')] = tileSurf
            i += 1
    return allOverworldTiles


def loadMapData():
    # Returns a 2D list of list, where mapData[x][y] stores the two-digit hex
    # number of the tile for that location.
    # mapData[0][0] is the topmost, leftmost tile on the world map
    fp = open(os.path.join('overworld_map', 'nes_zelda_overworld_tile_map.txt'))
    content = fp.read()
    fp.close()

    content = content.split('\n')
    content = [line.split(' ') for line in content]

    # invert the xy
    mapData = [[] for i in range(len(content[0]))]
    for y in range(len(content)):
        for x in range(len(content[y])):
            mapData[x].append(content[y][x])

    return mapData


def getRoomSurface(leftPixel, topPixel, mapData, tileData):
    # returns a single 256 x 168 pixel Surface of 16 x 10.5 tiles (since this is a standard zelda room size)
    leftmostTile = leftPixel // 16
    topmostTile = ((topPixel // 168) * 11) + ((topPixel % 168) // 16)
    roomSurf = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT))

    for tiley in range(topmostTile, topmostTile + 11):
        for tilex in range(leftmostTile, leftmostTile + 16):
            roomSurf.blit(tileData[mapData[tilex][tiley]], ((tilex - leftmostTile) * 16, (tiley - topmostTile) * 16))
    roomSurf = pygame.transform.scale(roomSurf, (ROOM_WIDTH * WINDOW_MAGNIFICATION, ROOM_HEIGHT * WINDOW_MAGNIFICATION))
    return roomSurf

def slideRoomAnimation(slideDirection, mapData, tileData):
    global CAMERA_LEFT, CAMERA_TOP, LINK_LEFT, LINK_TOP

    # get the pygame Surface object of the room link is moving into
    # (and adjust link's position a little bit towards the new room)
    if slideDirection == UP:
        nextRoomLeft, nextRoomTop = CAMERA_LEFT, CAMERA_TOP + (ROOM_HEIGHT)
        LINK_TOP += LINK_HEIGHT // 2
    if slideDirection == DOWN:
        nextRoomLeft, nextRoomTop = CAMERA_LEFT, CAMERA_TOP - (ROOM_HEIGHT)
        LINK_TOP -= LINK_HEIGHT // 2
    if slideDirection == LEFT:
        nextRoomLeft, nextRoomTop = CAMERA_LEFT + (ROOM_WIDTH), CAMERA_TOP
        LINK_LEFT += LINK_WIDTH // 2
    if slideDirection == RIGHT:
        nextRoomLeft, nextRoomTop = CAMERA_LEFT - (ROOM_WIDTH), CAMERA_TOP
        LINK_LEFT -= LINK_WIDTH // 2

    nextRoomSurf = getRoomSurface(nextRoomLeft, nextRoomTop, mapData, tileData)
    curRoomSurf = getRoomSurface(CAMERA_LEFT, CAMERA_TOP, mapData, tileData)

    # perform the slide animation by drawing both room images on the window:
    if slideDirection == UP:
        for sliding in range(0, ROOM_HEIGHT * WINDOW_MAGNIFICATION, WINDOW_MAGNIFICATION):
            DISPLAYSURF.blit(curRoomSurf, (0, -sliding))
            DISPLAYSURF.blit(nextRoomSurf, (0, ROOM_HEIGHT * WINDOW_MAGNIFICATION - sliding))
            pygame.display.update()
            mainClock.tick()
        CAMERA_TOP += ROOM_HEIGHT
    elif slideDirection == DOWN:
        for sliding in range(0, ROOM_HEIGHT * WINDOW_MAGNIFICATION, WINDOW_MAGNIFICATION):
            DISPLAYSURF.blit(curRoomSurf, (0, sliding))
            DISPLAYSURF.blit(nextRoomSurf, (0, -ROOM_HEIGHT * WINDOW_MAGNIFICATION + sliding))
            pygame.display.update()
            mainClock.tick()
        CAMERA_TOP -= ROOM_HEIGHT
    elif slideDirection == LEFT:
        for sliding in range(0, ROOM_WIDTH * WINDOW_MAGNIFICATION, WINDOW_MAGNIFICATION):
            DISPLAYSURF.blit(curRoomSurf, (-sliding, 0))
            DISPLAYSURF.blit(nextRoomSurf, (ROOM_WIDTH * WINDOW_MAGNIFICATION - sliding, 0))
            pygame.display.update()
            mainClock.tick()
        CAMERA_LEFT += ROOM_WIDTH
    elif slideDirection == RIGHT:
        for sliding in range(0, ROOM_WIDTH * WINDOW_MAGNIFICATION, WINDOW_MAGNIFICATION):
            DISPLAYSURF.blit(curRoomSurf, (sliding, 0))
            DISPLAYSURF.blit(nextRoomSurf, (-ROOM_WIDTH * WINDOW_MAGNIFICATION + sliding, 0))
            pygame.display.update()
            mainClock.tick()
        CAMERA_LEFT -= ROOM_WIDTH



def main():
    global LINK_LEFT, LINK_TOP, CAMERA_LEFT, CAMERA_TOP

    mapData = loadMapData()
    tileData = loadOverworldTiles()

    leftKeyPressed = rightKeyPressed = upKeyPressed = downKeyPressed = False
    DIRECTION = UP

    while True:
        DISPLAYSURF.fill((255,0,255)) # this purple will show up really bright to point out any undrawn areas, but if everything is working you should never see it
        for event in pygame.event.get(): # event handling loop

            # handle ending the program
            if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    upKeyPressed = True
                    DIRECTION = UP
                elif event.key == K_DOWN:
                    downKeyPressed = True
                    DIRECTION = DOWN
                elif event.key == K_LEFT:
                    leftKeyPressed = True
                    DIRECTION = LEFT
                elif event.key == K_RIGHT:
                    rightKeyPressed = True
                    DIRECTION = RIGHT

            elif event.type == KEYUP:
                if event.key == K_UP:
                    upKeyPressed = False
                elif event.key == K_DOWN:
                    downKeyPressed = False
                elif event.key == K_LEFT:
                    leftKeyPressed = False
                elif event.key == K_RIGHT:
                    rightKeyPressed = False

        if upKeyPressed or downKeyPressed or leftKeyPressed or rightKeyPressed:
            # let PygAnim draw the correct walking sprite from the animation object
            animConductor.play() # calling play() while the animation objects are already playing is okay; in that case play() is a no-op

            # actually move the position of the player
            if DIRECTION == UP:
                LINK_TOP -= WALKRATE
            if DIRECTION == DOWN:
                LINK_TOP += WALKRATE
            if DIRECTION == LEFT:
                LINK_LEFT -= WALKRATE
            if DIRECTION == RIGHT:
                LINK_LEFT += WALKRATE

        else:
            # Link is not moving, so pause the walking animation
            animConductor.pause()

        # draw the current room to the window
        roomSurf = getRoomSurface(CAMERA_LEFT, CAMERA_TOP, mapData, tileData)
        DISPLAYSURF.blit(roomSurf, (0,0))

        # calculate link's position on the screen
        onScreenLINK_LEFT = (LINK_LEFT - CAMERA_LEFT) * WINDOW_MAGNIFICATION
        onScreenLINK_TOP = (LINK_TOP - CAMERA_TOP) * WINDOW_MAGNIFICATION

        # if link has moved off the edge of the screen
        didSlide = False
        if onScreenLINK_LEFT < -(LINK_WIDTH // 2):
            slideRoomAnimation(RIGHT, mapData, tileData)
            didSlide = True
        if onScreenLINK_LEFT + LINK_WIDTH > WINDOW_WIDTH - LINK_WIDTH + (LINK_WIDTH // 2):
            slideRoomAnimation(LEFT, mapData, tileData)
            didSlide = True
        if onScreenLINK_TOP < -(LINK_HEIGHT // 2):
            slideRoomAnimation(DOWN, mapData, tileData)
            didSlide = True
        if onScreenLINK_TOP + LINK_HEIGHT > WINDOW_HEIGHT - LINK_HEIGHT + (LINK_HEIGHT // 2):
            slideRoomAnimation(UP, mapData, tileData)
            didSlide = True

        if didSlide:
            # if Link slid into a new room, recalculate his "on screen" position
            onScreenLINK_LEFT = (LINK_LEFT - CAMERA_LEFT) * WINDOW_MAGNIFICATION
            onScreenLINK_TOP = (LINK_TOP - CAMERA_TOP) * WINDOW_MAGNIFICATION

        # draw link on the screen
        if DIRECTION == UP:
            walkingAnim[UP].blit(DISPLAYSURF, (onScreenLINK_LEFT, onScreenLINK_TOP))
        elif DIRECTION == DOWN:
            walkingAnim[DOWN].blit(DISPLAYSURF, (onScreenLINK_LEFT, onScreenLINK_TOP))
        elif DIRECTION == LEFT:
            walkingAnim[LEFT].blit(DISPLAYSURF, (onScreenLINK_LEFT, onScreenLINK_TOP))
        elif DIRECTION == RIGHT:
            walkingAnim[RIGHT].blit(DISPLAYSURF, (onScreenLINK_LEFT, onScreenLINK_TOP))

        # do the actual screen update
        pygame.display.update()
        mainClock.tick(30)

if __name__ == '__main__':
    main()