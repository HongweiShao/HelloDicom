"""
压缩对话框组件
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTextEdit, QGroupBox, QRadioButton, QButtonGroup,
    QSlider, QSpinBox, QMessageBox, QListWidget, QFileDialog,
    QWidget, QCheckBox
)
from PyQt5.QtCore import Qt
from typing import Optional, List, Tuple


class CompressDialog(QDialog):
    """压缩对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.selected_level = None
        self.quality = 90
        self.rois = []
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('数据压缩')
        self.setModal(True)
        self.resize(650, 600)
        
        main_layout = QVBoxLayout(self)
        
        # 压缩级别选择
        level_group = QGroupBox("选择压缩级别")
        level_layout = QVBoxLayout(level_group)
        
        self.level_buttons = QButtonGroup(self)
        
        # 级别1 - 无压缩
        self.level1_radio = QRadioButton("级别1 - 无压缩")
        self.level1_radio.setToolTip("Explicit VR Little Endian")
        self.level_buttons.addButton(self.level1_radio, 1)
        level_layout.addWidget(self.level1_radio)
        
        level1_desc = QLabel("  无压缩，保持原始图像质量")
        level1_desc.setStyleSheet("color: gray; font-size: 10px;")
        level_layout.addWidget(level1_desc)
        
        # 级别2 - 标准压缩
        self.level2_radio = QRadioButton("级别2 - 标准压缩")
        self.level2_radio.setToolTip("RLE Lossless")
        self.level_buttons.addButton(self.level2_radio, 2)
        level_layout.addWidget(self.level2_radio)
        
        level2_desc = QLabel("  压缩比: 2-3x，质量: 100%，适用于诊断用途，兼容性好")
        level2_desc.setStyleSheet("color: gray; font-size: 10px;")
        level_layout.addWidget(level2_desc)
        
        # 级别3 - 无损压缩
        self.level3_radio = QRadioButton("级别3 - 无损压缩")
        self.level3_radio.setToolTip("JPEG 2000 Lossless")
        self.level_buttons.addButton(self.level3_radio, 3)
        level_layout.addWidget(self.level3_radio)
        
        level3_desc = QLabel("  压缩比: 4-6x，适用于数据存储")
        level3_desc.setStyleSheet("color: gray; font-size: 10px;")
        level_layout.addWidget(level3_desc)

        # 级别4 - 有损压缩
        self.level4_radio = QRadioButton("级别4 - 有损压缩")
        self.level4_radio.setToolTip("JPEG 2000 Lossy")
        self.level_buttons.addButton(self.level4_radio, 4)
        level_layout.addWidget(self.level4_radio)
        
        level4_desc = QLabel("  压缩比: 10-40x，适适用于数据存档/数据预览")
        level4_desc.setStyleSheet("color: gray; font-size: 10px;")
        level_layout.addWidget(level4_desc)
        
        # 级别选择变化
        self.level_buttons.buttonClicked.connect(self.on_level_changed)
        
        main_layout.addWidget(level_group)
        
        # 质量设置
        quality_group = QGroupBox("压缩质量设置")
        quality_layout = QVBoxLayout(quality_group)
        
        quality_slider_layout = QHBoxLayout()
        quality_slider_layout.addWidget(QLabel("质量:"))
        
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setMinimum(30)
        self.quality_slider.setMaximum(100)
        self.quality_slider.setValue(90)
        self.quality_slider.valueChanged.connect(self.on_quality_changed)
        quality_slider_layout.addWidget(self.quality_slider)
        
        self.quality_spin = QSpinBox()
        self.quality_spin.setMinimum(30)
        self.quality_spin.setMaximum(100)
        self.quality_spin.setValue(90)
        self.quality_spin.setSuffix("%")
        self.quality_spin.valueChanged.connect(self.on_quality_spin_changed)
        quality_slider_layout.addWidget(self.quality_spin)
        
        quality_layout.addLayout(quality_slider_layout)
        
        self.estimated_ratio_label = QLabel("预估压缩比: ~10x")
        quality_layout.addWidget(self.estimated_ratio_label)
        
        main_layout.addWidget(quality_group)
        
        # ROI设置(暂未启用)
        self.roi_group = QGroupBox("ROI设置 (暂未启用)")
        roi_layout = QVBoxLayout(self.roi_group)
        
        roi_hint = QLabel("提示: 在图像查看器中绘制ROI区域")
        roi_hint.setStyleSheet("color: blue; font-size: 10px;")
        roi_layout.addWidget(roi_hint)
        
        # ROI列表
        roi_list_layout = QHBoxLayout()
        
        self.roi_list = QListWidget()
        self.roi_list.setMaximumHeight(100)
        roi_list_layout.addWidget(self.roi_list)
        
        roi_buttons = QVBoxLayout()
        
        self.clear_roi_btn = QPushButton("清除所有")
        self.clear_roi_btn.clicked.connect(self.clear_rois)
        roi_buttons.addWidget(self.clear_roi_btn)
        
        self.load_roi_btn = QPushButton("加载ROI")
        self.load_roi_btn.clicked.connect(self.load_rois)
        roi_buttons.addWidget(self.load_roi_btn)
        
        self.save_roi_btn = QPushButton("保存ROI")
        self.save_roi_btn.clicked.connect(self.save_rois)
        roi_buttons.addWidget(self.save_roi_btn)
        
        roi_buttons.addStretch()
        
        roi_list_layout.addLayout(roi_buttons)
        roi_layout.addLayout(roi_list_layout)
        
        # ROI质量设置
        roi_quality_layout = QHBoxLayout()
        
        self.roi_quality_label = QLabel("ROI质量:")
        roi_quality_layout.addWidget(self.roi_quality_label)
        
        self.roi_quality_spin = QSpinBox()
        self.roi_quality_spin.setMinimum(80)
        self.roi_quality_spin.setMaximum(100)
        self.roi_quality_spin.setValue(95)
        self.roi_quality_spin.setSuffix("%")
        roi_quality_layout.addWidget(self.roi_quality_spin)
        
        roi_quality_layout.addWidget(QLabel("非ROI质量:"))
        
        self.non_roi_quality_spin = QSpinBox()
        self.non_roi_quality_spin.setMinimum(50)
        self.non_roi_quality_spin.setMaximum(90)
        self.non_roi_quality_spin.setValue(70)
        self.non_roi_quality_spin.setSuffix("%")
        roi_quality_layout.addWidget(self.non_roi_quality_spin)
        
        roi_layout.addLayout(roi_quality_layout)
        
        self.roi_group.setEnabled(False)
        main_layout.addWidget(self.roi_group)
        
        # 压缩说明
        info_group = QGroupBox("压缩说明")
        info_layout = QVBoxLayout(info_group)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(120)
        self.update_info_text(0)
        info_layout.addWidget(self.info_text)
        
        main_layout.addWidget(info_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        # 默认选择级别1
        self.level1_radio.setChecked(True)
        self.on_level_changed(self.level1_radio)
    
    def on_level_changed(self, button):
        """级别选择变化"""
        level_id = self.level_buttons.id(button)
        
        # 启用/禁用ROI设置
        self.roi_group.setEnabled(False)
        
        # 更新质量设置
        if level_id == 1 or level_id == 2 or level_id == 3:
            self.quality_slider.setValue(100)
            self.quality_slider.setEnabled(False)
            self.quality_spin.setEnabled(False)
        else:
            self.quality_slider.setEnabled(True)
            self.quality_spin.setEnabled(True)
            self.quality_slider.setValue(75)
        
        # 更新说明文本
        self.update_info_text(level_id)
        
        # 更新预估压缩比
        self.update_estimated_ratio()
    
    def on_quality_changed(self, value):
        """质量滑块改变"""
        self.quality_spin.blockSignals(True)
        self.quality_spin.setValue(value)
        self.quality_spin.blockSignals(False)
        self.quality = value
        self.update_estimated_ratio()
    
    def on_quality_spin_changed(self, value):
        """质量数值框改变"""
        self.quality_slider.blockSignals(True)
        self.quality_slider.setValue(value)
        self.quality_slider.blockSignals(False)
        self.quality = value
        self.update_estimated_ratio()
    
    def update_estimated_ratio(self):
        """更新预估压缩比"""
        level_id = self.level_buttons.checkedId()
        
        if level_id == 1:
            ratio = "2-4x"
        elif level_id == 2:
            # 根据质量估算
            quality_factor = self.quality / 100.0
            min_ratio = 8 + (15 - 8) * (1 - quality_factor)
            max_ratio = 15
            ratio = f"~{min_ratio:.0f}-{max_ratio:.0f}x"
        else:
            # ROI压缩
            ratio = "20-40x"
        
        self.estimated_ratio_label.setText(f"预估压缩比: {ratio}")
    
    def update_info_text(self, level_id: int):
        """更新说明文本"""
        info_texts = {
            0: "请选择压缩级别...",
            1: """级别1 - 无压缩

特性:
• 无压缩
• 压缩比: 1x
• 无任何质量损失
• 完全可逆

适用场景: 诊断用途，需要保持图像完整质量""",
            
            2: """级别2 - 标准压缩

特性:
• RLE无损压缩
• 压缩比: 2-3x
• 无质量损失
• 完全可逆

适用场景: 诊断用途，需要保持图像完整质量，兼容性好""",
            
            3: """级别3 - 无损压缩

特性:
• JPEG 2000无损压缩
• 压缩比: 4-8x
• 无质量损失
• 完全可逆

适用场景: 适用于日常数据存储""",

            4: """级别4 - 有损压缩

特性:
• JPEG 2000有损压缩
• 压缩比: 20-40x
• 质量可调，默认75%
• 不可逆

适用场景: 高压缩比,适用于数据存档/数据预览"""
        }
        
        self.info_text.setText(info_texts.get(level_id, ""))
    
    def set_rois(self, rois: List[Tuple[int, int, int, int]]):
        """设置ROI列表"""
        self.rois = rois
        self.roi_list.clear()
        
        for i, (x1, y1, x2, y2) in enumerate(rois):
            self.roi_list.addItem(f"ROI_{i+1}: ({x1},{y1}) - ({x2},{y2})")
    
    def clear_rois(self):
        """清除所有ROI"""
        self.rois.clear()
        self.roi_list.clear()
    
    def load_rois(self):
        """加载ROI文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '加载ROI文件',
            '',
            'JSON文件 (*.json);;所有文件 (*.*)'
        )
        
        if file_path:
            try:
                from core.roi_manager import ROIManager
                
                manager = ROIManager()
                manager.load_from_file(file_path)
                
                self.rois = manager.get_rois()
                self.roi_list.clear()
                
                for i, name in enumerate(manager.roi_names):
                    x1, y1, x2, y2 = self.rois[i]
                    self.roi_list.addItem(f"{name}: ({x1},{y1}) - ({x2},{y2})")
                
                QMessageBox.information(self, '成功', f'已加载 {len(self.rois)} 个ROI')
                
            except Exception as e:
                QMessageBox.critical(self, '错误', f'加载ROI失败: {e}')
    
    def save_rois(self):
        """保存ROI文件"""
        if not self.rois:
            QMessageBox.warning(self, '警告', '没有ROI可保存')
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            '保存ROI文件',
            '',
            'JSON文件 (*.json);;所有文件 (*.*)'
        )
        
        if file_path:
            try:
                from core.roi_manager import ROIManager
                
                manager = ROIManager()
                for i, roi in enumerate(self.rois):
                    manager.add_roi(*roi, f"ROI_{i+1}")
                
                manager.save_to_file(file_path)
                
                QMessageBox.information(self, '成功', f'已保存 {len(self.rois)} 个ROI')
                
            except Exception as e:
                QMessageBox.critical(self, '错误', f'保存ROI失败: {e}')
    
    def get_selected_level(self) -> str:
        """获取选择的压缩级别"""
        level_id = self.level_buttons.checkedId()
        level_map = {
            1: 'uncompressed',
            2: 'RLELossless',
            3: 'JPEG2000Lossless',
            4: 'JPEG2000Lossy'
        }
        return level_map.get(level_id, 'uncompressed')
    
    def get_quality(self) -> int:
        """获取压缩质量"""
        return self.quality
    
    def get_rois(self) -> List[Tuple[int, int, int, int]]:
        """获取ROI列表"""
        return self.rois if self.level_buttons.checkedId() == 3 else []
    
    def get_roi_quality(self) -> int:
        """获取ROI质量"""
        return self.roi_quality_spin.value()
    
    def get_non_roi_quality(self) -> int:
        """获取非ROI质量"""
        return self.non_roi_quality_spin.value()
