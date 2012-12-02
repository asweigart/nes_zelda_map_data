
# Google image search for "nes zelda overworld" https://www.google.com/search?q=nes+zelda+overworld&oe=utf-8&aq=t&ie=UTF-8&hl=en&tbm=isch&source=og&sa=N&tab=wi
# Special thanks to Tartarus for collecting the room graphics: http://tartarus.rpgclassics.com/zelda1/1stquest/overworldhighyes.shtml
# and to Zephiel87 for the overworld tiles: http://spriters-resource.com/nes/thelegendofzelda/sheet/8375

# Note, the border and center of each room has a different palette, but I don't bother saving the palette info because it's not 1985 and we have enough memory these days.

"""
world is 16 x 8 rooms, 256 x 88 tiles (including half tiles), 4096 x 1344 pixels
rooms are 16 x 10.5 tiles, 256 x 168 pixels
tiles are 16 x 16 pixels (except bottom row which is 16 x 8)


World map colors:
['(32, 56, 236, 255)',      # OKAY blue
 '(252, 252, 252, 255)',    # OKAY white
 '(200, 76, 12, 255)',      # OKAY brown
 '(0, 168, 0, 255)',        # OKAY green
 '(116, 116, 116, 255)',    # OKAY gray
 '(252, 216, 168, 255)',    # OKAY tan
 '(0, 0, 0, 255)']          # OKAY black
"""

UNBLOCKED_TILES = ['00', '02', '06', '0c', '0e', '14', '18', '1a', '20', '24', '40', '4c', '53', '54', '55', '59', '5a', '5b', '5f', '60', '61', '67', '68', '69', '6d', '6e', '6f', '73', '74', '75', '7b', '7c', '7d', '81', '82', '83', '87', '88', '89', '8c', '8d', '8e', '8f', '91', '92', '93', '94', '95', '97', '98', '99', '9a', '9b', '9d']

import pygame, sys, os, pprint, time
from pygame.locals import *

pygame.init()
BASICFONT = pygame.font.Font('freesansbold.ttf', 12)

def getEachOverworldTileFromSpriteSheet():
    # load the individual tiles from overworldtiles.png
    overworldTiles = pygame.image.load('overworldtiles.png')

    allOverworldTiles = []

    i = 0
    for top in range(0, 8*17, 17):
        for left in range(0, 20*17, 17):
            tileSurf = pygame.Surface((16, 16))
            tileSurf.blit(overworldTiles, (0,0), (left + 1, top + 1, 16, 16))
            #pygame.image.save(tileSurf, '%s.png' % (i)) # uncomment to create the individual tile image files

            allOverworldTiles.append(tileSurf)
            i += 1
    return allOverworldTiles


def allRoomImages():
    for col in 'ABCDEFGHIJKLMNOP':
        for row in range(1, 9):
            roomImg = pygame.image.load(os.path.join('roomImages', '%s%s.png' % (row, col)))
            yield 'ABCDEFGHIJKLMNOP'.find(col), row - 1, roomImg


def allRoomTiles(roomImg):
    for x in range(16):
        for y in range(11):
            if y != 10:
                # not the bottom row
                tileHeight = 16
            else:
                # bottom row, where only the top half of the tile is shown
                tileHeight = 8
            img = pygame.Surface((16, tileHeight))
            img.blit(roomImg, (0,0), (x*16, y*16, 16, tileHeight))

            yield x, y, img, y == 10


def isSameImage(surfaceA, surfaceB):
    if surfaceA.get_size() != surfaceB.get_size():
        return False

    pixA = pygame.PixelArray(surfaceA)
    pixB = pygame.PixelArray(surfaceB)

    for x in range(surfaceA.get_width()):
        for y in range(surfaceB.get_height()):
            #print(pixA[x][y], pixB[x][y], surfaceA.unmap_rgb(pixA[x][y]), surfaceB.unmap_rgb(pixB[x][y]))
            #print(surfaceA.unmap_rgb(pixA[x][y]) == surfaceB.unmap_rgb(pixB[x][y]), surfaceA.unmap_rgb(pixA[x][y]), surfaceB.unmap_rgb(pixB[x][y]))
            if surfaceA.unmap_rgb(pixA[x][y]) != surfaceB.unmap_rgb(pixB[x][y]):
                return False
    return True

def stitchIntoOneWorldImage():
    # Combines all room images into a single image
    worldmap = pygame.Surface((4096,1344))
    for roomx, roomy, roomImg in allRoomImages():
        worldmap.blit(roomImg, (roomx*16*16, int(roomy*16*10.5)))
    pygame.image.save(worldmap, 'worldmap.png')



def listAllColorsInImage(img):
    # Grabs all the color values from the map
    colors = {}
    pix = pygame.PixelArray(img)
    for y in range(img.get_height()):
        for x in range(img.get_width()):
            c = str(img.unmap_rgb(pix[x][y]))
            if c not in colors:
                colors[c] = None
    pprint.pprint(list(colors.keys()))
    #['(206, 74, 8, 255)', '(32, 56, 236, 255)', '(252, 252, 252, 255)', '(189, 66, 0, 255)', '(200, 76, 12, 255)', '(0, 168, 0, 255)', '(116, 116, 116, 255)', '(255, 222, 173, 255)', '(32, 64, 192, 255)', '(192, 64, 0, 255)', '(33, 57, 239, 255)', '(252, 152, 56, 255)', '(252, 216, 168, 255)', '(224, 224, 128, 255)', '(216, 40, 0, 255)', '(0, 0, 0, 255)']

#listAllColorsInImage(pygame.image.load('worldmap_colorfixed.png'))



"""
LEFT OFF - replaced brown in spritesheet.
['(206, 74, 8, 255)',
 '(32, 56, 236, 255)',
 '(252, 252, 252, 255)',
 '(189, 66, 0, 255)',
 '(200, 76, 12, 255)',
 '(0, 168, 0, 255)',
 '(116, 116, 116, 255)',
 '(255, 222, 173, 255)',
 '(32, 64, 192, 255)',
 '(192, 64, 0, 255)',
 '(33, 57, 239, 255)',
 '(252, 152, 56, 255)',
 '(252, 216, 168, 255)',
 '(224, 224, 128, 255)',
 '(216, 40, 0, 255)',
 '(0, 0, 0, 255)']
 """

"""
'(0, 0, 0, 255)',       # black
'(0, 168, 0, 255)',     # green
'(32, 56, 236, 255)',   # blue
'(32, 64, 192, 255)',   # ???
'(33, 57, 239, 255)'    # ???
'(116, 116, 116, 255)', # gray
'(189, 66, 0, 255)',    # ??? brown?
'(192, 64, 0, 255)',    # brown
'(200, 76, 12, 255)',   # ??? brown?
'(206, 74, 8, 255)',    # ??? brown?
'(216, 40, 0, 255)',    # ??? brown?
'(224, 224, 128, 255)', # ??? tan?
'(252, 152, 56, 255)',  # ???
'(252, 216, 168, 255)', # tan
'(252, 252, 252, 255)', # white
'(255, 222, 173, 255)', # ??? tan?
"""



"""
BAD_COLORS = {  '(32, 64, 192, 255)':   (32, 56, 236),   # ??? blue
                '(33, 57, 239, 255)':   (32, 56, 236),    # ??? blue
                '(189, 66, 0, 255)':    (192, 64, 0),    # ??? brown?
                '(200, 76, 12, 255)':   (192, 64, 0),   # ??? brown?
                '(206, 74, 8, 255)':    (192, 64, 0),    # ??? brown?
                '(216, 40, 0, 255)':    (192, 64, 0),    # ??? brown?
                '(224, 224, 128, 255)': (252, 216, 168), # ??? tan?
                '(252, 152, 56, 255)':  (252, 216, 168),  # ??? tan?
                '(255, 222, 173, 255)': (252, 216, 168), # ??? tan?
              }

# Go through all the rooms and recolor any off color pixels
for roomx, roomy, roomImg in allRoomImages():
    pixelsChanged = False
    col = 'ABCDEFGHIJKLMNOP'[roomx]
    row = roomy + 1

    pix = pygame.PixelArray(roomImg)
    for x in range(roomImg.get_width()):
        for y in range(roomImg.get_height()):
            pixcolor = str(roomImg.unmap_rgb(pix[x][y]))
            if pixcolor in BAD_COLORS:
                pixelsChanged = True
                pix[x][y] = roomImg.map_rgb(BAD_COLORS[pixcolor])
    if pixelsChanged:
        #tempSurf = pix.make_surface()
        del pix
        #roomImg = tempSurf
        print('Changed %s %s' % (row, col))
        pygame.image.save( roomImg, os.path.join('roomImages', '%s%s_recolored.png' % (row, col)) )
"""


def tileCoordToPixelCoord(tilex, tiley):
    pixy = 0
    for ty in range(tiley):
        isBottomRow = (ty+1) % 11 == 0
        if isBottomRow:
            pixy += 8
        else:
            pixy += 16
    return tilex * 16, pixy


def generateMapData():
    tilesNotUsed = dict([(hex(x)[2:].rjust(2, '0'), None) for x in range(180)])

    allOverworldTiles = getEachOverworldTileFromSpriteSheet()

    mapData = [['..' for y in range(8 * 11)] for x in range(16 * 16)]
    unrecognizedNum = 0
    #DISPLAYSURF = pygame.display.set_mode((80, 80))
    worldImg = pygame.image.load('worldmap_colorfixed.png')
    labeledWorldImg = pygame.image.load('worldmap_colorfixed.png')

    for tilex in range(256):
        for tiley in range(88):
            px, py = tileCoordToPixelCoord(tilex, tiley)
            isBottomRow = (tiley+1) % 11 == 0

            if isBottomRow:
                # bottom row
                tileImg = pygame.Surface((16,8))
                tileImg.blit(worldImg, (0,0), (px, py, 16, 8))
            else:
                tileImg = pygame.Surface((16,16))
                tileImg.blit(worldImg, (0,0), (px, py, 16, 16))




            tileIdentified = False
            for tileIndex in range(len(allOverworldTiles)):
                currentOverworldTile = allOverworldTiles[tileIndex]

                if isBottomRow:
                    # cut tile in half
                    tempTile = pygame.Surface((16,8))
                    tempTile.blit(currentOverworldTile, (0,0), (0,0,16,8))
                    currentOverworldTile = tempTile

                if isSameImage(tileImg, currentOverworldTile):
                    tileIdentified = True
                    hexTileIndex = hex(tileIndex)[2:].rjust(2, '0')
                    mapData[tilex][tiley] = hexTileIndex

                    #print('Tile %s, %s in is tile number %s' % (tilex, tiley, tileIndex))
                    break

            if not tileIdentified:
                print("Couldn't ID tile %s, %s" % (tilex, tiley))
                #DISPLAYSURF.fill((0,0,0))
                #DISPLAYSURF.blit(tileImg, (0,0))
                #pygame.display.update()
                #time.sleep(5.5)
                pygame.image.save(tileImg, 'unrec\\unrecognizedTile_%s_%s_%s.png' % (unrecognizedNum, tilex, tiley))
                unrecognizedNum += 1
                #if unrecognizedNum > 10: sys.exit()
            else:
                if hexTileIndex in tilesNotUsed:
                    del tilesNotUsed[hexTileIndex]

                if int(hexTileIndex, 16) in (39, 58, 59, 78, 98, 99, 118, 138, 158):
                    print('Tile %s found at %s, %s' % (hexTileIndex, tilex,tiley))
                    text = BASICFONT.render(hexTileIndex, True, (255,0,255))
                    textRect = text.get_rect()
                    textRect.topleft = (px, py)
                    labeledWorldImg.blit(text, textRect)



    fp = open('nes_zelda_overworld_tile_map.txt', 'w')
    for y in range(len(mapData[0])):
        for x in range(len(mapData)):
            fp.write(' ' + mapData[x][y])
        fp.write('\n')
    fp.close()

    fp = open('nes_zelda_overworld_blocking_map.txt', 'w')
    for y in range(len(mapData[0])):
        for x in range(len(mapData)):
            fp.write((mapData[x][y] in UNBLOCKED_TILES) and '.' or 'X')
        fp.write('\n')
    fp.close()

    pygame.image.save(labeledWorldImg, 'labeled_map.png')
    #print('Tiles not used: %s' % ([int(i, 16) for i in list(tilesNotUsed.keys())]))


def makeLabeledOverworldTilesImage():
    map = pygame.image.load('overworldtiles.png')
    tileIndex = 0
    for tiley in range(0, 8*17, 17):
        for tilex in range(0, 20*17, 17):
            text = BASICFONT.render(hex(tileIndex)[2:].rjust(2, '0'), True, (255,0,255))
            textRect = text.get_rect()
            textRect.topleft = (tilex, tiley)
            map.blit(text,textRect)
            tileIndex += 1
    pygame.image.save(map, 'labeled_overworld_tiles.png')


generateMapData()


"""
Just in case I lose the data, here's the overworldtiles.png file in base64 encoding:

The md5 of the file is 1e357d56acaad8a98699f858dbba8abe and the sha1 of the file is 383601f579bbe685f4da640e5c206d93a15e9a01

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
"""