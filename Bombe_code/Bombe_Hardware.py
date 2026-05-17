# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 14:39:17 2024

@author: chris
"""
import lcddriver
from time import *
import lcddriver
import RPi.GPIO as GPIO
import os
import threading


while True:
	lcd = lcddriver.lcd()
	lcd.lcd_clear()

	 
	lcd.lcd_display_string(" Turing - ", 1)
	lcd.lcd_display_string("       Welchman", 2)
	lcd.lcd_display_string("              Bombe", 3)
	lcd.lcd_display_string("V3.1-1B", 4)

	PUL1 = 4  # Stepper Drive Pulses
	PUL2 = 15
	PUL3 = 18
	ENA1 = 14  # Controller Enable Bit (LOW to Enable / HIGH to Disable).
	ENA2 = 5
	ENA3 = 26

	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	#GPIO.cleanup()

	GPIO.setup(PUL1, GPIO.OUT)
	GPIO.setup(PUL2, GPIO.OUT)
	GPIO.setup(PUL3, GPIO.OUT)
	GPIO.setup(ENA1, GPIO.OUT)
	GPIO.setup(ENA2, GPIO.OUT)
	GPIO.setup(ENA3, GPIO.OUT)

	GPIO.output(ENA1, GPIO.LOW)
	GPIO.output(ENA2, GPIO.LOW)
	GPIO.output(ENA3, GPIO.LOW)

	#os.system("ticcmd")
	# os.system("ticcmd --energize")
	# os.system("ticcmd --exit-safe-start")

	# os.system("ticcmd --step-mode 2")
	# os.system("ticcmd --max-speed 3000000")
	# os.system("ticcmd --starting-speed 3000000")
	# os.system("ticcmd --halt-and-set-position 0")

	durationFwd = 15 # This is the duration of the motor spinning.
	delay = 1/500 # This is actualy a delay between PUL pulses - effectively sets the mtor rotation speed.


	sleep(1.5)
	lcd.lcd_clear()

	# Path to the USB memory stick
	usb_path = "/media/pi/MENU_USB"  # Update this path if necessary

	# GPIO setup
	GPIO.setup(10, GPIO.IN)  # Scroll Button
	GPIO.setup(25, GPIO.IN)  # Select Button

	import subprocess

	def list_and_clean(directory, target_to_remove):
		try:
			# List items in the directory
			items = os.listdir(directory)
			# print(f"Items in {directory}: {items}")

			# Attempt to open each item
			for item in items:
				item_path = os.path.join(directory, item)
				try:
					# Try accessing the directory or file
					if os.path.isdir(item_path):
						os.listdir(item_path)
						# print(f"Accessed {item_path}")
					# else:
						# print(f"{item_path} is not a directory.")
				except PermissionError:
					# print(f"Permission denied for {item_path}")
					# print(f"Removing {item_path} with sudo...")
					subprocess.run(['sudo', 'rm', '-rf', item_path], check=True)
					# print(f"{item_path} removed successfully.")
					

		except FileNotFoundError:
                        print("Error")
			# print(f"The directory {directory} does not exist.")
		except Exception as e:
                        print("Error")
			# print(f"An error occurred: {e}")

	# Specify the directory and target directory name
	directory_to_check = "/media/pi/"
	target_directory_name = "MENU_USB"

	list_and_clean(directory_to_check, target_directory_name)

	def list_files(path):
		"""List files in the given directory."""
		try:
			return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
		except FileNotFoundError:
			return []
		except PermissionError:
			# print(f"Permission denied: '{path}'")
			# print(f"Removing {path} with sudo...")
			subprocess.run(['sudo', 'rm', '-rf', path], check=True)
			# print(f"{path} removed successfully.")
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

	while not files:
		lcd.lcd_display_string("No files found!", 1)
		lcd.lcd_display_string("Reloading...", 2)
		items = os.listdir(directory_to_check)
		if len(items) > 1:
			# print(f"Removing {usb_path}  with sudo...")
			subprocess.run(['sudo', 'rm', '-rf', usb_path ], check=True)
			# print(f"{usb_path} removed successfully.")
		sleep(2)
		files = list_files(usb_path)

	del files[0]

	selected_index = 0
	display_files_on_lcd(files, selected_index)

	try:
		while (GPIO.input(10) == GPIO.LOW):
			if GPIO.input(25) == GPIO.HIGH:  # Scroll Button pressed (GPIO10 is LOW)
				selected_index = (selected_index + 1) % len(files)
				display_files_on_lcd(files, selected_index)
				sleep(0.3)  # Debounce time to avoid rapid cycling
			
			if GPIO.input(10) == GPIO.HIGH:  # Select Button pressed (GPIO25 is LOW)
				display_selected_file_on_lcd(files[selected_index])
				while GPIO.input(10) == GPIO.HIGH:
					sleep(0.1)  # Wait until button is released
				
			sleep(0.1)  # Polling delay
	except KeyboardInterrupt:
		print("Exiting...")
	finally:
		GPIO.cleanup()

	menuFile = usb_path + '/' + files[selected_index]



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

	# Function to select a channel on the multiplexer
	def select_channel(channel):
		binary_channel = [int(bit) for bit in format(channel, '04b')]
		for i in range(4):
			GPIO.output(MUX_ADDR_PINS[i], binary_channel[i])

	# Function to read all inputs from two multiplexers
	def read_multiplexers():
			# Setup GPIO
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(MUX1_SIG_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		GPIO.setup(MUX2_SIG_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		for pin in MUX_ADDR_PINS:
			GPIO.setup(pin, GPIO.OUT)
			
		active_inputs = []
		for channel in range(NUM_CHANNELS):
			select_channel(channel)
			sleep(0.1)  # Small delay to allow for stable reading
			value_mux1 = GPIO.input(MUX1_SIG_PIN)
			value_mux2 = GPIO.input(MUX2_SIG_PIN)
			
			if value_mux1 == GPIO.HIGH and MUX1_INPUTS[channel] is not None:
				active_inputs.append(MUX1_INPUTS[channel])
			
			if value_mux2 == GPIO.HIGH and MUX2_INPUTS[channel] is not None:
				active_inputs.append(MUX2_INPUTS[channel])

		return active_inputs

	def should_stop(active_inputs):
		contains_letter = any(input.isalpha() for input in active_inputs if input not in ["CA", "HO"])
		contains_ca_ho = "CA" in active_inputs or "HO" in active_inputs
		contains_both_ca_ho = "CA" in active_inputs and "HO" in active_inputs
		return contains_letter and (contains_ca_ho or contains_both_ca_ho)

	def filter_mux_pins():
		try:
			active_inputs = []
			while not should_stop(active_inputs):  # Loop until the stop condition is met
				active_inputs = read_multiplexers()
				sleep(0.1)  # Adjust the read interval as needed
			
			if active_inputs:
				# Filter out "CA" and "HO" from active_inputs
				global filtered_inputs 
				filtered_inputs = [input for input in active_inputs if input not in ["CA", "HO"]]
				global filtered_inputs_alt 
				filtered_inputs_alt = [input for input in active_inputs if input in ["CA", "HO"]]
				print("The active inputs are:", ", ".join(filtered_inputs))
		except KeyboardInterrupt:
			pass
		finally:
			GPIO.cleanup()
			
	filter_mux_pins()
		
	#print(filtered_inputs_alt)
	   
	#print(filtered_inputs)
	#print(filtered_inputs[0])
		


	lcd.lcd_clear()
	lcd.lcd_display_string("", 1)
	lcd.lcd_display_string("   ABCDEFGHIJKLMN", 2)
	lcd.lcd_display_string("", 3)
	lcd.lcd_display_string("    OPQRSTUVWXYZ", 4)
	# 
	# ENIGMA rotors.
	#         ABCDEFGHIJKLMNOPQRSTUVWXYZ ABCDEFGHIJKLMNOPQRSTUVWXYZ
	rotor1 = "EKMFLGDQVZNTOWYHXUSPAIBRCJ UWYGADFPVZBECKMTHXSLRINQOJ"
	rotor2 = "AJDKSIRUXBLHWTMCQGZNPYFVOE AJPCZWRLFBDKOTYUQGENHXMIVS"
	rotor3 = "BDFHJLCPRTXVZNYEIWGAKMUSQO TAGBPCSDQEUFVNZHYIXJWLRKOM"
	rotor4 = "ESOVPZJAYQUIRHXLNFTGKDCMWB HZWVARTNLGUPXQCEJMBSKDYOIF"
	rotor5 = "VZBRGITYUPSDNHLXAWMJQOFECK QCYLXWENFTZOSMVJUDKGIARPHB"

	# Enigma reflectors.
	reflectorAlpha = "LEYJVCNIXWPBQMDRTAKZGFUHOS"
	reflectorBeta = "FSOKANUERHMBTIYCWLQPZXVGJD"
	reflectorA = "EJMZALYXVBWFCRQUONTSPIKHGD"
	reflectorB = "YRUHQSLDPXNGOKMIEBFZCWVJAT"
	reflectorC = "FVPJIAOYEDRZXWGCTKUQSBNMHL"
	reflectorBthin = "ENKQAUYWJICOPBLMDXZVFTHRGS"
	reflectorCthin = "RDOBJNTKVEHMLFCWZAXGYIPSUQ"

	# Set up Bombe drums.
	drum1 = ' '
	drum2 = ' '
	drum3 = ' '
	# Bombe drum offsets fomr Enigma rotors.
	drum1CoreOffset = 0
	drum2CoreOffset = 0
	drum3CoreOffset = 0
	ROTOR1COREOFFSET = 1
	ROTOR2COREOFFSET = 1
	ROTOR3COREOFFSET = 1
	ROTOR4COREOFFSET = 2
	ROTOR5COREOFFSET = 3

	stepCount = 0
	stepCount2 = 0
	stepCount3 = 0

	# Drums.
	drums = [0 for i in range(3)]
	# Menu connections.
	MAXNUMBERCONNECTIONS = 6
	menuConnections = [[0 for j in range(MAXNUMBERCONNECTIONS)] for i in range(36)]
	# Scramblers.
	numberOfScramblers = 0
	#scramblerOffsets = ["" for i in range(36)]
	scramblerOffsets = []
	scramblerConnections = ["" for i in range(36)]
	# Menu letters.
	numberMenuLetters = 0
	menuLetters = ""
	# Test input voltage.
	inputLetter = ' '
	# Test register.
	testMenuLetter = ' '

	# Ring setting for all drums.
	# 25 = Z.
	RINGSETTING = 25

	# Set up Bombe reflector.
	reflector = ""

	diagonalBoard = [[' ' for j in range(26)] for i in range(26)]
	diagonalBoardLetter = ' '

	# Initial indicator drum positions.
	indicatorDrums = "ZZZ"

	global currentLetter
	currentLetter = indicatorDrums[0]

	# Number of untraced voltages.
	untraced = 0

	# Number of stops.
	numStops = 0

	# Number of iterations.
	numIterations = 0

	# States.
	allIterationsDone = False
	stopFound = False
	runComplete = False

	# Debugging.
	debugDiagonal = False
	debugOther    = False
	debugEnigma   = False

	# ----------------------------------------------------------------------------
	# Read rotors.
	# ----------------------------------------------------------------------------
	def ReadRotors(buffer):
		drums[0] = int(buffer[8])
		drums[1] = int(buffer[11])
		drums[2] = int(buffer[14])

	# ----------------------------------------------------------------------------
	# Read reflector.
	# ----------------------------------------------------------------------------
	def ReadReflector(buffer):
		global reflector
		if buffer[11] == 'B':
			reflector = reflectorB
		elif buffer[11] == 'C':
			reflector = reflectorC

	# ----------------------------------------------------------------------------
	# Read test register.
	# ----------------------------------------------------------------------------
	def ReadTestRegister(buffer):
		global testMenuLetter
		testMenuLetter = buffer[15]

	# ----------------------------------------------------------------------------
	# Read input voltage.
	# ----------------------------------------------------------------------------
	def ReadInputVoltage(buffer):
		global inputLetter
		#inputLetter = buffer[15]
		inputLetter = filtered_inputs[0]

	# ----------------------------------------------------------------------------
	# Read scramblers.
	# ----------------------------------------------------------------------------
	def ReadScramblers(buffer):
		global numberOfScramblers
		# Work out how many scramblers are being used.
		breakout = buffer[7:].split(',')
		numberOfScramblers = len(breakout)

	#    # Copy the scramblers.
	#    for i in range(numberOfScramblers):
	#        scramblerOffsets[i] = breakout[i].strip()
		# Copy the scramblers.
		for token in breakout:
			scramblerOffsets.append(token.strip())

	# ----------------------------------------------------------------------------
	# Read connections.
	# ----------------------------------------------------------------------------
	def ReadConnections(buffer, connectionCount):
		global numberMenuLetters, menuLetters
		tokenCount = 0

		# Set the menu letter.
		menuLetter = buffer[0]
		menuLetters += menuLetter
		numberMenuLetters += 1
		tokenInt = -1

		# Extract the tokens
		breakout = buffer[3:].split(',')
	#    for i in range(len(breakout)):
	#        breakout[i] = breakout[i].strip()

		# Loop through the tokens
		for token in breakout:
			token = token.strip()
			tokenCount += 1
			# Remove the 'i' or 'o'.
			token = token[:-1]
			tokenInt = int(token)
				# Store the connection.
			menuConnections[connectionCount][tokenCount - 1] = tokenInt
				# Store the menu letter against the correct scrambler.
			scramblerConnections[tokenInt - 1] += menuLetter
	#
	# ----------------------------------------------------------------------------
	# Read the set up information from a file.
	# ----------------------------------------------------------------------------
	def ReadSetupFile(filename):
		buffer = ""
		lineCount = 0
		# Open the file for reading.
		menuFile = open(filename, 'r')
		print("Menu file opened.")
		# Read each line.
		for buffer in menuFile:
			buffer = buffer[:len(buffer)-1]
			lineCount += 1
			if lineCount == 1:
				ReadRotors(buffer)
			elif lineCount == 2:
				ReadReflector(buffer)
			elif lineCount == 3:
				ReadTestRegister(buffer)
			elif lineCount == 4:
				ReadInputVoltage(buffer)
			elif lineCount == 5:
				ReadScramblers(buffer)
			elif lineCount > 6:
				ReadConnections(buffer, lineCount - 7)

		# Close the file.
		menuFile.close()
		return True

	# ----------------------------------------------------------------------------
	# Setup the drums.
	# ----------------------------------------------------------------------------
	def SetupDrums():
		global drum1, drum2, drum3, drum1CoreOffset, drum2CoreOffset, drum3CoreOffset

		drum1, drum1CoreOffset = SetDrumAndOffset(drums[0])
		drum2, drum2CoreOffset = SetDrumAndOffset(drums[1])
		drum3, drum3CoreOffset = SetDrumAndOffset(drums[2])

	# ----------------------------------------------------------------------------
	# Set the correct drum and core wiring offset.
	# ----------------------------------------------------------------------------
	def SetDrumAndOffset(rotor):
		drum = ""
		offset = ""
		if rotor == 1:
			drum = rotor1
			offset = ROTOR1COREOFFSET
		elif rotor == 2:
			drum = rotor2
			offset = ROTOR2COREOFFSET
		elif rotor == 3:
			drum = rotor3;
			offset = ROTOR3COREOFFSET
		elif rotor == 4:
			drum = rotor4;
			offset = ROTOR4COREOFFSET
		elif rotor == 5:
			drum = rotor5;
			offset = ROTOR5COREOFFSET
		else:
				print("Unknown rotor specified.")
		return drum, offset

	# ----------------------------------------------------------------------------
	# Print the setup data to the screen.
	# ----------------------------------------------------------------------------
	def PrintSetupData():
		print("Top drum: %i" % (drums[0]))
		print("Middle drum: %i" % (drums[1]))
		print("Bottom drum: %i" % (drums[2]))
		if reflector[0] == 'Y':
			print("Reflector: B")
		elif reflector[0] == 'F':
			print("Reflector: C")
		print("Test register: %c" % (testMenuLetter))
		print("Test voltage: %c" % (inputLetter))
		print("Number of scramblers: %i" % (numberOfScramblers))
		PrintScramblers()
		print("Number of menu letters: %i" % (numberMenuLetters))
		print("Menu connections:")
		for i in range(numberMenuLetters):
			print("%c:" % menuLetters[i], end = '')
			for j in range(MAXNUMBERCONNECTIONS):
				if menuConnections[i][j] != 0:
					print("%3i " % menuConnections[i][j], end = '')
			print()

	# ----------------------------------------------------------------------------
	# Pass a value through the given scrambler.
	# ----------------------------------------------------------------------------
	def Scrambler(value, currentScrambler):
		currentDrum = ""
		currentDrumOffset = 0
		drumCoreOffset = 0

		# Through drum 3.
		currentDrum = drum3
		currentDrumOffset = ord(currentScrambler[2]) - ord('A') # ord('A') = 65
		drumCoreOffset = drum3CoreOffset
		value = CalculateScramblerOffset(value, currentDrumOffset, drumCoreOffset)
		value = ForwardThroughScrambler(value, currentDrum, currentDrumOffset, 
										drumCoreOffset)

		# Through drum 2.
		currentDrum = drum2
		currentDrumOffset = ord(currentScrambler[1]) - ord('A')
		drumCoreOffset = drum2CoreOffset
		value = CalculateScramblerOffset(value, currentDrumOffset, drumCoreOffset)
		value = ForwardThroughScrambler(value, currentDrum, currentDrumOffset, drumCoreOffset)

		# Through drum 1.
		currentDrum = drum1
		currentDrumOffset = ord(currentScrambler[0]) - ord('A')
		drumCoreOffset = drum1CoreOffset
		value = CalculateScramblerOffset(value, currentDrumOffset, drumCoreOffset)
		value = ForwardThroughScrambler(value, currentDrum, currentDrumOffset, drumCoreOffset)

		# Through reflector.
		value = ord(reflector[value - 1]) - 64
		value = WrapScramblerOffset(value)
		if (debugEnigma == True):
			print("%c" % (value + 64), end = '')
		# Back through drum 1.
		currentDrum = drum1
		currentDrumOffset = ord(currentScrambler[0]) - ord('A')
		drumCoreOffset = drum1CoreOffset
		value = CalculateScramblerOffset(value, currentDrumOffset, drumCoreOffset)
		value = BackwardThroughScrambler(value, currentDrum, currentDrumOffset, drumCoreOffset)

		# Back through drum 2.
		currentDrum = drum2
		currentDrumOffset = ord(currentScrambler[1]) - ord('A')
		drumCoreOffset = drum2CoreOffset
		value = CalculateScramblerOffset(value, currentDrumOffset, drumCoreOffset)
		value = BackwardThroughScrambler(value, currentDrum, currentDrumOffset, drumCoreOffset)

		# Back through drum 3.
		currentDrum = drum3
		currentDrumOffset = ord(currentScrambler[2]) - ord('A')
		drumCoreOffset = drum3CoreOffset
		value = CalculateScramblerOffset(value, currentDrumOffset, drumCoreOffset)
		value = BackwardThroughScrambler(value, currentDrum, currentDrumOffset, drumCoreOffset)
		
		return value

	# ----------------------------------------------------------------------------
	# Wrap the scrambler value so it is in the range 1-26.
	# ----------------------------------------------------------------------------
	def WrapScramblerOffset(value):
		while (value < 1):
			value = value + 26
		while (value > 26):
			value = value - 26
		return value

	# ----------------------------------------------------------------------------
	# Calculate the current scrambler offset.
	# We take the current drum offset, the ring value (Z) and the Bombe core
	# wiring offset into account.
	# ----------------------------------------------------------------------------
	def CalculateScramblerOffset(value, currentDrumOffset, drumCoreOffset):
		returnValue = -1
		
		returnValue = value + currentDrumOffset - RINGSETTING - drumCoreOffset
		returnValue = WrapScramblerOffset(returnValue)
		return returnValue

	# ----------------------------------------------------------------------------
	# Pass the value forwards through the given scrambler.
	# ----------------------------------------------------------------------------
	def ForwardThroughScrambler(value, currentDrum, currentDrumOffset, drumCoreOffset):
		currentValue = -1
		
		currentValue = ord(currentDrum[(value - 1)]) - 64
		currentValue = currentValue - currentDrumOffset + RINGSETTING + drumCoreOffset
		currentValue = WrapScramblerOffset(currentValue)
		if (debugEnigma == True):
			print("%c" % (currentValue + 64), end = '')
		return currentValue

	# ----------------------------------------------------------------------------
	# Pass the value backwards through the given scrambler.
	# ----------------------------------------------------------------------------
	def BackwardThroughScrambler(value, currentDrum, currentDrumOffset, drumCoreOffset):
		currentValue = -1
		
		currentValue = ord(currentDrum[(value - 1) + 27]) - 64
		currentValue = currentValue - currentDrumOffset + RINGSETTING + drumCoreOffset
		currentValue = WrapScramblerOffset(currentValue)
		if (debugEnigma == True):
			print("%c" % (currentValue + 64), end = '')
		return currentValue

	# ----------------------------------------------------------------------------
	# Increment all the scramblers.
	# ----------------------------------------------------------------------------
	def IncrementScramblers():
		for i in range(numberOfScramblers):
			# Always increment the top drum.
			# Top drum.
			letter1 = chr(ord(scramblerOffsets[i][0])+1)
			if letter1 > 'Z':
				letter1 = 'A'
		
			# The middle one increments after the top one has done 1 and a half turns
			# or 39 steps (26 + 13).
			if (numIterations % 39) == 0:
				# Middle drum.
				letter2 = chr(ord(scramblerOffsets[i][1])+1)
				if letter2 > 'Z':
					letter2 = 'A'
			else:
				letter2 = scramblerOffsets[i][1]
		
			# Bottom drum increments when the second drum has done one whole turn.
			if (numIterations % (39 * 26)) == 0:
				letter3 = chr(ord(scramblerOffsets[i][2])+1)
				if letter3 > 'Z':
					letter3 = 'A'
			else:
				letter3 = scramblerOffsets[i][2]
			scramblerOffsets[i] = letter1 + letter2 + letter3

	# ----------------------------------------------------------------------------
	# Decrement the indicator.
	# ----------------------------------------------------------------------------

	def move_rotor_with_ticcmd(position):
		"""Function to move rotor 1 using ticcmd."""
		#os.system(f"ticcmd --position-relative {position}")
		#wait_for_ticcmd_to_finish(position)
		
		GPIO.setmode(GPIO.BCM)
		
		GPIO.setup(PUL1, GPIO.OUT)
		GPIO.setup(ENA1, GPIO.OUT)
		
		for x in range(position): 
				GPIO.output(PUL1, GPIO.HIGH)
				sleep(delay)
				GPIO.output(PUL1, GPIO.LOW)
				sleep(delay)

	def DecrementIndicator():
		global allIterationsDone, indicatorDrums, stepCount, stepCount2, stepCount3

		GPIO.setmode(GPIO.BCM)

		GPIO.setup(PUL1, GPIO.OUT)
		GPIO.setup(PUL2, GPIO.OUT)
		GPIO.setup(PUL3, GPIO.OUT)
		GPIO.setup(ENA1, GPIO.OUT)
		GPIO.setup(ENA2, GPIO.OUT)
		GPIO.setup(ENA3, GPIO.OUT)
		
		GPIO.output(ENA1, GPIO.LOW)#
		GPIO.output(ENA2, GPIO.LOW)
		GPIO.output(ENA3, GPIO.LOW)

		letter2 = indicatorDrums[1]
		letter3 = indicatorDrums[2]
		
		letter1 = chr(ord(indicatorDrums[0]) - 1)
		if letter1 < 'A':
			letter1 = 'Z'
		#os.system("ticcmd --position 31")
		#wait_for_ticcmd_to_finish(31)
		#os.system("ticcmd --halt-and-set-position 0")
		# Top indicator drum always decrements.
		# for x in range(durationFwd): 
			# GPIO.output(PUL1, GPIO.HIGH)
			# sleep(delay)
			# GPIO.output(PUL1, GPIO.LOW)
			# sleep(delay)
			# stepCount += 1
			
			# if (stepCount % 40) == 39:
				# GPIO.output(PUL1, GPIO.HIGH)
				# sleep(delay)
				# GPIO.output(PUL1, GPIO.LOW)
				# sleep(delay)
				# stepCount += 1
		# The middle one decrements after the top one has done 1 and a half turns
		# or 39 steps (26 + 13).
		
		#move_rotor_with_ticcmd(durationFwd)
		
		if (numIterations % 39) == 0:
			#threading.Thread(target=move_rotor_with_ticcmd, args=(1200,)).start()
			#wait_for_ticcmd_to_finish(1200)
			#os.system("ticcmd --position 800")
			#wait_for_ticcmd_to_finish(800)
			#os.system("ticcmd --position-relative 400")
			#threading.Thread(target=move_rotor_with_ticcmd, args=(31,)).start()
			for x in range(durationFwd): 
				GPIO.output(PUL2, GPIO.HIGH)
				#GPIO.output(PUL1, GPIO.HIGH)
				sleep(delay)
				GPIO.output(PUL2, GPIO.LOW)
				#GPIO.output(PUL1, GPIO.LOW)
				sleep(delay)
				stepCount2 += 1
				if (stepCount2 % 40 ) == 39:
					GPIO.output(PUL2, GPIO.HIGH)
					sleep(delay)
					GPIO.output(PUL2, GPIO.LOW)
					sleep(delay)
					stepCount2 += 1
			letter2 = chr(ord(indicatorDrums[1]) - 1)
			if letter2 < 'A':
				letter2 = 'Z'

				# The bottom one decrements if the middle one has just finished one turn.
				for x in range(durationFwd): 
					GPIO.output(PUL3, GPIO.HIGH)
					#GPIO.output(PUL2, GPIO.HIGH)
					#GPIO.output(PUL1, GPIO.HIGH)
					sleep(delay)
					GPIO.output(PUL3, GPIO.LOW)
					#GPIO.output(PUL2, GPIO.LOW)
					#GPIO.output(PUL1, GPIO.LOW)
					sleep(delay)
					stepCount3 += 1
					if (stepCount3 % 40) == 39:
						GPIO.output(PUL3, GPIO.HIGH)
						sleep(delay)
						GPIO.output(PUL3, GPIO.LOW)
						sleep(delay)
						stepCount3 += 1
						
				letter3 = chr(ord(indicatorDrums[2]) - 1)
				if letter3 < 'A':
					letter3 = 'Z'
							# When this happens we are done.
					allIterationsDone = True
					print
					print("All stops found.")

		indicatorDrums = letter1 + letter2 + letter3
		

	def wait_for_ticcmd_to_finish(target_position, tolerance=1):
		"""
		Waits for the ticcmd rotor to finish moving by checking the current position
		until it matches the target position (within a tolerance).

		Parameters:
		- target_position: The desired position to wait for (in steps).
		- tolerance: The acceptable margin of error between the current and target position.
		"""
		while True:
			# Get the current position using ticcmd --status
			status_output = os.popen("ticcmd --status").read()
			
			# Parse the current position from the output
			current_position = parse_current_position(status_output)
			
			if current_position is None:
				#print("Error: Could not parse current position from ticcmd status.")
				break
			
			# Check if current position is within the tolerance of the target position
			if abs(current_position - target_position) <= tolerance:
				#print(f"Rotor reached target position: {current_position}")
				break
			if (target_position) <= current_position:
				break 
			
			#print(f"Waiting for rotor to reach target position. Current: {current_position}, Target: {target_position}")
			sleep(0.1)  # Wait for a short time before checking again
		os.system("ticcmd --halt-and-set-position 0")

	def parse_current_position(status_output):
		"""
		Parses the current position from the ticcmd --status output.

		Parameters:
		- status_output: The output from the `ticcmd --status` command as a string.

		Returns:
		- The current position as an integer, or None if parsing fails.
		"""
		for line in status_output.splitlines():
			if "Current position" in line:
				# Extract the number from the line (e.g., "Current position: 1234")
				try:
					return int(line.split(":")[1].strip())
				except (IndexError, ValueError):
					return None
		return None



	# ----------------------------------------------------------------------------
	# Reset the diagonal board to all zero.
	# ----------------------------------------------------------------------------
	def ResetDiagonalBoard():
		global untraced
		
		if debugDiagonal == True:
			print("Resetting diagonal board.")
		
		# Set all voltages to 0.
		for i in range(26):
			for j in range(26):
				diagonalBoard[i][j] = 0
		# Set the untraced count to 0.
		untraced = 0

	# ----------------------------------------------------------------------------
	# Set voltages on the diagonal board.
	# ----------------------------------------------------------------------------
	def SetDiagonalBoard(menuLetter, letter):
		global untraced
		if (debugOther == True):
			print("Setting diagonal: %c:%c" % (menuLetter, letter))
		if (diagonalBoard[ord(menuLetter) - ord('A')][ord(letter) - ord('A')] == 0):
			# Always update the menu letter.
			diagonalBoard[ord(menuLetter) - ord('A')][ord(letter) - ord('A')] = -1
			# Update the count of untraced voltages.
			untraced += 1

		# If it's not the same letter in the pair set the diagonal.
		if (menuLetter != letter):
			if (diagonalBoard[ord(letter) - ord('A')][ord(menuLetter) - ord('A')] == 0):
				# Update the untraced count if this is a menu letter.
				if menuLetters.find(letter) != -1:
					diagonalBoard[ord(letter) - ord('A')][ord(menuLetter) - ord('A')] = -1
					untraced += 1
				else:
					diagonalBoard[ord(letter) - ord('A')][ord(menuLetter) - ord('A')] = 2

	# ----------------------------------------------------------------------------
	# Print out the scramblers.
	# ----------------------------------------------------------------------------
	def PrintScramblers():
		scramblerNumber = 0

		print("Scramblers:")
		for i in range(numberOfScramblers):
			print("%2i:%s-%s " % (i + 1, scramblerOffsets[i], 
								  scramblerConnections[i]), end = '')
			scramblerNumber += 1
			if scramblerNumber % 6 == 0:
					print()
		print()

	# ----------------------------------------------------------------------------
	# Print out a scrambler corrected to match Enigma.
	# ----------------------------------------------------------------------------
	def PrintCorrectedScrambler(scrambler):
		drum = ''
		drumValue = -1
		
		drum = scrambler[0];
	#    drumValue = (int)drum - 64 - drum1CoreOffset;
		drumValue = ord(drum) - 64 - drum1CoreOffset
		drumValue = WrapScramblerOffset(drumValue)
		print("%c" % (drumValue + 64), end = '')
		drum = scrambler[1]
	#    drumValue = (int)drum - 64 - drum2CoreOffset;
		drumValue = ord(drum) - 64 - drum2CoreOffset
		drumValue = WrapScramblerOffset(drumValue)
		print("%c" % (drumValue + 64), end = '')
		drum = scrambler[2]
	#    drumValue = (int)drum - 64 - drum3CoreOffset;
		drumValue = ord(drum) - 64 - drum3CoreOffset
		drumValue = WrapScramblerOffset(drumValue)
		print("%c" % (drumValue + 64), end = '')

	# ----------------------------------------------------------------------------
	# Print out the diagonal board.
	# ----------------------------------------------------------------------------
	def PrintDiagonalBoard():
		print()
		print(" ", end = '')
		for i in range(26):
			print("%2c" % (chr(ord('A') + i)), end = '')
		print()
		for i in range(26):
			for j in range(26):
				# Print the rows.
				if j == 0:
					# If this is the test register print a ?
					if (chr(i + ord('A')) == testMenuLetter):
						print("?", end = '')
					else:
						print("%c" % (chr(i + ord('A'))), end = '')
				# Print the board.
				if (diagonalBoard[i][j] == -1):
					print(" x", end = '')
				elif (diagonalBoard[i][j] == 1):
					print(" |", end = '')
				elif (diagonalBoard[i][j] == 2):
					print(" o", end = '')
				else:
					print("  ", end = '')
			print()	#os.system("ticcmd --position 31")
		#wait_for_ticcmd_to_finish(31)
		print()

	# ----------------------------------------------------------------------------
	# Print out the test register.
	#----------------------------------------------------------------------------
	def PrintTestRegister():
		# Initialise the LCD
		lcd.lcd_clear()
		
		line1 = "   "  # Start with three spaces for alignment with line 2
		line3 = "   "  # Start with four spaces for alignment with line 4
		
		# The alphabet lines (fixed)
		line2 = "   ABCDEFGHIJKLMN"
		line4 = "    OPQRSTUVWXYZ"
		
		# Generate the first and third row of output for the | characters
		for i in range(26):
			if i < 13:  # Characters A-M align with line 1
				if (diagonalBoard[ord(testMenuLetter) - ord('A')][i] == 1):
					line1 += " "  # Add a space
				else:
					line1 += "|"  # Add a | character
			else:  # Characters N-Z align with line 3
				if (diagonalBoard[ord(testMenuLetter) - ord('A')][i] == 1):
					line3 += " "  # Add a space
				else:
					line3 += "|"  # Add a | character

		for i in range(26):
			if (diagonalBoard[ord(testMenuLetter) - ord('A')][i] == 1):
				print("%c" % (' '), end = '')
			else:
				print("%c" % ('|'), end = '')
		print()
		for i in range(26):
			print("%c" % (chr(ord('A') + i)), end = '')
		print()

		# Update the LCD with the generated lines
		lcd.lcd_display_string(line1.ljust(16), 1)  # First line on the LCD
		lcd.lcd_display_string(line2.ljust(16), 2)  # Second line on the LCD
		lcd.lcd_display_string(line3.ljust(16), 3)  # Third line on the LCD
		lcd.lcd_display_string(line4.ljust(16), 4)  # Fourth line on the LCD

	def calculate_steps_to_letter(current_letter, target_letter):
		"""
		Helper function to calculate the number of steps needed to move from the current letter
		to the target letter on the rotor.
		"""
		print(current_letter)
		print(target_letter)
		step_per_letter = 400 / 26  # Assuming 800 steps for a full cycle, and 26 letters (A to Z)
		current_pos = ord(current_letter) - ord('A')
		target_pos = ord(target_letter) - ord('A')
		print(target_pos - current_pos)
		# Calculate steps (handle both forward and backward rotations)
		if (current_pos > target_pos):
			steps_needed = -(target_pos - current_pos) * step_per_letter
			print('1')
		else:
			steps_needed = -(target_pos - current_pos) * step_per_letter + 400
		#if steps_needed < 0:
		#steps_needed += 800  # Adjust for wraparound if going backward
		print(round(steps_needed))
		return round(steps_needed)
	# ----------------------------------------------------------------------------
	# Check position function.
	# ----------------------------------------------------------------------------
	def CheckDrumPosition(iteration, current_Letter):
		global stopFound, numStops, currentLetter

		numberVoltages = 0
		#potentialStecker = ' '

		# Clear the diagonal board.
		ResetDiagonalBoard()


		# Set up the initial letters.
		SetDiagonalBoard(testMenuLetter, inputLetter)

		# Trace all voltages.
		Trace()

		# If we've traced all voltages check if we have a stop.
		numberVoltages = CheckRegister(testMenuLetter)

		# If not all letters have a voltage we have a stop.
		if numberVoltages < 26:
			stopFound = True
			numStops += 1
			print("Stop %i found." % (numStops))
			print("Indicator: %s Iteration: %i" % (indicatorDrums, iteration))
			PrintTestRegister()
			
			steps = calculate_steps_to_letter(current_Letter, indicatorDrums[0])
			move_rotor_with_ticcmd(steps)
			#os.system(f"ticcmd --position {steps}")
			#wait_for_ticcmd_to_finish(steps)
			currentLetter = indicatorDrums[0]
			
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(10, GPIO.IN)  # Scroll Button

			while (GPIO.input(10) == GPIO.LOW):
				if GPIO.input(10) == GPIO.HIGH:  # Select Button pressed (GPIO25 is LOW)
					#while GPIO.input(10) == GPIO.HIGH:
					
					#read_multiplexers()
					#filter_mux_pins()
			
					#if ('HO' in filtered_inputs_alt):
						#print('Returning Home')
					#else:
					sleep(0.1)  # Wait until button is released
			read_multiplexers()
			filter_mux_pins()
			print(filtered_inputs_alt)
			if 'HO' in filtered_inputs_alt:
				print('Going home - not working yet')
			
			lcd.lcd_clear()
			lcd.lcd_display_string("", 1)
			lcd.lcd_display_string("   ABCDEFGHIJKLMN", 2)
			lcd.lcd_display_string("", 3)
			lcd.lcd_display_string("    OPQRSTUVWXYZ", 4)
			return

	# ----------------------------------------------------------------------------
	# Check a register to see if we have traced all voltages.
	# ----------------------------------------------------------------------------
	def CheckRegister(letter):
		traceCount = 0
		potentialStecker1 = ''
		potentialStecker25 = ''
		stecker = ''
		
		# If we've traced all voltages check for a stop.
		# Check each voltage.
	#    PrintDiagonalBoard()
		for i in range(26):
			# Decrement count for each set voltage.
			if (diagonalBoard[ord(letter) - ord('A')][i] != 0):
				traceCount += 1

			# Store the potential stecker.
			if (diagonalBoard[ord(letter) - ord('A')][i] == 1):
				# Either the single voltage set.
				potentialStecker1 = i + ord('A')
			elif (diagonalBoard[ord(letter) - ord('A')][i] == 0):
				# Or the single voltage unset.
				potentialStecker25 = i + ord('A')

		# Return the correct stecker.
		if (traceCount == 1):
			# If one set return that one.
			stecker = potentialStecker1
		elif (traceCount == 25):
			# If 25 set return the one unset.
			stecker = potentialStecker25
		else:
			# Else return null.
			stecker = ''

		return traceCount#, stecker

	# ----------------------------------------------------------------------------
	# Trace voltages.
	# ----------------------------------------------------------------------------
	def Trace():
		# Loop until we've finished tracing every voltage.
		while (untraced > 0):
			# For each menu letter.
			for j in range(numberMenuLetters):
				if (debugDiagonal == True):
					PrintDiagonalBoard()
				if (debugOther == True):
					print("Indicator: %s" % (indicatorDrums))
					print("Checking letter: %c" % (menuLetters[j]))
					print("Total untraced: %i" % (untraced))
				
				# Trace the voltage through the menu.
				# For each input voltage on this menu letter.
				for k in range(26):
					if (diagonalBoard[ord(menuLetters[j]) - ord('A')][k] == -1):
						# If there is a -1 we trace it through.
						TraceMenuLetterVoltages(j, k)
				if (untraced == 0):
					break;

	# ----------------------------------------------------------------------------
	# Trace voltages for this menu letter.
	# ----------------------------------------------------------------------------
	def TraceMenuLetterVoltages(menuLetterIndex, voltage):
		global untraced
		
		currentScrambler = 0
	#    currentConnections = 0
		currentScramblerLetters = 0
		output = 0
		connectionCount = 0
		
		#Set this voltage as traced.
		diagonalBoard[ord(menuLetters[menuLetterIndex]) - ord('A')][voltage] = 1
		untraced -= 1
		
		if (debugOther == True):
			print("Tracing voltage on letter %c" % (voltage + ord('A')))
		# For each connected scrambler.
		for i in range(MAXNUMBERCONNECTIONS):
			# If we checked all scramblers we are done tracing.
			if (menuConnections[menuLetterIndex][i] == 0):
				break
			# Else send the voltage through this scrambler.
	#        currentScrambler = scramblerOffsets[(menuConnections[menuLetterIndex][i]) - 1][0]
			currentScrambler = scramblerOffsets[(menuConnections[menuLetterIndex][i]) - 1]
			currentScramblerLetters = scramblerConnections[(menuConnections[menuLetterIndex][i]) - 1][0]
			if (debugOther == True):
				print("%2i:" % (menuConnections[menuLetterIndex][i]), end = '')
				PrintCorrectedScrambler(currentScrambler)
				print(" %c>" % (voltage + 65), end = '')
			output = Scrambler(voltage + 1, currentScrambler)
			if (debugOther == True):
				print("%c" % (output + 64))
			
			# Set a -1 on the other end of each connected scrambler.
			letter = chr(output + 64)
			for j in range(2):
				# Each scrambler is between two letters.
				if (scramblerConnections[(menuConnections[menuLetterIndex][i]) - 1][j] != menuLetters[menuLetterIndex]):
					# If its not this menu letter it's the opposite end.
					SetDiagonalBoard(scramblerConnections[(menuConnections[menuLetterIndex][i]) - 1][j], letter)

	# ----------------------------------------------------------------------------
	# Main program.
	# ----------------------------------------------------------------------------
	fileRead = False
	#menuFile = "/media/raspberrypi/USB DISK/menu_PV.txt"
	# Read the menu file.
	print("Reading menu file...")
	fileRead = ReadSetupFile(menuFile)
	if fileRead == False:
		print("Could not open input menu file.")
		print("Press STOP to shutdown.")
		runComplete = True

	# Set up the drums and print out the configuration.
	SetupDrums()
	PrintSetupData()

	print("Bombe finding next stop...")
	print("Menu loaded. Press START to run.")
	 
	#	main loop.
	while True:
		# If we are still calculating.
		if ((allIterationsDone == False) and (stopFound == False)):
			# Next iteration.
			numIterations += 1
			# Increment all the scramblers.	
			IncrementScramblers()
			# Decrement the indicator drums.
			DecrementIndicator()
			# Don't check the half cycles.
			if (numIterations % 39) >= 13:
				# Check this position.
				CheckDrumPosition(numIterations, currentLetter)
				if debugOther == True:
					print("Iteration: %i\tIndicator: %s\t%i *" % (numIterations, indicatorDrums, numIterations % 39))
					PrintScramblers()
			elif debugOther == True: 
				print("Iteration: %i\tIndicator: %s\t%i" % (numIterations, indicatorDrums, numIterations % 39))
				PrintScramblers();
		#       print
		#		# If a stop was found and the Arduino is running wait for it
		#		# to catch up.
		if ((allIterationsDone == False) and (stopFound == True)):
			stopFound = False
		#
		#    # If we've found all stops and the Arduino is running wait for it
		#    # to finish.
		if ((allIterationsDone == True) and (runComplete == False)): 
			runComplete = True  
			#GPIO.output(ENA1, GPIO.LOW)
			GPIO.output(ENA2, GPIO.LOW)
			GPIO.output(ENA3, GPIO.LOW)
			# Complete.
			
			steps = calculate_steps_to_letter(currentLetter, 'Z')
			move_rotor_with_ticcmd(steps)
			#os.system(f"ticcmd --position {steps}")
			#wait_for_ticcmd_to_finish(steps)
			currentLetter = indicatorDrums[0]
			print("Bombe run complete.")
			print("Press STOP to shutdown.")
			print("Iterations:", numIterations)
			break		
