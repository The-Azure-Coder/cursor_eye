import time
import subprocess
import sys
import requests
from clients.cursor_client import EyeControlClient
from api import server
def is_server_ready(url="http://localhost:5000", timeout=90):
    """Check if the server is ready to accept connections"""
    print("Waiting for server to be ready...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/api/eye-coordinates", timeout=1)
            if response.status_code == 200:
                print("Server is ready!")
                return True
        except Exception as e:
            # print(f"\nServer failed to start within timeout {e}")
            pass
        
        print(".", end="", flush=True)
        time.sleep(1)
    
    print("\n Server failed to start within timeout")
    return False

def main():
    print("Starting Complete Eye Tracking System...")
    print("=" * 50)
    
    # Start server in background
    print("Starting Eye Trackering Server...")
    server_process = subprocess.Popen([sys.executable, "app.py"])
    
    # Wait for server to be ready
    if is_server_ready():
        # Server is ready, start client
        print("🎮 Starting Cursor Control Client...")
        try:
            client = EyeControlClient()
            client.run()
            server.api_app.run("http://localhost",5050)
        except Exception as e:
            print(f"Client error: {e}")
    else:
        print("Failed to start system")
    
    # Cleanup subprocess
    server_process.terminate()

if __name__ == '__main__':
    main()