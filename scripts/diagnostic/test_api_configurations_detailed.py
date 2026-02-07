"""
详细的API配置测试脚本
提供更全面的诊断信息和修复建议
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
import httpx
from datetime import datetime

# 加载环境变量
load_dotenv()

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class DetailedAPITester:
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
    
    def print_header(self, title):
        """打印标题"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
    
    def print_subheader(self, title):
        """打印子标题"""
        print(f"\n--- {title} ---")
    
    def log_result(self, api_name, test_name, success, message, details=None):
        """记录测试结果"""
        result = {
            "api": api_name,
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} [{api_name}] {test_name}: {message}")
        if details:
            for key, value in details.items():
                if key != "traceback":
                    print(f"   - {key}: {value}")
    
    async def test_llm_api_detailed(self):
        """详细测试 LLM API"""
        self.print_header("LLM API 详细测试（豆包 DeepSeek-V3）")
        
        api_key = os.getenv("API_KEY")
        base_url = os.getenv("LLM_BASE_URL")
        model = os.getenv("CHAT_MODEL")
        
        self.print_subheader("配置验证")
        
        if not api_key:
            self.log_result("LLM", "API Key", False, "未配置")
            return
        else:
            self.log_result("LLM", "API Key", True, f"已配置 (前20位: {api_key[:20]})")
        
        if not base_url:
            self.log_result("LLM", "Base URL", False, "未配置")
            return
        else:
            self.log_result("LLM", "Base URL", True, base_url)
        
        if not model:
            self.log_result("LLM", "Model", False, "未配置")
            return
        else:
            self.log_result("LLM", "Model", True, model)
        
        self.print_subheader("API端点测试")
        
        endpoints = [
            ("Models List", f"{base_url}/models"),
            ("Chat Completions", f"{base_url}/chat/completions"),
        ]
        
        for name, url in endpoints:
            try:
                async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
                    response = await client.get(
                        url,
                        headers={"Authorization": f"Bearer {api_key}"}
                    )
                    self.log_result("LLM", f"端点 {name}", True, f"状态码: {response.status_code}")
            except Exception as e:
                self.log_result("LLM", f"端点 {name}", False, str(e))
        
        self.print_subheader("实际API调用测试")
        
        try:
            async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 10
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result("LLM", "API调用", True, "成功", {
                        "状态码": response.status_code,
                        "响应长度": len(str(data)),
                        "模型": data.get("model", "N/A")
                    })
                else:
                    self.log_result("LLM", "API调用", False, f"失败: {response.status_code}", {
                        "错误": response.text[:300]
                    })
        except Exception as e:
            import traceback
            self.log_result("LLM", "API调用", False, str(e), {
                "错误类型": type(e).__name__,
                "traceback": traceback.format_exc()[:300]
            })
    
    async def test_image_api_detailed(self):
        """详细测试 Image API"""
        self.print_header("Image API 详细测试（OmniMaaS）")
        
        api_key = os.getenv("IMAGE_API_KEY")
        base_url = os.getenv("IMAGE_API_URL")
        model = os.getenv("IMAGE_MODEL")
        
        self.print_subheader("配置验证")
        
        if not api_key:
            self.log_result("Image", "API Key", False, "未配置")
            return
        else:
            self.log_result("Image", "API Key", True, f"已配置 (前20位: {api_key[:20]})")
        
        if not base_url:
            self.log_result("Image", "Base URL", False, "未配置")
            return
        else:
            self.log_result("Image", "Base URL", True, base_url)
        
        if not model:
            self.log_result("Image", "Model", False, "未配置")
            return
        else:
            self.log_result("Image", "Model", True, model)
        
        self.print_subheader("API端点测试")
        
        endpoints = [
            ("Models List", f"{base_url}/models"),
            ("Image Generations", f"{base_url}/images/generations"),
        ]
        
        for name, url in endpoints:
            try:
                async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
                    response = await client.get(
                        url,
                        headers={"Authorization": f"Bearer {api_key}"}
                    )
                    self.log_result("Image", f"端点 {name}", True, f"状态码: {response.status_code}")
            except Exception as e:
                self.log_result("Image", f"端点 {name}", False, str(e))
        
        self.print_subheader("实际API调用测试")
        
        try:
            async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
                response = await client.post(
                    f"{base_url}/images/generations",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "prompt": "A beautiful sunset",
                        "size": "1024x1024",
                        "n": 1
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result("Image", "API调用", True, "成功", {
                        "状态码": response.status_code,
                        "有数据": bool(data)
                    })
                else:
                    try:
                        error_data = response.json()
                        self.log_result("Image", "API调用", False, f"失败: {response.status_code}", {
                            "错误代码": error_data.get("error", {}).get("code", "N/A"),
                            "错误消息": error_data.get("error", {}).get("message", "N/A")[:200]
                        })
                    except:
                        self.log_result("Image", "API调用", False, f"失败: {response.status_code}", {
                            "响应": response.text[:300]
                        })
        except Exception as e:
            import traceback
            self.log_result("Image", "API调用", False, str(e), {
                "错误类型": type(e).__name__,
                "traceback": traceback.format_exc()[:300]
            })
    
    async def test_video_api_detailed(self):
        """详细测试 Video API"""
        self.print_header("Video API 详细测试（OmniMaaS Sora2）")
        
        api_key = os.getenv("VIDEO_API_KEY")
        base_url = os.getenv("VIDEO_API_URL")
        model = os.getenv("VIDEO_MODEL")
        
        self.print_subheader("配置验证")
        
        if not api_key:
            self.log_result("Video", "API Key", False, "未配置")
            return
        else:
            self.log_result("Video", "API Key", True, f"已配置 (前20位: {api_key[:20]})")
        
        if not base_url:
            self.log_result("Video", "Base URL", False, "未配置")
            return
        else:
            self.log_result("Video", "Base URL", True, base_url)
        
        if not model:
            self.log_result("Video", "Model", False, "未配置")
            return
        else:
            self.log_result("Video", "Model", True, model)
        
        self.print_subheader("API端点测试")
        
        endpoints = [
            ("Models List", f"{base_url}/models"),
            ("Videos", f"{base_url}/videos"),
        ]
        
        for name, url in endpoints:
            try:
                async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
                    response = await client.get(
                        url,
                        headers={"Authorization": f"Bearer {api_key}"}
                    )
                    self.log_result("Video", f"端点 {name}", True, f"状态码: {response.status_code}")
            except Exception as e:
                self.log_result("Video", f"端点 {name}", False, str(e))
        
        self.print_subheader("实际API调用测试")
        
        try:
            async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
                response = await client.post(
                    f"{base_url}/videos",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "prompt": "A cat running",
                        "seconds": "4",
                        "size": "720x1280"
                    }
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    task_id = data.get("id") or data.get("task_id")
                    self.log_result("Video", "API调用", True, "成功", {
                        "状态码": response.status_code,
                        "任务ID": task_id
                    })
                else:
                    try:
                        error_data = response.json()
                        self.log_result("Video", "API调用", False, f"失败: {response.status_code}", {
                            "错误代码": error_data.get("code", "N/A"),
                            "错误消息": error_data.get("message", "N/A")[:200]
                        })
                    except:
                        self.log_result("Video", "API调用", False, f"失败: {response.status_code}", {
                            "响应": response.text[:300]
                        })
        except Exception as e:
            import traceback
            self.log_result("Video", "API调用", False, str(e), {
                "错误类型": type(e).__name__,
                "traceback": traceback.format_exc()[:300]
            })
    
    def print_recommendations(self):
        """打印修复建议"""
        self.print_header("修复建议")
        
        print("\n【高优先级】")
        print("1. Video API 配额问题")
        print("   - 检查 OmniMaaS 账户余额")
        print("   - 充值或升级套餐")
        print("   - 联系技术支持")
        
        print("\n2. Image API 模型不可用")
        print("   - 联系 OmniMaaS 技术支持")
        print("   - 配置模型访问渠道")
        print("   - 或更换为其他可用模型")
        
        print("\n【中优先级】")
        print("3. 安装 PostgreSQL")
        print("   pip install psycopg2-binary")
        
        print("\n4. 启动 Redis 服务")
        print("   redis-server")
        
        print("\n【低优先级】")
        print("5. 添加监控和日志")
        print("   - 记录 API 调用")
        print("   - 监控配额使用")
        print("   - 设置告警机制")
    
    def print_summary(self):
        """打印测试总结"""
        self.print_header("测试总结")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n总计: {total_tests} 个测试")
        print(f"✅ 通过: {passed_tests}")
        print(f"❌ 失败: {failed_tests}")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print("\n失败的测试:")
            for result in self.results:
                if not result["success"]:
                    print(f"  - [{result['api']}] {result['test']}: {result['message']}")
        
        print(f"\n测试耗时: {(datetime.now() - self.start_time).total_seconds():.2f} 秒")
    
    def save_results(self):
        """保存测试结果到文件"""
        output_file = "api_test_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": self.start_time.isoformat(),
                "duration": (datetime.now() - self.start_time).total_seconds(),
                "total_tests": len(self.results),
                "passed_tests": sum(1 for r in self.results if r["success"]),
                "failed_tests": sum(1 for r in self.results if not r["success"]),
                "results": self.results
            }, f, indent=2, ensure_ascii=False)
        print(f"\n测试结果已保存到: {output_file}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("开始详细API配置测试...")
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        await self.test_llm_api_detailed()
        await self.test_image_api_detailed()
        await self.test_video_api_detailed()
        
        self.print_recommendations()
        self.print_summary()
        self.save_results()


async def main():
    tester = DetailedAPITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
