import cv2.cv2 as cv2
import sys

img = cv2.imread('dum.png')
while True:
    cv2.imshow('img', img)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == -1:
        print(key)
    else:
        print(key)