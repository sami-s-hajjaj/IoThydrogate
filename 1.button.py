#######################################################################################
#																					  #
#      					IoT FloodGate - Button Control (local)						  #	
#																					  #
#      NOTE: gate must be in CLOSED position at the start of the program (lowered)	  #	
#																					  #	
#######################################################################################

import RPi.GPIO as GPIO
from time import sleep, time

# numbering system
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# motor settings 
motor_speed = 100
motor_rate  = 6.5

# Gate motor setup
# pins
motor_pwm = 17	# PWM (white) rate of motor commands (pulses/s)
motor_dir = 27 	# DIR (yellow) 
# GPIOs
GPIO.setup(motor_pwm, GPIO.OUT)
GPIO.setup(motor_dir, GPIO.OUT)


# Buttons setup
# pins
open_button = 5		# button to open gate
close_button = 6 	# button to close gate
# GPIOs
GPIO.setup(open_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)   	# button 5 to close gate
GPIO.setup(close_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)   	# button 6 to close gate


# Initial setup
pulse_rate = GPIO.PWM(motor_pwm,60)				# init pulse rate = 60 p/s
gate_dir = GPIO.output(motor_dir, GPIO.HIGH)	# init direction up	
gate_openned = False  							# init gate status = closed (refer to above) 
sleep(1)										# to stabilize sensor

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


while True:
	try:
		# button control - open
		if (GPIO.input(open_button)==0):		# if button 5 is pressed 
			open_gate(motor_speed,motor_rate)	# call open gate 
			sleep(0.2)

		# button control - close
		if (GPIO.input(close_button)==0):		# if button 6 is pressed 
			close_gate(motor_speed,motor_rate)	# call close gate  
			sleep(0.2)
			
	except KeyboardInterrupt:
		GPIO.cleanup()
		exit()

