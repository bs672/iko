import paho.mqtt.client as mqtt
import AWSIoTPythonSDK
import os
import socket
import ssl
import RPi.GPIO as GPIO
import string
import Adafruit_DHT
from time import sleep
import time
from random import uniform
import datetime
import ast
from pytz import timezone
import json
import atexit

# output pins in GPIO
outputs = []
INTAKE_FAN = 14; outputs.append(INTAKE_FAN)
EXHAUST_FAN = 15; outputs.append(EXHAUST_FAN) # RXD
RE_FAN = 20; outputs.append(RE_FAN)
HEAT_PIN = 18; outputs.append(HEAT_PIN)
VALVE_PIN = 25; outputs.append(VALVE_PIN)
LED_HIGH = 12; outputs.append(LED_HIGH)
LED_DIM = 23; outputs.append(LED_DIM)
BUTTON_OUT = 4; outputs.append(BUTTON_OUT) # always high, gp17 is the read pin
HRES_OUT = 22; outputs.append(HRES_OUT)
MRES_OUT = 13; outputs.append(MRES_OUT)
TRAY_OUT = 6; outputs.append(TRAY_OUT)
# input pins in GPIO
inputs = []
BUTTON_IN = 17; inputs.append(BUTTON_IN)
DHT_PIN = 2; inputs.append(DHT_PIN)
HRES_READ = 27; inputs.append(HRES_READ)
MRES_READ = 19; inputs.append(MRES_READ)
TRAY_READ = 5; inputs.append(TRAY_READ)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
for pin in outputs:
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, True)
for pin in inputs:
	GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# GPIO.setup(LED_HIGH, GPIO.OUT)
# GPIO.setup(INTAKE_FAN, GPIO.OUT)
# GPIO.setup(HEAT_PIN, GPIO.OUT)
# GPIO.setup(EXHAUST_FAN, GPIO.OUT)
# GPIO.setup(RE_FAN, GPIO.OUT)
# GPIO.setup(VALVE_PIN, GPIO.OUT)
# GPIO.output(LED_HIGH, True)
# GPIO.output(INTAKE_FAN, True)
# GPIO.output(HEAT_PIN, True)
# GPIO.output(EXHAUST_FAN, True)
# GPIO.output(VALVE_PIN, True)
# GPIO.output(RE_FAN, True)
# GPIO.setup(TRAY_LEVEL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# GPIO.setup(HIGH_WATER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# GPIO.setup(MEDIUM_WATER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

while (1):
	pass