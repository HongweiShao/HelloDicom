"""
ROI管理模块
"""
from typing import List, Tuple, Optional
import json
from pathlib import Path


class ROIManager:
    """ROI区域管理器"""
    
    def __init__(self):
        self.rois: List[Tuple[int, int, int, int]] = []
        self.roi_names: List[str] = []
    
    def add_roi(self, x1: int, y1: int, x2: int, y2: int, name: str = ""):
        """
        添加ROI区域
        
        Args:
            x1, y1: 左上角坐标
            x2, y2: 右下角坐标
            name: ROI名称
        """
        # 确保坐标顺序正确
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        self.rois.append((x1, y1, x2, y2))
        self.roi_names.append(name if name else f"ROI_{len(self.rois)}")
    
    def remove_roi(self, index: int):
        """删除指定索引的ROI"""
        if 0 <= index < len(self.rois):
            self.rois.pop(index)
            self.roi_names.pop(index)
    
    def clear_rois(self):
        """清除所有ROI"""
        self.rois.clear()
        self.roi_names.clear()
    
    def get_rois(self) -> List[Tuple[int, int, int, int]]:
        """获取所有ROI区域"""
        return self.rois.copy()
    
    def get_roi_count(self) -> int:
        """获取ROI数量"""
        return len(self.rois)
    
    def update_roi(self, index: int, x1: int, y1: int, x2: int, y2: int):
        """更新指定索引的ROI"""
        if 0 <= index < len(self.rois):
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            self.rois[index] = (x1, y1, x2, y2)
    
    def rename_roi(self, index: int, name: str):
        """重命名ROI"""
        if 0 <= index < len(self.roi_names):
            self.roi_names[index] = name
    
    def get_roi_by_name(self, name: str) -> Optional[Tuple[int, int, int, int]]:
        """根据名称获取ROI"""
        try:
            index = self.roi_names.index(name)
            return self.rois[index]
        except ValueError:
            return None
    
    def save_to_file(self, file_path: str):
        """
        保存ROI到文件
        
        Args:
            file_path: 文件路径
        """
        data = {
            'rois': [
                {
                    'name': name,
                    'coordinates': roi
                }
                for name, roi in zip(self.roi_names, self.rois)
            ]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, file_path: str):
        """
        从文件加载ROI
        
        Args:
            file_path: 文件路径
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.clear_rois()
            
            for roi_data in data.get('rois', []):
                name = roi_data.get('name', '')
                coords = roi_data.get('coordinates', (0, 0, 0, 0))
                self.rois.append(tuple(coords))
                self.roi_names.append(name)
                
        except Exception as e:
            print(f"加载ROI失败: {e}")
    
    def calculate_total_roi_area(self) -> int:
        """计算所有ROI的总面积"""
        total_area = 0
        for x1, y1, x2, y2 in self.rois:
            area = (x2 - x1) * (y2 - y1)
            total_area += area
        return total_area
    
    def get_roi_info(self) -> List[dict]:
        """获取所有ROI的详细信息"""
        info = []
        for i, (roi, name) in enumerate(zip(self.rois, self.roi_names)):
            x1, y1, x2, y2 = roi
            info.append({
                'index': i,
                'name': name,
                'coordinates': roi,
                'width': x2 - x1,
                'height': y2 - y1,
                'area': (x2 - x1) * (y2 - y1)
            })
        return info
