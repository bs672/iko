#This is a test for hardware componenents. The test order is
#lights on, light ramp, refan, exhaust fan, intake fan, heat 

import time  # Library will let us put in delays
import RPi.GPIO as GPIO # Import the RPi Library for GPIO pin control
import pigpio

GPIO.setmode(GPIO.BCM) # We want to use the physical pin number scheme

LED1=12					#GPIO 12 (pin 32 on the PI zero)
REFAN_PIN=20
EXHAUST_PIN=15
INTAKE_PIN=14
HEAT_PIN=18

pi = pigpio.pi()

GPIO.setup(REFAN_PIN, GPIO.OUT)
GPIO.setup(EXHAUST_PIN, GPIO.OUT)
GPIO.setup(INTAKE_PIN, GPIO.OUT)
GPIO.setup(HEAT_PIN, GPIO.OUT)

#Turn lights on
pi.set_PWM_frequency(LED1, 1000)
pi.set_PWM_dutycycle(LED1, 0) #PWM off
time.sleep(0.25) #Briefly Pause

#ramp up brightness
bright=13                   # Set initial brightness to 5%

for bright in range(13, 153, 5):
	pi.set_PWM_dutycycle(LED1, bright)
	time.sleep(0.25) #Briefly Pause

#Turn re_fan on for 5 seconds then off
GPIO.output(REFAN_PIN, True)
time.sleep(5) #Briefly Pause
GPIO.output(REFAN_PIN, False)
time.sleep(0.25) #Briefly Pause

#Turn exhaust fan on for 5 seconds then off
GPIO.output(EXHAUST_PIN, True)
time.sleep(5) #Briefly Pause
GPIO.output(EXHAUST_PIN, False)
time.sleep(0.25) #Briefly Pause

#Turn intake fan on for 5 seconds then off
GPIO.output(INTAKE_PIN, True)
time.sleep(5) #Briefly Pause
GPIO.output(INTAKE_PIN, False)
time.sleep(0.25) #Briefly Pause

#Turn heat on for 5 seconds
GPIO.output(HEAT_PIN, True)
time.sleep(5) #Briefly Pause
GPIO.output(HEAT_PIN, False)
time.sleep(0.25) #Briefly Pause

#safe turn off
pi.set_PWM_dutycycle(LED1, 0)
GPIO.cleanup()
pi.stop()