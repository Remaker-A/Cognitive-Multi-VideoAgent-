"""
LLM 客户端

支持 OpenAI 和 Claude API。
"""

import logging
import os
from typing import Optional, Dict, Any
import asyncio


logger = logging.getLogger(__name__)


class LLMClient:
    """
    LLM 客户端
    
    支持 OpenAI 和 Claude API 调用。
    """
    
    def __init__(self, provider: str = "openai", api_key: Optional[str] = None):
        """
        初始化 LLM 客户端
        
        Args:
            provider: LLM 提供商 ("openai" 或 "claude")
            api_key: API 密钥（可选，默认从环境变量读取）
        """
        self.provider = provider.lower()
        self.api_key = api_key or self._get_api_key()
        self.client = None
        
        self._init_client()
        
        logger.info(f"LLMClient initialized with provider: {self.provider}")
    
    def _get_api_key(self) -> str:
        """从环境变量获取 API 密钥"""
        if self.provider == "openai":
            return os.getenv("OPENAI_API_KEY", "")
        elif self.provider == "claude":
            return os.getenv("ANTHROPIC_API_KEY", "")
        return ""
    
    def _init_client(self) -> None:
        """初始化客户端"""
        try:
            if self.provider == "openai":
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.api_key)
            elif self.provider == "claude":
                from anthropic import AsyncAnthropic
                self.client = AsyncAnthropic(api_key=self.api_key)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except ImportError as e:
            logger.error(f"Failed to import {self.provider} library: {e}")
            raise
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        生成文本
        
        Args:
            prompt: 用户 prompt
            system_prompt: 系统 prompt（可选）
            temperature: 温度参数
            max_tokens: 最大 token 数
            response_format: 响应格式（OpenAI 支持 JSON mode）
            
        Returns:
            str: 生成的文本
        """
        try:
            if self.provider == "openai":
                return await self._generate_openai(
                    prompt, system_prompt, temperature, max_tokens, response_format
                )
            elif self.provider == "claude":
                return await self._generate_claude(
                    prompt, system_prompt, temperature, max_tokens
                )
        except Exception as e:
            logger.error(f"LLM generation failed: {e}", exc_info=True)
            raise
    
    async def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict]
    ) -> str:
        """OpenAI API 调用"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        kwargs = {
            "model": "gpt-4-turbo-preview",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # JSON mode
        if response_format:
            kwargs["response_format"] = response_format
        
        response = await self.client.chat.completions.create(**kwargs)
        
        return response.choices[0].message.content
    
    async def _generate_claude(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Claude API 调用"""
        kwargs = {
            "model": "claude-3-opus-20240229",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        if system_prompt:
            kwargs["system"] = system_prompt
        
        response = await self.client.messages.create(**kwargs)
        
        return response.content[0].text
