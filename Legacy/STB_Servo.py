#!/usr/bin/env python

## BEFORE RUNNING ON NEW COMPUTER
# Install Phidget Libraries: http://www.phidgets.com/docs/OS_-_Linux#Getting_Started_with_Linux
# Install Phidget Python libraries: http://www.phidgets.com/docs/Language_-_Python#Linux
# Test Phidget with demo code: http://www.phidgets.com/downloads/examples/Python.zip
# Make sure it works with demo code, this code is pretty basic

# Phidget Python API reference: http://www.phidgets.com/documentation/web/PythonDoc/Phidgets.html

import time

import numpy as np
import hapticsstb

import math 


from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Devices.AdvancedServo import AdvancedServo

FORCE_SCALE  = 0.1
def Error(e):
    try:
        source = e.device
        print("Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))

# Setup Phidget
servo = AdvancedServo()
servo.setOnErrorhandler(Error)

# Open Phidget
servo.openPhidget()
servo.waitForAttach(500)

# Set Phidget servo parameters
try:
	motor = 0
	servo.setEngaged(0, True)
	servo.setEngaged(1, True)
	servo_min = servo.getPositionMin(motor) + 130
	servo_max = servo.getPositionMax(motor) - 30
	servo_mid = (servo_max - servo_min)/2
	servo.setAcceleration(1, 500)
	servo.setAcceleration(motor, 500) # I just picked these to be smooth, feel free to change
	servo.setVelocityLimit(1, 2000)
	servo.setVelocityLimit(motor, 2000)
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

# Set up STB
sample_rate = 25 # This works best with low sampling rates

# Call STB's constructer (init)
sensor = hapticsstb.STB(sample_rate)

sensor.bias() # Tares the sensor, make sure that nothing's touching the boardcr
print sensor.bias_vector

run_time = 500
volt = 5.0
start_time = time.time()
sensor.start_sampling() # Starts the STB hardware sampling loop
try:
   while time.time() - start_time <= run_time:
        # read_M40 returns [Fx, Fy, Fz, Tx, Ty, Tz]
	sensor_data = sensor.read_m40()
	handedness = sensor.read_acc()
	#print("left hand" + str((handedness[0])))
	#print("right hand" + str((handedness[1])))
	#print sensor_data[0]
	#print sensor_data[1]
	#print sensor_data[2]
	
	
	pos = servo_min + ((sensor_data[0]**2 + sensor_data[1]**2 + sensor_data[2]**2)**1/2)*(servo_max - servo_min)/FORCE_SCALE
	if handedness[0] < volt and pos <= servo_max and pos >= servo_min:
		servo.setPosition(0, pos)
	elif handedness[0] and pos > servo_max:
		servo.setPosition(0, servo_max)
	elif handedness[0] and pos < servo_min:
		servo.setPosition(0, servo_min)
	if handedness[1] < volt and pos <= servo_max and pos >= servo_min:
		servo.setPosition(1, pos)
	elif handedness[1] and pos > servo_max:
		servo.setPosition(1, servo_max)
	elif handedness[1] and pos < servo_min:
		servo.setPosition(1, servo_min)

        # Scale force to +- 30N for whole range of servo
		#pos = servo_mid + (sensor_data[2])*(servo_max - servo_mid)/FORCE_SCALE
		#if pos <= servo_max and pos >= servo_min:
		#	servo.setPosition(motor, pos)
		#	servo.setPosition(1, pos)
		#elif pos > servo_max:
		#	servo.setPosition(motor, servo_max)
		#	servo.setPosition(1, servo_max)
		#	
		#elif pos < servo_min:
		#	servo.setPosition(motor, servo_min)
		#	servo.setPosition(1, servo_min)
		# print( "Sensor data: " + str(sensor_data) );
		


except KeyboardInterrupt:
    pass

except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

except:
	sensor.close() # Need to run this when you're done, stops STB and closes serial port
	servo.closePhidget()
	raise

sensor.close()
servo.closePhidget()
