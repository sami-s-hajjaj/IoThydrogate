#######################################################################################
#																					  #
#					IoT FloodGate - Ultrasonic Sensor + Button Control				  #	
#																					  #
#      NOTE: gate must be in CLOSED position at the start of the program (lowered)	  #	
#																					  #	
#######################################################################################


import RPi.GPIO as GPIO
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

def reset_sensor():
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
	while GPIO.input(echo)==0: 	
		echo_start = time()		# measure time from sensor was actually on
	
	while GPIO.input(echo)==1: 
		echo_end = time()		# measure time from sensor was actually off

	echo_duration = echo_end - echo_start	
	distance = round((echo_duration * 17150),2)  	# distance = time * velocity (17150 is speed of echo, sensor propery) 
	reset_sensor()
	
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

def move_gate(speed, dur):
	pulse_rate.start(speed)
	sleep(dur)
	pulse_rate.start(0)

def open_gate(gate_speed, duration):
	global gate_openned
	if not gate_openned: 								# if gate already closed (not openned)
		gate_dir = GPIO.output(motor_dir, GPIO.HIGH)	# open it
		GPIO.output(motor_dir, GPIO.HIGH)
		move_gate(gate_speed,duration)
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


#################### Main Program ################################################################
 
maximum_water_height = 16.0  # maximum acceptable level of water (measured from river base)

reset_sensor()

while True:
	try:
		# sensor control (open or close gate as per water level
		water_height = maximum_water_height - measure_distance()		# measure water height
		if water_height > 7.0: close_gate(motor_speed, motor_rate)		# if height exceeded limit, close gate
		else: open_gate(motor_speed, motor_rate)						# else, open gate
		
		
		# button control - open
		if (GPIO.input(open_button)==0):		# if open button (5) is pressed 
			open_gate(motor_speed,motor_rate)	# open gate 
			sleep(0.2)
			

		# button control - close
		if (GPIO.input(close_button)==0):		# if close button (6) is pressed 
			close_gate(motor_speed,motor_rate)	# close gate  
			sleep(0.2)
			
		
	except KeyboardInterrupt:
		GPIO.cleanup()
		exit()



