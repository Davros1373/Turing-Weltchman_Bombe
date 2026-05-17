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
    
def simple_test_motor():
    write_i2c_command(0x85)
    write_i2c_command(0x83)
    set_motor_parameters(1000000, 1000000)  # Set low speed and acceleration

    # Test moving a small number of steps
    target_position = 10  # Move to position 100
    write_i2c_command(CMD_SET_TARGET_POSITION, target_position)

    time.sleep(1)  # Wait for the movement to complete


# Run the simple test
simple_test_motor()
