#This file will run on a continuous loop, posting image data to the runestory assistant api every so often
#It is meant to provide up to date images for top players/guilds in vanguard over the course of it running
#Since conquest and vanguard take up the same space in the game, this only needs to be ran once per server (WEST, EAST, etc.)

#The current flow should be this:
#0: initial state is the "my guild" tab
#1: center mouse to initial position (center of "Ranking" tab)
#2: click banner
#3: capture image (this results in the image for the individual 1-3 spots)
#4: move mouse to bottom of the top 3 results
#5: initiate left click
#6: drag up by specific amount, and release click
#7: move mouse to "guild" position
#8: capture image (this results in the image for the individual 4-6 spots)
#9: click mouse (should already be on "guild"). This effectively changes to the guild rankings
#10: capture image (this results in the image for the guild ranking 1-3 spots)
#11: move mouse to bottom of the top 3 results
#12: initiate left click
#13: drag up by specific amount, and release click
#14: move mouse to "my guild" position (the initial position)
#15: capture image (this results in the image for the guild ranking 4-6 spots)
#16: click (to effectively put onself back into the initial state)

import time
import ctypes
from autopy import mouse
import requests
import os
import json
import pyscreenshot as ImageGrab
import cStringIO
import base64

#Poor mans configuration: This is based on a resolution of 1920x1028 monitor, with bluestacks fullscreen
MY_GUILD_TAB = (809, 244) #in pixels, x,y
RANKING_TAB = (956, 244) #in pixels, x,y
SCROLL_START = (951, 906) #in pixels, x,y
SCROLL_END = (951, 460) #in pixels, x,y
GUILD_BUTTON = (809, 460) #in pixels, x,y
IMAGE_TL = (704, 248) #in pixels, x,y, represents top left of image rectangle
IMAGE_BR = (1202, 925) #in pixels, x,y, represents bottom right of image rectangle

POST_DATA_ENDPOINT = "%s/api/competitive_standings.json" % os.environ["RUNESTORY_ASSISTANT_API"]

TIME_BETWEEN_RUNS = 5 #interval at which the process will run, in seconds

RS_SERVER = "WEST" #The game server(s) which are being monitored

OS = "WINDOWS" #what os is being used, to handle mouse controlling effectively

def leftClickStart():
    mouse.toggle(True)

def leftClickEnd():
    mouse.toggle(False)

def leftClick():
    mouse.click()
    return

def moveMouse(point):
    mouse.smooth_move(point[0], point[1])

def captureImageAsBase64Str(tl, br):
    im = ImageGrab.grab(bbox=(tl[0], tl[1], br[0], br[1]))
    pngBuffer = cStringIO.StringIO()
    im.save(pngBuffer, format="PNG")
    imgStr = base64.b64encode(pngBuffer.getvalue())
    pngBuffer.close()
    return imgStr

def saveResults(personalFirst, personalSecond, guildFirst, guildSecond, server):
    print "Saving results..."
    payload = {
                'server': server,
                'personal_first_image': personalFirst,
                'personal_second_image': personalSecond,
                'guild_first_image': guildFirst,
                'guild_second_image': guildSecond,
            }

    r = requests.post(POST_DATA_ENDPOINT, json=payload)

def run():
    print "starting job..."
    moveMouse(MY_GUILD_TAB)
    moveMouse(RANKING_TAB)
    leftClick()
    time.sleep(4)
    personalRankingImageFirst = captureImageAsBase64Str(IMAGE_TL, IMAGE_BR)

    moveMouse(SCROLL_START)
    leftClickStart()
    moveMouse(SCROLL_END)
    leftClickEnd()
    time.sleep(1)
    moveMouse(GUILD_BUTTON)
    personalRankingImageSecond = captureImageAsBase64Str(IMAGE_TL, IMAGE_BR)

    leftClick()
    time.sleep(4)
    guildRankingImageFirst = captureImageAsBase64Str(IMAGE_TL, IMAGE_BR)

    moveMouse(SCROLL_START)
    leftClickStart()
    moveMouse(SCROLL_END)
    leftClickEnd()

    moveMouse(MY_GUILD_TAB)
    time.sleep(1)
    guildRankingImageSecond = captureImageAsBase64Str(IMAGE_TL, IMAGE_BR)
    leftClick()
    saveResults(personalRankingImageFirst, personalRankingImageSecond, guildRankingImageFirst, guildRankingImageSecond, RS_SERVER)

if __name__ == '__main__':
    while True: #poor mans scheduling
        run()
        # saveResults("1", "2", "3", "4", RS_SERVER)
        print "sleeping..."
        time.sleep(TIME_BETWEEN_RUNS)
        # print mouse.get_pos() #for testing cursor position
        # time.sleep(.1)


# # Testing only, works on windows only
# from ctypes import windll, Structure, c_ulong, byref
#
# class POINT(Structure):
#     _fields_ = [("x", c_ulong), ("y", c_ulong)]
#
# def queryMousePosition():
#     pt = POINT()
#     windll.user32.GetCursorPos(byref(pt))
#     return { "x": pt.x, "y": pt.y}
#
# def printCursorPos():
#     print "cursor position: %s" % queryMousePosition()
