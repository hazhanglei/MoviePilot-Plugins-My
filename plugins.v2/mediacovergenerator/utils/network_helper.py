"""
网络请求优化工具类
用于优化字体下载和其他网络操作，防止阻塞和超时
"""
import asyncio
import aiohttp
import requests
import time
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import hashlib
import subprocess
from app.log import logger
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NetworkHelper:
    """网络请求助手类，提供超时控制和重试机制"""

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        connector = aiohttp.TCPConnector(
            limit=10,
            limit_per_host=5,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'MoviePilot-MediaCoverGenerator/1.0'},
            trust_env=True
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()

    async def download_file_async(self, url: str, save_path: Path,
                                  expected_size: Optional[int] = None) -> bool:
        """异步下载文件"""
        if not self.session:
            raise RuntimeError("NetworkHelper must be used as async context manager")
        for attempt in range(self.max_retries):
            try:
                logger.info(f"开始下载文件 (尝试 {attempt + 1}/{self.max_retries}): {url}")
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        if expected_size and len(content) != expected_size:
                            logger.warning(f"文件大小不匹配: 期望 {expected_size}, 实际 {len(content)}")
                            if attempt < self.max_retries - 1:
                                continue
                        save_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(save_path, 'wb') as f:
                            f.write(content)
                        logger.info(f"文件下载成功: {save_path}")
                        return True
                    else:
                        logger.warning(f"下载失败，HTTP状态码: {response.status}")
            except asyncio.TimeoutError:
                logger.warning(f"下载超时 (尝试 {attempt + 1}/{self.max_retries}): {url}")
            except Exception as e:
                logger.warning(f"下载出错 (尝试 {attempt + 1}/{self.max_retries}): {e}")
            if attempt < self.max_retries - 1:
                await asyncio.sleep(2 ** attempt)
        logger.error(f"文件下载失败，已重试 {self.max_retries} 次: {url}")
        return False

    def download_file_sync(self, url: str, save_path: Path,
                           expected_size: Optional[int] = None) -> bool:
        """同步下载文件"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"开始下载文件 (尝试 {attempt + 1}/{self.max_retries}): {url}")
                verify_ssl = True
                try:
                    response = requests.get(
                        url,
                        timeout=self.timeout,
                        headers={'User-Agent': 'MoviePilot-MediaCoverGenerator/1.0'},
                        stream=True,
                        verify=verify_ssl
                    )
                except requests.exceptions.SSLError:
                    logger.warning(f"SSL验证失败，尝试忽略证书验证 (尝试 {attempt + 1}/{self.max_retries})")
                    verify_ssl = False
                    response = requests.get(
                        url,
                        timeout=self.timeout,
                        headers={'User-Agent': 'MoviePilot-MediaCoverGenerator/1.0'},
                        stream=True,
                        verify=verify_ssl
                    )
                if response.status_code == 200:
                    content = response.content
                    if expected_size and len(content) != expected_size:
                        logger.warning(f"文件大小不匹配: 期望 {expected_size}, 实际 {len(content)}")
                        if attempt < self.max_retries - 1:
                            continue
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(save_path, 'wb') as f:
                        f.write(content)
                    logger.info(f"文件下载成功: {save_path}")
                    return True
                else:
                    logger.warning(f"下载失败，HTTP状态码: {response.status_code}")
            except requests.exceptions.Timeout:
                logger.warning(f"下载超时 (尝试 {attempt + 1}/{self.max_retries}): {url}")
            except Exception as e:
                logger.warning(f"下载出错 (尝试 {attempt + 1}/{self.max_retries}): {e}")
            if attempt < self.max_retries - 1:
                time.sleep(2 ** attempt)

        try:
            logger.info(f"Python下载失败，尝试使用系统 wget 命令: {url}")
            save_path.parent.mkdir(parents=True, exist_ok=True)

            cmd = ["wget", "-O", str(save_path), url]
            if "github.com" in url or "raw.githubusercontent.com" in url:
                cmd.append("--no-check-certificate")

            subprocess.run(cmd, check=True, timeout=self.timeout * 2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if save_path.exists() and save_path.stat().st_size > 0:
                if expected_size and save_path.stat().st_size != expected_size:
                    logger.warning(f"wget下载文件大小不匹配")
                    return False
                logger.info(f"wget 下载成功: {save_path}")
                return True
        except Exception as e:
            logger.error(f"wget 下载也失败: {e}")
        logger.error(f"文件下载失败，已重试 {self.max_retries} 次 + wget: {url}")
        return False


def validate_font_file(font_path: Path) -> bool:
    """验证字体文件是否有效"""
    try:
        if not font_path.exists() or font_path.stat().st_size == 0:
            return False
        from PIL import ImageFont
        font = ImageFont.truetype(str(font_path), 12)
        return True
    except Exception as e:
        logger.warning(f"字体文件验证失败: {font_path}, 错误: {e}")
        return False


def get_file_hash(file_path: Path) -> Optional[str]:
    """计算文件的MD5哈希值"""
    try:
        if not file_path.exists():
            return None
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logger.warning(f"计算文件哈希失败: {file_path}, 错误: {e}")
        return None