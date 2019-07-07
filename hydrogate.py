#######################################################################################
#																					  #
#      NOTE: gate must be in CLOSED position at the start of the program (lowered)	  #	
#																					  #	
#######################################################################################

from bottle import route, run
import RPi.GPIO as GPIO
from time import sleep, time
import thread
import dweepy

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# misc  (set global for water sensor code) 
echo_start = 0.0
echo_end = 0.0
#water_limit = 12
#water_height = 0 

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

# Water Sensor setup
# pins
echo = 24
trig = 23
#GPIO
GPIO.setup(echo, GPIO.IN)		# echo measures distance (like sonar)
GPIO.setup(trig, GPIO.OUT)		# trig triggers the motor to move

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
	if not gate_openned: # not openned	= closed		# if gate not already openned,
		gate_dir = GPIO.output(motor_dir, GPIO.HIGH)	# open it
		GPIO.output(motor_dir, GPIO.HIGH)
		move_gate(gate_speed,duration)
		gate_openned = True 	
		print("Gate Openned")
	else: 
		print("Gate already Openned")

def close_gate(gate_speed, duration):
	global gate_openned
	if gate_openned: 							# if gate already openned,
		gate_dir = GPIO.output(motor_dir, GPIO.LOW)	# close it 
		GPIO.output(motor_dir, GPIO.LOW)	
		move_gate(gate_speed,(duration-0.5))
		gate_openned = False 
		print("Gate Closed")			
	else: 
		print("Gate already Closed")

def button_control(thread_id, thread_name):
	global open_button, close_button, motor_speed, motor_rate
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

def sensor_control(thread_id, thread_name):
	global open_button, close_button, motor_speed, motor_rate
	global trig, echo
	
	def reset_sensor():
		# Initial setup
		GPIO.output(trig, False)						# reset sensor 
		#print("init sensor")
		sleep(0.6)										

	def measure_distance():
		# The actual echo
		GPIO.output(trig, True)							# take a reading
		sleep(0.00001) 
		GPIO.output(trig, False)

		global echo_start, echo_end
		# analyzing the echo
		while GPIO.input(echo)==0: 
			echo_start = time()
	
		while GPIO.input(echo)==1: 
			echo_end = time()

		echo_duration = echo_end - echo_start	
		distance = round((echo_duration * 17150),2)  		# # distance = time * velocity (17150 is speed of echo, sensor props) 
		reset_sensor()	
		return distance
	
	reset_sensor()
		
	while True:
		try:
			water_height = 18 - measure_distance()
			if (water_height > 0 or water_height > 18):	
			#if (water_height > 0):					
				gate_status = "OPEN" if gate_openned else "CLOSED"
				dweepy.dweet_for('iot_hydrogate', {'Gate Status': gate_openned,'Gate Status text': gate_status, 'Water Level': water_height})	
				#sleep(0.6)										
				print("The Gate is :" + gate_status + " and the water height is: " + str(water_height)) 				
				#print(str(water_height))

				if water_height > 7.0: close_gate(motor_speed, motor_rate)				
				else: open_gate(motor_speed, motor_rate)				
			else: 
				reset_sensor()
			
		except KeyboardInterrupt:
			GPIO.cleanup()
			exit()

def runhost(host_ip, port_numb):
	run(host=host_ip, port=port_numb)

try:
	thread.start_new_thread(button_control, (1, "buttons"))
	thread.start_new_thread(sensor_control, (2, "sensors"))
	#thread.start_new_thread(iot_hydrogate, (1, "IoT HydroGate"))	
	
except:
	print "Error: Unable to start thread"
	
while 1: 
	pass


GPIO.cleanup()
