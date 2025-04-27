# Authors: Ian Wilson, Andrew Uriell, Peter Pham, Michael Oliver, Jack Youngquist
# Class: Senior Design -- EECS582
# Date: April 10, 2025
# Purpose: Python3 helper script to play music from webserver
# Code soures: Stackoverflow, chatgpt, ourselves
import http.server
import json
import os
import time
import ssl

PORT = 6969
AUTH_TOKEN = "super_secret_token"
CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"

class CommandHandler(http.server.SimpleHTTPRequestHandler):

    def do_OPTIONS(self):
        # Handle the preflight request for CORS
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow all origins or specific ones
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')  # Allow credentials if needed
        self.end_headers()

    def do_POST(self):
            # Auth check via tokens
            token = self.headers.get("Authorization")
            if token != f"Bearer {AUTH_TOKEN}":
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b'{"error": "Unauthorized"}')
                return
    
            # Read content of the request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode("utf-8")
    
            # Will only work with json request data
            if "application/json" in self.headers.get("Content-Type", ""):
                try:
                    data = json.loads(post_data)
                    self.handle_command(data)
                except json.JSONDecodeError:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'{"error": "Invalid JSON format"}')
            else:
                self.send_response(415)
                self.end_headers()
                self.wfile.write(b'{"error": "Unsupported media type"}')
    
    # Handles commands supplied via the json input 
    def handle_command(self, data):
        command = data.get("command")
    
        # Executes commands for starting the car
        if command == "start_car":
            os.system('/usr/bin/tmux send-keys -t "Car:0.0" "ros2 service call /ctrl_pkg/vehicle_state deepracer_interfaces_pkg/srv/ActiveStateSrv \'{\"state\": 3}\'" ENTER')
            time.sleep(1)
            os.system('/usr/bin/tmux send-keys -t "Car:0.0" "ros2 service call /ctrl_pkg/enable_state deepracer_interfaces_pkg/srv/EnableStateSrv \'{\"is_active\": True}\'" ENTER')
            time.sleep(1)
            os.system('/usr/bin/tmux send-keys -t "Car:0.0" "ros2 service call /ftl_navigation_pkg/set_max_speed deepracer_interfaces_pkg/srv/SetMaxSpeedSrv \'{\"max_speed_pct\": 0.99}\'" ENTER')
            response = {"status": "Car started\n"}
    
        # Executes commands for setting the speed based on the user input
        elif command == "set_speed":
            try:
                speed = int(data.get("speed"))
                if 0 <= speed <= 100:
                    os.system(f'/usr/bin/tmux send-keys -t "Car:0.0" "ros2 service call /ftl_navigation_pkg/set_max_speed deepracer_interfaces_pkg/srv/SetMaxSpeedSrv \'{{\"max_speed_pct\": {speed / 100}}}\'" ENTER')
                    response = {"status": f"Speed set to {speed}%\n"}
                else:
                    response = {"error": "Invalid speed value. Please provide a value between 0 and 100."}
            except ValueError:
                response = {"error": "Invalid speed value."}
    
        # Executes command for stopping FTL on the car
        elif command == "stop_car":
            os.system('/usr/bin/tmux send-keys -t "Car:0.0" "ros2 service call /ctrl_pkg/enable_state deepracer_interfaces_pkg/srv/EnableStateSrv \'{\"is_active\": False}\'" ENTER')
            response = {"status": "Car stopped\n"}
    
        # Ignore all other commands
        else:
            response = {"error": "Unknown command"}
    
        # Finished CORs responses / general responses
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow cross-origin access
        self.send_header('Content-Type', 'application/json')  # Response type as JSON
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

# Runs the sever with the given ip and port
def run():
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, CommandHandler)

    # Wrap in TLS (HTTPS)
    httpd.socket = ssl.wrap_socket(httpd.socket,
                                   keyfile=KEY_FILE,
                                   certfile=CERT_FILE,
                                   server_side=True)

    print(f"Secure server running on https://localhost:{PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()

