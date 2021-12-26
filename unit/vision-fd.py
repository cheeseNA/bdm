from io import BytesIO
from time import sleep

import numpy as np
import cv2
from picamera import PiCamera
from google.cloud import vision

client = vision.ImageAnnotatorClient()

print('capturing started')
content = BytesIO()
camera = PiCamera()
camera.start_preview()
sleep(2)
camera.capture(content, 'jpeg')
print('capturing finished')

content.seek(0)
cv2image = cv2.imdecode(np.frombuffer(content.read(), np.uint8), 1)

content.seek(0)
image = vision.Image(content=content.read())

response = client.face_detection(image=image)

if response.error.message:
    raise Exception(response.error.message)

print(f'{len(response.face_annotations)} faces')

likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                   'LIKELY', 'VERY_LIKELY')

for face in response.face_annotations:
    print(f'detection_confidence: {face.detection_confidence}')
    print(f'landmarking_confidence: {face.landmarking_confidence}')

    print(f'joy_likelihood: {likelihood_name[face.joy_likelihood]}')
    print(f'sorrow_likelihood: {likelihood_name[face.sorrow_likelihood]}')
    print(f'.anger_likelihood: {likelihood_name[face.anger_likelihood]}')
    print(f'surprise_likelihood: {likelihood_name[face.surprise_likelihood]}')
    print(
        'under_exposed_likelihood: '
        f'{likelihood_name[face.under_exposed_likelihood]}')
    print(f'blurred_likelihood: {likelihood_name[face.blurred_likelihood]}')
    print(f'headwear_likelihood: {likelihood_name[face.headwear_likelihood]}')

    pt1 = (face.bounding_poly.vertices[0].x, face.bounding_poly.vertices[0].y)
    pt2 = (face.bounding_poly.vertices[2].x, face.bounding_poly.vertices[2].y)
    cv2.rectangle(cv2image, pt1, pt2, (0, 255, 0), 2)

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

cv2.imwrite('vision.jpg', cv2image)
