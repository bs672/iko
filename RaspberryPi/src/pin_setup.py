# PIN SETUP FOR A SINGLE TIER

import RPi.GPIO as GPIO

DHT_PIN = 2

output_map = {}
output_map['intake_fan'] = 14
output_map['exhaust_fan'] = 15
output_map['re_fan'] = 20
output_map['heat_pin'] = 18
output_map['valve_pin'] = 25
output_map['led_high'] = 12
output_map['led_dim'] = 23
output_map['button_out'] = 10
output_map['hres_out'] = 6
output_map['mres_out'] = 13
output_map['tray_out'] = 22

input_map = {}
input_map['button_in'] = 21
input_map['dht_pin'] = DHT_PIN
input_map['hres_read'] = 5
input_map['mres_read'] = 19
input_map['tray_read'] = 27

pin_map = {}

class Pin(GPIO.PWM):
	def __init__(self,pin,pwm=0,input=0):
	""" An object representing an input or output pin.
	Attributes:
		pin: the pin number
		duty cycle: the duty cycle for pwm
		is_pwm: an int indicating if it is a pwm pin or not
		is_input: an int indicating if it is an input pin or not
	"""
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
		""" Writes to the output pin. Does either digital write or pwm
		depending on whether the Pin was set up as a pwm pin or not.
		Uses helpers set_pwm and set_digital.
		Args:
			val: The value to write to the pin. Should be 1 or 0 for
			digital and 0 <= val <= 100 for pwm
		Returns void
		"""
		if self.is_pwm:
			self.__set_pwm(val)
		else:
			self.__set_digital(val)

	def get(self):
		""" Gets the value the pin is outputting.
		Returns:
			An int representing the output of the Pin.
			1 or 0 for digital, between 0 and 100 for pwm.
		"""
		return GPIO.input(self.pin)
		if self.is_pwm:
			self.__get_pwm()
		else:
			self.__get_digital()

def setup_gpios(num_tiers=1):
	""" Sets up the gpio pins.
	Instantiates each of the pin objects and returns them as a dictionary.
	Args:
		num_tiers: an int indicating the number of tiers to set up pins for
	Returns:
		pin_map: A dictionary containing all the pin objects that have been set up.
		key - string like 'light'; value - pin object
	"""
	# TODO: Use pin_number_map
	global output_map; global input_map; global pin_map
	GPIO.setwarnings(False)
	GPIO.cleanup()
	GPIO.setmode(GPIO.BCM)
	for pin_name in output_map:
		pin_map[pin_name] = Pin(output_map[pin_name])
	for pin_name in inputs:
		pin_map[pin_name] = Pin(input_map[pin_name],input=1)
	pin_map[BUTTON_OUT].set(1)
	return pin_map