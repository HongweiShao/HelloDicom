"""
配置管理模块
"""
import json
import os
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent.parent / "config"
        self.anonymize_rules = self._load_anonymize_rules()
        self.compression_presets = self._load_compression_presets()
    
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """加载JSON配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件未找到: {file_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            return {}
    
    def _load_anonymize_rules(self) -> Dict[str, Any]:
        """加载脱敏规则"""
        return self._load_json(self.config_dir / "anonymize_rules.json")
    
    def _load_compression_presets(self) -> Dict[str, Any]:
        """加载压缩预设"""
        return self._load_json(self.config_dir / "compression_presets.json")
    
    def get_anonymize_level(self, level_name: str) -> Dict[str, Any]:
        """获取指定脱敏级别的配置"""
        return self.anonymize_rules.get(level_name, {})
    
    def get_compression_preset(self, preset_name: str) -> Dict[str, Any]:
        """获取指定压缩预设的配置"""
        return self.compression_presets.get(preset_name, {})
    
    def reload(self):
        """重新加载配置"""
        self.anonymize_rules = self._load_anonymize_rules()
        self.compression_presets = self._load_compression_presets()


# 全局配置管理器实例
config_manager = ConfigManager()
