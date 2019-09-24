import sys
import traceback
import tellopy
import av
import cv2
import numpy
import time
import os
from subprocess import Popen, PIPE
from keybuffer import KeyBuffer

video_player = None
video_flight_data = None
video_recorder = None
font = None
wid = None
date_fmt = "%Y-%m-%d_%H%m%S"

def take_picture(drone, speed):
    if speed == 0:
        return
    drone.take_picture()

controls = {
    46: 'forward',
    101: 'backward',
    111: 'left',
    117: 'right',
    32: 'up',
    225: 'down',
    226: 'down',
    44: 'counter_clockwise',
    112: 'clockwise',
    9: lambda drone, speed: drone.takeoff(),
    8: lambda drone, speed: drone.land(),
    13: take_picture,
}

def main():
    drone = tellopy.Tello()
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    speed = 30
    queue_size = 20
    key_buffer = KeyBuffer(queue_size)

    try:
        drone.connect()
        drone.wait_for_connection(60.0)

        retry = 3
        container = None
        while container is None and 0 < retry:
            retry -= 1
            try:
                container = av.open(drone.get_video_stream())
            except av.AVError as ave:
                print(ave)
                print('retry...')

        frame_skip = 300
        key_handler = None
        while True:
            for frame in container.decode(video=0):
                if 0 < frame_skip:
                    frame_skip = frame_skip - 1
                    continue
                
                start_time = time.time()

                image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
                faces = face_cascade.detectMultiScale(image, 1.1, 4)
                for (x, y, w, h) in faces:
                    cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)

                cv2.imshow('Face Detection', image)
                key = cv2.waitKey(100)
                key_buffer.push(key)
                key = key_buffer.get_pressed_key() or -1
                if key == 27:
                    drone.land()
                    drone.quit()
                    exit(0)
                elif key in controls.keys():
                    key_handler_name = controls[key]
                    if type(key_handler_name) == str:
                        key_handler = getattr(drone, key_handler_name)
                        key_handler(speed)
                    else:
                        key_handler_name(drone, speed)
                else:
                    if key_handler is not None:
                        key_handler(0)

                if frame.time_base < 1.0/60:
                    time_base = 1.0/60
                else:
                    time_base = frame.time_base

                frame_skip = int((time.time() - start_time) / time_base)
            

    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print(ex)
    finally:
        drone.quit()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
