import os
import time
import smbus2
import RPi.GPIO as GPIO

# I2C and LCD configuration
I2C_ADDR = 0x27  # I2C address of the LCD
LCD_WIDTH = 16   # Max characters per line
LCD_LINES = 4    # Number of display lines

# GPIO setup
BUTTON_NEXT = 10
BUTTON_SELECT = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_NEXT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_SELECT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Initialise I2C (SMBus)
bus = smbus2.SMBus(1)

# LCD Commands
LCD_CHR = 1  # Mode - Sending data
LCD_CMD = 0  # Mode - Sending command

LCD_LINE = [0x80, 0xC0, 0x94, 0xD4]  # Memory addresses for LCD lines
LCD_BACKLIGHT = 0x08  # On
ENABLE = 0b00000100  # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# LCD initialization
def lcd_init():
    lcd_byte(0x33, LCD_CMD)  # 110011 Initialize
    lcd_byte(0x32, LCD_CMD)  # 110010 Initialize
    lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
    lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
    lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    time.sleep(E_DELAY)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(E_PULSE)
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
    time.sleep(E_DELAY)

def lcd_string(message, line):
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(LCD_LINE[line], LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)

# Helper function to list files
def list_files(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

# Main function
def main():
    # Mount point of the USB drive
    usb_path = "/media/pi/YOUR_USB_DRIVE_NAME"
    
    # Initialize the LCD display
    lcd_init()
    
    # Get list of files
    files = list_files(usb_path)
    if not files:
        lcd_string("No files found", 0)
        return

    # File selection variables
    selected_file_idx = 0

    while True:
        # Display current file on the LCD
        lcd_string(files[selected_file_idx][:LCD_WIDTH], 0)

        # Scroll through files
        if GPIO.input(BUTTON_NEXT) == GPIO.HIGH:
            selected_file_idx = (selected_file_idx + 1) % len(files)
            time.sleep(0.2)  # Debounce delay

        # Select file
        if GPIO.input(BUTTON_SELECT) == GPIO.HIGH:
            lcd_string("Selected:", 1)
            lcd_string(files[selected_file_idx][:LCD_WIDTH], 2)
            break

    # Add your file handling logic here
    # Example: Open or execute the selected file
    selected_file = os.path.join(usb_path, files[selected_file_idx])
    lcd_string("Opening file...", 3)
    time.sleep(1)
    # os.system(f"xdg-open '{selected_file}'")  # Uncomment to open file

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        lcd_byte(0x01, LCD_CMD)  # Clear the display
        GPIO.cleanup()
