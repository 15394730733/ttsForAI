"""API test script.

Tests TTS API endpoints manually.
"""
import asyncio
import time
import httpx


async def test_tts_api():
    """Test TTS API endpoints."""

    base_url = "http://localhost:8000"  # 使用基础URL，路由前缀由FastAPI管理

    async with httpx.AsyncClient(timeout=30.0) as client:
        print("=" * 60)
        print("TTS API 测试")
        print("=" * 60)

        # Test 1: 健康检查
        print("\n1. 测试健康检查...")
        response = await client.get("http://localhost:8000/health")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        assert response.status_code == 200, "健康检查失败"
        print("   [OK] 健康检查通过")

        # Test 2: 创建 TTS 任务
        print("\n2. 创建 TTS 任务...")
        task_request = {
            "text": "你好，这是一个测试。",
            "voice_name": "zh-CN-XiaoxiaoNeural",
            "rate": 1.0,
            "pitch": 1.0,
            "volume": 1.0,
        }

        response = await client.post(f"{base_url}/tts/generate", json=task_request)  # 使用实际路由
        print(f"   状态码: {response.status_code}")

        if response.status_code != 201:
            print(f"   [ERROR] 创建任务失败: {response.text}")
            return

        task_data = response.json()
        task_id = task_data["task_id"]
        print(f"   任务ID: {task_id}")
        print(f"   状态: {task_data['status']}")
        print("   [OK] 任务创建成功")

        # Test 3: 查询任务状态
        print("\n3. 查询任务状态...")
        max_wait = 30  # 最多等待30秒
        start_time = time.time()

        while time.time() - start_time < max_wait:
            response = await client.get(f"{base_url}/tts/tasks/{task_id}")

            if response.status_code != 200:
                print(f"   [ERROR] 查询失败: {response.text}")
                break

            task = response.json()
            status = task["status"]
            progress = task["progress"]

            print(f"   状态: {status}, 进度: {progress}%")

            if status == "completed":
                print("   [OK] 任务完成")
                break
            elif status == "failed":
                print(f"   [ERROR] 任务失败: {task.get('error_message', '未知错误')}")
                break

            await asyncio.sleep(2)

        # Test 4: 下载音频文件
        if task["status"] == "completed" and task.get("file_path"):
            print("\n4. 下载音频文件...")
            response = await client.get(f"{base_url}/tts/download/{task_id}")

            if response.status_code == 200:
                file_size = len(response.content)
                print(f"   文件大小: {file_size} bytes")
                print("   [OK] 音频下载成功")

                # 保存到本地
                with open(f"test_audio_{task_id}.mp3", "wb") as f:
                    f.write(response.content)
                print(f"   已保存为: test_audio_{task_id}.mp3")
            else:
                print(f"   [ERROR] 下载失败: {response.status_code}")
        else:
            print("\n4. 跳过音频下载（任务未完成）")

        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_tts_api())
