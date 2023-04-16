import sys
import RPi.GPIO as GPIO
import time

triggerPIN = 38
GPIO.setmode(GPIO.BOARD)
GPIO.setup(triggerPIN,GPIO.OUT)

buzzer = GPIO.PWM(triggerPIN, 2000) # Set frequency to 1 Khz
buzzer.start(0) # Set dutycycle to 10
for i in range (0,100,10):

    buzzer.ChangeDutyCycle(10)
    time.sleep(1)

buzzer.stop()
GPIO.cleanup()
sys.exit()