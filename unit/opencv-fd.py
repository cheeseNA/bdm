import time
import picamera
import picamera.array
import cv2

image = False

print('capturing started')
with picamera.PiCamera() as camera:
    camera.start_preview()
    time.sleep(2)
    with picamera.array.PiRGBArray(camera) as stream:
        camera.capture(stream, format='bgr')
        image = stream.array
print('capturing finished')

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

print('detecting faces')
faces = face_cascade.detectMultiScale(gray, 1.3, 5)

print(f'{len(faces)} faces detected')
for (x, y, w, h) in faces:
    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

cv2.imwrite('opencv_face.jpeg', image)
