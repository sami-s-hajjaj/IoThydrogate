#######################################################################################
#																					  #
#							IoT FloodGate - Sensor, Buttons, IoT					  #	
#																					  #
#      NOTE: gate must be in CLOSED position at the start of the program (lowered)	  #	
#																					  #	
#######################################################################################


import RPi.GPIO as GPIO
import dweepy
from time import sleep, time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

###########  Sensor code #############################

# variables 
echo_start = 0.0
echo_end = 0.0

# pins
echo = 24
trig = 23

#GPIO
GPIO.setup(echo, GPIO.IN)		# echo measures distance (like sonar)
GPIO.setup(trig, GPIO.OUT)		# trig triggers the motor to move

# methods & other commands 

def init_sensor():
	# Initial setup
	GPIO.output(trig, False)	# switch off sensor  
	#print("init sensor")
	sleep(0.6)										

def measure_distance():
	# The actual echo
	GPIO.output(trig, True)		# switch on the sensor, take a reading 
	sleep(0.00001) 				# for just 0.00001 seconds
	GPIO.output(trig, False)	# switch off sensor
    
	global echo_start, echo_end
	while GPIO.input(echo)==0:  echo_start = time()	# measure time of sound sent
	while GPIO.input(echo)==1:  echo_end = time()	# measure time of echo return

	echo_duration = echo_end - echo_start	        # calculate duration
	distance = round((echo_duration * 17150),2)     # Distance = Duration * Speed 
	init_sensor()               # reset sensor for next run
		
	return distance

###########  Motor code ############################################################

# variables
motor_speed = 100
motor_rate  = 6.5

# pins
motor_pwm = 17	# PWM (white) rate of motor commands (pulses/s)
motor_dir = 27 	# DIR (yellow) 

# GPIOs
GPIO.setup(motor_pwm, GPIO.OUT)
GPIO.setup(motor_dir, GPIO.OUT)

# methods & other commands 

# Initial setup
pulse_rate = GPIO.PWM(motor_pwm,60)				# init pulse rate = 60 p/s
gate_dir = GPIO.output(motor_dir, GPIO.HIGH)	# init direction up	
gate_openned = False  							# init gate status = closed (refer to above) 
sleep(1)

"""
def open_gate(gate_speed, duration):
	global gate_openned
	if not gate_openned: # if gate is already closed
		gate_dir = GPIO.output(motor_dir, GPIO.HIGH)
		GPIO.output(motor_dir, GPIO.HIGH)
        pulse_rate.start(gate_speed)
        sleep(duration)
        pulse_rate.start(0)        
		gate_openned = True 	
		print("Gate Openned")
	else: print("Gate already Openned")
"""

def move_gate(speed, dur):
	pulse_rate.start(speed)
	sleep(dur)
	pulse_rate.start(0)

def open_gate(gate_speed, duration):
	global gate_openned
	if not gate_openned: # if gate is already closed
		gate_dir = GPIO.output(motor_dir, GPIO.HIGH)
		GPIO.output(motor_dir, GPIO.HIGH)
        move_gate(gate_speed, duration)
		gate_openned = True 	
		print("Gate Openned")
	else: 
		print("Gate already Openned")

def close_gate(gate_speed, duration):
	global gate_openned
	if gate_openned: 								# if gate already openned,
		gate_dir = GPIO.output(motor_dir, GPIO.LOW)	# close it 
		GPIO.output(motor_dir, GPIO.LOW)	
		move_gate(gate_speed,(duration-0.5))
		gate_openned = False 
		print("Gate Closed")			
	else: 
		print("Gate already Closed")


###########  buttons code ############################################################

# variables 

# pins
open_button = 5		# button to open gate
close_button = 6 	# button to close gate

# GPIOs
GPIO.setup(open_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)   	# button 5 to close gate
GPIO.setup(close_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)   	# button 6 to close gate

#################### IoT code ################################################################

# IoT code 
def update_iot(height, gate_status):
	# global iot_historical_data
	# construct data in a Dictionary
	iot_data = {
		'Water Level': round(height,2)
		,'Gate Status': gate_status
	#	,'Historical Data': iot_historical_data
		}				
	dweepy.dweet_for('iotfloodgate', iot_data)	# Dweet the IoT_data to the cloud	

#################### Main Program ################################################################
 
init_sensor()
maximum_water_height = 16.0  # maximum acceptable level of water (measured from river base)
iot_historical_data = [10.7, 16.4, 9.3, 5.5]


while True:
	try:

		# Button Control 
		# Open Gate
		if (GPIO.input(open_button)==0):								# open gate when open button is pressed 
            # updatre IoT here 
			open_gate(motor_speed,motor_rate)	
			sleep(0.2)
			
		# Close Gate
		if (GPIO.input(close_button)==0):								# close gate when close button is pressed 
            # updatre IoT here 
			close_gate(motor_speed,motor_rate)	
			sleep(0.2)
			
		# Capture water level for IoT & sensor control
		water_height = maximum_water_height - measure_distance()		# measure water height as per sensor
		
		update_iot(water_height, gate_openned)										# IoT - publish data to the cloud 
		
		# sensor control: Open or Close gate as per water level		
		if water_height > 7.0: close_gate(motor_speed, motor_rate)		# if height exceeded limit, close gate
		else: open_gate(motor_speed, motor_rate)						# else, open gate
		#sleep(1)       #wait 2 second		

		update_iot(water_height, gate_openned)										# IoT - publish data to the cloud 

		
	except KeyboardInterrupt:
		close_gate(motor_speed,motor_rate)
		GPIO.cleanup()
		exit()



