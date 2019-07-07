#######################################################################################
#																					  #
#							IoT FloodGate - Sensor, Buttons, IoT					  #	
#																					  #
#      This program publishes fake data for testing & Troubleshooting purposes  	  #	
#																					  #	
#######################################################################################


#import RPi.GPIO as GPIO
import dweepy
from time import sleep, time

# init_sensor()
maximum_water_height = 9.0  # maximum acceptable level of water (measured from river base)
gate_openned = False  	

# IoT code 
def update_iot(height, gate_status):
	# global iot_historical_data
	# construct data in a Dictionary
    if gate_status: status_text = "Water level below Maximum Limit"
    else: status_text = "Water level Exceeds Maximum Limit"
    
    iot_data = {
		'Water Level': round(height,2)
		,'Gate Status': gate_status
		,'Gate Status Text': status_text        
	#	,'Historical Data': iot_historical_data
		}
    dweepy.dweet_for('iotfloodgate', iot_data)	# Dweet the IoT_data to the cloud	

#################### Main Program ################################################################

while True:
    try: 
        # set of simulated water heights
        data_set = [3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 4.1, 4.3, 4.7]
        
        #5.1, 5.5, 5.7, 5.8, 5.6, 5.8, 6.1, 6.3, 5.9, 5.8, 6.1, 6.2, 6.5, 6.6, 6.5, 6.4, 6.3, 6.2, 6.3, 6.2, 6.1, 5.9, 5.8, 5.9, 6.2, 6.3, 6.4, 6.5, 6.7, 6.8, 6.9, 7.1, 7.3, 7.4, 7.3, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.7, 7.8, 7.9, 8.1, 8.3, 8.4, 8.5, 8.7, 8.5, 8.6, 8.7, 8.9, 9.0, 9.1, 9.3, 9.5, 9.6, 9.8, 9.7

        # loop through data set, and update IoT accordingly
        i = 0
        while i < len(data_set):
            water_height = data_set[i]

            update_iot(water_height, gate_openned)                          # update IoT (before)
        
            if water_height > maximum_water_height: gate_openned = False    # if water level > max , close gate
            else:   gate_openned = True                                     # else, open it

            update_iot(water_height, gate_openned)							# update IoT (before)
            #sleep(1)       # time delay, to simulate sensor delays
            print("Current water height: "+ str(water_height))
            i=i+1
    
    except KeyboardInterrupt:
        print "\nGoodby"
        exit()



