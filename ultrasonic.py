'''
ESC204 Lab 3, Task F
Task: Take readings using an ultrasonic sensor.
'''

import board
import digitalio
import time

# Configure GPIO for the LED and button
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
button = digitalio.DigitalInOut(board.GP16)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# Configure GPIO for the sensor input to/output from the Pico
trigger = digitalio.DigitalInOut(board.GP2)
trigger.direction = digitalio.Direction.OUTPUT
echo = digitalio.DigitalInOut(board.GP3)
echo.direction = digitalio.Direction.INPUT
echo.pull = digitalio.Pull.UP

# Set up loop variable and start plotter
prev_button_value = button.value
print((1,))

def trigger_on_button_pressed(prev_button_value):
    # set default button state to "not pressed"
    button_pressed = False

    # if button is pressed (and not just bouncing)
    if(button.value and not prev_button_value):
        # push the trigger and update button state
        trigger.value = True
        button_pressed = True
        print('trigger')

        # reset trigger
        trigger.value = False

    return button_pressed, button.value

def capture_echo(timeout):
    #initialize data array and counter
    data = []
    i = 0

    # wait for echo and timeout if not seen
    while(not(echo.value) and not(i == timeout)):
        i+=1

    # if timeout reached, no data collection
    if i == timeout:
        print('timeout!')

    # if timeout not reached, then keep collecting data
    else:
        while(echo.value):
            data.append((1,))

    return data

def plot_data(data):
    # plot points with pauses in between to avoid overloading
    for point in data:
        print(point)
        time.sleep(0.01)

while True:
    points = capture_echo(1000)
    if(len(points) > 0):
        plot_data(points)

    # print a low value and wait a second to avoid overloading
    print((0.001,))
    time.sleep(1.0)
