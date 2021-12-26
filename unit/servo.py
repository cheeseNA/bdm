import RPi.GPIO as GPIO
import time

pin = 17

GPIO.setmode(GPIO.BCM)

GPIO.setup(pin, GPIO.OUT)
print('setup')

servo = GPIO.PWM(pin, 50)
servo.start(0.0)

try:
    while True:
        high = float(input('servo duty ratio: '))
        servo.ChangeDutyCycle(high)
        time.sleep(0.5)
        servo.ChangeDutyCycle(0.0)
finally:
    servo.stop()
    print('cleanup')
    GPIO.cleanup()
