import RPi.GPIO as GPIO
import time

xpin = 17
ypin = 27

GPIO.setmode(GPIO.BCM)

GPIO.setup(xpin, GPIO.OUT)
GPIO.setup(ypin, GPIO.OUT)
print('setup')

xservo = GPIO.PWM(xpin, 50)
xservo.start(0.0)
yservo = GPIO.PWM(ypin, 50)
yservo.start(0.0)

try:
    while True:
        high = float(input('servo duty ratio: '))
        xservo.ChangeDutyCycle(high)
        yservo.ChangeDutyCycle(high)
        time.sleep(0.5)
        xservo.ChangeDutyCycle(0.0)
        yservo.ChangeDutyCycle(0.0)
finally:
    xservo.stop()
    yservo.stop()
    print('cleanup')
    GPIO.cleanup()
