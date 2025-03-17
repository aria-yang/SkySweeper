'''
Improved Ultrasonic Sensor Distance Detection
Features:
- Enhanced small distance detection
- Improved error handling
- Optional averaging for stability
- Maintained calibration formula
'''
import time
import board
import adafruit_hcsr04
import array

# Configuration
TRIGGER_PIN = board.GP2
ECHO_PIN = board.GP3
SAMPLE_INTERVAL = 0.5  # Faster sampling for better responsiveness
NUM_SAMPLES = 3        # Number of samples to average (reduces noise)
MIN_DISTANCE = 2       # Minimum distance in cm the sensor can reliably detect
TIMEOUT = 1.0          # Timeout for sensor readings in seconds

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
