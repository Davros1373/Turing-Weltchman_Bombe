import smbus
import time

# I2C address of the Tic T249 (default is 0x0E)
TIC_I2C_ADDRESS = 0x0E

# Initialise I2C bus
bus = smbus.SMBus(1)  # 1 indicates /dev/i2c-1

# Define registers
CMD_EXIT_SAFE_START = 0x83
CMD_ENERGIZE = 0x85
CMD_SET_TARGET_POSITION = 0xE0
CMD_GET_VARIABLE = 0xA1  # Command to read variables from Tic
CMD_SET_STEP_MODE = 0x94  # Command to set microstepping mode

# Tic variables offsets (for CMD_GET_VARIABLE)
CURRENT_POSITION = 0x22  # Current position register address (4 bytes)
ERROR_STATUS = 0x02      # Error status register address
INPUT_VOLTAGE = 0x24     # Input voltage register address (2 bytes)
CMD_SET_MAX_SPEED = 0xE6
CMD_SET_ACCELERATION = 0xEA
CMD_SET_DECELERATION = 0xEC
CMD_SET_STEP_MODE = 0x94  # Step mode command

# Function to write 32-bit value to Tic T249 via I2C
def write_i2c_command(command, value=None):
    """
    Sends an I2C command to the Tic T249 controller.
    
    Parameters:
    - command: The command byte to send.
    - value: An optional 32-bit integer value to accompany the command.
    """
    try:
        if value is None:
            # Send the command byte only
            bus.write_byte(TIC_I2C_ADDRESS, command)
            print(f"Sent command {hex(command)} without value.")
        else:
            # Prepare the 32-bit value as 4 separate bytes
            data = [
                (value >> 0) & 0xFF,   # Least significant byte
                (value >> 8) & 0xFF,
                (value >> 16) & 0xFF,
                (value >> 24) & 0xFF    # Most significant byte
            ]
            # Send the command byte followed by the 4 bytes of the value
            bus.write_i2c_block_data(TIC_I2C_ADDRESS, command, data)
            print(f"Sent command {hex(command)} with value {value}. Data sent: {data}")
    except OSError as e:
        # Catch OS errors like I2C bus errors
        print(f"Failed to send command {hex(command)}: I2C communication error: {e}")
    except Exception as e:
        # Catch any other exceptions
        print(f"Failed to send command {hex(command)}: {e}")


# Function to read a 32-bit value from the Tic T249
def read_i2c_value(variable_offset, num_bytes=4):
    try:
        # Send the request for the variable with a given offset
        bus.write_byte(TIC_I2C_ADDRESS, CMD_GET_VARIABLE)
        time.sleep(0.1)
        
        # Read the requested number of bytes (usually 4 bytes for a 32-bit variable)
        data = bus.read_i2c_block_data(TIC_I2C_ADDRESS, variable_offset, num_bytes)
        result = 0
        for i in range(num_bytes):
            result |= data[i] << (8 * i)
        return result
    except Exception as e:
        print(f"Failed to read variable: {e}")
        return None

# Exit safe start (required before movement)
def exit_safe_start():
    write_i2c_command(CMD_EXIT_SAFE_START)
    time.sleep(0.2)  # Delay for safe start

# Energize the motor (turn it on)
def energize_motor():
    write_i2c_command(CMD_ENERGIZE)
    time.sleep(0.2)  # Delay for energizing motor

# Set step mode to full-step (0 for full step)
def set_step_mode(mode=0):
    write_i2c_command(CMD_SET_STEP_MODE, mode)
    print(f"Step mode set to {mode}")

# Move the motor to a specific absolute position
def move_to_position(position):
    write_i2c_command(CMD_SET_TARGET_POSITION, position)
    time.sleep(0.5)  # Delay for movement

# Read the current position of the motor
def get_current_position():
    return read_i2c_value(CURRENT_POSITION)

# Read error status
def get_error_status():
    return read_i2c_value(ERROR_STATUS, 2)  # Error status is 2 bytes

# Read input voltage (to check for power issues)
def get_input_voltage():
    voltage_raw = read_i2c_value(INPUT_VOLTAGE, 2)
    # Convert raw voltage value to readable format (millivolts)
    return voltage_raw / 1000.0  # Convert to volts

# Set max speed and acceleration
def set_motor_parameters(speed, acceleration):
    set_max_speed(speed)
    set_acceleration(acceleration)

# Function to set speed
def set_max_speed(speed):
    write_i2c_command(CMD_SET_MAX_SPEED, speed)

# Function to set acceleration and deceleration
def set_acceleration(acceleration):
    write_i2c_command(CMD_SET_ACCELERATION, acceleration)
    write_i2c_command(CMD_SET_DECELERATION, acceleration)
    
# Main sequence
def main():
    energize_motor()         # Energize the motor
    exit_safe_start()        # Disable safe start
    set_step_mode(0)         # Set to full-step mode (0 means full step)
    set_motor_parameters(10000, 1000)  # Set low speed and acceleration

    print("Current position before move:", get_current_position())

    # Check input voltage
    input_voltage = get_input_voltage()
    print(f"Input voltage: {input_voltage}V")

    # Move motor to position 1000 (or any target position)
    current_position = get_current_position()
    move_to_position(1000 + current_position)

    time.sleep(2)  # Wait for the movement to finish

    # Read back the current position to verify if movement occurred
    current_position = get_current_position()
    print(f"Motor moved to position {current_position}")

    # Check if there are any error flags
    error_status = get_error_status()
    print(f"Error status: {hex(error_status)}")



# Run the main sequence
main()
