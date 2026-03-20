"""
工具函数模块
"""
from datetime import datetime, timedelta
from typing import Optional
import re


def shift_date(date_str: str, shift_days: int) -> str:
    """
    日期偏移处理
    
    Args:
        date_str: DICOM日期格式字符串 (YYYYMMDD)
        shift_days: 偏移天数
    
    Returns:
        偏移后的日期字符串
    """
    try:
        if not date_str or len(date_str) != 8:
            return date_str
        
        date_obj = datetime.strptime(date_str, "%Y%m%d")
        shifted_date = date_obj + timedelta(days=shift_days)
        return shifted_date.strftime("%Y%m%d")
    except ValueError:
        return date_str


def generate_uid() -> str:
    """
    生成新的DICOM UID
    
    Returns:
        新的UID字符串
    """
    import uuid
    import time
    
    # 使用UUID和时间戳生成UID
    # 这里使用一个简化的方法,实际应用中应使用官方注册的UID根
    root = "1.2.826.0.1.3680043.8.498."  # 示例根,实际应替换
    unique_suffix = str(uuid.uuid4().int)
    return f"{root}{unique_suffix}"


def format_tag(tag_str: str) -> str:
    """
    格式化DICOM标签显示
    
    Args:
        tag_str: 标签字符串 (如: 0x00100010)
    
    Returns:
        格式化后的标签 (如: (0010,0010))
    """
    # 移除0x前缀
    tag_hex = tag_str.replace("0x", "")
    
    if len(tag_hex) == 8:
        group = tag_hex[:4]
        element = tag_hex[4:]
        return f"({group.upper()},{element.upper()})"
    
    return tag_str


def validate_dicom_file(file_path: str) -> bool:
    """
    验证DICOM文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        是否为有效的DICOM文件
    """
    import os
    
    if not os.path.exists(file_path):
        return False
    
    # 检查文件扩展名
    if not file_path.lower().endswith('.dcm'):
        return False
    
    # 检查文件大小
    if os.path.getsize(file_path) < 132:
        return False
    
    return True


def bytes_to_readable(size_bytes: int) -> str:
    """
    将字节数转换为可读格式
    
    Args:
        size_bytes: 字节数
    
    Returns:
        可读的大小字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    """
    计算压缩比
    
    Args:
        original_size: 原始大小
        compressed_size: 压缩后大小
    
    Returns:
        压缩比
    """
    if compressed_size == 0:
        return 0.0
    return original_size / compressed_size
