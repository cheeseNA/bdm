import RPi.GPIO as GPIO
import time

pin = 15

GPIO.setmode(GPIO.BCM)

GPIO.setup(pin, GPIO.OUT)
print('setup')

try:
    while True:
        print('on')
        GPIO.output(pin, 1)
        time.sleep(1)
        print('off')
        GPIO.output(pin, 0)
        time.sleep(1)
finally:
    print('cleanup')
    GPIO.cleanup()
