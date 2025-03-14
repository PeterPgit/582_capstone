import os
import json
import http.server
import time

PORT = 6970  

# Define a handler class for HTTP requests
class CommandHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
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
            os.system('/usr/bin/tmux send-keys -t "Car:0.0" "ros2 service call /ctrl_pkg/vehicle_state deepracer_interfaces_pkg/srv/ActiveStateSrv \'{\"state\": 3}\'" ENTER')
            time.sleep(1)
            os.system('/usr/bin/tmux send-keys -t "Car:0.0" "ros2 service call /ctrl_pkg/enable_state deepracer_interfaces_pkg/srv/EnableStateSrv \'{\"is_active\": True}\'" ENTER')
            time.sleep(1)
            os.system('/usr/bin/tmux send-keys -t "Car:0.0" "ros2 service call /ftl_navigation_pkg/set_max_speed deepracer_interfaces_pkg/srv/SetMaxSpeedSrv \'{\"max_speed_pct\": 0.90}\'" ENTER')
            response = {"status": "Car started\n"}
        elif command == "stop_car":
            os.system('/usr/bin/tmux send-keys -t "Car:0.0" "ros2 service call /ctrl_pkg/enable_state deepracer_interfaces_pkg/srv/EnableStateSrv \'{\"is_active\": False}\'" ENTER')
            response = {"status": "Car stopped\n"}
        elif command == "play_music":
            os.system("Play_music")
            response = {"status": "Playing music"}
        else:
            response = {"error": "Unknown command"}

        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

# Set up the server and start listening on port 6969
def run(server_class=http.server.HTTPServer, handler_class=CommandHandler):
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on port {PORT}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
