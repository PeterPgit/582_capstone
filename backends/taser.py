# Authors: Ian Wilson, Andrew Uriell, Peter Pharm, Michael Oliver
# Class: Senior Design -- EECS582
# Date: April 10, 2025
# Purpose: Python3 script to control the taser through software
# Code sources: Stackoverflow, ChatGPT, ourselves

# imports necessary packages
import mraa
import time

# Initialize the GPIO pin 8
pin_8 = mraa.Gpio(8)
pin_8.dir(mraa.DIR_OUT)  # Set pin 8 as output


# Continuously loops so the user can control the output of the pin to enable/disable the taser
try:
    while True:
        key = input("Type '1' to enable pin 8, '2' to disable pin 8, or 'exit' to quit: ")

        if key == '1':  # When '1' is typed, enable pin 8
            pin_8.write(1)  # Set pin 8 HIGH
#            print("Pin 8 enabled!")
        elif key == '2':  # When '2' is typed, disable pin 8
            pin_8.write(0)  # Set pin 8 LOW
#            print("Pin 8 disabled.")
        elif key.lower() == 'exit':  # Exit condition
            break
        else:
#            print("Invalid input. Please type '1' to enable, '2' to disable, or 'exit' to quit.")
            continue
        time.sleep(0.1)  # Small delay to prevent busy-waiting

except KeyboardInterrupt:
    print("Program interrupted")
finally:
    pin_8.write(0)  # Ensure pin is set to LOW when the program exits

