import time
import board
import adafruit_hcsr04
import array
import digitalio
import pwmio
import digitalio

# Configuration
TRIGGER_PIN = board.GP18
ECHO_PIN = board.GP19
SAMPLE_INTERVAL = 0.5  # Faster sampling for better responsiveness
NUM_SAMPLES = 3        # Number of samples to average (reduces noise)
MIN_DISTANCE = 2       # Minimum distance in cm the sensor can reliably detect
TIMEOUT = 1.0          # Timeout for sensor readings in seconds

# set up direction pins as digital outputs for DC motor 1
in1 = digitalio.DigitalInOut(board.GP14)
in2 = digitalio.DigitalInOut(board.GP15)
in1.direction = digitalio.Direction.OUTPUT
in2.direction = digitalio.Direction.OUTPUT

# set up direction pins as digital outputs for DC motor 2
in3 = digitalio.DigitalInOut(board.GP12)
in4 = digitalio.DigitalInOut(board.GP13)
in3.direction = digitalio.Direction.OUTPUT
in4.direction = digitalio.Direction.OUTPUT

# set up motor driving signal as PWM output for DC motor 1
ena = pwmio.PWMOut(board.GP16, duty_cycle = 0)
enb = pwmio.PWMOut(board.GP17, duty_cycle = 0)

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

# Main loop
while True:
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

    # rotate motor shaft in alternating directions with decreasing speed
    while (time.time() - start_time) < time_limit:
        # rotate motor 1
        # rotate clockwise
        in1.value, in2.value = (False, True)
        ena.duty_cycle = CW_duty
        print("Rotating 1 CW at %f duty cycle"%(100*CW_duty/max_int))
        CW_duty = CW_duty - duty_step
        time.sleep(2)

        # rotate counterclockwise
        in1.value, in2.value = (True, False)
        ena.duty_cycle = CCW_duty
        print("Rotating 1 CCW at %f duty cycle"%(100*CCW_duty/max_int))
        CCW_duty = CCW_duty - duty_step
        time.sleep(2)

        # rotate motor 2
        # rotate clockwise
        in3.value, in4.value = (False, True)
        enb.duty_cycle = CW_duty
        print("Rotating 2 CW at %f duty cycle"%(100*CW_duty/max_int))
        CW_duty = CW_duty - duty_step
        time.sleep(2)

        # rotate counterclockwise
        in3.value, in4.value = (True, False)
        enb.duty_cycle = CCW_duty
        print("Rotating 2 CCW at %f duty cycle"%(100*CCW_duty/max_int))
        CCW_duty = CCW_duty - duty_step
        time.sleep(2)
