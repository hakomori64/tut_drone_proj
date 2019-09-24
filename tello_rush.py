import tellopy
import cv2
import sys
import traceback
import av
import numpy
import os
import time
import math

def calculate_dist(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def get_closestface(faces, center_x, center_y):
    closest_face = None
    closest_dist = 1e10
    for (x, y, w, h) in faces:
        object_center_x = x + w // 2
        object_center_y = y + h // 2
        dist = calculate_dist(
            object_center_x,
            object_center_y,
            center_x,
            center_y
        )
        if dist < closest_dist:
            closest_face = (x, y, w, h)
            closest_dist = dist

        return closest_face


def main():
    drone = tellopy.Tello()
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    speed = 30


    try:
        drone.connect()
        drone.wait_for_connection(60.0)
        drone.takeoff()
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
                height, width, channels = image.shape
                center_x = width // 2
                center_y = height * 3 // 4
                faces = face_cascade.detectMultiScale(image, 1.1, 4)
                if len(faces) != 0:
                    face = get_closestface(faces, center_x, center_y)
                    (x, y, w, h) = face
                    cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)

                    x_diff = (x + w // 2) - center_x
                    y_diff = (y + h // 2) - center_y
                    if x_diff > 0:
                        drone.counter_clockwise(speed)
                    else:
                        drone.clockwise(speed)
                    if y_diff > 0:
                        drone.down(speed)
                    else:
                        drone.up(speed)

                else:
                    drone.counter_clockwise(speed)

                cv2.imshow("Face Detection", image)
                cv2.waitKey(1)

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
