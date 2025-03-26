import http.server
import json
import os
import time

PORT = 6969  # Set the desired port number

class CommandHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_OPTIONS(self):
        # Handle the CORS preflight (OPTIONS) request
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow any origin
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')  # Allowed methods
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')  # Allowed headers
        self.end_headers()

    def do_POST(self):
        # Process POST requests only
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")

        # Handle JSON requests
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

    def handle_command(self, data):
        # Extract the command from the JSON payload
        command = data.get("command")
        
        if command == "start_car":
            # Execute command to start the car (replace with your actual command)
            os.system('/usr/bin/tmux send-keys -t "Car:0.0" "ros2 service call /ctrl_pkg/vehicle_state deepracer_interfaces_pkg/srv/ActiveStateSrv \'{\"state\": 3}\'" ENTER')
            time.sleep(1)
            os.system('/usr/bin/tmux send-keys -t "Car:0.0" "ros2 service call /ctrl_pkg/enable_state deepracer_interfaces_pkg/srv/EnableStateSrv \'{\"is_active\": True}\'" ENTER')
            time.sleep(1)
            os.system('/usr/bin/tmux send-keys -t "Car:0.0" "ros2 service call /ftl_navigation_pkg/set_max_speed deepracer_interfaces_pkg/srv/SetMaxSpeedSrv \'{\"max_speed_pct\": 0.99}\'" ENTER')
            response = {"status": "Car started\n"}
        elif command == "stop_car":
            os.system('/usr/bin/tmux send-keys -t "Car:0.0" "ros2 service call /ctrl_pkg/enable_state deepracer_interfaces_pkg/srv/EnableStateSrv \'{\"is_active\": False}\'" ENTER')
            response = {"status": "Car stopped\n"}
        else:
            response = {"error": "Unknown command"}

        # Send the response back to the client
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow any origin
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

# Set up the server and start listening on port 6969
def run(server_class=http.server.HTTPServer, handler_class=CommandHandler):
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {PORT}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
