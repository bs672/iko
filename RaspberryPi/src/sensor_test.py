#report entire system sensor state including: tray, hres, mres and DHT

import RPi.GPIO as GPIO
import time
import Adafruit_DHT

GPIO.setmode(GPIO.BCM)

DHT_PIN=2
HRES_READ=5 
MRES_READ=19
TRAY_READ=27 

HRES_OUT=6 
MRES_OUT=13
TRAY_OUT=22 

GPIO.setup(DHT_PIN, GPIO.IN)
GPIO.setup(HRES_READ, GPIO.IN)
GPIO.setup(MRES_READ, GPIO.IN)
GPIO.setup(TRAY_READ, GPIO.IN)

GPIO.setup(HRES_OUT, GPIO.OUT)
GPIO.setup(MRES_OUT, GPIO.OUT)
GPIO.setup(TRAY_OUT, GPIO.OUT)

#GPIO.output(HEAT_PIN, True)
#GPIO.input(self.pin)

def tray_update():
		GPIO.output(TRAY_OUT, True)
		if (GPIO.input(TRAY_READ) == 0):
			#self.valve.set(1)
			GPIO.output(TRAY_OUT, False)
			#print("valve opened")
			return 0
		## If waterval > 10 and the valve is currently open
		#if (self.valve.get() == 1):
		#	self.valve.set(0)
		#	print("valve closed")
		
		if (GPIO.input(TRAY_READ) == 1):
			GPIO.output(TRAY_OUT, False)
			return 1

def reservoir_update():
	GPIO.output(HRES_OUT, True)
	GPIO.output(MRES_OUT, True)
	res = 0
	if (GPIO.input(HRES_READ) == 1):
		res = 2
	elif (GPIO.input(MRES_READ) == 1):
		res = 1		
	GPIO.output(HRES_OUT, False)
	GPIO.output(MRES_OUT, False)
	return res

def get_readings():
	humreading, tempreading = None, None
	reading_counter = 0
	while (humreading is None or tempreading is None) and reading_counter < 5:
		print("DHT reading")
		reading_counter = reading_counter + 1
		humreading, tempreading = Adafruit_DHT.read(Adafruit_DHT.DHT22, DHT_PIN)
	if (humreading is not None and tempreading is not None):
		humidity = humreading
		temperature = (tempreading*1.8) + 32 # converting to fahrenheit
		print("temperature: " + str(temperature))
		print("humidity: " + str(humidity))
		#return True
	else:
		print("DHT failed")
		#return False

k=0
while k<10:
	tray_level = tray_update()
	print("tray level: " + str(tray_level))
	water_level = reservoir_update()
	print("res level: " + str(water_level))
	get_readings()
	k+=1
	time.sleep(0.25)

GPIO.cleanup()
