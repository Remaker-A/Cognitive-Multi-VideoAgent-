"""
S3 客户端封装

封装 boto3 S3 客户端，提供简化的上传/下载/URL生成接口。
"""

import logging
from typing import List, Optional
import boto3
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


class S3Client:
    """
    S3/MinIO 客户端封装
    
    Features:
    - 文件上传/下载
    - Signed URL 生成
    - 对象管理
    """
    
    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        region: str = "us-east-1"
    ):
        """
        初始化 S3 客户端
        
        Args:
            endpoint_url: S3 端点 URL
            access_key: 访问密钥
            secret_key: 密钥
            bucket_name: 存储桶名称
            region: 区域
        """
        self.bucket_name = bucket_name
        
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # 确保 bucket 存在
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self) -> None:
        """确保 bucket 存在"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            try:
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to create bucket: {e}")
    
    def upload_file(self, file_path: str, object_key: str, content_type: Optional[str] = None) -> str:
        """
        上传文件
        
        Args:
            file_path: 本地文件路径
            object_key: S3 对象键
            content_type: 内容类型
            
        Returns:
            str: S3 URL
        """
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                object_key,
                ExtraArgs=extra_args
            )
            
            url = f"s3://{self.bucket_name}/{object_key}"
            logger.info(f"Uploaded file to {url}")
            return url
            
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise
    
    def upload_bytes(self, data: bytes, object_key: str, content_type: Optional[str] = None) -> str:
        """
        上传字节数据
        
        Args:
            data: 字节数据
            object_key: S3 对象键
            content_type: 内容类型
            
        Returns:
            str: S3 URL
        """
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=data,
                **extra_args
            )
            
            url = f"s3://{self.bucket_name}/{object_key}"
            logger.info(f"Uploaded bytes to {url}")
            return url
            
        except Exception as e:
            logger.error(f"Failed to upload bytes: {e}")
            raise
    
    def download_file(self, object_key: str, file_path: str) -> None:
        """
        下载文件
        
        Args:
            object_key: S3 对象键
            file_path: 本地文件路径
        """
        try:
            self.s3_client.download_file(
                self.bucket_name,
                object_key,
                file_path
            )
            logger.info(f"Downloaded {object_key} to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            raise
    
    def download_bytes(self, object_key: str) -> bytes:
        """
        下载为字节数据
        
        Args:
            object_key: S3 对象键
            
        Returns:
            bytes: 文件内容
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            return response['Body'].read()
            
        except Exception as e:
            logger.error(f"Failed to download bytes: {e}")
            raise
    
    def generate_signed_url(self, object_key: str, expires_in: int = 3600) -> str:
        """
        生成签名 URL
        
        Args:
            object_key: S3 对象键
            expires_in: 过期时间（秒）
            
        Returns:
            str: 签名 URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expires_in
            )
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {e}")
            raise
    
    def delete_object(self, object_key: str) -> bool:
        """
        删除对象
        
        Args:
            object_key: S3 对象键
            
        Returns:
            bool: 是否成功
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            logger.info(f"Deleted object: {object_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete object: {e}")
            return False
    
    def object_exists(self, object_key: str) -> bool:
        """
        检查对象是否存在
        
        Args:
            object_key: S3 对象键
            
        Returns:
            bool: 是否存在
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            return True
        except ClientError:
            return False
    
    def list_objects(self, prefix: str = "") -> List[str]:
        """
        列出对象
        
        Args:
            prefix: 前缀过滤
            
        Returns:
            List[str]: 对象键列表
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            return [obj['Key'] for obj in response['Contents']]
            
        except Exception as e:
            logger.error(f"Failed to list objects: {e}")
            return []
