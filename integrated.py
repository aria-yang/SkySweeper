import time
import board
import adafruit_hcsr04
import array
import digitalio
import pwmio
import servo
import asyncio

# Configuration
TRIGGER_PIN = board.GP19
ECHO_PIN = board.GP18
SAMPLE_INTERVAL = 0.5  # Faster sampling for better responsiveness
NUM_SAMPLES = 3        # Number of samples to average (reduces noise)
MIN_DISTANCE = 2       # Minimum distance in cm the sensor can reliably detect
TIMEOUT = 1.0          # Timeout for sensor readings in seconds

# set up buttons as digital input with pull-up resistor
button1 = digitalio.DigitalInOut(board.GP9)
button1.direction = digitalio.Direction.INPUT
button1.pull = digitalio.Pull.UP
# set up button as digital input with pull-up resistor
button2 = digitalio.DigitalInOut(board.GP8)
button2.direction = digitalio.Direction.INPUT
button2.pull = digitalio.Pull.UP
# set up button as digital input with pull-up resistor
button3 = digitalio.DigitalInOut(board.GP7)
button3.direction = digitalio.Direction.INPUT
button3.pull = digitalio.Pull.UP

# set up direction pins as digital outputs for DC motor 1
in1 = digitalio.DigitalInOut(board.GP14)
in2 = digitalio.DigitalInOut(board.GP13)
in1.direction = digitalio.Direction.OUTPUT
in2.direction = digitalio.Direction.OUTPUT

# set up direction pins as digital outputs for DC motor 2
in3 = digitalio.DigitalInOut(board.GP12)
in4 = digitalio.DigitalInOut(board.GP11)
in3.direction = digitalio.Direction.OUTPUT
in4.direction = digitalio.Direction.OUTPUT

# set up direction pins as digital outputs for DC motor 3
in5 = digitalio.DigitalInOut(board.GP1)
in6 = digitalio.DigitalInOut(board.GP0)
in5.direction = digitalio.Direction.OUTPUT
in6.direction = digitalio.Direction.OUTPUT

# set up motor driving signal as PWM output for DC motor 1
ena = pwmio.PWMOut(board.GP15, duty_cycle = 0)
enb = pwmio.PWMOut(board.GP10, duty_cycle = 0)
ena2 = pwmio.PWMOut(board.GP2, duty_cycle = 0)
# enb2 = pwmio.PWMOut(bo ard.GP21, duty_cycle = 0)

# create a PWMOut object for servomotor
pwm = pwmio.PWMOut(board.GP4, duty_cycle=2 ** 15, frequency=50)

# Create a servo object, my_servo.
my_servo = servo.Servo(pwm)

# set time limits
start_time = time.time()
time_limit = 20

# set starting (fastest) motor duty cycles
CW_duty = 50000
CCW_duty = 50000
duty_step = 5000
max_int = 65535

# Initialize sensor
sonar = adafruit_hcsr04.HCSR04(trigger_pin=TRIGGER_PIN, echo_pin=ECHO_PIN, timeout=TIMEOUT)

# Buffer for averaging readings
distance_buffer = array.array('f', [0] * NUM_SAMPLES)
buffer_index = 0

def calibrate_distance(raw_distance):
    """Apply calibration formula to raw distance measurement"""
    # Using the same calibration formula
    return 3.1385 * raw_distance - 0.5

def get_averaged_distance():
    """Take multiple readings and return the average"""
    samples_collected = 0
    attempts = 0
    max_attempts = 5

    # Try to fill the buffer with valid readings
    while samples_collected < NUM_SAMPLES and attempts < max_attempts:
        try:
            raw_distance = sonar.distance

            # Filter out unreasonably small values that might be errors
            if raw_distance >= MIN_DISTANCE:
                distance_buffer[buffer_index % NUM_SAMPLES] = raw_distance
                samples_collected += 1

        except RuntimeError:
            pass  # Skip failed readings

        attempts += 1
        time.sleep(0.1)  # Brief pause between samples

    # If we have at least one sample, calculate average
    if samples_collected > 0:
        return sum(distance_buffer) / samples_collected
    else:
        raise RuntimeError("Could not get valid readings")

# Add a state variable to track the button press
button1_pressed = False
last_button1_state = button1.value  # Store the initial button state

async def main():
    # Run both tasks concurrently
    await asyncio.gather(check_buttons(), main_functions())

# Start the asyncio event loop
asyncio.run(main())

def ultrasonic_test():
    # Get distance reading with improved small distance detection
    raw_distance = get_averaged_distance()

    # Apply calibration
    calibrated_distance = calibrate_distance(raw_distance)

    # Print the result
    print(f"Distance: {calibrated_distance:.1f} cm")
    # Arm movement logic, moves arm down if distance is greater than 17 cm and up if less than 15 cm
    if calibrated_distance >= 15:
        print("Eavesdrop!")
        arm_down()
        time.sleep(0.5)
    elif calibrated_distance < 13:
        print("Arm up!")
        arm_up()
        time.sleep(0.5)
    time.sleep(SAMPLE_INTERVAL)
    
def rotate_clockwise(speed=255):
    # rotate motor 1 clockwise
    in1.value, in2.value = (False, True)
    ena.duty_cycle = CW_duty
    print("Rotating 1 CW at %f duty cycle" % (100 * CW_duty / max_int))
    CW_duty = CW_duty - duty_step
    # rotate motor 2 clockwise
    in3.value, in4.value = (False, True)
    enb.duty_cycle = CW_duty
    print("Rotating 2 CW at %f duty cycle" % (100 * CW_duty / max_int))
    CW_duty = CW_duty - duty_step
    # rotate motor 3 clockwise
    in5.value, in6.value = (False, True)
    ena2.duty_cycle = CW_duty
    print("Rotating 3 CW at %f duty cycle" % (100 * CW_duty / max_int))
    CW_duty = CW_duty - duty_step
    time.sleep(2)

def rotate_counter_clockwise(speed=255):
    # rotate motor 1 counterclockwise
    in1.value, in2.value = (True, False)
    ena.duty_cycle = CCW_duty
    print("Rotating 1 CCW at %f duty cycle" % (100 * CCW_duty / max_int))
    CCW_duty = CCW_duty - duty_step
    # rotate motor 2 counterclockwise
    in3.value, in4.value = (True, False)
    enb.duty_cycle = CCW_duty
    print("Rotating 2 CCW at %f duty cycle" % (100 * CCW_duty / max_int))
    CCW_duty = CCW_duty - duty_step
    # rotate motor 3 counterclockwise
    in5.value, in6.value = (True, False)
    ena2.duty_cycle = CCW_duty
    print("Rotating 3 CCW at %f duty cycle" % (100 * CCW_duty / max_int))
    CCW_duty = CCW_duty - duty_step
    time.sleep(2)

# Function to move forward
def move_forward(speed=255):
    # Motor 1 counterclockwise, Motor 2 clockwise, Motor 3 slide
    # rotate motor 1 counterclockwise
    in1.value, in2.value = (True, False)
    ena.duty_cycle = CCW_duty
    print("Rotating 1 CCW at %f duty cycle" % (100 * CCW_duty / max_int))
    CCW_duty = CCW_duty - duty_step
    # rotate motor 2 clockwise
    in3.value, in4.value = (False, True)
    enb.duty_cycle = CW_duty
    print("Rotating 2 CW at %f duty cycle" % (100 * CW_duty / max_int))
    CW_duty = CW_duty - duty_step
    time.sleep(2)

# Function to move backward
def move_backward(speed=255):
    # Motor 1 clockwise, Motor 2 counterclockwise, Motor 3 slide
    # rotate motor 1 clockwise
    in1.value, in2.value = (False, True)
    ena.duty_cycle = CW_duty
    print("Rotating 1 CW at %f duty cycle" % (100 * CW_duty / max_int))
    CW_duty = CW_duty - duty_step
    # rotate motor 2 counterclockwise
    in3.value, in4.value = (True, False)
    enb.duty_cycle = CCW_duty
    print("Rotating 2 CCW at %f duty cycle" % (100 * CCW_duty / max_int))
    CCW_duty = CCW_duty - duty_step
    time.sleep(2)

# Function to move left
def move_left(speed=255):
    # Motor 1 clockwise, Motor 2 clockwise, Motor 3 counterclockwise at half speed
    # rotate motor 1 clockwise
    in1.value, in2.value = (False, True)
    ena.duty_cycle = CW_duty
    print("Rotating 1 CW at %f duty cycle" % (100 * CW_duty / max_int))
    CW_duty = CW_duty - duty_step
    # rotate motor 2 clockwise
    in3.value, in4.value = (False, True)
    enb.duty_cycle = CW_duty
    print("Rotating 2 CW at %f duty cycle" % (100 * CW_duty / max_int))
    CW_duty = CW_duty - duty_step
    time.sleep(2)
    # rotate motor 3 counterclockwise
    in5.value, in6.value = (True, False)
    ena2.duty_cycle = CCW_duty
    print("Rotating 3 CCW at %f duty cycle" % (100 * (CCW_duty // 2) / max_int))
    CCW_duty = CCW_duty - duty_step
    time.sleep(2)

# Function to move right
def move_right(speed=255):
    # Motor 1 counterclockwise, Motor 2 counterclockwise, Motor 3 clockwise at half speed
    # rotate motor 1 counterclockwise
    in1.value, in2.value = (True, False)
    ena.duty_cycle = CCW_duty
    print("Rotating 1 CCW at %f duty cycle" % (100 * CCW_duty / max_int))
    CCW_duty = CCW_duty - duty_step
    # rotate motor 2 counterclockwise
    in3.value, in4.value = (True, False)
    enb.duty_cycle = CCW_duty
    print("Rotating 2 CCW at %f duty cycle" % (100 * CCW_duty / max_int))
    CCW_duty = CCW_duty - duty_step
    # rotate motor 3 clockwise
    in5.value, in6.value = (False, True)
    ena2.duty_cycle = CW_duty
    print("Rotating 3 CW at %f duty cycle" % (100 * (CW_duty // 2) / max_int))
    CW_duty = CW_duty - duty_step
    time.sleep(2)

def arm_up():
    my_servo.angle = 110
            
def arm_down():
    my_servo.angle = 0

def rotation_test():
    rotate_clockwise()
    time.sleep(2)
    rotate_counter_clockwise()
    time.sleep(2)

def movement_test():
    move_forward()
    time.sleep(2)
    move_backward()
    time.sleep(2)
    move_left()
    time.sleep(2)
    move_right()
    time.sleep(2)

async def check_buttons():
    global button1_pressed, last_button1_state
    global button2_pressed, last_button2_state
    global button3_pressed, last_button3_state

    # Initialize button states
    button1_pressed = False
    button2_pressed = False
    button3_pressed = False
    last_button1_state = button1.value
    last_button2_state = button2.value
    last_button3_state = button3.value

    while True:
        # Check button 1
        current_button1_state = button1.value
        if not current_button1_state and last_button1_state:  # Detect button press (falling edge)
            button1_pressed = not button1_pressed  # Toggle the state
            print(f"Button 1 pressed. Running: {button1_pressed}")
            await asyncio.sleep(0.05)  # Debounce delay
        last_button1_state = current_button1_state  # Update the last button state

        # Check button 2
        current_button2_state = button2.value
        if not current_button2_state and last_button2_state:  # Detect button press (falling edge)
            if button3_pressed:  # If button 3 is pressed, set it to false
                button3_pressed = False
            button2_pressed = not button2_pressed  # Toggle the state
            print(f"Button 2 pressed. Running: {button2_pressed}")
            await asyncio.sleep(0.05)  # Debounce delay
        last_button2_state = current_button2_state  # Update the last button state

        # Check button 3
        current_button3_state = button3.value
        if not current_button3_state and last_button3_state:  # Detect button press (falling edge)
            if button2_pressed:  # If button 2 is pressed, set it to false
                button2_pressed = False
            button3_pressed = not button3_pressed  # Toggle the state
            print(f"Button 3 pressed. Running: {button3_pressed}")
            await asyncio.sleep(0.05)  # Debounce delay
        last_button3_state = current_button3_state  # Update the last button state

        await asyncio.sleep(0.01)  # Small delay to prevent busy-waiting

async def main_functions():
    while True:
        # State: ultrasonic
        if button1_pressed and not button2_pressed and not button3_pressed:
            ultrasonic_test()
            await asyncio.sleep(SAMPLE_INTERVAL)
        
        # State: rotation test
        elif not button1_pressed and button2_pressed and not button3_pressed:
            rotation_test()
            await asyncio.sleep(SAMPLE_INTERVAL)
            
        # State: rotation test w/ ultrasonic
        elif button1_pressed and button2_pressed and not button3_pressed:
            ultrasonic_test()
            rotation_test()
            await asyncio.sleep(SAMPLE_INTERVAL)

        # State: movement test
        elif not button1_pressed and not button2_pressed and button3_pressed:
            movement_test()
            await asyncio.sleep(SAMPLE_INTERVAL)

        # State: movement test w/ ultrasonic
        elif button1_pressed and not button2_pressed and button3_pressed:
            ultrasonic_test()
            movement_test()
            await asyncio.sleep(SAMPLE_INTERVAL)
        else:
            await asyncio.sleep(0.1)  # Check less frequently if button is not pressed

