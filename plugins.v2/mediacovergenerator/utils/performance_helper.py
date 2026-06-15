"""
性能优化工具类
用于优化图像处理性能，减少CPU和内存占用
"""
import time
import threading
from typing import Tuple, Optional, Callable, Any
from PIL import Image, ImageFilter
import numpy as np
from app.log import logger


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        logger.debug(f"开始执行: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        if duration > 1.0:
            logger.info(f"完成执行: {self.operation_name}, 耗时: {duration:.2f}秒")
        else:
            logger.debug(f"完成执行: {self.operation_name}, 耗时: {duration:.3f}秒")


class OptimizedImageProcessor:
    """优化的图像处理器"""

    @staticmethod
    def optimized_gaussian_blur(image: Image.Image, radius: int,
                                max_size: Tuple[int, int] = (800, 600)) -> Image.Image:
        """优化的高斯模糊"""
        with PerformanceMonitor(f"高斯模糊 (半径={radius})"):
            original_size = image.size
            if original_size[0] > max_size[0] or original_size[1] > max_size[1]:
                scale_x = max_size[0] / original_size[0]
                scale_y = max_size[1] / original_size[1]
                scale = min(scale_x, scale_y)
                small_size = (int(original_size[0] * scale), int(original_size[1] * scale))
                small_image = image.resize(small_size, Image.Resampling.LANCZOS)
                adjusted_radius = max(1, int(radius * scale))
                blurred_small = small_image.filter(ImageFilter.GaussianBlur(radius=adjusted_radius))
                blurred_image = blurred_small.resize(original_size, Image.Resampling.LANCZOS)
                return blurred_image
            else:
                return image.filter(ImageFilter.GaussianBlur(radius=radius))

    @staticmethod
    def optimized_color_analysis(image: Image.Image, num_colors: int = 6,
                                 max_size: Tuple[int, int] = (200, 200)) -> list:
        """优化的颜色分析"""
        with PerformanceMonitor("颜色分析"):
            analysis_image = image.copy()
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                analysis_image.thumbnail(max_size, Image.Resampling.LANCZOS)
            img_array = np.array(analysis_image)
            pixels = img_array.reshape(-1, 3)
            return OptimizedImageProcessor._simple_color_extraction(pixels, num_colors)

    @staticmethod
    def _simple_color_extraction(pixels: np.ndarray, num_colors: int) -> list:
        """简化的颜色提取方法"""
        quantized = (pixels // 32) * 32
        unique_colors, counts = np.unique(quantized, axis=0, return_counts=True)
        sorted_indices = np.argsort(counts)[::-1]
        top_colors = unique_colors[sorted_indices[:num_colors]]
        return [tuple(color) for color in top_colors]


class ProgressTracker:
    """进度跟踪器"""

    def __init__(self, total_steps: int, operation_name: str = "操作"):
        self.total_steps = total_steps
        self.current_step = 0
        self.operation_name = operation_name
        self.start_time = time.time()
        self.last_report_time = self.start_time
        self._lock = threading.Lock()

    def update(self, step_name: str = ""):
        """更新进度"""
        with self._lock:
            self.current_step += 1
            current_time = time.time()
            if (current_time - self.last_report_time > 5.0 or
                    self.current_step == self.total_steps):
                progress = (self.current_step / self.total_steps) * 100
                elapsed = current_time - self.start_time
                if self.current_step < self.total_steps:
                    eta = (elapsed / self.current_step) * (self.total_steps - self.current_step)
                    logger.info(f"{self.operation_name}进度: {progress:.1f}% "
                               f"({self.current_step}/{self.total_steps}) "
                               f"预计剩余: {eta:.1f}秒 - {step_name}")
                else:
                    logger.info(f"{self.operation_name}完成: 100% "
                               f"总耗时: {elapsed:.1f}秒")
                self.last_report_time = current_time

    def is_complete(self) -> bool:
        """检查是否完成"""
        return self.current_step >= self.total_steps


def memory_efficient_operation(func):
    """装饰器：内存高效操作"""

    def wrapper(*args, **kwargs):
        import gc
        gc.collect()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            gc.collect()

    return wrapper