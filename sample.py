from time import sleep
from pynput.mouse import Listener, Button
from pynput import keyboard
from pynput.keyboard import Key
import tellopy
import cv2
import numpy


drone = tellopy.Tello()
drone.connect()
drone.wait_for_connection(60.0)

drone.takeoff()

def on_press(key):

    try:
        if key.char == 'g':
            drone.down(10)
        elif key.char == 'r':
            drone.up(10)
        elif key.char == 'h':
            drone.left(3)
        elif key.char == 'n':
            drone.right(3)
        elif key.char == 't':
            drone.backward(3)
        elif key.char == 'c':
            drone.forward(3)
        elif key.char == 'v':
            drone.clockwise(10)
        elif key.char == 'q':
            drone.down(50)
            sleep(5)
            drone.land()
            sleep(5)
            drone.quit()

    except AttributeError:
        print(key)

def on_release(key):
    pass

with keyboard.Listener(on_press=on_press, on_release=on_release) as key_listener:
    key_listener.join()