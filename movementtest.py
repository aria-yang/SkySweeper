# Write your code here :-)
import time
import board
import adafruit_hcsr04
import array
import digitalio
import pwmio
import servo

# Configuration
TRIGGER_PIN = board.GP19
ECHO_PIN = board.GP18
SAMPLE_INTERVAL = 0.5  # Faster sampling for better responsiveness
NUM_SAMPLES = 3        # Number of samples to average (reduces noise)
MIN_DISTANCE = 2       # Minimum distance in cm the sensor can reliably detect
TIMEOUT = 1.0          # Timeout for sensor readings in seconds

# set up button as digital input with pull-up resistor
button = digitalio.DigitalInOut(board.GP26)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP
button2 = digitalio.DigitalInOut(board.GP28)
button2.direction = digitalio.Direction.INPUT
button2.pull = digitalio.Pull.UP
button3 = digitalio.DigitalInOut(board.GP27)
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
in5 = digitalio.DigitalInOut(board.GP21)
in6 = digitalio.DigitalInOut(board.GP22)
in5.direction = digitalio.Direction.OUTPUT
in6.direction = digitalio.Direction.OUTPUT

# set up motor driving signal as PWM output for DC motor 1
ena = pwmio.PWMOut(board.GP16, duty_cycle=0)
enb = pwmio.PWMOut(board.GP10, duty_cycle=0)
ena2 = pwmio.PWMOut(board.GP20, duty_cycle=0)

# create a PWMOut object for servomotor
pwm = pwmio.PWMOut(board.GP6, duty_cycle=0, frequency=50)

# Create a servo object, my_servo.
my_servo = servo.Servo(pwm)
my_servo.angle = 110  # Initialize servo position

# set time limits
start_time = time.time()
time_limit = 18
time_limit2 = 32

# set starting (fastest) motor duty cycles
CW_duty_wood = 50000
CW_duty = 39000
CCW_duty_wood = 50000
CCW_duty = 39000
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


def rotate_clockwise(speed=255):
    # rotate motor 1 clockwise
    in1.value, in2.value = (False, True)
    ena.duty_cycle = CCW_duty
    print("Rotating 1 CW at %f duty cycle" % (100 * CCW_duty / max_int))
    # rotate motor 2 clockwise
    in3.value, in4.value = (False, True)
    enb.duty_cycle = CW_duty
    print("Rotating 2 CW at %f duty cycle" % (100 * CW_duty / max_int))
    # rotate motor 3 clockwise
    in5.value, in6.value = (False, True)
    ena2.duty_cycle = CW_duty
    print("Rotating 3 CW at %f duty cycle" % (100 * CW_duty_wood / max_int))
    time.sleep(2)


def rotate_counter_clockwise(speed=255):
    # rotate motor 1 counterclockwise
    in1.value, in2.value = (True, False)
    ena.duty_cycle = CW_duty
    print("Rotating 1 CCW at %f duty cycle" % (100 * CW_duty / max_int))
    # rotate motor 2 counterclockwise
    in3.value, in4.value = (True, False)
    enb.duty_cycle = CCW_duty
    print("Rotating 2 CCW at %f duty cycle" % (100 * CCW_duty / max_int))
    CCW_duty = CCW_duty - duty_step
    # rotate motor 3 counterclockwise
    in5.value, in6.value = (True, False)
    ena2.duty_cycle = CCW_duty
    print("Rotating 3 CCW at %f duty cycle" % (100 * CCW_duty_wood / max_int))
    CCW_duty = CCW_duty - duty_step
    time.sleep(2)


# Function to move forward
def move_forward(speed=255):
    # Motor 1 counterclockwise, Motor 2 clockwise, Motor 3 slide
    # rotate motor 1 counterclockwise
    in1.value, in2.value = (True, False)
    ena.duty_cycle = CW_duty
    print("Rotating 1 CCW at %f duty cycle" % (100 * CW_duty / max_int))
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
    ena.duty_cycle = CCW_duty
    print("Rotating 1 CW at %f duty cycle" % (100 * CCW_duty / max_int))
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
    ena.duty_cycle = CCW_duty
    print("Rotating 1 CW at %f duty cycle" % (100 * CCW_duty / max_int))
    # rotate motor 2 clockwise
    in3.value, in4.value = (False, True)
    enb.duty_cycle = CW_duty
    print("Rotating 2 CW at %f duty cycle" % (100 * CW_duty / max_int))
    CW_duty = CW_duty
    time.sleep(2)
    # rotate motor 3 counterclockwise
    in5.value, in6.value = (True, False)
    ena2.duty_cycle = CCW_duty
    print("Rotating 3 CCW at %f duty cycle" % (100 * (CCW_duty_wood // 2) / max_int))
    CCW_duty = CCW_duty
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
    print("Rotating 3 CW at %f duty cycle" % (100 * (CW_duty_wood // 2) / max_int))
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

def arm_test():
    if calibrated_distance >= 21:
        lower_arm()
    elif calibrated_distance < 20.5:
        raise_arm()
    else:
        print("Distance is within range, no action taken.")
        
# Add a state variable to track the button press
button_pressed = False
last_button_state = button.value  # Store the initial button state

# Main loop
while True:
    # Check for button press
    current_button_state = button.value
    if not current_button_state and last_button_state:  # Detect button press (falling edge)
        button_pressed = not button_pressed  # Toggle the state
        print(f"Button pressed. Running: {button_pressed}")
        time.sleep(0.05)  # Debounce delay

    last_button_state = current_button_state  # Update the last button state

    if button_pressed:
        try:
            # Get distance reading with improved small distance detection
            raw_distance = get_averaged_distance()

            # Apply calibration
            calibrated_distance = calibrate_distance(raw_distance)

            # Print the result
            print(f"Distance: {calibrated_distance:.1f} cm")

        except RuntimeError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("Program stopped by user")
            break

        time.sleep(SAMPLE_INTERVAL)

        # WRITE CODE HERE FOR TEST
        movement_test()
        button_pressed = False  # Reset button pressed state
