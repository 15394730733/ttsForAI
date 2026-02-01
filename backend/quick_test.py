"""Quick API route checker."""
import urllib.request
import json

def check_server():
    """Check if server is running and list routes."""
    try:
        # Check health
        with urllib.request.urlopen("http://localhost:8000/health", timeout=5) as response:
            data = json.load(response)
            print(f"Health check: {response.status}")
            print(f"Response: {data}")

        # Get OpenAPI spec
        with urllib.request.urlopen("http://localhost:8000/openapi.json", timeout=5) as response:
            data = json.load(response)
            paths = data.get("paths", {})
            print(f"\nAvailable routes ({len(paths)}):")
            for path in sorted(paths.keys()):
                methods = list(paths[path].keys())
                print(f"  {path}: {', '.join(methods)}")

            # Check expected routes
            print("\nRoute check:")
            if "/health" in paths:
                print("  [OK] /health exists")
            if "/api/v1/tts/generate" in paths:
                print("  [OK] /api/v1/tts/generate exists")
            elif "/tts/generate" in paths:
                print("  [WARN] /tts/generate exists (missing /api/v1 prefix)")
            else:
                print("  [ERROR] TTS routes not found!")

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Checking server...")
    if check_server():
        print("\n[OK] Server check complete")
    else:
        print("\n[ERROR] Server check failed")
