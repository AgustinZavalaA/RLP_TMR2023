import sys
import RPi.GPIO as GPIO
import time

triggerPIN = 38
GPIO.setmode(GPIO.BOARD)
GPIO.setup(triggerPIN,GPIO.OUT)

buzzer = GPIO.PWM(triggerPIN, 1000) # Set frequency to 1 Khz
buzzer.start(10) # Set dutycycle to 10

time.sleep(1)
GPIO.cleanup()
sys.exit()
