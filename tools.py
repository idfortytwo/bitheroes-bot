import time, sys, pyautogui, cv2

import numpy as np
from numpy import int64

THRESHOLD = 0.8


def get_template_location(source, template_filename):
    source_gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)

    template = cv2.imread(f'templates/{template_filename}', 0)
    w, h = template.shape[::-1]

    result = cv2.matchTemplate(source_gray, template, cv2.TM_CCOEFF_NORMED)
    location = np.where(result >= THRESHOLD)

    first_point = None
    for point in zip(*location[::-1]):
        first_point = point
        break

    if first_point is None:
        return None

    second_point = (first_point[0] + w, first_point[1] + h)

    # cv2.rectangle(source, first_point, second_point, (0,255,255), 2)
    # winname = f'{template_filename} on screen'
    # cv2.namedWindow(winname)
    # cv2.moveWindow(winname, 400, 400)
    # cv2.imshow(winname, source)
    # cv2.waitKey(0)

    return (first_point, second_point,)


def get_template_locations_list(source, template_filename):
    source_gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)

    template = cv2.imread(f'templates/{template_filename}', 0)
    w, h = template.shape[::-1]

    result = cv2.matchTemplate(source_gray, template, cv2.TM_CCOEFF_NORMED)
    location = np.where(result >= THRESHOLD)

    mmr = cv2.minMaxLoc(result)
    print(mmr[::-1])

    points = []
    for point in zip(*location[::-1]):
        print(f'POINT: {point}')
        first_point = point
        second_point = (first_point[0] + w, first_point[1] + h)
        points.append((first_point, second_point,))

    # cv2.rectangle(source, first_point, second_point, (0,255,255), 2)
    # winname = f'{template_filename} on screen'
    # cv2.namedWindow(winname)
    # cv2.moveWindow(winname, 400, 400)
    # cv2.imshow(winname, source)
    # cv2.waitKey(0)

    return points


def get_template_center_point(source, template_filename):
    location = get_template_location(source, template_filename)
    if location is None:
        return None
    center_point = get_center_point(location)
    return center_point


def get_center_point(location):
    try:
        first_point = location[0]
    except TypeError:
        print('not found')
        sys.exit(0)
    second_point = location[1]
    center_point = ((first_point[0] + second_point[0])/2, (first_point[1] + second_point[1])/2,)
    return center_point


def template_is_on_screen(source, template_filename):
    location = get_template_location(source, template_filename)
    if location:
        return True
    else:
        return False


def locate(screen, template_filename):
    needle_image = cv2.imread(f'templates/{template_filename}', 0)
    haystackImage=screen
    location = pyautogui.locate(needleImage=needle_image, haystackImage=screen)
    return location
