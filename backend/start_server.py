"""Start server and run tests."""
import subprocess
import time
import sys
import urllib.request
import json

def start_server():
    """Start the server."""
    print("Starting server on port 8001...")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"],
        cwd="E:/ai编程实战营/tts/backend",
        stdout=open("E:/ai编程实战营/tts/server_test.log", "w"),
        stderr=subprocess.STDOUT
    )
    return process

def wait_for_server(max_attempts=10):
    """Wait for server to be ready."""
    print("Waiting for server to start...")
    for i in range(max_attempts):
        try:
            with urllib.request.urlopen("http://localhost:8001/health", timeout=2) as response:
                data = json.load(response)
                print(f"Server is ready! Status: {data['status']}")
                return True
        except Exception as e:
            print(f"Attempt {i+1}/{max_attempts}: {e}")
            time.sleep(2)
    return False

def check_routes():
    """Check available routes."""
    print("\nChecking routes...")
    try:
        with urllib.request.urlopen("http://localhost:8001/openapi.json", timeout=5) as response:
            data = json.load(response)
            paths = list(data.get("paths", {}).keys())
            print(f"Found {len(paths)} routes:")
            for path in sorted(paths):
                print(f"  {path}")
    except Exception as e:
        print(f"Error checking routes: {e}")

if __name__ == "__main__":
    # Start server
    server_process = start_server()

    try:
        # Wait for server
        if wait_for_server():
            check_routes()
            print("\n[OK] Server is running on port 8001")
            print("\nPress Ctrl+C to stop...")

            # Keep running
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()
        print("Server stopped.")
