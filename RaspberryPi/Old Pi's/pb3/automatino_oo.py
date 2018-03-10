# Automatino-Pi
# Created by: Bhai Jaiveer Singh
# First implementation of the automated petal box using AWS and RaspberryPi
# This program will publish and subscribe mqtt messages using the AWS IoT hub as a broker

# TODO: Create box class which contains a pin map and put water functions etc in it
# TODO: change it so that most up to date temp,hum is sent every x seconds and in the background data is being polled
# TODO: change the publish function so that if it cant publish it doesnt fail. overwrite method in client.py
# GPIO.input(pin) - digital read

import paho.mqtt.client as mqtt
import AWSIoTPythonSDK
import os
import sys
import socket
import string
import Adafruit_DHT
import time
import datetime
import json
import atexit
from time import sleep
from random import uniform
from pytz import timezone
import client
import time
import pin_setup
import RPi.GPIO as GPIO
import random
import threading
from pin_setup import *

thingName = 'pb3'

def digital_write(pin, val):
	if (val >= 1 or val == True or val == "HIGH"):
		GPIO.output(pin, True)
	else:
		GPIO.output(pin, False)

def set_pwm(pwm_object, val):
	pwm_object.ChangeDutyCycle(val)

# TODO: Change set_pin get_pin NOT digital_write when switching to pwm
def set_pin(pin, val):
	digital_write(12, val)

def get_pin(pin):
	return GPIO.input(pin)

def led_toggle(payload):
	if (int(payload) == 1):
		analog_write(light_pwm, 100)
	if (int(payload) == 0):
		analog_write(light_pwm, 0)

def get_time():
	time = str(datetime.datetime.now(timezone('US/Eastern')).time())
	time = time[0:2] + time[3:5]
	return time

def before(time1, time2):
	""" Return true if time1 is before (or equal to) time2
	Inputs time1 and time2 are strings """
	hr1 = int(time1[0:2])
	min1 = int(time1[2:4])
	hr2 = int(time2[0:2])
	min2 = int(time2[2:4])
	if hr1 < hr2:
		return True
	elif hr2 < hr1:
		return False
	# hr1 = hr2
	elif min2 < min1:
		return False
	else:
		return True

def reservoir_update():
	h_res_out.set(1)
	m_res_out.set(1)
	res = 0
	if (h_res_read.get() == 1):
		res = 2
	elif (m_res_read.get() == 1):
		res = 1		
	h_res_out.set(0)
	m_res_out.set(0)
	return res

class Tier():
	def __init__(self,name,dht_pin,fan=None,light=None,heat=None,exhaust=None,
		circ=None,tray=None,blue=0,buffer=2,light_override=0,fan_override=0,
		heat_override=0,blue_override=0,auto=1,valve=None,tray_out=None,
		tray_read=None,mode=0):
		self.name = name
		self.temperature = 70 # TODO: Change to None after testing
		self.humidity = 20 # TODO: Change to None after testing
		self.water_level = 0
		self.blue,self.light_override,self.heat_override,self.blue_override = blue,light_override,heat_override,blue_override   
		self.light, self.fan, self.heat, self.exhaust, self.circ = light, fan, heat, exhaust, circ
		self.buffer,self.auto,self.valve,self.tray_out,self.tray_read,self.mode = buffer,auto,valve,tray_out,tray_read,mode
		self.dht_pin = dht_pin
		self.profiles = [
			{'name': 'day', 'temperatureSP': 80, 'humiditySP': 60, 'light': 1, 'blue': 0}, 
			{'name': 'night','temperatureSP': 65, 'humiditySP': 60, 'light': 0, 'blue': 0},
			{'name': 'germ','temperatureSP': 80, 'humiditySP': 60, 'light': 0, 'blue': 1}
		]
		self.current_profile = self.last_profile = self.profiles[0]
		self.schedule = [['day','0400'],['night','2200']]
		self.last_update = time.time()
		self.circ.set(1)

	# def set_light(self, val):
	# 	self.light.ChangeDutyCycle(val)
	# 	self.dict['light'] = val

	# def get_light(self):
	# 	return self.dict['light']

	# def set_fan(self, val):
	# 	# self.fan.ChangeDutyCycle(val)
	# 	GPIO.output(self.fan, bool(val))
	# 	self.dict['fan'] = val

	# def get_fan(self):
	# 	return self.dict['fan']

	# def set_heat(self, val):
	# 	# self.heat.ChangeDutyCycle(val)
	# 	GPIO.output(self.heat, bool(val))
	# 	self.dict['heat'] = val

	# def get_heat(self):
	# 	return self.dict['heat']

	# def set_exhaust(self, val):
	# 	# self.exhaust.ChangeDutyCycle(val)
	# 	GPIO.output(self.exhaust, bool(val))
	# 	self.dict['exhaust'] = val

	# def get_exhaust(self):
	# 	# return self.dict['exhaust']
	# 	return self.get(self.exhaust)

	# def set_circ(self, val):
	# 	# self.light.ChangeDutyCycle(val)
	# 	GPIO.output(self.circ, bool(val))
	# 	self.dict['circ'] = val

	# def get_circ(self):
	# 	# return self.light.dutycycle
	# 	return self.dict['circ']

	def add_profile(self, profile):
		""" Add a new profile to profiles or update an existing one
		Input must be a valid profile (must have 'name' as a key) """
		indices = [self.profiles.index(x) for x in self.profiles if x['name'] == profile['name']]
		if len(indices) == 0:
			print("adding new profile \"" + profile['name'] + "\": " + str(profile))
			self.profiles.append(profile)
		else:
			print("updating existing profile \"" + profile['name'] + "\": " + str(profile))
			self.profiles[indices[0]] = profile
		self.update_current_profile(True)

	def change_schedule(self, new_schedule):
		""" Changes the schedule of profiles and times
		Input must be a schedule in the correct format
		Sorts the schedule according to start times of profiles
		Updates the current profile as well """
		if len(new_schedule) == 0:
			print('Not a valid schedule 2')
			return
		for x in new_schedule:
			print x
			# check if profile exists in profiles
			# any way of making this not o(n^2) ??
			indices = False
			for y in self.profiles:
				if y['name'] == x[0]:
					indices or True
			if indices:
				print('Profile ' + x[0] + ' has not been created yet')
				return
			if (len(x) != 2) or (not isinstance(x[1],str)):
				print('Not a valid schedule')
				return
		else:
			# sort the schedule
			for i in range(len(new_schedule) - 1):
				min = i
				for j in range(i,len(new_schedule)):
					if before(new_schedule[j][1], new_schedule[min][1]):
						min = j;
					temp = new_schedule[i];
					new_schedule[i] = new_schedule[min];
					new_schedule[min] = temp;
			# change schedule
			print('New schedule: ' + str(new_schedule))
			self.schedule = new_schedule
			self.update_current_profile(True)

	def update_current_profile(self, arg = False):
		""" Check the current time to figure out what the current profile is (amongst the ones in the schedule)
		Don't assume schedule is sorted """
		time = get_time()
		if len(self.profiles) == 1:
			self.current_profile = self.profiles[0]
		else:
			maximin = None  # an index of the schedule
			last = 0
			for i in range(len(self.schedule)):
				if before(self.schedule[i][1], time):
					if maximin is None:
						maximin = i
					elif before(self.schedule[maximin][1], self.schedule[i][1]):
						maximin = i
				if before(self.schedule[last][1], self.schedule[i][1]):
					last = i
			if maximin is None:
				maximin = last
			indices = [self.profiles.index(x) for x in self.profiles if x['name'] == self.schedule[maximin][0]]
			if len(indices) >= 1:
				if not (self.current_profile['name'] == self.profiles[indices[0]]["name"]):
					# turn off the light override if we are switching schedules
					self.light_override = 0
					mqttc.publish(self.name + "/light_override","0", qos=1)
				self.current_profile = self.profiles[indices[0]]
			if arg:
				print("current profile is \"" + str(self.current_profile) + "\"")

	def automate(self):
		print("automating")
		tempSP = int(self.current_profile['temperatureSP'])
		if (self.temperature < tempSP - int(self.buffer)):
			self.heat.set(1)
			self.fan.set(0)
			self.exhaust.set(0)
			self.mode = 1
		elif (self.temperature > tempSP + self.buffer):
			self.fan.set(1)
			self.exhaust.set(1)
			self.heat.set(0)
			self.mode = 2
		elif ((self.temperature < tempSP + 0.5) & (self.temperature > tempSP - 0.5)):
			self.heat.set(0)
			self.fan.set(0)
			self.exhaust.set(0)
			self.mode = 0
		# if not self.light_override:
		# 	self.set_light(self.current_profile['light'])
		# self.set(self.light,self.current_profile['light'])
		if not self.light_override:
			self.light.set(self.current_profile['light'])
		self.blue = self.current_profile['blue']
		self.last_button = 0

	def change_light(self, val):
		print("changing light")
		self.light.set(val)
		mqttc.publish("$aws/things/" + self.name + "/shadow/update",
			"{\"state\":{\"reported\":{\"light\":\""+str(val)+"\"},\"desired\":{\"light\":null}}}", qos=1)

	def change_in_out(self, val):
		print("changing in out")
		self.fan.set(val)
		self.exhaust.set(val)
		mqttc.publish("$aws/things/" + self.name + "/shadow/update",
			"{\"state\":{\"reported\":{\"in_out\":\""+str(val)+"\"},\"desired\":{\"in_out\":null}}}", qos=1)
	
	def change_heat(self, val):
		print("changing heat")
		self.heat.set(val)
		mqttc.publish("$aws/things/" + self.name + "/shadow/update",
			"{\"state\":{\"reported\":{\"heat\":\""+str(val)+"\"},\"desired\":{\"heat\":null}}}", qos=1)
	
	def change_buffer(self, val):
		print("changing buffer")
		self.buffer = val
		mqttc.publish("$aws/things/" + self.name + "/shadow/update",
			"{\"state\":{\"reported\":{\"buffer\":\""+str(val)+"\"},\"desired\":{\"buffer\":null}}}", qos=1)

	def set_auto(self, val):
		print("changing auto")
		self.auto = val
		if val:
			self.light_override = 0
		else:
			self.light_override = 1
		mqttc.publish("$aws/things/" + self.name + "/shadow/update",
			"{\"state\":{\"reported\":{\"auto\":\""+str(val)+"\"},\"desired\":{\"auto\":null}}}", qos=1)

	def shadow_update(self, topic, val):
		mqttc.publish("$aws/things/" + self.name + "/shadow/update",
			"{\"state\":{\"reported\":{\""+topic+"\":\""+str(val)+"\"},\"desired\":{\"auto\":null}}}", qos=1)

	def resolve_deltas(self, json):
		if 'light' in json["state"]:
			val = json["state"]["light"]
			self.change_light(int(val))
		if 'buffer' in json["state"]:
			val = json["state"]["buffer"]
			self.change_buffer(int(val))
		if 'heat' in json["state"]:
			val = json["state"]["heat"]
			self.change_heat(int(val))
		if 'in_out' in json["state"]:
			val = json["state"]["in_out"]
			self.change_in_out(int(val))
		if 'auto' in json["state"]:
			val = json["state"]["auto"]
			self.set_auto(int(val))

	def get_readings(self):
		humreading, tempreading = None, None
		reading_counter = 0
		while (humreading is None or tempreading is None) and reading_counter < 5:
			print("reading")
			reading_counter = reading_counter + 1
			humreading, tempreading = Adafruit_DHT.read(Adafruit_DHT.DHT11, self.dht_pin)
		if (humreading is not None and tempreading is not None):
			self.humidity = humreading
			self.temperature = (tempreading*1.8) + 32 # converting to fahrenheit
			return True
		else:
			print("Failed to get readings")
			return False

	def tray_update(self):
		self.tray_out.set(1)
		if (self.tray_read.get() == 0):
			self.valve.set(1)
			self.tray_out.set(0)
			print("valve opened")
			return 0
		self.tray_out.set(0)
		# If waterval > 10 and the valve is currently open
		if (self.valve.get() == 1):
			self.valve.set(0)
			print("valve closed")
		return 1

	def big_loop(self):
		sleep(3)
		# mqttc.loop(timeout=1.0, max_packets=1)
		self.update_current_profile()
		tray_level = 0
		if self.valve != None:
			tray_level = self.tray_update()
		print("tray level: " + str(tray_level))
		self.water_level = reservoir_update()
		self.get_readings()
		# Maybe only do the below things if there's a change in something?
		if self.auto:
			self.automate()
		self.check_light_button()

	def check_light_button(self):
		current = GPIO.input(21)
		if current == 1 and self.last_button == 0:
			self.light_override = 1
			if self.light.get() == 1:
				self.change_light(0)
			else:
				self.change_light(1)
		self.last_button = current

	def update_cloud(self):
		if time.time() - self.last_update > 5:
			# mqttc.publish("$aws/things/" + self.name + "/shadow/get","", qos=1)
			self.last_update = time.time()
			mqttc.publish("$aws/things/" + self.name + "/shadow/update",
				"{\"state\":{\"reported\":{\"temperature\": " + str(self.temperature) + ", \"humidity\":" + str(self.humidity) +
				", \"tempSP\":" + str(self.current_profile['temperatureSP']) + 
				", \"light\":" + str(self.light.get()) + 
				", \"light_override\":" + str(self.light_override) + 
				", \"mode\":" + str(self.mode) + 
				", \"auto\":" + str(self.auto) + 
				", \"water\":" + str(self.water_level) + 
				", \"exhaust\":" + str(self.exhaust.get()) + 
				", \"heat\":" + str(self.heat.get()) +
				", \"fan\":" + str(self.fan.get()) + "}}}", qos=1)
			if self.temperature is not None and self.humidity is not None:
				print("msg sent: temperature  %.2f; humidity %.2f" % (self.temperature, self.humidity))

class lightButtonThread(threading.Thread):
    def __init__(self, tier):
        threading.Thread.__init__(self)
        self.tier = tier

    def run(self):
        while True:
        	tier.check_light_button()

if __name__ == '__main__':
	num_tiers = 1
	water = 1
	assert len(sys.argv), "Need 2 arguments. Arg 1: Number of tiers, must be int < 5. Arg 2: Water or not, 1 or 0"
	assert int(sys.argv[1]) <= 5, "Arg 1: Number of tiers, must be int < 5"
	# assert int(sys.argv[2]) == 1 or int(sys.argv[2]) == 0, "Arg 2: Water or not, 1 or 0"
	num_tiers, water = int(sys.argv[1]), int(sys.argv[2])
	pin_map = pin_setup.setup_gpios(num_tiers)
	if water:
		# pin_setup.setup_valve()
		# pin_setup.setup_reservoir()
		pass
	
	tiers = [None for x in range(num_tiers)]
	for i in range(num_tiers):
		tiers[i] = Tier(thingName,pin_setup.DHT_PIN,light=pin_map['led_high'],
			fan=pin_map['intake_fan'],heat=pin_map['heat_pin'],
			exhaust=pin_map['exhaust_fan'],circ=pin_map['re_fan'],
			tray_out=pin_map['tray_out'],tray_read=pin_map['tray_read'],
			valve=pin_map['valve_pin'])
	for tier in tiers:
		lightButtonThread(tier).start()
		#pwm test 2/25/18
		#pi.set_PWM_frequency(output_map['led_high'], 1000)
		#pi.set_PWM_dutycycle(output_map['led_high'], 255)

	h_res_read = pin_map['hres_read']
	h_res_out = pin_map['hres_out']
	m_res_read = pin_map['mres_read']
	m_res_out = pin_map['mres_out']
	tray_read = pin_map['tray_read']
	tray_out = pin_map['tray_out']

	mqttc = client.Client(tiers)
	while True:
		for tier in tiers:
			tier.big_loop()
			if mqttc.connflag != False:
				tier.update_cloud()
		if mqttc.connflag == False:
			mqttc.reconnect()
			print("connflag false, reconnecting")

	GPIO.cleanup()
	mqttc.disconnect()
