# PIN SETUP FOR A SINGLE TIER

import RPi.GPIO as GPIO

# output pins in GPIO
outputs = []
INTAKE_FAN = 14; outputs.append(INTAKE_FAN)
EXHAUST_FAN = 15; outputs.append(EXHAUST_FAN) # RXD
RE_FAN = 20; outputs.append(RE_FAN)
HEAT_PIN = 18; outputs.append(HEAT_PIN)
VALVE_PIN = 25; outputs.append(VALVE_PIN)
LED_HIGH = 12; outputs.append(LED_HIGH)
LED_DIM = 23; outputs.append(LED_DIM)
BUTTON_OUT = 10; outputs.append(BUTTON_OUT) # always high, gp21 is the read pin
HRES_OUT = 6; outputs.append(HRES_OUT)
MRES_OUT = 13; outputs.append(MRES_OUT)
TRAY_OUT = 22; outputs.append(TRAY_OUT)
# input pins in GPIO
inputs = []
BUTTON_IN = 21; inputs.append(BUTTON_IN)
DHT_PIN = 2; inputs.append(DHT_PIN)
HRES_READ = 5; inputs.append(HRES_READ)
MRES_READ = 19; inputs.append(MRES_READ)
TRAY_READ = 27; inputs.append(TRAY_READ)
dict = {}

class Pin(GPIO.PWM):
	def __init__(self,pin,pwm=0,input=0):
		self.pin = pin
		self.duty_cycle = 0
		self.is_pwm = pwm
		self.is_input = input
		if not self.is_input:
			GPIO.setup(pin, GPIO.OUT)
			if self.is_pwm:
				GPIO.PWM.__init__(self,self.pin, 100)
				self.start(0)
			else:
				GPIO.output(self.pin, False)
		else:
			GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

	def __set_pwm(self, val):
		if (val >= 0 and val <= 100):
			self.ChangeDutyCycle(val)
		else:
			print("invalid pwm")

	def __set_digital(self, val):
		if (val >= 1 or val == True or val == "HIGH" or val == "1"):
			GPIO.output(self.pin, True)
		else:
			GPIO.output(self.pin, False)

	def __get_pwm(self):
		return self.duty_cycle

	def __get_digital(self):
		return GPIO.input(self.pin)

	def set(self, val):
		if self.is_pwm:
			self.__set_pwm(val)
		else:
			self.__set_digital(val)

	def get(self):
		return GPIO.input(self.pin)
		if self.is_pwm:
			self.__get_pwm()
		else:
			self.__get_digital()

def setup_gpios(num_tiers):
	global outputs; global inputs; global dict
	GPIO.setwarnings(False)
	GPIO.cleanup()
	GPIO.setmode(GPIO.BCM)
	for pin in outputs:
		dict[pin] = Pin(pin)
	for pin in inputs:
		dict[pin] = Pin(pin,input=1)
	dict[BUTTON_OUT].set(1)