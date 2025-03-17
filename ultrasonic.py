'''
ESC204 Lab 3, Task G
Task: Calibrate an ultrasonic sensor.
'''

import time
import board
import adafruit_hcsr04

# Set up the ultrasonic sensor using a library
sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.GP2, echo_pin=board.GP3)

# Take readings and output calibrated values
while True:
    try:
        # Take a reading (no button needed) of the range
        X = sonar.distance

        # Use calibration data to adjust this value
        real_dist = 1.084*(X-9.044)+10
        print((real_dist,))

    except RuntimeError:
        print("Retrying!")

    time.sleep(2)
