"""
VideoGen 性能优化测试脚本

测试所有优化组件是否正常工作
"""

import asyncio
import time
import logging
from typing import List

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_imports():
    """测试1: 验证所有优化组件可以正常导入"""
    print("\n" + "="*60)
    print("测试1: 验证优化组件导入")
    print("="*60)

    try:
        from src.infrastructure.performance import (
            model_manager,
            image_decode_cache,
            BatchProcessor,
            BatchConfig
        )
        print("✅ 性能优化组件导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_model_manager():
    """测试2: 验证共享模型管理器"""
    print("\n" + "="*60)
    print("测试2: 共享模型管理器")
    print("="*60)

    try:
        from src.infrastructure.performance import model_manager

        # 检测设备
        print(f"检测到设备: {model_manager.device}")

        # 加载CLIP模型
        print("加载CLIP模型...")
        start = time.time()
        model, processor = model_manager.get_clip_model()
        load_time = time.time() - start

        print(f"✅ CLIP模型加载成功 (耗时: {load_time:.2f}秒)")

        # 查看内存使用
        memory_info = model_manager.get_memory_usage()
        if 'allocated_gb' in memory_info:
            print(f"GPU内存使用: {memory_info['allocated_gb']:.2f} GB")
        else:
            print(f"设备: {memory_info['device']}")

        # 查看模型信息
        info = model_manager.get_model_info()
        print(f"已加载模型: {info['loaded_models']}")
        print(f"引用计数: {info['ref_counts']}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_image_cache():
    """测试3: 验证图像解码缓存"""
    print("\n" + "="*60)
    print("测试3: 图像解码缓存")
    print("="*60)

    try:
        from src.infrastructure.performance import image_decode_cache

        # 测试数据（1x1像素的PNG）
        test_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

        # 第一次解码（缓存未命中）
        print("第一次解码（缓存未命中）...")
        start = time.time()
        image1 = image_decode_cache.get_or_decode(test_data)
        time1 = time.time() - start

        # 第二次解码（缓存命中）
        print("第二次解码（缓存命中）...")
        start = time.time()
        image2 = image_decode_cache.get_or_decode(test_data)
        time2 = time.time() - start

        print(f"第一次解码: {time1*1000:.2f}ms")
        print(f"第二次解码: {time2*1000:.2f}ms")
        print(f"加速比: {time1/time2:.1f}x")

        # 查看缓存统计
        stats = image_decode_cache.get_stats()
        print(f"\n缓存统计:")
        print(f"  命中: {stats['hits']}")
        print(f"  未命中: {stats['misses']}")
        print(f"  命中率: {stats['hit_rate']:.2%}")
        print(f"  缓存大小: {stats['cache_size']}/{stats['max_size']}")

        if stats['hits'] > 0:
            print("✅ 图像解码缓存工作正常")
            return True
        else:
            print("⚠️ 缓存未命中，可能有问题")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_batch_processor():
    """测试4: 验证批处理器"""
    print("\n" + "="*60)
    print("测试4: 批处理器")
    print("="*60)

    try:
        from src.infrastructure.performance import BatchProcessor, BatchConfig

        # 创建批处理器
        config = BatchConfig(
            max_concurrent=3,
            timeout=10.0,
            max_retries=2
        )
        processor = BatchProcessor(config)

        # 模拟异步任务
        async def mock_task(item: int):
            await asyncio.sleep(0.1)  # 模拟耗时操作
            return item * 2

        # 批量处理
        items = list(range(10))
        print(f"批量处理 {len(items)} 个任务（并发数: {config.max_concurrent}）...")

        start = time.time()
        results = await processor.process_batch(
            items=items,
            processor_func=mock_task
        )
        duration = time.time() - start

        # 验证结果
        expected = [i * 2 for i in items]
        success = results == expected

        print(f"处理时间: {duration:.2f}秒")
        print(f"预期时间（串行）: {len(items) * 0.1:.2f}秒")
        print(f"加速比: {(len(items) * 0.1) / duration:.1f}x")

        # 查看统计
        stats = processor.get_stats()
        print(f"\n批处理统计:")
        print(f"  总数: {stats['total']}")
        print(f"  成功: {stats['success']}")
        print(f"  失败: {stats['failed']}")
        print(f"  重试: {stats['retried']}")

        if success and stats['success'] == len(items):
            print("✅ 批处理器工作正常")
            return True
        else:
            print("❌ 批处理器结果不正确")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_clip_scorer():
    """测试5: 验证CLIP Scorer优化"""
    print("\n" + "="*60)
    print("测试5: CLIP Scorer优化")
    print("="*60)

    try:
        from src.agents.cognitive.image_gen.clip_scorer import CLIPScorer

        # 初始化（应该使用共享模型）
        print("初始化CLIP Scorer...")
        scorer = CLIPScorer()

        # 测试图像
        test_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

        # 计算相似度
        print("计算CLIP相似度...")
        score = scorer.calculate_similarity(test_data, "a red pixel")

        if score is not None:
            print(f"✅ CLIP Scorer工作正常 (相似度: {score:.4f})")
            return True
        else:
            print("❌ CLIP Scorer返回None")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_embedding_extractor():
    """测试6: 验证Embedding Extractor优化"""
    print("\n" + "="*60)
    print("测试6: Embedding Extractor优化")
    print("="*60)

    try:
        from src.agents.cognitive.image_gen.embedding_extractor import EmbeddingExtractor

        # 初始化（应该使用共享模型）
        print("初始化Embedding Extractor...")
        extractor = EmbeddingExtractor()

        # 测试图像
        test_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

        # 提取embedding
        print("提取embedding...")
        embedding = extractor.extract(test_data)

        if embedding is not None:
            print(f"✅ Embedding Extractor工作正常 (维度: {embedding.shape})")
            return True
        else:
            print("❌ Embedding Extractor返回None")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_frame_extractor():
    """测试7: 验证视频帧提取优化"""
    print("\n" + "="*60)
    print("测试7: 视频帧提取优化")
    print("="*60)

    try:
        from src.agents.cognitive.video_gen.frame_extractor import FrameExtractor

        # 初始化
        print("初始化Frame Extractor...")
        extractor = FrameExtractor()

        # 检查是否使用decord
        try:
            import decord
            print("✅ decord已安装（将使用快速解码）")
        except ImportError:
            print("⚠️ decord未安装（将回退到OpenCV）")

        print("✅ Frame Extractor初始化成功")
        print("注意: 需要实际视频文件才能测试帧提取功能")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_optimization():
    """测试8: 验证内存优化"""
    print("\n" + "="*60)
    print("测试8: 内存优化验证")
    print("="*60)

    try:
        import psutil
        import os

        process = psutil.Process(os.getpid())

        # 记录初始内存
        mem_before = process.memory_info().rss / 1024**3
        print(f"初始内存: {mem_before:.2f} GB")

        # 初始化所有组件（应该共享CLIP模型）
        from src.agents.cognitive.image_gen.clip_scorer import CLIPScorer
        from src.agents.cognitive.image_gen.embedding_extractor import EmbeddingExtractor
        from src.agents.cognitive.video_gen.frame_extractor import FrameExtractor

        print("初始化所有组件...")
        scorer = CLIPScorer()
        extractor = EmbeddingExtractor()
        frame_ext = FrameExtractor()

        # 记录最终内存
        mem_after = process.memory_info().rss / 1024**3
        mem_increase = mem_after - mem_before

        print(f"最终内存: {mem_after:.2f} GB")
        print(f"内存增加: {mem_increase:.2f} GB")

        # 验证内存增加是否合理（应该约0.6GB而不是1.8GB）
        if mem_increase < 1.0:
            print(f"✅ 内存优化有效（增加 {mem_increase:.2f} GB < 1.0 GB）")
            return True
        else:
            print(f"⚠️ 内存增加较多（{mem_increase:.2f} GB），可能未使用共享模型")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("VideoGen 性能优化测试套件")
    print("="*60)

    results = {}

    # 运行同步测试
    results['imports'] = test_imports()
    results['model_manager'] = test_model_manager()
    results['image_cache'] = test_image_cache()
    results['clip_scorer'] = test_clip_scorer()
    results['embedding_extractor'] = test_embedding_extractor()
    results['frame_extractor'] = test_frame_extractor()
    results['memory_optimization'] = test_memory_optimization()

    # 运行异步测试
    results['batch_processor'] = await test_batch_processor()

    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:25s}: {status}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！系统优化工作正常。")
    else:
        print(f"\n⚠️ {total - passed} 个测试失败，请检查错误信息。")

    return passed == total


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(run_all_tests())

    # 退出码
    import sys
    sys.exit(0 if success else 1)
