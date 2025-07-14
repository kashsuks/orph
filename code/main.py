# main.py for Raspberry Pi Pico (MicroPython)
# Controls a servo motor using text commands from the computer.
# All LED and button functionality has been removed.
import machine
import time
import sys     # For reading serial input
import uselect # For non-blocking serial read
# --- Pin Definitions ---
# Servo motor signal pin (connect to GP2 / Physical Pin 4)
SERVO_PIN = machine.Pin(2)
# --- Global State Variables ---
continuous_swinging = False
# --- Servo Configuration ---
# PWM frequency for servo (standard is 50Hz)
PWM_FREQ = 50
# Duty cycle range for typical hobby servos (SG90/MG90S)
# These values might need slight adjustment for your specific servo.
# The `duty_u16` range is 0-65535.
def map_angle_to_duty(angle):
    """Maps an angle (0-180) to a 16-bit PWM duty cycle."""
    # Adjust these values (1500 and 8500) to get the full range of your servo.
    min_duty = 1500 # Corresponds to approx 0.5ms pulse
    max_duty = 8500 # Corresponds to approx 2.5ms pulse
    # Linear interpolation
    duty = int(min_duty + (max_duty - min_duty) * (angle / 180))
    return duty
# Initialize PWM for the servo
pwm = machine.PWM(SERVO_PIN)
pwm.freq(PWM_FREQ)
# --- Servo Swing Function ---
def swing_sword(start_angle, end_angle, swing_time_ms=500):
    """
    Swings the servo between start_angle and end_angle.
    swing_time_ms: total time for one swing (e.g., 500ms for 0.5 seconds)
    """
    steps = 30 # Number of steps for smoother movement
    # Calculate delay per step for forward and reverse motion
    delay_ms = swing_time_ms / (2 * steps)
    # Swing forward
    for i in range(steps + 1):
        angle = int(start_angle + (end_angle - start_angle) * (i / steps))
        pwm.duty_u16(map_angle_to_duty(angle))
        time.sleep_ms(int(delay_ms))
    # Swing back
    for i in range(steps + 1): # Ensure it returns to the start_angle
        angle = int(end_angle - (end_angle - start_angle) * (i / steps))
        pwm.duty_u16(map_angle_to_duty(angle))
        time.sleep_ms(int(delay_ms))
# --- Serial Command Processing ---
def process_serial_command(command):
    global continuous_swinging
    if command == 's': # Single swing
        print("Command: Single swing initiated.")
        swing_sword(SWING_ANGLE_1, SWING_ANGLE_2)
        print("Single swing complete.")
    elif command == 'c': # Continuous swinging
        print("Command: Continuous swinging started.")
        continuous_swinging = True
    elif command == 'x': # Stop continuous swinging
        print("Command: Continuous swinging stopped.")
        continuous_swinging = False
        pwm.duty_u16(map_angle_to_duty(90)) # Return servo to center
    else:
        print(f"Unknown command: '{command}'. Use 's' for single, 'c' for continuous, 'x' to stop.")
# --- Main Program Loop ---
# Define swing angles (adjust these for your servo and desired swing)
SWING_ANGLE_1 = 30  # One end of the swing
SWING_ANGLE_2 = 150 # The other end of the swing
# Initial position for the servo
pwm.duty_u16(map_angle_to_duty(90)) # Start at 90 degrees (center)
time.sleep(1) # Give servo time to move
print("Starting Pico Servo Control. Send commands via serial: 's', 'c', 'x'")
# Setup polling for non-blocking serial input
poll_obj = uselect.poll()
poll_obj.register(sys.stdin, uselect.POLLIN)
while True:
    # --- Handle Serial Input ---
    if poll_obj.poll(0): # Check for input with 0ms timeout (non-blocking)
        # Read the entire line from stdin and strip whitespace (including newline)
        full_command_line = sys.stdin.readline().strip()
        if full_command_line:
            # Process only the first character if multiple are typed before Enter
            command = full_command_line[0]
            process_serial_command(command)
    # --- Handle Continuous Swinging ---
    if continuous_swinging:
        swing_sword(SWING_ANGLE_1, SWING_ANGLE_2)
        time.sleep(0.5) # Short pause between continuous swings
    time.sleep_ms(50) # Small delay to prevent busy-waiting and allow other tasks






