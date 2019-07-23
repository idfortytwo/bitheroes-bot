import pyautogui, cv2, sys, time, random, tools, queue
import numpy as np
from threading import Thread, Lock
from PIL import Image
from numpy import array

def get_frame(filename):
    lol_png = Image.open(f'{filename}.png')
    lol_frame = np.array(lol_png)
    lol_frame = cv2.cvtColor(lol_frame, cv2.COLOR_RGB2BGR)
    return lol_frame

def enough_shards(frame):
    crystal_bar = frame[53:80, 356:444]
    purple_pixel = np.array([130, 49, 162])
    if np.any(crystal_bar == purple_pixel):
        return True
    else:
        return False

def get_energy_coef(frame):
    green_pixel = np.array([44, 197, 136])
    dark_green_pixel = np.array([21, 133, 87])
    black_pixel = np.array([51, 50, 49])
    black, green = 0, 0

    energy_bar = frame[12:20, 439:518]
    for pixel in energy_bar[0]:
        if np.all(pixel == green_pixel) or np.all(pixel == dark_green_pixel):
            green += 1
        elif np.all(pixel == black_pixel):
            black += 1

    try:
        green_coef = green / (green + black) * 100
        return green_coef
    except ZeroDivisionError:
        cv2.imshow(None, energy_bar)
        cv2.waitKey(0)
        return None

def detect_dialogue(frame):
    corner_pixel = np.array([99, 91, 83])
    if (np.any(frame[207, 478] == corner_pixel) \
        and np.any(frame[207, 683] == corner_pixel)  \
        and np.any(frame[247, 478] == corner_pixel)  \
        and np.any(frame[247, 683] == corner_pixel)) \
    or (np.any(frame[207, 116] == corner_pixel)  \
        and np.any(frame[207, 322] == corner_pixel) \
        and np.any(frame[247, 116] == corner_pixel) \
        and np.any(frame[247, 322] == corner_pixel)):

        print('True')

def detect_cleared(frame):
    if np.any(frame[118, 260] == np.array([114, 173, 152])) and \
      np.any(frame[118, 535] == np.array([42, 162, 98])) and \
      np.any(frame[354, 238] == np.array([51, 51, 88])):
      # self.click_game(362, 326)

frame = get_frame('cleared')
detect_cleared(frame)
