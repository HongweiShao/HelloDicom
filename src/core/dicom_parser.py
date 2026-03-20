"""
DICOM文件解析模块
"""
import pydicom
from pydicom.dataset import Dataset
from typing import Optional, Dict, Any, List, Tuple
import numpy as np
from pathlib import Path


class DicomParser:
    """DICOM文件解析器"""
    
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path
        self.dataset: Optional[Dataset] = None
        self.metadata: Dict[str, Any] = {}
        
        if file_path:
            self.load(file_path)
    
    def load(self, file_path: str) -> bool:
        """
        加载DICOM文件
        
        Args:
            file_path: DICOM文件路径
        
        Returns:
            是否加载成功
        """
        try:
            self.file_path = file_path
            self.dataset = pydicom.dcmread(file_path)
            self._extract_metadata()
            return True
        except Exception as e:
            print(f"加载DICOM文件失败: {e}")
            return False
    
    def _extract_metadata(self):
        """提取元数据"""
        if not self.dataset:
            return
        
        self.metadata = {
            'PatientName': str(getattr(self.dataset, 'PatientName', 'Unknown')),
            'PatientID': str(getattr(self.dataset, 'PatientID', 'Unknown')),
            'StudyDate': str(getattr(self.dataset, 'StudyDate', '')),
            'Modality': str(getattr(self.dataset, 'Modality', 'Unknown')),
            'StudyDescription': str(getattr(self.dataset, 'StudyDescription', '')),
            'SeriesDescription': str(getattr(self.dataset, 'SeriesDescription', '')),
            'Rows': getattr(self.dataset, 'Rows', 0),
            'Columns': getattr(self.dataset, 'Columns', 0),
            'BitsStored': getattr(self.dataset, 'BitsStored', 8),
            'PixelRepresentation': getattr(self.dataset, 'PixelRepresentation', 0),
        }
    
    def get_pixel_array(self) -> Optional[np.ndarray]:
        """
        获取图像像素数据
        
        Returns:
            像素数组
        """
        if not self.dataset:
            return None
        
        try:
            return self.dataset.pixel_array
        except Exception as e:
            print(f"获取像素数据失败: {e}")
            return None
    
    def get_all_tags(self) -> List[Tuple[str, str, str, str]]:
        """
        获取所有标签信息
        
        Returns:
            标签列表 [(标签ID, VR, 名称, 值), ...]
        """
        if not self.dataset:
            return []
        
        tags = []
        for elem in self.dataset.iterall():
            tag_id = str(elem.tag)
            vr = elem.VR
            name = elem.name
            value = str(elem.value) if not elem.is_undefined_length else "undefined"
            tags.append((tag_id, vr, name, value))
        
        return tags
    
    def get_tag_value(self, tag: str) -> Optional[Any]:
        """
        获取指定标签的值
        
        Args:
            tag: 标签ID (如: 0x00100010 或 PatientName)
        
        Returns:
            标签值
        """
        if not self.dataset:
            return None
        
        try:
            # 尝试通过标签ID访问
            if tag.startswith('0x'):
                return self.dataset[tag].value
            # 尝试通过属性名访问
            else:
                return getattr(self.dataset, tag, None)
        except (KeyError, AttributeError):
            return None
    
    def set_tag_value(self, tag: str, value: Any) -> bool:
        """
        设置标签值
        
        Args:
            tag: 标签ID或名称
            value: 新值
        
        Returns:
            是否设置成功
        """
        if not self.dataset:
            return False
        
        try:
            if tag.startswith('0x'):
                self.dataset[tag].value = value
            else:
                setattr(self.dataset, tag, value)
            return True
        except Exception as e:
            print(f"设置标签值失败: {e}")
            return False
    
    def remove_tag(self, tag: str) -> bool:
        """
        删除标签
        
        Args:
            tag: 标签ID或名称
        
        Returns:
            是否删除成功
        """
        if not self.dataset:
            return False
        
        try:
            if tag.startswith('0x'):
                del self.dataset[tag]
            else:
                delattr(self.dataset, tag)
            return True
        except Exception as e:
            print(f"删除标签失败: {e}")
            return False
    
    def save(self, output_path: str) -> bool:
        """
        保存DICOM文件
        
        Args:
            output_path: 输出文件路径
        
        Returns:
            是否保存成功
        """
        if not self.dataset:
            return False
        
        try:
            self.dataset.save_as(output_path)
            return True
        except Exception as e:
            print(f"保存DICOM文件失败: {e}")
            return False
    
    def get_transfer_syntax(self) -> str:
        """获取传输语法"""
        if not self.dataset:
            return ""
        
        try:
            return str(self.dataset.file_meta.TransferSyntaxUID)
        except AttributeError:
            return "Implicit VR Little Endian"
    
    def is_compressed(self) -> bool:
        """判断是否为压缩格式"""
        transfer_syntax = self.get_transfer_syntax()
        # 常见压缩格式的UID
        compressed_uids = [
            '1.2.840.10008.1.2.4.50',  # JPEG Baseline
            '1.2.840.10008.1.2.4.51',  # JPEG Extended
            '1.2.840.10008.1.2.4.57',  # JPEG Lossless
            '1.2.840.10008.1.2.4.70',  # JPEG Lossless SV1
            '1.2.840.10008.1.2.4.80',  # JPEG-LS Lossless
            '1.2.840.10008.1.2.4.81',  # JPEG-LS Lossy
            '1.2.840.10008.1.2.4.90',  # JPEG 2000 Lossless
            '1.2.840.10008.1.2.4.91',  # JPEG 2000
        ]
        return transfer_syntax in compressed_uids
    
    def get_file_size(self) -> int:
        """获取文件大小"""
        if self.file_path and Path(self.file_path).exists():
            return Path(self.file_path).stat().st_size
        return 0
