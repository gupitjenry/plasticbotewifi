#!/usr/bin/env python3
"""
E3F-DS100C4 NPN NO Proximity Sensor Reading
Outputs JSON for bottle detection
- LOW (0) when bottle detected → True
- HIGH (1) when no bottle → False
"""

import RPi.GPIO as GPIO
import time
import json
import sys
import signal
import uuid

# -------------------
# Configuration
# -------------------
SENSOR_PIN = 17         # GPIO pin
DEBOUNCE_READS = 3      # Number of readings for debounce
DEBOUNCE_DELAY = 0.05   # 50ms between readings

# -------------------
# Setup GPIO
# -------------------
try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
except Exception as e:
    print(json.dumps({
        'detected': False,
        'error': f'GPIO setup failed: {str(e)}'
    }))
    sys.exit(1)

# -------------------
# Graceful exit
# -------------------
def signal_handler(sig, frame):
    try:
        GPIO.cleanup()
    except:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# -------------------
# Helper function
# -------------------
def bottle_detected():
    """
    Read sensor with debouncing
    NPN NO: LOW (0) = bottle detected, HIGH (1) = no bottle
    """
    try:
        readings = []
        for _ in range(DEBOUNCE_READS):
            state = GPIO.input(SENSOR_PIN)
            readings.append(state == 0)  # LOW = bottle detected
            time.sleep(DEBOUNCE_DELAY)
        return all(readings)
    except Exception as e:
        print(json.dumps({
            'detected': False,
            'error': f'Sensor read failed: {str(e)}'
        }))
        sys.exit(1)

# -------------------
# Main execution
# -------------------
try:
    detected = bottle_detected()
    
    # Generate verification token if bottle detected
    verification_token = str(uuid.uuid4()) if detected else None
    
    # Output JSON (MUST be single line, valid JSON)
    output = {
        'detected': detected,
        'sensor_type': 'E3F-DS100C4 NPN NO',
        'gpio_state': 'LOW' if detected else 'HIGH',
        'status': 'bottle_detected' if detected else 'waiting',
        'verification_token': verification_token,
        'pin': SENSOR_PIN
    }
    
    # Output as single line JSON (critical for PHP parsing)
    print(json.dumps(output, separators=(',', ':')))
    sys.stdout.flush()
    
except Exception as e:
    # Output error as valid JSON
    error_output = {
        'detected': False,
        'error': f'Script error: {str(e)}',
        'sensor_type': 'E3F-DS100C4 NPN NO'
    }
    print(json.dumps(error_output, separators=(',', ':')))
    sys.exit(1)

finally:
    try:
        GPIO.cleanup()
    except:
        pass
