"""
DICOM敏感信息脱敏模块
"""
import pydicom
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from utils.helpers import generate_uid, shift_date
from utils.config import config_manager


class Anonymizer:
    """DICOM脱敏处理器"""
    
    def __init__(self):
        self.config = config_manager
    
    def anonymize(self, dataset: pydicom.Dataset, 
                  level: str, 
                  custom_key: Optional[str] = None) -> bool:
        """
        执行脱敏
        
        Args:
            dataset: DICOM数据集
            level: 脱敏级别 (level1_basic, level2_standard, level3_strict, level4_encrypted)
            custom_key: 自定义公钥(仅level4使用)
        
        Returns:
            是否成功
        """
        level_config = self.config.get_anonymize_level(level)
        
        if not level_config:
            print(f"未找到脱敏级别配置: {level}")
            return False
        
        try:
            if level == "level4_encrypted":
                return self._anonymize_encrypted(dataset, level_config, custom_key)
            else:
                return self._anonymize_standard(dataset, level_config)
        except Exception as e:
            print(f"脱敏失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _anonymize_standard(self, dataset: pydicom.Dataset, 
                           level_config: Dict) -> bool:
        """标准脱敏处理"""
        fields = level_config.get('fields', [])
        
        for field in fields:
            tag = field['tag']
            action = field['action']
            value = field.get('value', '')
            
            try:
                if action == 'replace':
                    self._replace_tag(dataset, tag, value)
                elif action == 'remove':
                    self._remove_tag(dataset, tag)
                elif action == 'shift_date':
                    shift_days = field.get('shift_days', 0)
                    self._shift_date_tag(dataset, tag, shift_days)
            except Exception as e:
                print(f"处理标签 {tag} 失败: {e}")
        
        # 处理特殊动作
        special_actions = level_config.get('special_actions', [])
        for action in special_actions:
            if action == 'shift_all_dates':
                self._shift_all_dates(dataset, -365)
            elif action == 'regenerate_all_uids':
                self._regenerate_all_uids(dataset)
            elif action == 'remove_physician_names':
                self._remove_physician_names(dataset)
            elif action == 'remove_device_serials':
                self._remove_device_serials(dataset)
        
        return True
    
    def _anonymize_encrypted(self, dataset: pydicom.Dataset,
                            level_config: Dict,
                            custom_key: Optional[str]) -> bool:
        """加密脱敏处理"""
        from core.encryptor import Encryptor
        
        encryptor = Encryptor()
        
        # 获取基础脱敏配置
        base_level = level_config.get('base_level', 'level2_standard')
        base_config = self.config.get_anonymize_level(base_level)
        
        # 执行基础脱敏
        if base_config:
            self._anonymize_standard(dataset, base_config)
        
        # 加密敏感标签
        encryption_config = level_config.get('encryption', {})
        encrypt_fields = encryption_config.get('encrypt_fields', [])
        
        if custom_key:
            encryptor.load_public_key(custom_key)
        else:
            # 生成新密钥对
            encryptor.generate_key_pair()
        
        for tag in encrypt_fields:
            try:
                value = self._get_tag_value(dataset, tag)
                if value:
                    encrypted_value = encryptor.encrypt(str(value))
                    self._replace_tag(dataset, tag, encrypted_value)
            except Exception as e:
                print(f"加密标签 {tag} 失败: {e}")
        
        return True
    
    def _replace_tag(self, dataset: pydicom.Dataset, tag: str, value: str):
        """替换标签值"""
        try:
            if tag.startswith('0x'):
                tag_obj = pydicom.tag.Tag(tag)
                if tag_obj in dataset:
                    dataset[tag_obj].value = value
                else:
                    # 如果标签不存在,则添加
                    VR = 'LO'  # 默认VR
                    dataset.add_new(tag_obj, VR, value)
            else:
                setattr(dataset, tag, value)
        except Exception as e:
            raise Exception(f"替换标签 {tag} 失败: {e}")
    
    def _remove_tag(self, dataset: pydicom.Dataset, tag: str):
        """删除标签"""
        try:
            if tag.startswith('0x'):
                tag_obj = pydicom.tag.Tag(tag)
                if tag_obj in dataset:
                    del dataset[tag_obj]
            else:
                if hasattr(dataset, tag):
                    delattr(dataset, tag)
        except Exception as e:
            raise Exception(f"删除标签 {tag} 失败: {e}")
    
    def _shift_date_tag(self, dataset: pydicom.Dataset, tag: str, shift_days: int):
        """偏移日期标签"""
        try:
            value = self._get_tag_value(dataset, tag)
            if value:
                shifted = shift_date(str(value), shift_days)
                self._replace_tag(dataset, tag, shifted)
        except Exception as e:
            raise Exception(f"偏移日期标签 {tag} 失败: {e}")
    
    def _get_tag_value(self, dataset: pydicom.Dataset, tag: str) -> Optional[Any]:
        """获取标签值"""
        try:
            if tag.startswith('0x'):
                tag_obj = pydicom.tag.Tag(tag)
                if tag_obj in dataset:
                    return dataset[tag_obj].value
            else:
                return getattr(dataset, tag, None)
        except:
            return None
    
    def _shift_all_dates(self, dataset: pydicom.Dataset, shift_days: int):
        """偏移所有日期标签"""
        date_tags = [
            'StudyDate', 'SeriesDate', 'AcquisitionDate', 
            'ContentDate', 'PatientBirthDate'
        ]
        
        for tag in date_tags:
            try:
                if hasattr(dataset, tag):
                    value = getattr(dataset, tag)
                    if value:
                        shifted = shift_date(str(value), shift_days)
                        setattr(dataset, tag, shifted)
            except:
                pass
    
    def _regenerate_all_uids(self, dataset: pydicom.Dataset):
        """重新生成所有UID"""
        uid_tags = [
            'StudyInstanceUID', 'SeriesInstanceUID', 'SOPInstanceUID',
            'SOPClassUID', 'FrameOfReferenceUID'
        ]
        
        uid_map = {}
        
        for tag in uid_tags:
            try:
                if hasattr(dataset, tag):
                    old_uid = getattr(dataset, tag)
                    if old_uid not in uid_map:
                        uid_map[old_uid] = generate_uid()
                    setattr(dataset, tag, uid_map[old_uid])
            except:
                pass
    
    def _remove_physician_names(self, dataset: pydicom.Dataset):
        """删除医生姓名"""
        physician_tags = [
            'ReferringPhysicianName', 'PerformingPhysicianName',
            'NameOfPhysiciansReadingStudy', 'PhysiciansOfRecord'
        ]
        
        for tag in physician_tags:
            try:
                if hasattr(dataset, tag):
                    setattr(dataset, tag, 'ANONYMOUS')
            except:
                pass
    
    def _remove_device_serials(self, dataset: pydicom.Dataset):
        """删除设备序列号"""
        device_tags = [
            'DeviceSerialNumber', 'StationName'
        ]
        
        for tag in device_tags:
            try:
                if hasattr(dataset, tag):
                    setattr(dataset, tag, 'ANONYMOUS')
            except:
                pass
    
    def get_anonymize_levels(self) -> List[str]:
        """获取所有脱敏级别"""
        return ['level1_basic', 'level2_standard', 'level3_strict', 'level4_encrypted']
    
    def get_level_description(self, level: str) -> str:
        """获取脱敏级别描述"""
        level_config = self.config.get_anonymize_level(level)
        return level_config.get('description', '') if level_config else ''
