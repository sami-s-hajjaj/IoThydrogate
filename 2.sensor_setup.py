#######################################################################################
#																					  #
#      					IoT FloodGate - Ultrasonic Sensor setup						  #	
#																					  #
#      NOTE: gate must be in CLOSED position at the start of the program (lowered)	  #	
#																					  #	
#######################################################################################


import RPi.GPIO as GPIO
from time import sleep, time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# misc  (set global for water sensor code) 
echo_start = 0.0
echo_end = 0.0
maximum_water_height = 16.0  # maximum acceptable level of water (measured from river base)


# Water Sensor setup
# pins
echo = 24
trig = 23
#GPIO
GPIO.setup(echo, GPIO.IN)		# echo measures distance (like sonar)
GPIO.setup(trig, GPIO.OUT)		# trig triggers the motor to move


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
	
reset_sensor()

while True:
	try:
		water_height = maximum_water_height - measure_distance()
		print(str(water_height))
			
	except KeyboardInterrupt:
		GPIO.cleanup()
		exit()
