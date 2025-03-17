import time
import board
import adafruit hcsr04
# Set up the ultrasonic sensor using a library
sonar = adafruit hcsr04.HCSR04(trigger pin=board.GP2, echo pin=board.
GP3)
# Take readings and output calibrated values
while True:
try:
# Take a reading (no button needed) of the range
X = sonar.distance
# Use calibration data to adjust this value
real dist = 1.084∗(X−9.044)+10
print((real dist ,))
except RuntimeError:
print("Retrying!")
time.sleep(2)
