"""
测试 MiniMax 视频生成 API
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加 src 到路径
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from interfaces.api.video_generator import VideoGenerator


async def test_basic_video_generation():
    """测试基础视频生成"""
    print("\n=== 测试基础视频生成 ===")
    
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("❌ 未找到 API_KEY")
        return
    
    print(f"✓ API Key: {api_key[:20]}...")
    
    generator = VideoGenerator(api_key)
    print(f"✓ API URL: {generator.api_url}")
    print(f"✓ Model: {generator.model}")
    
    # 测试简单视频生成
    prompt = "A mouse runs toward the camera, smiling and blinking."
    print(f"\n生成视频，提示词: {prompt}")
    
    result = await generator.generate(
        prompt=prompt,
        duration=6,
        resolution="1080P"
    )
    
    if result.get("success"):
        print(f"✓ 视频生成成功!")
        print(f"  - 视频 URL: {result.get('video_url')}")
        print(f"  - 时长: {result.get('duration')}秒")
        print(f"  - 分辨率: {result.get('resolution')}")
        if result.get("task_id"):
            print(f"  - 任务 ID: {result.get('task_id')}")
    else:
        print(f"❌ 视频生成失败: {result.get('error')}")
    
    return result


async def test_video_with_first_frame():
    """测试带首帧图像的视频生成"""
    print("\n=== 测试带首帧图像的视频生成 ===")
    
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("❌ 未找到 API_KEY")
        return
    
    generator = VideoGenerator(api_key)
    
    # 使用示例中的首帧图像
    first_frame_image = "https://cdn.hailuoai.com/prod/2024-09-18-16/user/multi_chat_file/9c0b5c14-ee88-4a5b-b503-4f626f018639.jpeg"
    prompt = "A mouse runs toward the camera, smiling and blinking."
    
    print(f"生成视频:")
    print(f"  - 提示词: {prompt}")
    print(f"  - 首帧图像: {first_frame_image}")
    
    result = await generator.generate(
        prompt=prompt,
        first_frame_image=first_frame_image,
        duration=6,
        resolution="1080P"
    )
    
    if result.get("success"):
        print(f"✓ 视频生成成功!")
        print(f"  - 视频 URL: {result.get('video_url')}")
        print(f"  - 首帧图像: {result.get('first_frame_image')}")
    else:
        print(f"❌ 视频生成失败: {result.get('error')}")
    
    return result


async def test_different_resolutions():
    """测试不同分辨率"""
    print("\n=== 测试不同分辨率 ===")
    
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("❌ 未找到 API_KEY")
        return
    
    generator = VideoGenerator(api_key)
    
    resolutions = ["720P", "1080P"]
    prompt = "A beautiful sunset over the ocean with waves crashing"
    
    results = []
    for resolution in resolutions:
        print(f"\n测试分辨率: {resolution}")
        result = await generator.generate(
            prompt=prompt,
            duration=6,
            resolution=resolution
        )
        
        if result.get("success"):
            print(f"✓ {resolution} 视频生成成功")
            print(f"  - URL: {result.get('video_url')}")
        else:
            print(f"❌ {resolution} 视频生成失败: {result.get('error')}")
        
        results.append((resolution, result))
        
        # 避免请求过快
        await asyncio.sleep(2)
    
    return results


async def test_from_shots():
    """测试从分镜生成视频"""
    print("\n=== 测试从分镜生成视频 ===")
    
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("❌ 未找到 API_KEY")
        return
    
    generator = VideoGenerator(api_key)
    
    # 模拟分镜数据
    shots = [
        {
            "description": "A cat sitting on a windowsill",
            "image_url": "https://example.com/cat.jpg"  # 可选的首帧图像
        },
        {
            "description": "looking out at the rain"
        },
        {
            "description": "then turning to the camera and meowing"
        }
    ]
    
    print(f"从 {len(shots)} 个分镜生成视频:")
    for i, shot in enumerate(shots, 1):
        print(f"  镜头 {i}: {shot['description']}")
    
    result = await generator.generate_from_shots(
        shots=shots,
        resolution="1080P",
        duration=6
    )
    
    if result.get("success"):
        print(f"✓ 视频生成成功!")
        print(f"  - 视频 URL: {result.get('video_url')}")
    else:
        print(f"❌ 视频生成失败: {result.get('error')}")
    
    return result


async def main():
    """主测试函数"""
    print("=" * 60)
    print("MiniMax 视频生成 API 测试")
    print("=" * 60)
    
    # 运行测试
    tests = [
        ("基础视频生成", test_basic_video_generation),
        ("带首帧图像的视频生成", test_video_with_first_frame),
        ("不同分辨率测试", test_different_resolutions),
        ("从分镜生成视频", test_from_shots),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n❌ {test_name} 出错: {e}")
            results[test_name] = {"error": str(e)}
        
        # 测试之间等待
        await asyncio.sleep(3)
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for test_name, result in results.items():
        if isinstance(result, dict):
            if result.get("success"):
                print(f"✓ {test_name}: 成功")
            else:
                print(f"❌ {test_name}: {result.get('error', '未知错误')}")
        elif isinstance(result, list):
            # 处理多个结果
            success_count = sum(1 for _, r in result if r.get("success"))
            print(f"{'✓' if success_count > 0 else '❌'} {test_name}: {success_count}/{len(result)} 成功")
        else:
            print(f"? {test_name}: 结果类型未知")


if __name__ == "__main__":
    asyncio.run(main())
