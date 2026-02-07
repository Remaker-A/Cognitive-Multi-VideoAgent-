"""
测试项目所有API配置情况
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import httpx

# 加载环境变量
load_dotenv()

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class APITester:
    def __init__(self):
        self.results = []
    
    def log_result(self, api_name, test_name, success, message, details=None):
        """记录测试结果"""
        result = {
            "api": api_name,
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} [{api_name}] {test_name}: {message}")
        if details:
            for key, value in details.items():
                print(f"   - {key}: {value}")
    
    async def test_llm_api(self):
        """测试 LLM API（豆包 DeepSeek-V3）"""
        print("\n" + "="*60)
        print("测试 LLM API（豆包 DeepSeek-V3）")
        print("="*60)
        
        api_key = os.getenv("API_KEY")
        base_url = os.getenv("LLM_BASE_URL")
        model = os.getenv("CHAT_MODEL")
        
        if not api_key or not base_url or not model:
            self.log_result("LLM", "配置检查", False, "缺少必要的配置项")
            return
        
        self.log_result("LLM", "配置检查", True, "配置完整", {
            "model": model,
            "base_url": base_url,
            "api_key_prefix": api_key[:20] + "..."
        })
        
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
                    self.log_result("LLM", "API调用", True, "API调用成功", {
                        "status_code": response.status_code,
                        "response_length": len(str(data))
                    })
                else:
                    self.log_result("LLM", "API调用", False, f"API调用失败: {response.status_code}", {
                        "error": response.text[:200]
                    })
        except Exception as e:
            import traceback
            self.log_result("LLM", "API调用", False, f"连接错误: {str(e)}", {
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()[:500]
            })
    
    async def test_image_api(self):
        """测试 Image API（OmniMaaS）"""
        print("\n" + "="*60)
        print("测试 Image API（OmniMaaS）")
        print("="*60)
        
        api_key = os.getenv("IMAGE_API_KEY")
        base_url = os.getenv("IMAGE_API_URL")
        model = os.getenv("IMAGE_MODEL")
        
        if not api_key or not base_url or not model:
            self.log_result("Image", "配置检查", False, "缺少必要的配置项")
            return
        
        self.log_result("Image", "配置检查", True, "配置完整", {
            "model": model,
            "base_url": base_url,
            "api_key_prefix": api_key[:20] + "..."
        })
        
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
                    self.log_result("Image", "API调用", True, "API调用成功", {
                        "status_code": response.status_code,
                        "has_data": bool(data)
                    })
                else:
                    self.log_result("Image", "API调用", False, f"API调用失败: {response.status_code}", {
                        "error": response.text[:200]
                    })
        except Exception as e:
            import traceback
            self.log_result("Image", "API调用", False, f"连接错误: {str(e)}", {
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()[:500]
            })
    
    async def test_video_api(self):
        """测试 Video API（OmniMaaS Sora2）"""
        print("\n" + "="*60)
        print("测试 Video API（OmniMaaS Sora2）")
        print("="*60)
        
        api_key = os.getenv("VIDEO_API_KEY")
        base_url = os.getenv("VIDEO_API_URL")
        model = os.getenv("VIDEO_MODEL")
        
        if not api_key or not base_url or not model:
            self.log_result("Video", "配置检查", False, "缺少必要的配置项")
            return
        
        self.log_result("Video", "配置检查", True, "配置完整", {
            "model": model,
            "base_url": base_url,
            "api_key_prefix": api_key[:20] + "..."
        })
        
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
                    self.log_result("Video", "API调用", True, "API调用成功", {
                        "status_code": response.status_code,
                        "task_id": task_id
                    })
                else:
                    self.log_result("Video", "API调用", False, f"API调用失败: {response.status_code}", {
                        "error": response.text[:200]
                    })
        except Exception as e:
            import traceback
            self.log_result("Video", "API调用", False, f"连接错误: {str(e)}", {
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()[:500]
            })
    
    async def test_database_connections(self):
        """测试数据库连接"""
        print("\n" + "="*60)
        print("测试数据库连接")
        print("="*60)
        
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
        
        redis_host = os.getenv("REDIS_HOST")
        redis_port = os.getenv("REDIS_PORT")
        
        self.log_result("Database", "PostgreSQL配置", True, "配置已设置", {
            "host": db_host,
            "port": db_port,
            "database": db_name
        })
        
        self.log_result("Database", "Redis配置", True, "配置已设置", {
            "host": redis_host,
            "port": redis_port
        })
        
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
            conn.close()
            self.log_result("Database", "PostgreSQL连接", True, "连接成功")
        except ImportError:
            self.log_result("Database", "PostgreSQL连接", False, "psycopg2未安装")
        except Exception as e:
            self.log_result("Database", "PostgreSQL连接", False, f"连接失败: {str(e)}")
        
        try:
            import redis
            r = redis.Redis(host=redis_host, port=redis_port, db=0)
            r.ping()
            self.log_result("Database", "Redis连接", True, "连接成功")
        except ImportError:
            self.log_result("Database", "Redis连接", False, "redis未安装")
        except Exception as e:
            self.log_result("Database", "Redis连接", False, f"连接失败: {str(e)}")
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        
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
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("开始测试项目所有API配置...")
        print("="*60)
        
        await self.test_llm_api()
        await self.test_image_api()
        await self.test_video_api()
        await self.test_database_connections()
        
        self.print_summary()


async def main():
    tester = APITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
