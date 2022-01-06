import simpleaudio
from io import BytesIO
from time import sleep, time

import numpy as np
import cv2
from picamera import PiCamera
import RPi.GPIO as GPIO
from google.cloud import vision

# constants for aim_face
x_servo_pin = 27
y_servo_pin = 17
# ratio_to_degree: camera angle of view / 2
ratio_to_degree = 130
controlable_angle = 70
min_duty = 3.7
max_duty = 10.7

# constants for fire
valve_pin = 15
button_pin = 23
valve_open_sec = 2.0
valve_close_sec = 1.0


def alarm():
    print('alarm')
    print('detecting faces')
    faces = face_detect()
    print('detecting faces done')

    if len(faces) == 0:
        print('face not detected')
        return

    width = faces[0]['width']
    height = faces[0]['height']
    target_x = (faces[0]['left_x'] + faces[0]['right_x']) // 2
    target_y = (faces[0]['up_y'] + faces[0]['down_y']) // 2
    print(f'target: ({target_x}, {target_y})')
    print(f'(width, height): ({width}, {height})')

    wave_obj = simpleaudio.WaveObject.from_wave_file('yukumo.wav')
    play_obj = wave_obj.play()
    print('playing')
    play_obj.wait_done()
    print('playing done')

    GPIO.setmode(GPIO.BCM)

    print('aiming')
    aim_face(width, height, target_x, target_y)
    print('aiming done')

    print('firing')
    fire()
    print('firing done')

    GPIO.cleanup()
    return


def face_detect():
    face_boundings = []
    client = vision.ImageAnnotatorClient()

    print('capturing started')
    content = BytesIO()
    camera = PiCamera()
    camera.start_preview()
    sleep(2)
    camera.capture(content, 'jpeg')
    print('capturing finished')
    camera.close()

    # create cv2 image object to draw boxes on
    content.seek(0)
    cv2image = cv2.imdecode(np.frombuffer(content.read(), np.uint8), 1)

    # create vision image object for vision API
    content.seek(0)
    image = vision.Image(content=content.read())

    response = client.face_detection(image=image)

    if response.error.message:
        raise Exception(response.error.message)

    print(f'{len(response.face_annotations)} faces')

    likelihood = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                  'LIKELY', 'VERY_LIKELY')

    for face in response.face_annotations:
        print(f'detection_confidence: {face.detection_confidence}')
        print(f'landmarking_confidence: {face.landmarking_confidence}')

        print(f'joy: {likelihood[face.joy_likelihood]}')
        print(f'sorrow: {likelihood[face.sorrow_likelihood]}')
        print(f'anger: {likelihood[face.anger_likelihood]}')
        print(f'surprise: {likelihood[face.surprise_likelihood]}')
        print(f'under_exposed: {likelihood[face.under_exposed_likelihood]}')
        print(f'blurred: {likelihood[face.blurred_likelihood]}')
        print(f'headwear: {likelihood[face.headwear_likelihood]}')

        # draw face bounding box
        pt1 = (
            face.bounding_poly.vertices[0].x,
            face.bounding_poly.vertices[0].y)
        pt2 = (
            face.bounding_poly.vertices[2].x,
            face.bounding_poly.vertices[2].y)
        cv2.rectangle(cv2image, pt1, pt2, (0, 255, 0), 2)

        # draw skin bounding box
        pt1 = (
            face.fd_bounding_poly.vertices[0].x,
            face.fd_bounding_poly.vertices[0].y)
        pt2 = (
            face.fd_bounding_poly.vertices[2].x,
            face.fd_bounding_poly.vertices[2].y)
        cv2.rectangle(cv2image, pt1, pt2, (0, 0, 255), 2)

        for landmark in face.landmarks:
            cv2.drawMarker(
                cv2image, (int(
                    landmark.position.x), int(
                    landmark.position.y)), (255, 0, 0))

        face_boundings.append({
            'left_x': pt1[0],
            'right_x': pt2[0],
            'up_y': pt1[1],
            'down_y': pt2[1],
            'width': cv2image.shape[1],
            'height': cv2image.shape[0],
            'confidence': face.detection_confidence
        })

    cv2.imwrite('vision.jpg', cv2image)
    return sorted(face_boundings, key=lambda x: x['confidence'], reverse=True)


def aim_face(width, height, target_x, target_y):
    # -1.0 to 1.0
    ratio_x = -1.0 * (target_x - width / 2) / (max(width, height) / 2)
    ratio_y = (target_y - height / 2) / (max(width, height) / 2)

    GPIO.setup(x_servo_pin, GPIO.OUT)
    GPIO.setup(y_servo_pin, GPIO.OUT)
    x_servo = GPIO.PWM(x_servo_pin, 50)
    y_servo = GPIO.PWM(y_servo_pin, 50)

    def degree_to_duty(x):
        return (min_duty + max_duty) / 2 + \
            (max_duty - min_duty) * x / controlable_angle

    x_servo.start(0.0)
    y_servo.start(0.0)
    print(f'control x_servo to {ratio_x}')
    print(f'x_servo duty {degree_to_duty(ratio_x * ratio_to_degree)}')
    sleep(0.2)
    x_servo.ChangeDutyCycle(degree_to_duty(ratio_x * ratio_to_degree))
    sleep(1.0)
    x_servo.ChangeDutyCycle(0.0)
    print(f'control y_servo to {ratio_y}')
    print(f'y_servo duty {degree_to_duty(ratio_y * ratio_to_degree)}')
    y_servo.ChangeDutyCycle(degree_to_duty(ratio_y * ratio_to_degree))
    sleep(1.0)
    y_servo.ChangeDutyCycle(0.0)
    sleep(0.2)
    x_servo.stop()
    y_servo.stop()


def fire():
    GPIO.setup(valve_pin, GPIO.OUT)
    GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def listening_while_sleep(sleep_time):
        start_time = time()
        while True:
            if time() - start_time > sleep_time:
                return False
            if not GPIO.input(button_pin):
                return True

    while True:
        GPIO.output(valve_pin, 1)
        if listening_while_sleep(valve_open_sec):
            break
        GPIO.output(valve_pin, 0)
        if listening_while_sleep(valve_close_sec):
            break


if __name__ == '__main__':
    alarm()
