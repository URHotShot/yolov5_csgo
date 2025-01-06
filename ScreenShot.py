import cv2
from mss import mss
import numpy

screenX = 1920
screenY = 1080
window_size = (
    int(screenX / 2 - 320),
    int(screenY / 2 - 320),
    int(screenX / 2 + 320),
    int(screenY / 2 + 320))
screenshot_value = mss()

def screenshot():
    img = screenshot_value.grab(window_size)
    img = numpy.array(img)
    img =cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    return img

