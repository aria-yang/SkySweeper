import time
import board
import adafruit_hcsr04
import array
import pwmio
import digitalio
from adafruit_motor import servo

# Configuration for ultrasonic sensor
TRIGGER_PIN = board.GP18
ECHO_PIN = board.GP19
SAMPLE_INTERVAL = 0.5  # Faster sampling for better responsiveness
NUM_SAMPLES = 3        # Number of samples to average (reduces noise)
MIN_DISTANCE = 2       # Minimum distance in cm the sensor can reliably detect
TIMEOUT = 1.0          # Timeout for sensor readings in seconds

# Define GPIO pins for motor control
pins = {
    'out1_positive': 17,  # Motor 1 forward
    'out1_negative': 18,  # Motor 1 reverse
    'out2_positive': 27,  # Motor 2 forward
    'out2_negative': 22,  # Motor 2 reverse
    'out3_positive': 23,  # Motor 3 forward
    'out3_negative': 24   # Motor 3 reverse
}

# Initialize PWM (100Hz frequency)
pwm = {}
for name, pin in pins.items():
    GPIO.setup(pin, GPIO.OUT)
    pwm[name] = GPIO.PWM(pin, 100)  # 100Hz PWM
    pwm[name].start(0)              # Start with 0% duty cycle

# create a PWMOut object on Pin A2 for servomotor
pwm = pwmio.PWMOut(board.GP14, duty_cycle=2 ** 15, frequency=50)
# Create a servo object, my_servo.
my_servo = servo.Servo(pwm)

# # set up direction pins as digital outputs for DC motors
# in1 = digitalio.DigitalInOut(board.GP14)
# in2 = digitalio.DigitalInOut(board.GP15)
# in1.direction = digitalio.Direction.OUTPUT
# in2.direction = digitalio.Direction.OUTPUT

# # set up motor driving signal as PWM output for DC motor
# ena = pwmio.PWMOut(board.GP16, duty_cycle = 0)

# # set time limits for DC motors
# start_time = time.time()
# time_limit = 20

# # set starting (fastest) motor duty cycles for DC motors
# CW_duty = 50000
# CCW_duty = 50000
# duty_step = 5000
# max_int = 65535

# Initialize sensor
sonar = adafruit_hcsr04.HCSR04(trigger_pin=TRIGGER_PIN, echo_pin=ECHO_PIN, timeout=TIMEOUT)

# Buffer for averaging readings
distance_buffer = array.array('f', [0] * NUM_SAMPLES)
buffer_index = 0

def calibrate_distance(raw_distance):
    """Apply calibration formula to raw distance measurement"""
    # Using the same calibration formula
    return 1.084 * (raw_distance - 9.044) + 10

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

def raise_arm():
    for angle in range (0, 120, 5): # 0 − 180 degrees, 5 degrees at a time.
        my_servo.angle = angle
        time. sleep (0.05)
def lower_arm():
    for angle in range (120 , 0, -5): # 180 - 0 degrees, 5 degrees at a time.
        my_servo.angle = angle
        time.sleep (0.05)

# Function to stop all DC motors
def stop():
    for name in pwm:
        pwm[name].ChangeDutyCycle(0)

# Function to move forward
def move_forward(speed=255):
    # speed: 0 to 255, controls how fast it moves
    out1 = speed   # Motor 1 forward
    out2 = speed   # Motor 2 forward
    out3 = speed   # Motor 3 forward
    control_motors(out1, out2, out3)

# Function to move backward
def move_backward(speed=255):
    out1 = -speed  # Motor 1 reverse
    out2 = -speed  # Motor 2 reverse
    out3 = -speed  # Motor 3 reverse
    control_motors(out1, out2, out3)

# Function to move left
def move_left(speed=255):
    out1 = speed   # Motor 1 forward
    out2 = -speed  # Motor 2 reverse
    out3 = 0       # Motor 3 stopped
    control_motors(out1, out2, out3)

# Function to move right
def move_right(speed=255):
    out1 = -speed  # Motor 1 reverse
    out2 = speed   # Motor 2 forward
    out3 = 0       # Motor 3 stopped
    control_motors(out1, out2, out3)

# Function to control the motors
def control_motors(out1, out2, out3):
    # Limit the range to -255 to 255
    out1 = max(-255, min(255, out1))
    out2 = max(-255, min(255, out2))
    out3 = max(-255, min(255, out3))

    # Motor 1 control
    if out1 >= 0:
        pwm['out1_positive'].ChangeDutyCycle(out1 / 255 * 100)
        pwm['out1_negative'].ChangeDutyCycle(0)
    else:
        pwm['out1_positive'].ChangeDutyCycle(0)
        pwm['out1_negative'].ChangeDutyCycle(abs(out1) / 255 * 100)

    # Motor 2 control
    if out2 >= 0:
        pwm['out2_positive'].ChangeDutyCycle(out2 / 255 * 100)
        pwm['out2_negative'].ChangeDutyCycle(0)
    else:
        pwm['out2_positive'].ChangeDutyCycle(0)
        pwm['out2_negative'].ChangeDutyCycle(abs(out2) / 255 * 100)

    # Motor 3 control
    if out3 >= 0:
        pwm['out3_positive'].ChangeDutyCycle(out3 / 255 * 100)
        pwm['out3_negative'].ChangeDutyCycle(0)
    else:
        pwm['out3_positive'].ChangeDutyCycle(0)
        pwm['out3_negative'].ChangeDutyCycle(abs(out3) / 255 * 100)

# Main loop
def main():
    try:
        print("Starting the program...")
        while True:
            try:
                # Get distance reading with improved small distance detection
                raw_distance = get_averaged_distance()

                # Apply calibration
                calibrated_distance = calibrate_distance(raw_distance)

                # Print the result
                print(f"Distance: {calibrated_distance:.1f} cm")

                # Example: Test each direction based on distance
                if calibrated_distance > 50:
                    move_forward(200)  # Move forward at speed 200
                elif 20 < calibrated_distance <= 50:
                    move_left(200)     # Move left
                else:
                    stop()             # Stop if too close

            except RuntimeError as e:
                print(f"Error: {e}")
            time.sleep(SAMPLE_INTERVAL)

    except KeyboardInterrupt:
        print("Program stopped by user")
    finally:
        stop()          # Ensure all motors stop
        for p in pwm.values():
            p.stop()    # Stop PWM signals
        GPIO.cleanup()  # Clean up GPIO resources

if __name__ == "__main__":
    main()
