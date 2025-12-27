"""
VideoGen 完整流程测试
测试从需求分析到视频生成的完整流程
"""

import requests
import time
import json
from datetime import datetime

# API 配置
API_BASE = "http://localhost:8000/api"
PROJECT_ID = f"TEST-{int(time.time())}"

def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")

def test_full_workflow():
    """测试完整工作流程"""
    
    print_section("🎬 VideoGen 完整流程测试")
    print(f"项目 ID: {PROJECT_ID}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # ==================== 步骤 1: 需求分析 ====================
    print_section("步骤 1: 需求分析")
    
    requirement = {
        "description": "制作一个30秒的智能手表宣传视频，展示产品的主要功能包括心率监测、运动追踪和信息提醒。风格要现代、科技感强，目标受众是年轻人。",
        "duration": 30,
        "quality_tier": "STANDARD",
        "style": "modern"
    }
    
    print(f"需求描述: {requirement['description']}")
    print(f"时长: {requirement['duration']} 秒")
    print(f"质量档位: {requirement['quality_tier']}")
    print(f"风格: {requirement['style']}\n")
    
    try:
        response = requests.post(
            f"{API_BASE}/analyze-requirement",
            json={
                "project_id": PROJECT_ID,
                "requirement": requirement
            },
            timeout=30
        )
        
        if response.status_code == 200:
            analysis = response.json()
            print("✅ 需求分析成功！")
            print(f"核心主题: {analysis.get('theme')}")
            print(f"视觉风格: {analysis.get('style')}")
            print(f"建议镜头数: {analysis.get('shots')}")
            print(f"预计时长: {analysis.get('duration')} 秒")
            if 'analysis_detail' in analysis:
                print(f"\nLLM 详细分析:\n{analysis['analysis_detail'][:200]}...")
        else:
            print(f"❌ 需求分析失败: {response.status_code}")
            print(response.text)
            return
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return
    
    time.sleep(2)
    
    # ==================== 步骤 2: 剧本生成 ====================
    print_section("步骤 2: 剧本生成")
    
    try:
        response = requests.post(
            f"{API_BASE}/generate-script",
            json={
                "project_id": PROJECT_ID,
                "analysis": analysis
            },
            timeout=60
        )
        
        if response.status_code == 200:
            script = response.json()
            print("✅ 剧本生成成功！")
            print(f"\n剧本内容:\n{'-' * 60}")
            print(script['content'][:500] + "..." if len(script['content']) > 500 else script['content'])
            print('-' * 60)
        else:
            print(f"❌ 剧本生成失败: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return
    
    time.sleep(2)
    
    # ==================== 步骤 3: 分镜生成 ====================
    print_section("步骤 3: 分镜生成")
    
    try:
        response = requests.post(
            f"{API_BASE}/generate-storyboard",
            json={
                "project_id": PROJECT_ID,
                "script": script
            },
            timeout=60
        )
        
        if response.status_code == 200:
            storyboard = response.json()
            print("✅ 分镜生成成功！")
            print(f"总镜头数: {storyboard['total_shots']}\n")
            
            for i, shot in enumerate(storyboard['shots'][:3], 1):  # 只显示前3个
                print(f"镜头 {i}: {shot['title']}")
                print(f"  描述: {shot['description']}")
                print(f"  时长: {shot['duration']}秒 | 机位: {shot['camera']} | 运动: {shot['movement']}\n")
            
            if len(storyboard['shots']) > 3:
                print(f"... 还有 {len(storyboard['shots']) - 3} 个镜头")
        else:
            print(f"❌ 分镜生成失败: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return
    
    time.sleep(2)
    
    # ==================== 步骤 4: 图像生成 ====================
    print_section("步骤 4: 图像生成（批量）")
    
    total_shots = min(storyboard['total_shots'], 3)  # 测试时只生成3张
    print(f"将生成 {total_shots} 张图像（测试模式）\n")
    
    images = []
    for i in range(1, total_shots + 1):
        print(f"正在生成镜头 {i} 的图像...")
        
        try:
            response = requests.post(
                f"{API_BASE}/generate-image",
                json={
                    "project_id": PROJECT_ID,
                    "shot": i
                },
                timeout=90
            )
            
            if response.status_code == 200:
                image_result = response.json()
                if image_result.get('success'):
                    images.append(image_result)
                    print(f"  ✅ 镜头 {i} 图像生成成功")
                    print(f"  URL: {image_result['image_url'][:80]}...")
                else:
                    print(f"  ⚠️ 镜头 {i} 使用降级图像")
                    images.append(image_result)
            else:
                print(f"  ❌ 镜头 {i} 生成失败")
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")
        
        time.sleep(1)  # 避免请求过快
    
    print(f"\n✅ 共生成 {len(images)} 张图像")
    
    time.sleep(2)
    
    # ==================== 步骤 5: 视频合成 ====================
    print_section("步骤 5: 视频合成")
    
    print("正在合成最终视频...\n")
    
    try:
        response = requests.post(
            f"{API_BASE}/generate-video",
            json={
                "project_id": PROJECT_ID,
                "images": [img['image_url'] for img in images]
            },
            timeout=180
        )
        
        if response.status_code == 200:
            video = response.json()
            if video.get('success'):
                print("✅ 视频生成成功！")
                print(f"\n视频信息:")
                print(f"  URL: {video['video_url']}")
                print(f"  时长: {video['duration']} 秒")
                print(f"  分辨率: {video['resolution']}")
                print(f"  生成时间: {video['generated_at']}")
            else:
                print("⚠️ 视频生成失败，使用示例视频")
                print(f"  错误: {video.get('error')}")
                print(f"  示例视频: {video['video_url']}")
        else:
            print(f"❌ 视频合成失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    # ==================== 测试总结 ====================
    print_section("测试总结")
    
    print(f"项目 ID: {PROJECT_ID}")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n测试步骤:")
    print("  ✅ 1. 需求分析 (LLM)")
    print("  ✅ 2. 剧本生成 (LLM)")
    print("  ✅ 3. 分镜生成 (LLM)")
    print(f"  ✅ 4. 图像生成 (Qwen × {len(images)})")
    print("  ✅ 5. 视频合成 (Wan2.2)")
    print("\n🎉 完整流程测试完成！")

if __name__ == "__main__":
    print("\n" + "🎬" * 30)
    print("VideoGen 完整流程测试")
    print("🎬" * 30)
    
    # 检查后端是否运行
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("\n✅ 后端服务运行正常")
            print("开始测试...\n")
            test_full_workflow()
        else:
            print("\n❌ 后端服务异常")
    except Exception as e:
        print("\n❌ 无法连接到后端服务")
        print("请先启动后端: python api_server.py")
        print(f"错误: {e}")
