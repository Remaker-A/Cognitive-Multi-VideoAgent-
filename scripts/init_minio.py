#!/usr/bin/env python3
"""
MinIO 初始化脚本

创建必需的S3 buckets并设置访问策略
"""

import os
from dotenv import load_dotenv
from minio import Minio
from minio.error import S3Error

load_dotenv()


def init_minio():
    """初始化MinIO buckets"""
    print("正在连接MinIO...")
    
    endpoint = os.getenv('S3_ENDPOINT', 'localhost:9000').replace('http://', '').replace('https://', '')
    client = Minio(
        endpoint,
        access_key=os.getenv('S3_ACCESS_KEY', 'minioadmin'),
        secret_key=os.getenv('S3_SECRET_KEY', 'minioadmin123'),
        secure=False
    )
    
    # 定义需要创建的buckets
    buckets = [
        {
            'name': os.getenv('S3_BUCKET_ARTIFACTS', 'videogen-artifacts'),
            'description': '存储最终产物（图像、视频）'
        },
        {
            'name': os.getenv('S3_BUCKET_TEMP', 'videogen-temp'),
            'description': '存储临时文件'
        }
    ]
    
    for bucket in buckets:
        bucket_name = bucket['name']
        
        # 检查bucket是否已存在
        if client.bucket_exists(bucket_name):
            print(f"✅ Bucket '{bucket_name}' 已存在")
        else:
            # 创建bucket
            print(f"创建bucket '{bucket_name}'...")
            client.make_bucket(bucket_name)
            print(f"✅ Bucket '{bucket_name}' 创建成功")
        
        print(f"   用途: {bucket['description']}")
    
    print()
    print("💡 MinIO访问信息:")
    print(f"   Console: http://{endpoint.split(':')[0]}:9001")
    print(f"   用户名: {os.getenv('S3_ACCESS_KEY', 'minioadmin')}")
    print(f"   密码: {os.getenv('S3_SECRET_KEY', 'minioadmin123')}")
    print()
    print("💡 Python客户端使用示例:")
    print(f"""
    from minio import Minio
    
    client = Minio(
        '{endpoint}',
        access_key='{os.getenv('S3_ACCESS_KEY', 'minioadmin')}',
        secret_key='{os.getenv('S3_SECRET_KEY', 'minioadmin123')}',
        secure=False
    )
    
    # 上传文件
    client.fput_object(
        '{buckets[0]['name']}',
        'series-001/ep001/shot001/keyframe.png',
        'local_file.png'
    )
    
    # 生成下载URL（7天有效）
    url = client.presigned_get_object(
        '{buckets[0]['name']}',
        'series-001/ep001/shot001/keyframe.png',
        expires=timedelta(days=7)
    )
    """)


if __name__ == '__main__':
    try:
        init_minio()
    except S3Error as e:
        print(f"❌ MinIO错误: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        print()
        print("请确保:")
        print("  1. MinIO服务已启动: docker-compose up -d minio")
        print("  2. 配置正确: 检查.env中的S3_ENDPOINT、S3_ACCESS_KEY、S3_SECRET_KEY")
        exit(1)
