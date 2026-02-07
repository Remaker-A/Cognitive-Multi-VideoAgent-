"""
测试 Sora2 Adapter
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


async def test_basic_video_generation():
    """测试基础视频生成"""
    print("\n=== 测试基础视频生成 ===")
    
    api_key = os.getenv("VIDEO_API_KEY")
    if not api_key:
        print("❌ 未找到 VIDEO_API_KEY")
        return False
    
    print(f"✓ API Key: {api_key[:20]}...")
    
    from src.interfaces.api.video_generator import VideoGenerator
    
    generator = VideoGenerator(api_key)
    print(f"✓ VideoGenerator initialized")
    
    # 测试简单视频生成
    prompt = "A mouse runs toward the camera, smiling and blinking, cinematic quality, smooth motion"
    print(f"\n生成视频，提示词: {prompt}")
    
    result = await generator.generate(
        prompt=prompt,
        duration=4,  # OmniMaaS 只支持 4, 8, 12 秒
        resolution="720x1280"  # 使用 OmniMaaS 支持的分辨率
    )
    
    if result.get("success"):
        print(f"✅ 视频生成成功!")
        print(f"  - 视频 URL: {result.get('video_url')}")
        print(f"  - 时长: {result.get('duration')}秒")
        print(f"  - 分辨率: {result.get('resolution')}")
        print(f"  - 帧率: {result.get('fps')}fps")
        print(f"  - 帧数: {result.get('frames')}")
        print(f"  - 成本: ${result.get('cost', 0):.4f}")
        if result.get("task_id"):
            print(f"  - 任务 ID: {result.get('task_id')}")
        return True
    else:
        print(f"❌ 视频生成失败: {result.get('error')}")
        return False


async def test_video_with_first_frame():
    """测试带首帧图像的视频生成"""
    print("\n=== 测试带首帧图像的视频生成 ===")
    
    api_key = os.getenv("VIDEO_API_KEY")
    if not api_key:
        print("❌ 未找到 VIDEO_API_KEY")
        return False
    
    from src.interfaces.api.video_generator import VideoGenerator
    
    generator = VideoGenerator(api_key)
    
    # 使用示例首帧图像
    first_frame_image = "https://cdn.hailuoai.com/prod/2024-09-18-16/user/multi_chat_file/9c0b5c14-ee88-4a5b-b503-4f626f018639.jpeg"
    prompt = "A mouse runs toward the camera, smiling and blinking, cinematic quality, smooth motion"
    
    print(f"生成视频:")
    print(f"  - 提示词: {prompt}")
    print(f"  - 首帧图像: {first_frame_image}")
    
    result = await generator.generate(
        prompt=prompt,
        first_frame_image=first_frame_image,
        duration=4,  # OmniMaaS 只支持 4, 8, 12 秒
        resolution="720x1280"  # 使用 OmniMaaS 支持的分辨率
    )
    
    if result.get("success"):
        print(f"✅ 视频生成成功!")
        print(f"  - 视频 URL: {result.get('video_url')}")
        print(f"  - 时长: {result.get('duration')}秒")
        print(f"  - 成本: ${result.get('cost', 0):.4f}")
        return True
    else:
        print(f"❌ 视频生成失败: {result.get('error')}")
        return False


async def test_video_with_motion_strength():
    """测试不同运动强度的视频生成"""
    print("\n=== 测试不同运动强度的视频生成 ===")
    
    api_key = os.getenv("VIDEO_API_KEY")
    if not api_key:
        print("❌ 未找到 VIDEO_API_KEY")
        return False
    
    from src.interfaces.api.video_generator import VideoGenerator
    
    generator = VideoGenerator(api_key)
    
    prompt = "A cat jumps over a fence, cinematic quality, smooth motion"
    
    # 测试低运动强度
    print(f"\n测试低运动强度 (0.3):")
    result_low = await generator.generate(
        prompt=prompt,
        duration=4,  # OmniMaaS 只支持 4, 8, 12 秒
        resolution="720x1280",
        motion_strength=0.3
    )
    
    # 测试高运动强度
    print(f"\n测试高运动强度 (0.8):")
    result_high = await generator.generate(
        prompt=prompt,
        duration=4,  # OmniMaaS 只支持 4, 8, 12 秒
        resolution="720x1280",
        motion_strength=0.8
    )
    
    success_count = sum([
        result_low.get("success", False),
        result_high.get("success", False)
    ])
    
    print(f"\n✅ 成功: {success_count}/2")
    return success_count == 2


async def test_generate_from_shots():
    """测试从镜头列表生成视频"""
    print("\n=== 测试从镜头列表生成视频 ===")
    
    api_key = os.getenv("VIDEO_API_KEY")
    if not api_key:
        print("❌ 未找到 VIDEO_API_KEY")
        return False
    
    from src.interfaces.api.video_generator import VideoGenerator
    
    generator = VideoGenerator(api_key)
    
    shots = [
        {
            "description": "A beautiful sunset over the ocean",
            "image_url": "https://cdn.hailuoai.com/prod/2024-09-18-16/user/multi_chat_file/9c0b5c14-ee88-4a5b-b503-4f626f018639.jpeg"
        },
        {
            "description": "Waves crashing on the shore",
            "image_url": "https://cdn.hailuoai.com/prod/2024-09-18-16/user/multi_chat_file/9c0b5c14-ee88-4a5b-b503-4f626f018639.jpeg"
        }
    ]
    
    print(f"从 {len(shots)} 个镜头生成视频")
    
    result = await generator.generate_from_shots(
        shots=shots,
        resolution="720x1280",  # 使用 OmniMaaS 支持的分辨率
        duration=4  # OmniMaaS 只支持 4, 8, 12 秒
    )
    
    if result.get("success"):
        print(f"✅ 视频生成成功!")
        print(f"  - 视频 URL: {result.get('video_url')}")
        print(f"  - 时长: {result.get('duration')}秒")
        return True
    else:
        print(f"❌ 视频生成失败: {result.get('error')}")
        return False


async def test_resolution_parsing():
    """测试分辨率解析"""
    print("\n=== 测试分辨率解析 ===")
    
    from src.interfaces.api.video_generator import VideoGenerator
    
    generator = VideoGenerator()
    
    test_cases = [
        ("1080P", (1920, 1080)),
        ("720P", (1280, 720)),
        ("1024x1024", (1024, 1024)),
        ("1328x1328", (1328, 1328)),
        ("4K", (3840, 2160)),
    ]
    
    all_passed = True
    for resolution, expected in test_cases:
        result = generator._parse_resolution(resolution)
        if result == expected:
            print(f"✅ {resolution} -> {result}")
        else:
            print(f"❌ {resolution} -> {result} (expected {expected})")
            all_passed = False
    
    return all_passed


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("Sora2 Adapter 测试套件")
    print("=" * 60)
    
    # 显示配置信息
    print("\n配置信息:")
    print(f"  VIDEO_MODEL: {os.getenv('VIDEO_MODEL', 'Not set')}")
    print(f"  VIDEO_API_URL: {os.getenv('VIDEO_API_URL', 'Not set')}")
    print(f"  VIDEO_API_KEY: {os.getenv('VIDEO_API_KEY', 'Not set')[:20]}...")
    
    # 运行测试
    tests = [
        ("分辨率解析", test_resolution_parsing),
        ("基础视频生成", test_basic_video_generation),
        ("带首帧图像的视频生成", test_video_with_first_frame),
        ("不同运动强度的视频生成", test_video_with_motion_strength),
        ("从镜头列表生成视频", test_generate_from_shots),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 测试 '{test_name}' 出错: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # 显示总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")


if __name__ == "__main__":
    asyncio.run(main())
