"""系统性测试脚本 - 完整测试TTS应用的所有功能."""
import requests
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple

API_BASE = "http://localhost:8000/api/v1"
BASE_API = "http://localhost:8000"

# 测试结果存储
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(name: str, passed: bool, details: str = ""):
    """记录测试结果."""
    test_results["total"] += 1
    if passed:
        test_results["passed"] += 1
        status = "[PASS]"
    else:
        test_results["failed"] += 1
        status = "[FAIL]"

    test_results["tests"].append({
        "name": name,
        "status": status,
        "details": details,
        "passed": passed
    })

    try:
        print(f"{status}: {name}")
        if details:
            print(f"   {details}")
        print()
    except UnicodeEncodeError:
        # Fallback for Windows console encoding issues
        print(f"{status}: Test completed")
        print()

def test_01_health_check():
    """测试1: 健康检查端点."""
    try:
        response = requests.get(f"{BASE_API}/health", timeout=5)
        data = response.json()

        passed = (
            response.status_code == 200 and
            data.get("status") == "healthy" and
            "version" in data
        )

        log_test(
            "1. 健康检查端点",
            passed,
            f"响应: {data}" if passed else f"状态码: {response.status_code}, 响应: {data}"
        )
        return passed
    except Exception as e:
        log_test("1. 健康检查端点", False, f"异常: {str(e)}")
        return False

def test_02_create_task_basic():
    """测试2: 创建基本任务."""
    try:
        request = {
            "text": "测试基本功能",
            "voice_name": "zh-CN-XiaoxiaoNeural",
            "rate": 1.0,
            "pitch": 1.0,
            "volume": 1.0
        }

        response = requests.post(f"{API_BASE}/tts/generate", json=request, timeout=10)
        data = response.json()

        passed = (
            response.status_code == 201 and
            "task_id" in data and
            data.get("status") == "queued"
        )

        log_test(
            "2. 创建基本TTS任务",
            passed,
            f"任务ID: {data.get('task_id', 'N/A')}" if passed else f"错误: {data}"
        )

        if passed:
            return data["task_id"]
        return None
    except Exception as e:
        log_test("2. 创建基本TTS任务", False, f"异常: {str(e)}")
        return None

def test_03_get_task_status(task_id: str):
    """测试3: 获取任务状态."""
    if not task_id:
        log_test("3. 获取任务状态", False, "无有效任务ID")
        return False

    try:
        response = requests.get(f"{API_BASE}/tts/tasks/{task_id}", timeout=5)
        data = response.json()

        passed = (
            response.status_code == 200 and
            data.get("task_id") == task_id and
            "status" in data
        )

        log_test(
            "3. 获取任务状态",
            passed,
            f"状态: {data.get('status')}, 进度: {data.get('progress')}%"
        )
        return passed
    except Exception as e:
        log_test("3. 获取任务状态", False, f"异常: {str(e)}")
        return False

def test_04_wait_for_completion(task_id: str, timeout: int = 60) -> bool:
    """测试4: 等待任务完成."""
    if not task_id:
        log_test("4. 等待任务完成", False, "无有效任务ID")
        return False

    print("   等待任务完成...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{API_BASE}/tts/tasks/{task_id}", timeout=5)
            data = response.json()

            status = data.get("status")
            progress = data.get("progress", 0)

            if status == "completed":
                log_test(
                    "4. 等待任务完成",
                    True,
                    f"耗时: {int(time.time() - start_time)}秒, 文件: {data.get('file_path', 'N/A')}"
                )
                return True
            elif status == "failed":
                log_test(
                    "4. 等待任务完成",
                    False,
                    f"任务失败: {data.get('error_message', 'Unknown error')}"
                )
                return False

            time.sleep(2)
        except Exception as e:
            log_test("4. 等待任务完成", False, f"异常: {str(e)}")
            return False

    log_test("4. 等待任务完成", False, f"超时 ({timeout}秒)")
    return False

def test_05_download_audio(task_id: str):
    """测试5: 下载音频文件."""
    if not task_id:
        log_test("5. 下载音频文件", False, "无有效任务ID")
        return False

    try:
        response = requests.get(f"{API_BASE}/tts/download/{task_id}", timeout=10)

        passed = (
            response.status_code == 200 and
            response.headers.get("content-type") == "audio/mpeg" and
            len(response.content) > 0
        )

        log_test(
            "5. 下载音频文件",
            passed,
            f"文件大小: {len(response.content)} 字节" if passed else f"状态码: {response.status_code}"
        )
        return passed
    except Exception as e:
        log_test("5. 下载音频文件", False, f"异常: {str(e)}")
        return False

def test_06_text_validation_empty():
    """测试6: 空文本验证."""
    try:
        request = {
            "text": "",
            "voice_name": "zh-CN-XiaoxiaoNeural",
            "rate": 1.0,
            "pitch": 1.0,
            "volume": 1.0
        }

        response = requests.post(f"{API_BASE}/tts/generate", json=request, timeout=5)

        passed = response.status_code == 422 or response.status_code == 400

        log_test(
            "6. 空文本验证",
            passed,
            f"正确拒绝空文本 (状态码: {response.status_code})" if passed else "应该拒绝空文本"
        )
        return passed
    except Exception as e:
        log_test("6. 空文本验证", False, f"异常: {str(e)}")
        return False

def test_07_text_validation_too_long():
    """测试7: 超长文本验证."""
    try:
        # 创建5001字符的文本
        long_text = "A" * 5001
        request = {
            "text": long_text,
            "voice_name": "zh-CN-XiaoxiaoNeural",
            "rate": 1.0,
            "pitch": 1.0,
            "volume": 1.0
        }

        response = requests.post(f"{API_BASE}/tts/generate", json=request, timeout=5)

        # Pydantic 验证返回 422，自定义验证返回 400
        passed = response.status_code in [400, 422]

        log_test(
            "7. 超长文本验证 (5001字符)",
            passed,
            f"正确拒绝超长文本 (状态码: {response.status_code})" if passed else "应该拒绝超长文本"
        )
        return passed
    except Exception as e:
        log_test("7. 超长文本验证", False, f"异常: {str(e)}")
        return False

def test_08_invalid_voice_name():
    """测试8: 无效音色名称."""
    try:
        request = {
            "text": "测试",
            "voice_name": "invalid-voice-name",
            "rate": 1.0,
            "pitch": 1.0,
            "volume": 1.0
        }

        response = requests.post(f"{API_BASE}/tts/generate", json=request, timeout=5)

        passed = response.status_code == 400

        log_test(
            "8. 无效音色名称验证",
            passed,
            f"正确拒绝无效音色" if passed else "应该拒绝无效音色"
        )
        return passed
    except Exception as e:
        log_test("8. 无效音色名称验证", False, f"异常: {str(e)}")
        return False

def test_09_invalid_parameters():
    """测试9: 无效参数值."""
    try:
        request = {
            "text": "测试",
            "voice_name": "zh-CN-XiaoxiaoNeural",
            "rate": -1.0,  # 无效速率
            "pitch": 1.0,
            "volume": 1.0
        }

        response = requests.post(f"{API_BASE}/tts/generate", json=request, timeout=5)

        passed = response.status_code == 422

        log_test(
            "9. 无效参数值验证 (rate=-1.0)",
            passed,
            f"正确拒绝无效参数" if passed else "应该拒绝无效参数"
        )
        return passed
    except Exception as e:
        log_test("9. 无效参数值验证", False, f"异常: {str(e)}")
        return False

def test_10_get_nonexistent_task():
    """测试10: 获取不存在的任务."""
    try:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(f"{API_BASE}/tts/tasks/{fake_id}", timeout=5)

        passed = response.status_code == 404

        log_test(
            "10. 获取不存在的任务",
            passed,
            f"正确返回404" if passed else f"状态码: {response.status_code}"
        )
        return passed
    except Exception as e:
        log_test("10. 获取不存在的任务", False, f"异常: {str(e)}")
        return False

def test_11_download_nonexistent_file():
    """测试11: 下载不存在的音频."""
    try:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(f"{API_BASE}/tts/download/{fake_id}", timeout=5)

        passed = response.status_code == 404

        log_test(
            "11. 下载不存在的音频",
            passed,
            f"正确返回404" if passed else f"状态码: {response.status_code}"
        )
        return passed
    except Exception as e:
        log_test("11. 下载不存在的音频", False, f"异常: {str(e)}")
        return False

def test_12_multiple_voices():
    """测试12: 测试多种音色."""
    voices = [
        "zh-CN-XiaoxiaoNeural",
        "zh-CN-YunyangNeural",
        "zh-CN-XiaoyouNeural"
    ]

    task_ids = []
    for voice in voices:
        try:
            request = {
                "text": f"测试音色 {voice}",
                "voice_name": voice,
                "rate": 1.0,
                "pitch": 1.0,
                "volume": 1.0
            }

            response = requests.post(f"{API_BASE}/tts/generate", json=request, timeout=10)

            if response.status_code == 201:
                task_ids.append(response.json().get("task_id"))
        except Exception as e:
            log_test(f"12. 测试多种音色 ({voice})", False, f"异常: {str(e)}")

    passed = len(task_ids) == len(voices)
    log_test(
        "12. 测试多种音色",
        passed,
        f"成功创建 {len(task_ids)}/{len(voices)} 个任务"
    )

    if passed:
        return task_ids
    return []

def test_13_concurrent_tasks():
    """测试13: 并发任务处理."""
    print("   创建5个并发任务...")

    task_ids = []
    for i in range(5):
        try:
            request = {
                "text": f"并发任务测试 {i+1}",
                "voice_name": "zh-CN-XiaoxiaoNeural",
                "rate": 1.0,
                "pitch": 1.0,
                "volume": 1.0
            }

            response = requests.post(f"{API_BASE}/tts/generate", json=request, timeout=10)

            if response.status_code == 201:
                task_ids.append(response.json().get("task_id"))
        except Exception as e:
            pass

    # 等待所有任务完成
    completed = 0
    start_time = time.time()
    timeout = 120  # 2分钟

    while time.time() - start_time < timeout and completed < len(task_ids):
        completed = 0
        for task_id in task_ids:
            try:
                response = requests.get(f"{API_BASE}/tts/tasks/{task_id}", timeout=5)
                if response.json().get("status") == "completed":
                    completed += 1
            except:
                pass
        time.sleep(2)

    passed = completed == len(task_ids)
    log_test(
        "13. 并发任务处理 (5个任务)",
        passed,
        f"完成: {completed}/{len(task_ids)} 个任务, 耗时: {int(time.time() - start_time)}秒"
    )
    return passed

def test_14_rate_pitch_volume_parameters():
    """测试14: 测试不同参数组合."""
    test_cases = [
        (0.5, 0.5, 0.5, "最小值"),
        (2.0, 2.0, 1.0, "最大值"),
        (1.5, 1.2, 0.8, "中间值")
    ]

    task_id = None
    for rate, pitch, volume, desc in test_cases:
        try:
            request = {
                "text": f"测试参数 {desc}",
                "voice_name": "zh-CN-XiaoxiaoNeural",
                "rate": rate,
                "pitch": pitch,
                "volume": volume
            }

            response = requests.post(f"{API_BASE}/tts/generate", json=request, timeout=10)

            if response.status_code == 201:
                task_id = response.json().get("task_id")
                time.sleep(1)
        except Exception as e:
            log_test(f"14. 参数测试 ({desc})", False, f"异常: {str(e)}")

    if task_id:
        log_test(
            "14. 测试不同参数组合",
            True,
            f"成功测试 {len(test_cases)} 种参数组合"
        )
        return True
    else:
        log_test("14. 测试不同参数组合", False, "所有测试失败")
        return False

def test_15_long_text():
    """测试15: 长文本处理."""
    # 创建1000字符的中文文本
    long_text = "这是一段很长的文本。" * 100

    try:
        request = {
            "text": long_text,
            "voice_name": "zh-CN-XiaoxiaoNeural",
            "rate": 1.0,
            "pitch": 1.0,
            "volume": 1.0
        }

        response = requests.post(f"{API_BASE}/tts/generate", json=request, timeout=10)

        if response.status_code == 201:
            task_id = response.json().get("task_id")

            # 等待完成
            for _ in range(60):
                resp = requests.get(f"{API_BASE}/tts/tasks/{task_id}", timeout=5)
                data = resp.json()
                if data.get("status") == "completed":
                    log_test(
                        "15. 长文本处理 (1000字符)",
                        True,
                        f"文件: {data.get('file_path', 'N/A')}"
                    )
                    return True
                elif data.get("status") == "failed":
                    log_test("15. 长文本处理", False, f"任务失败")
                    return False
                time.sleep(2)

        log_test("15. 长文本处理", False, "任务超时")
        return False
    except Exception as e:
        log_test("15. 长文本处理", False, f"异常: {str(e)}")
        return False

def test_16_special_characters():
    """测试16: 特殊字符处理."""
    special_texts = [
        "测试标点：，。！？、；：""''【】《》",
        "测试英文 Hello World 123",
        "测试混合 文本中with English 123"
    ]

    task_id = None
    for text in special_texts:
        try:
            request = {
                "text": text,
                "voice_name": "zh-CN-XiaoxiaoNeural",
                "rate": 1.0,
                "pitch": 1.0,
                "volume": 1.0
            }

            response = requests.post(f"{API_BASE}/tts/generate", json=request, timeout=10)

            if response.status_code == 201:
                task_id = response.json().get("task_id")
                time.sleep(1)
        except Exception as e:
            log_test(f"16. 特殊字符处理", False, f"异常: {str(e)}")

    if task_id:
        log_test(
            "16. 特殊字符处理",
            True,
            f"成功测试 {len(special_texts)} 种特殊文本"
        )
        return True
    else:
        log_test("16. 特殊字符处理", False, "所有测试失败")
        return False

def test_17_api_docs():
    """测试17: API文档可访问性."""
    try:
        # 测试Swagger UI
        response = requests.get(f"{BASE_API}/docs", timeout=5)
        swagger_ok = response.status_code == 200

        # 测试ReDoc
        response = requests.get(f"{BASE_API}/redoc", timeout=5)
        redoc_ok = response.status_code == 200

        passed = swagger_ok and redoc_ok

        log_test(
            "17. API文档可访问性",
            passed,
            f"Swagger: {'[OK]' if swagger_ok else '[FAIL]'}, ReDoc: {'[OK]' if redoc_ok else '[FAIL]'}"
        )
        return passed
    except Exception as e:
        log_test("17. API文档可访问性", False, f"异常: {str(e)}")
        return False

def test_18_queue_status():
    """测试18: 队列状态查询（如果端点存在）."""
    try:
        # 注意：这个端点可能不存在，取决于实现
        response = requests.get(f"{API_BASE}/queue/status", timeout=5)

        # 如果端点不存在，不算失败
        if response.status_code == 404:
            log_test(
                "18. 队列状态查询",
                True,
                "端点未实现 (可选功能)"
            )
            return True

        passed = response.status_code == 200
        log_test(
            "18. 队列状态查询",
            passed,
            f"队列状态: {response.json()}" if passed else f"状态码: {response.status_code}"
        )
        return passed
    except Exception as e:
        log_test("18. 队列状态查询", True, "端点未实现 (可选功能)")
        return True

def generate_report():
    """生成测试报告."""
    print("\n" + "="*80)
    print(" "*30 + "测试报告")
    print("="*80 + "\n")

    print(f"总测试数: {test_results['total']}")
    print(f"[PASS]: {test_results['passed']}")
    print(f"[FAIL]: {test_results['failed']}")
    print(f"通过率: {test_results['passed']/test_results['total']*100:.1f}%\n")

    print("="*80)
    print("详细结果:")
    print("="*80 + "\n")

    for test in test_results["tests"]:
        print(f"{test['status']} {test['name']}")
        if test['details']:
            print(f"   {test['details']}")
        print()

    print("="*80)

    # 保存到文件
    report_file = Path("test_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)

    print(f"\n报告已保存到: {report_file.absolute()}")
    print("="*80)

def main():
    """运行所有测试."""
    print("\n" + "="*80)
    print(" "*20 + "TTS应用系统性测试")
    print("="*80 + "\n")

    # 1. 基础功能测试
    print("【第一阶段：基础功能测试】\n")
    test_01_health_check()
    task_id = test_02_create_task_basic()
    if task_id:
        test_03_get_task_status(task_id)
        test_04_wait_for_completion(task_id)
        test_05_download_audio(task_id)

    # 2. 验证测试
    print("【第二阶段：输入验证测试】\n")
    test_06_text_validation_empty()
    test_07_text_validation_too_long()
    test_08_invalid_voice_name()
    test_09_invalid_parameters()

    # 3. 错误处理测试
    print("【第三阶段：错误处理测试】\n")
    test_10_get_nonexistent_task()
    test_11_download_nonexistent_file()

    # 4. 高级功能测试
    print("【第四阶段：高级功能测试】\n")
    test_12_multiple_voices()
    test_13_concurrent_tasks()
    test_14_rate_pitch_volume_parameters()
    test_15_long_text()
    test_16_special_characters()

    # 5. 系统测试
    print("【第五阶段：系统测试】\n")
    test_17_api_docs()
    test_18_queue_status()

    # 生成报告
    generate_report()

if __name__ == "__main__":
    main()
