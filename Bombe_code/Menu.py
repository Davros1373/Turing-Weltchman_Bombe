import lcddriver
import RPi.GPIO as GPIO
import os
from time import sleep

# Initialise the LCD
lcd = lcddriver.lcd()

# Path to the USB memory stick
usb_path = "/media/rpi4/USB DISK"  # Update this path if necessary

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(10, GPIO.IN)  # Scroll Button
GPIO.setup(25, GPIO.IN)  # Select Button


def list_files(path):
    """List files in the given directory."""
    try:
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    except FileNotFoundError:
        return []

def display_files_on_lcd(files, selected_index):
    """Display the list of files on the LCD screen, highlighting the selected one."""
    lcd.lcd_clear()
    max_lines = 4
    chunk_size = 20
    
    for i in range(max_lines):
        if i + selected_index < len(files):
            file_name = files[i + selected_index]
            if i == 0:
                # Highlight the selected file by adding an arrow or special marker
                lcd.lcd_display_string("-> " + file_name[:chunk_size], i + 1)
            else:
                lcd.lcd_display_string(file_name[:chunk_size], i + 1)

def display_selected_file_on_lcd(file_name):
    """Clear the LCD and display the selected file name."""
    lcd.lcd_clear()
    lcd.lcd_display_string(file_name[:20], 1)  # Display file name on the first line


files = list_files(usb_path)#
del files[0]
if not files:
	lcd.lcd_display_string("No files found!", 1)
	sleep(2)

selected_index = 0
display_files_on_lcd(files, selected_index)

try:
	while True:
		if GPIO.input(10) == GPIO.HIGH:  # Scroll Button pressed (GPIO10 is LOW)
			selected_index = (selected_index + 1) % len(files)
			display_files_on_lcd(files, selected_index)
			sleep(0.3)  # Debounce time to avoid rapid cycling
		
		if GPIO.input(25) == GPIO.HIGH:  # Select Button pressed (GPIO25 is LOW)
			display_selected_file_on_lcd(files[selected_index])
			while GPIO.input(25) == GPIO.HIGH:
				sleep(0.1)  # Wait until button is released
			
		sleep(0.1)  # Polling delay

except KeyboardInterrupt:
	print("Exiting...")
finally:
	GPIO.cleanup()
