import RPi.GPIO as GPIO
import time

# GPIO pin configuration
MUX1_SIG_PIN = 9  # Signal pin for the first multiplexer
MUX2_SIG_PIN = 11  # Signal pin for the second multiplexer

# Address pins (S0, S1, S2, S3) shared between the multiplexers
MUX_ADDR_PINS = [22, 23, 8, 24]

# Number of channels
NUM_CHANNELS = 16  # Number of channels per multiplexer

# Inputs mapped to each multiplexer channel
MUX1_INPUTS = [None, 'E', 'A', 'I', 'HO', 'G', 'C', 'K', None, 'F', 'B', 'J', 'CA', 'H', 'D', 'L']
MUX2_INPUTS = ['Z', 'R', 'V', 'N', 'X', 'P', 'T', None, 'Y', 'Q', 'U', 'M', 'W', 'O', 'S']

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(MUX1_SIG_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(MUX2_SIG_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
for pin in MUX_ADDR_PINS:
    GPIO.setup(pin, GPIO.OUT)

# Function to select a channel on the multiplexer
def select_channel(channel):
    binary_channel = [int(bit) for bit in format(channel, '04b')]
    for i in range(4):
        GPIO.output(MUX_ADDR_PINS[i], binary_channel[i])

# Function to read all inputs from two multiplexers
def read_multiplexers():
    active_inputs = []
    for channel in range(NUM_CHANNELS):
        select_channel(channel)
        time.sleep(0.1)  # Small delay to allow for stable reading
        value_mux1 = GPIO.input(MUX1_SIG_PIN)
        value_mux2 = GPIO.input(MUX2_SIG_PIN)
        
        if value_mux1 == GPIO.HIGH and MUX1_INPUTS[channel] is not None:
            active_inputs.append(MUX1_INPUTS[channel])
        
        if value_mux2 == GPIO.HIGH and MUX2_INPUTS[channel] is not None:
            active_inputs.append(MUX2_INPUTS[channel])
    
    return active_inputs

try:
    active_inputs = []
    while not active_inputs:  # Loop until active_inputs is not empty
        active_inputs = read_multiplexers()
        if active_inputs:
            print("The active inputs are:", ", ".join(active_inputs))
        time.sleep(0.1)  # Adjust the read interval as needed
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
