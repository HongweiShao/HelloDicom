"""
图像处理模块
"""
import numpy as np
from typing import Optional, Tuple
import cv2
from PIL import Image


class ImageProcessor:
    """图像处理器"""
    
    def __init__(self):
        self.current_window_center = 0
        self.current_window_width = 0
        self.default_window_center = 0
        self.default_window_width = 0
    
    def apply_window_level(self, pixel_array: np.ndarray, 
                          window_center: Optional[float] = None,
                          window_width: Optional[float] = None) -> np.ndarray:
        """
        应用窗宽窗位
        
        Args:
            pixel_array: 原始像素数组
            window_center: 窗位
            window_width: 窗宽
        
        Returns:
            应用窗宽窗位后的图像
        """
        if window_center is None:
            window_center = self.current_window_center
        if window_width is None:
            window_width = self.current_window_width
        
        # 确保窗宽大于0
        window_width = max(window_width, 1)
        
        # 计算最小值和最大值
        min_value = window_center - window_width / 2
        max_value = window_center + window_width / 2
        
        # 裁剪到窗宽范围
        normalized = np.clip(pixel_array, min_value, max_value)
        
        # 归一化到0-255
        normalized = ((normalized - min_value) / window_width * 255).astype(np.uint8)
        
        return normalized
    
    def auto_window_level(self, pixel_array: np.ndarray) -> Tuple[float, float]:
        """
        自动计算窗宽窗位
        
        Args:
            pixel_array: 像素数组
        
        Returns:
            (窗位, 窗宽)
        """
        # 排除0值后计算
        non_zero_pixels = pixel_array[pixel_array > 0]
        
        if len(non_zero_pixels) == 0:
            return 127, 256
        
        # 计算窗位和窗宽
        min_val = np.percentile(non_zero_pixels, 1)
        max_val = np.percentile(non_zero_pixels, 99)
        
        window_center = (min_val + max_val) / 2
        window_width = max_val - min_val
        
        self.current_window_center = window_center
        self.current_window_width = window_width
        self.default_window_center = window_center
        self.default_window_width = window_width
        
        return window_center, window_width
    
    def reset_window_level(self):
        """重置窗宽窗位到默认值"""
        self.current_window_center = self.default_window_center
        self.current_window_width = self.default_window_width
    
    def resize_image(self, image: np.ndarray, 
                    scale: Optional[float] = None,
                    size: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """
        调整图像大小
        
        Args:
            image: 图像数组
            scale: 缩放比例
            size: 目标尺寸 (width, height)
        
        Returns:
            调整后的图像
        """
        if scale is not None:
            new_width = int(image.shape[1] * scale)
            new_height = int(image.shape[0] * scale)
            size = (new_width, new_height)
        
        if size is None:
            return image
        
        return cv2.resize(image, size, interpolation=cv2.INTER_LINEAR)
    
    def flip_image(self, image: np.ndarray, 
                   horizontal: bool = False, 
                   vertical: bool = False) -> np.ndarray:
        """
        翻转图像
        
        Args:
            image: 图像数组
            horizontal: 水平翻转
            vertical: 垂直翻转
        
        Returns:
            翻转后的图像
        """
        if horizontal and vertical:
            return cv2.flip(image, -1)
        elif horizontal:
            return cv2.flip(image, 1)
        elif vertical:
            return cv2.flip(image, 0)
        return image
    
    def rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """
        旋转图像
        
        Args:
            image: 图像数组
            angle: 旋转角度(度)
        
        Returns:
            旋转后的图像
        """
        rows, cols = image.shape[:2]
        matrix = cv2.getRotationMatrix2D((cols/2, rows/2), angle, 1)
        return cv2.warpAffine(image, matrix, (cols, rows))
    
    def convert_to_pixmap(self, image: np.ndarray) -> np.ndarray:
        """
        转换为Qt可显示的格式
        
        Args:
            image: 灰度图像数组
        
        Returns:
            RGB图像数组
        """
        if len(image.shape) == 2:
            # 灰度转RGB
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        return image
    
    def invert_image(self, image: np.ndarray) -> np.ndarray:
        """
        反色
        
        Args:
            image: 图像数组
        
        Returns:
            反色后的图像
        """
        return 255 - image
    
    def save_image(self, image: np.ndarray, 
                   file_path: str, 
                   format: str = 'PNG') -> bool:
        """
        保存图像到文件
        
        Args:
            image: 图像数组
            file_path: 文件路径
            format: 图像格式 (PNG, JPEG, BMP)
        
        Returns:
            是否保存成功
        """
        try:
            pil_image = Image.fromarray(image)
            pil_image.save(file_path, format=format)
            return True
        except Exception as e:
            print(f"保存图像失败: {e}")
            return False
