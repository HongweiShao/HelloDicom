"""
DICOM数据压缩模块
"""
import pydicom
from pydicom.dataset import Dataset
from typing import Optional, List, Tuple
from utils.config import config_manager


class Compressor:
    """DICOM压缩处理器"""
    
    def __init__(self):
        self.config = config_manager
    
    def compress(self, dataset: Dataset, 
                 level: str,
                 rois: Optional[List[Tuple[int, int, int, int]]] = None,
                 quality: int = 90) -> bool:
        """
        执行压缩
        
        Args:
            dataset: DICOM数据集
            level: 压缩级别 (level1_lossless, level2_standard, level3_roi)
            rois: ROI区域列表 [(x1, y1, x2, y2), ...]
            quality: 压缩质量 (0-100)
        
        Returns:
            是否成功
        """
        level_config = self.config.get_compression_preset(level)
        
        if not level_config:
            print(f"未找到压缩级别配置: {level}")
            return False
        
        try:
            if level == "uncompressed":
                dataset.decompress()
                return True
            elif level == "RLELossless":
                dataset.decompress()
                RLELossless = pydicom.uid.UID("1.2.840.10008.1.2.5")
                dataset.compress(RLELossless)
                return True
            elif level == "JPEG2000Lossless":
                dataset.decompress()
                JPEG2000Lossless = pydicom.uid.UID("1.2.840.10008.1.2.4.90")
                dataset.compress(JPEG2000Lossless, j2k_psnr=[quality])
                return True
            elif level == "JPEG2000Lossy":
                dataset.decompress()
                JPEG2000Lossy = pydicom.uid.UID("1.2.840.10008.1.2.4.91")
                dataset.compress(JPEG2000Lossy, j2k_psnr=[2*quality])
                return True
            else:
                print(f"未支持的压缩级别: {level}")
                return False
        except Exception as e:
            print(f"压缩失败: {e}")
            import traceback
            traceback.print_exc()
            return False
       
    def get_compression_levels(self) -> List[str]:
        """获取所有压缩级别"""
        return ['level1_lossless', 'level2_standard', 'level3_roi']
    
    def get_level_description(self, level: str) -> str:
        """获取压缩级别描述"""
        level_config = self.config.get_compression_preset(level)
        return level_config.get('description', '') if level_config else ''
 