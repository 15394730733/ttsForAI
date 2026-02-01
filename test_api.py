"""Test script for TTS API."""
import requests
import time

API_BASE = "http://localhost:8000/api/v1"

# Test health
print("Testing health endpoint...")
response = requests.get(f"{API_BASE.replace('/api/v1', '')}/health")
print(f"Health: {response.json()}\n")

# Test TTS generation
print("Testing TTS generation...")
tts_request = {
    "text": "你好，这是一个测试。",
    "voice_name": "zh-CN-XiaoxiaoNeural",
    "rate": 1.0,
    "pitch": 1.0,
    "volume": 1.0
}

response = requests.post(f"{API_BASE}/tts/generate", json=tts_request)
print(f"Create task response: {response.json()}\n")

if response.status_code == 201:
    task_id = response.json()["task_id"]
    print(f"Task created: {task_id}\n")

    # Poll for completion
    print("Polling for task completion...")
    for i in range(30):
        response = requests.get(f"{API_BASE}/tts/tasks/{task_id}")
        task = response.json()
        print(f"Attempt {i+1}: Status={task['status']}, Progress={task['progress']}%")

        if task["status"] == "completed":
            print(f"\nTask completed! File: {task['file_path']}")
            print(f"\nYou can download at: http://localhost:8000{API_BASE}/tts/download/{task_id}")
            break
        elif task["status"] == "failed":
            print(f"\nTask failed: {task.get('error_message', 'Unknown error')}")
            break

        time.sleep(2)
    else:
        print("\nTask timed out")
else:
    print(f"Failed to create task: {response.text}")
