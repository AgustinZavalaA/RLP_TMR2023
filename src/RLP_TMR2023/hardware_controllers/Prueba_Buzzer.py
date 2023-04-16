import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

BUZZER_PIN = 38  # Buzzer pin number

GPIO.setup(BUZZER_PIN, GPIO.OUT)

while True:
	duration=int(input("Ingrese la duracion: "))
	for i in range(duration):
		GPIO.output(BUZZER_PIN, GPIO.HIGH)
		time.sleep(1)
		GPIO.output(BUZZER_PIN, GPIO.LOW)
		time.sleep(1)