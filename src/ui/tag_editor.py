"""
标签编辑器组件
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QPushButton, QLabel, QMessageBox, QComboBox,
    QGroupBox, QTextEdit, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from typing import List, Tuple


class TagEditor(QWidget):
    """DICOM标签编辑器"""
    
    tag_modified = pyqtSignal(str, str, str)  # tag_id, old_value, new_value
    
    def __init__(self):
        super().__init__()
        
        self.dataset = None
        self.tags_data = []
        self.filtered_tags = []
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        
        # 搜索和过滤区域
        search_group = QGroupBox("搜索和过滤")
        search_layout = QHBoxLayout(search_group)
        
        search_layout.addWidget(QLabel("搜索:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入标签ID、名称或值...")
        self.search_edit.textChanged.connect(self.filter_tags)
        search_layout.addWidget(self.search_edit)
        
        search_layout.addWidget(QLabel("标签组:"))
        self.group_combo = QComboBox()
        self.group_combo.addItem("全部", "all")
        self.group_combo.addItem("患者信息", "patient")
        self.group_combo.addItem("检查信息", "study")
        self.group_combo.addItem("图像信息", "image")
        self.group_combo.currentIndexChanged.connect(self.filter_by_group)
        search_layout.addWidget(self.group_combo)
        
        main_layout.addWidget(search_group)
        
        # 标签树
        self.tag_tree = QTreeWidget()
        self.tag_tree.setHeaderLabels(['标签ID', 'VR', '名称', '值'])
        self.tag_tree.setColumnWidth(0, 120)
        self.tag_tree.setColumnWidth(1, 50)
        self.tag_tree.setColumnWidth(2, 200)
        self.tag_tree.setColumnWidth(3, 300)
        self.tag_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tag_tree.itemSelectionChanged.connect(self.on_selection_changed)
        main_layout.addWidget(self.tag_tree)
        
        # 编辑区域
        edit_group = QGroupBox("编辑标签")
        edit_layout = QVBoxLayout(edit_group)
        
        # 当前标签信息
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel("当前标签:"))
        self.current_tag_label = QLabel("未选择")
        self.current_tag_label.setStyleSheet("font-weight: bold; color: blue;")
        info_layout.addWidget(self.current_tag_label)
        info_layout.addStretch()
        edit_layout.addLayout(info_layout)
        
        # 新值输入
        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("新值:"))
        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText("输入新值...")
        value_layout.addWidget(self.value_edit)
        
        self.apply_btn = QPushButton("应用")
        self.apply_btn.clicked.connect(self.apply_value)
        self.apply_btn.setEnabled(False)
        value_layout.addWidget(self.apply_btn)
        
        edit_layout.addLayout(value_layout)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.delete_btn = QPushButton("删除标签")
        self.delete_btn.clicked.connect(self.delete_tag)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)
        
        self.export_btn = QPushButton("导出标签")
        self.export_btn.clicked.connect(self.export_tags)
        button_layout.addWidget(self.export_btn)
        
        button_layout.addStretch()
        
        edit_layout.addLayout(button_layout)
        
        main_layout.addWidget(edit_group)
    
    def load_tags(self, tags: List[Tuple[str, str, str, str]]):
        """
        加载标签数据
        
        Args:
            tags: 标签列表 [(标签ID, VR, 名称, 值), ...]
        """
        self.tags_data = tags
        self.display_tags(tags)
    
    def display_tags(self, tags: List[Tuple[str, str, str, str]]):
        """显示标签"""
        self.tag_tree.clear()
        
        for tag_id, vr, name, value in tags:
            item = QTreeWidgetItem([tag_id, vr, name, value])
            
            # 高亮敏感标签
            if self._is_sensitive_tag(tag_id):
                item.setBackground(3, QColor(255, 230, 230))
            
            self.tag_tree.addTopLevelItem(item)
    
    def filter_tags(self):
        """过滤标签"""
        search_text = self.search_edit.text().lower()
        
        if not search_text:
            self.filtered_tags = self.tags_data
        else:
            self.filtered_tags = [
                tag for tag in self.tags_data
                if search_text in tag[0].lower() or
                   search_text in tag[2].lower() or
                   search_text in tag[3].lower()
            ]
        
        self.display_tags(self.filtered_tags)
    
    def filter_by_group(self):
        """按组过滤"""
        group = self.group_combo.currentData()
        
        if group == "all":
            self.display_tags(self.tags_data)
        elif group == "patient":
            patient_tags = [tag for tag in self.tags_data if tag[0].startswith('(0010')]
            self.display_tags(patient_tags)
        elif group == "study":
            study_tags = [tag for tag in self.tags_data if tag[0].startswith('(0008') or tag[0].startswith('(0020')]
            self.display_tags(study_tags)
        elif group == "image":
            image_tags = [tag for tag in self.tags_data if tag[0].startswith('(0028') or tag[0].startswith('(7FE0')]
            self.display_tags(image_tags)
    
    def _is_sensitive_tag(self, tag_id: str) -> bool:
        """判断是否为敏感标签"""
        sensitive_tags = [
            '(0010,0010)',  # PatientName
            '(0010,0020)',  # PatientID
            '(0010,0030)',  # PatientBirthDate
            '(0010,1040)',  # PatientAddress
            '(0010,2154)',  # PatientTelephoneNumbers
        ]
        return tag_id in sensitive_tags
    
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """双击编辑"""
        if column == 3:  # 值列
            current_value = item.text(3)
            self.value_edit.setText(current_value)
            self.value_edit.setFocus()
    
    def on_selection_changed(self):
        """选择改变"""
        selected_items = self.tag_tree.selectedItems()
        
        if selected_items:
            item = selected_items[0]
            tag_id = item.text(0)
            vr = item.text(1)
            name = item.text(2)
            value = item.text(3)
            
            self.current_tag_label.setText(f"{tag_id} - {name} ({vr})")
            self.value_edit.setText(value)
            self.apply_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
        else:
            self.current_tag_label.setText("未选择")
            self.value_edit.clear()
            self.apply_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
    
    def apply_value(self):
        """应用新值"""
        selected_items = self.tag_tree.selectedItems()
        
        if not selected_items:
            return
        
        item = selected_items[0]
        tag_id = item.text(0)
        old_value = item.text(3)
        new_value = self.value_edit.text()
        
        if old_value != new_value:
            item.setText(3, new_value)
            self.tag_modified.emit(tag_id, old_value, new_value)
            QMessageBox.information(self, '成功', f'标签 {tag_id} 已更新')
    
    def delete_tag(self):
        """删除标签"""
        selected_items = self.tag_tree.selectedItems()
        
        if not selected_items:
            return
        
        item = selected_items[0]
        tag_id = item.text(0)
        name = item.text(2)
        
        reply = QMessageBox.question(
            self, '确认删除',
            f'确定要删除标签 {tag_id} ({name}) 吗?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            index = self.tag_tree.indexOfTopLevelItem(item)
            self.tag_tree.takeTopLevelItem(index)
            QMessageBox.information(self, '成功', f'标签 {tag_id} 已删除')
    
    def export_tags(self):
        """导出标签"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            '导出标签',
            '',
            '文本文件 (*.txt);;CSV文件 (*.csv)'
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('标签ID\tVR\t名称\t值\n')
                    for i in range(self.tag_tree.topLevelItemCount()):
                        item = self.tag_tree.topLevelItem(i)
                        f.write(f'{item.text(0)}\t{item.text(1)}\t{item.text(2)}\t{item.text(3)}\n')
                
                QMessageBox.information(self, '成功', f'标签已导出到: {file_path}')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'导出失败: {e}')
    
    def get_modified_tags(self) -> List[Tuple[str, str]]:
        """
        获取修改后的所有标签
        
        Returns:
            [(标签ID, 新值), ...]
        """
        tags = []
        for i in range(self.tag_tree.topLevelItemCount()):
            item = self.tag_tree.topLevelItem(i)
            tags.append((item.text(0), item.text(3)))
        return tags
