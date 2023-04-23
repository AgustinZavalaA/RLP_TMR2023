import sys
import time

import RPi.GPIO as GPIO

triggerPIN = 38
GPIO.setmode(GPIO.BOARD)
GPIO.setup(triggerPIN, GPIO.OUT)

buzzer = GPIO.PWM(triggerPIN, 2000)  # Set frequency to 1 Khz
buzzer.start(0)  # Set dutycycle to 10
for i in range(0, 101, 10):
    buzzer.ChangeDutyCycle(i)
    time.sleep(1)

buzzer.stop()
GPIO.cleanup()
sys.exit()