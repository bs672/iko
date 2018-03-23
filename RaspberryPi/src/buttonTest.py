import time  # Library will let us put in delays
import RPi.GPIO as GPIO # Import the RPi Library for GPIO pin control
import pigpio

GPIO.setmode(GPIO.BCM) # We want to use the physical pin number scheme

LED1 = 12
BUTTON_IN = 9
BUTTON_OUT = 10

GPIO.setup(BUTTON_IN, GPIO.IN) 
GPIO.setup(BUTTON_OUT, GPIO.OUT)

pi = pigpio.pi()

#start with lights off and button_out always high
GPIO.output(BUTTON_OUT, True)
pi.set_PWM_frequency(LED1, 1000)
pi.set_PWM_dutycycle(LED1, 0)

#initialise a previous input variable to 0 (assume button not pressed last)
k = 0
prev_input = 0
startTime = 0
timePressed = 0
dim_min = 25
dim_rate = 10
dim_time = 1.5

while k<300:
  
  #take readings
  new_input = GPIO.input(BUTTON_IN) 
  ledState = pi.get_PWM_dutycycle(LED1)

  #if the last reading was low and the new one is high, the button was pressed, start timer
  if (not(prev_input) and new_input):

    #get processor time
    startTime = time.clock()

  #check if button is being held
  elif (prev_input and new_input):

    timePressed = 100*(time.clock() - startTime)

    #if button has been pressed for over one second and lights are on, start dimming
    if ((timePressed > dim_time) and (ledState > 0)):
      
      #dim to a minimum threshhol
      ledState = max(ledState - dim_rate, dim_min)
      pi.set_PWM_dutycycle(LED1, ledState)
  
  #button is released, reset timers and turn on off lights if under one second
  elif (prev_input and not(new_input)): 

    #lights off before and button pressed less than 1 second, turn them on
    if ((ledState == 0) and (timePressed < dim_time)):
      pi.set_PWM_dutycycle(LED1, 255)
      ledState = 1
    
    #lights on before and button pressed less than one second, turn them off
    elif ((ledState > 0) and (timePressed < dim_time)):
      pi.set_PWM_dutycycle(LED1, 0)
      ledState = 0

    #reset timers
    timePressed = 0
    startTime = 0

  #update previous input
  prev_input = new_input
  
  #update k counter
  k+=1
  
  #slight pause to debounce
  time.sleep(0.05)

GPIO.cleanup()

# #dimming while pressed
#   while(1):                  # Loop Forever
# 	if GPIO.input(button1)==0:             #If left button is pressed
# 		print "Button 1 was Pressed"   # Notify User
# 		bright=bright/2.               # Set brightness to half
# 		pwm1.ChangeDutyCycle(bright)   # Apply new brightness
# 		sleep(.25)                     # Briefly Pause
# 		print "New Brightness is: ",bright # Notify User of Brightness