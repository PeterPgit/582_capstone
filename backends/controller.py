# Authors: Ian Wilson, Andrew Uriell, Peter Pharm, Michael Oliver
# Class: Senior Design -- EECS582
# Date: April 20, 2025
# Purpose: Python3 script to enable controller support of the DeepRacer car
# Code sources: Stackoverflow, ChatGPT, ourselves

import os
import time
import pygame
import mraa
import requests
import threading

# Headless mode for pygame (no GUI needed)
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Environment Variables
X_CSRF_TOKEN = "ImFhN2JlMWYzZjM5OTA0ZjEyZGJiNDk4MWJiNmE1NWI0NWQzYTgyM2Ei.Z_rbLg.W6Dj0HL_v6uTRxmBM62oCpwVOXw"
SESSION = "eyJjc3JmX3Rva2VuIjoiYWE3YmUxZjNmMzk5MDRmMTJkYmI0OTgxYmI2YTU1YjQ1ZDNhODIzYSJ9.Z_rNwA.Ww-zHv2LB4mPgPWnO1bgO22QvTw"
DEEPRACER_TOKEN = "27e42bc1-518a-4bb1-b30c-d45c9d2ecb8c"

# DeepRacer endpoints and headers
DEEPRACER_IP = "192.168.0.102"
MANUAL_DRIVE_URL = f"https://{DEEPRACER_IP}/api/manual_drive"
START_STOP_URL = f"https://{DEEPRACER_IP}/api/start_stop"

MAX_SPEED_FORWARD = 0.50
MAX_SPEED_BACKWARD = 0.2

# Initialize pygame
pygame.init()
pygame.display.init()
pygame.joystick.init()

# Setup GPIO pin 8
pin_8 = mraa.Gpio(8)
pin_8.dir(mraa.DIR_OUT)
pin_8.write(0)  # Initial LOW

HEADERS = {
    "Content-Type": "application/json",
    "X-CSRF-TOKEN": {X_CSRF_TOKEN}
}

COOKIES = {
    "session": {SESSION},
    "deepracer_token": {DEEPRACER_TOKEN}
}

# Helper functions to start/stop the car
def start_car():
    payload = {"start_stop": "start"}
    try:
        res = requests.put(START_STOP_URL, json=payload, headers=HEADERS, cookies=COOKIES, verify=False)
        print(f"Start car: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Failed to start car: {e}")

def stop_car():
    payload = {"start_stop": "stop"}
    try:
        res = requests.put(START_STOP_URL, json=payload, headers=HEADERS, cookies=COOKIES, verify=False)
        print(f"Stop car: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Failed to stop car: {e}")

# Thread-safe flag for axis_4 state
axis_4_state = 0
axis_4_lock = threading.Lock()

# GPIO toggle function
def gpio_toggle_thread():
    global axis_4_state
    last_state = axis_4_state
    while True:
        with axis_4_lock:
            if axis_4_state != last_state:
                if axis_4_state == -1.0:
                    pin_8.write(0)
                    print("Axis 4 = -1.0 → GPIO LOW")
                else:
                    pin_8.write(1)
                    print("Axis 4 != -1.0 → GPIO HIGH")
                last_state = axis_4_state
        time.sleep(0.1)

# Check for joystick
if pygame.joystick.get_count() == 0:
    print("No joystick detected.")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Joystick detected: {joystick.get_name()}")

last_angle = None
last_throttle = None

try:
    start_car()  # Start the car at script launch

    # Start the GPIO toggle thread
    gpio_thread = threading.Thread(target=gpio_toggle_thread, daemon=True)
    gpio_thread.start()

    while True:
        pygame.event.pump()  # Update joystick state

        angle = joystick.get_axis(0)  # Left/right
        throttle = -joystick.get_axis(1)  # Up/down (inverted for forward)

        # Update axis_4_state for the GPIO toggle thread
        if joystick.get_numaxes() > 4:
            with axis_4_lock:
                axis_4_state = joystick.get_axis(4)

        # Determine max_speed based on throttle direction
        if throttle > 0:  # Forward throttle
            max_speed = {MAX_SPEED_FORWARD}  # Forward speed
        else:  # Backward throttle
            max_speed = {MAX_SPEED_BACKWARD}  # Slower speed for reverse

        # Only send the request if the values have changed
        if angle != last_angle or throttle != last_throttle:
            payload = {
                "angle": round(angle, 2),
                "throttle": round(-throttle, 2),
                "max_speed": max_speed
            }

            try:
                res = requests.put(MANUAL_DRIVE_URL, json=payload, headers=HEADERS, cookies=COOKIES, verify=False)
                print(f"Sent: {payload} | Status: {res.status_code} | Response: {res.text}")
            except Exception as e:
                print(f"Error sending control data: {e}")

            # Update the last sent values
            last_angle = angle
            last_throttle = throttle

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nInterrupted. Stopping...")

finally:
    stop_car()  # Stop the car on exit
    pin_8.write(0)  # Reset GPIO
    print("GPIO pin 8 set LOW. Exiting cleanly.")

