import simpleaudio
from io import BytesIO
from time import sleep

import numpy as np
import cv2
from picamera import PiCamera
from google.cloud import vision


def alarm():
    print('alarm')
    wave_obj = simpleaudio.WaveObject.from_wave_file(
        '/usr/share/sounds/alsa/Front_Center.wav')
    play_obj = wave_obj.play()
    print('playing')
    play_obj.wait_done()
    print('playing done')

    print('detecting faces')
    faces = face_detect()
    print('detecting faces done')

    if len(faces) == 0:
        print('face not detected')
        return

    target_x = (faces[0]['left_x'] + faces[0]['right_x']) // 2
    target_y = (faces[0]['up_y'] + faces[0]['down_y']) // 2
    print(f'target: ({target_x}, {target_y})')


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
            'confidence': face.detection_confidence
        })

    cv2.imwrite('vision.jpg', cv2image)
    return sorted(face_boundings, key=lambda x: x['confidence'], reverse=True)


if __name__ == '__main__':
    alarm()
