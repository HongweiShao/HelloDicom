"""
脱敏对话框组件
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTextEdit, QGroupBox, QRadioButton, QButtonGroup,
    QFileDialog, QMessageBox, QWidget
)
from PyQt5.QtCore import Qt
from typing import Optional


class AnonymizeDialog(QDialog):
    """脱敏对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.selected_level = None
        self.custom_key_path = None
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('敏感信息脱敏')
        self.setModal(True)
        self.resize(600, 500)
        
        main_layout = QVBoxLayout(self)
        
        # 脱敏级别选择
        level_group = QGroupBox("选择脱敏级别")
        level_layout = QVBoxLayout(level_group)
        
        self.level_buttons = QButtonGroup(self)
        
        # 级别1 - 基础脱敏
        self.level1_radio = QRadioButton("级别1 - 基础脱敏")
        self.level1_radio.setToolTip("患者姓名、ID、出生日期")
        self.level_buttons.addButton(self.level1_radio, 1)
        level_layout.addWidget(self.level1_radio)
        
        level1_desc = QLabel("  符合基本隐私要求")
        level1_desc.setStyleSheet("color: gray; font-size: 10px;")
        level_layout.addWidget(level1_desc)
        
        # 级别2 - 标准脱敏
        self.level2_radio = QRadioButton("级别2 - 标准脱敏 (HIPAA)")
        self.level2_radio.setToolTip("基础字段 + 地址、电话、机构、科室、检查日期等")
        self.level_buttons.addButton(self.level2_radio, 2)
        level_layout.addWidget(self.level2_radio)
        
        level2_desc = QLabel("  符合HIPAA要求")
        level2_desc.setStyleSheet("color: gray; font-size: 10px;")
        level_layout.addWidget(level2_desc)
        
        # 级别3 - 严格脱敏
        self.level3_radio = QRadioButton("级别3 - 严格脱敏")
        self.level3_radio.setToolTip("完全匿名化，所有UID重新生成")
        self.level_buttons.addButton(self.level3_radio, 3)
        level_layout.addWidget(self.level3_radio)
        
        level3_desc = QLabel("  完全匿名化，所有UID重新生成")
        level3_desc.setStyleSheet("color: gray; font-size: 10px;")
        level_layout.addWidget(level3_desc)
        
        # 级别4 - 加密脱敏
        self.level4_radio = QRadioButton("级别4 - 加密脱敏")
        self.level4_radio.setToolTip("RSA加密，可逆保护")
        self.level_buttons.addButton(self.level4_radio, 4)
        level_layout.addWidget(self.level4_radio)
        
        level4_desc = QLabel("  RSA非对称加密，可逆保护，支持自定义公钥")
        level4_desc.setStyleSheet("color: gray; font-size: 10px;")
        level_layout.addWidget(level4_desc)
        
        # 公钥选择(仅级别4)
        self.key_group = QGroupBox("公钥选择 (仅级别4)")
        key_layout = QHBoxLayout(self.key_group)
        
        self.key_path_label = QLabel("未选择")
        key_layout.addWidget(self.key_path_label)
        
        self.browse_key_btn = QPushButton("浏览...")
        self.browse_key_btn.clicked.connect(self.browse_key)
        key_layout.addWidget(self.browse_key_btn)
        
        self.generate_key_btn = QPushButton("生成新密钥对")
        self.generate_key_btn.clicked.connect(self.generate_key)
        key_layout.addWidget(self.generate_key_btn)
        
        self.key_group.setEnabled(False)
        level_layout.addWidget(self.key_group)
        
        # 级别选择变化
        self.level_buttons.buttonClicked.connect(self.on_level_changed)
        
        main_layout.addWidget(level_group)
        
        # 脱敏说明
        info_group = QGroupBox("脱敏说明")
        info_layout = QVBoxLayout(info_group)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        self.update_info_text(0)
        info_layout.addWidget(self.info_text)
        
        main_layout.addWidget(info_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.preview_btn = QPushButton("预览")
        self.preview_btn.clicked.connect(self.preview_anonymization)
        button_layout.addWidget(self.preview_btn)
        
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
        
        # 启用/禁用公钥选择
        self.key_group.setEnabled(level_id == 4)
        
        # 更新说明文本
        self.update_info_text(level_id)
    
    def update_info_text(self, level_id: int):
        """更新说明文本"""
        info_texts = {
            0: "请选择脱敏级别...",
            1: """级别1 - 基础脱敏

将处理以下字段:
• 患者姓名 (PatientName) → 替换为 ANONYMOUS
• 患者ID (PatientID) → 替换为 ANONYMOUS_ID
• 患者出生日期 (PatientBirthDate) → 删除

适用场景: 基本隐私保护需求""",
            
            2: """级别2 - 标准脱敏 (HIPAA)

将处理以下字段:
• 级别1的所有字段
• 患者地址 → 删除
• 患者电话 → 删除
• 医疗机构名称 → 替换
• 科室名称 → 替换
• 检查日期 → 偏移-365天
• 序列日期 → 偏移-365天
• 患者年龄 → 删除
• 患者体重 → 删除

适用场景: 符合HIPAA标准的临床数据预处理""",
            
            3: """级别3 - 严格脱敏

将处理以下字段:
• 级别2的所有字段
• 患者性别 → 删除
• 所有日期字段 → 偏移处理
• 所有UID → 重新生成
• 医生姓名 → 删除
• 设备序列号 → 删除

适用场景: 完全匿名化，数据共享和研究用途""",
            
            4: """级别4 - 加密脱敏

将处理以下字段:
• 标准脱敏涉及的所有字段
• 使用RSA非对称加密保护敏感信息
• 加密后的数据可使用对应私钥解密恢复

注意事项:
• 请妥善保管私钥，私钥丢失将无法解密
• 可选择自己的公钥或生成新的密钥对
• 适用场景: 需要保留原始信息但要求高安全性的场景"""
        }
        
        self.info_text.setText(info_texts.get(level_id, ""))
    
    def browse_key(self):
        """浏览公钥文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '选择公钥文件',
            '',
            'PEM文件 (*.pem);;所有文件 (*.*)'
        )
        
        if file_path:
            self.custom_key_path = file_path
            self.key_path_label.setText(file_path)
    
    def generate_key(self):
        """生成新密钥对"""
        from PyQt5.QtWidgets import QFileDialog
        from pathlib import Path
        
        # 选择保存目录
        save_dir = QFileDialog.getExistingDirectory(
            self,
            '选择密钥保存目录'
        )
        
        if save_dir:
            try:
                from core.encryptor import Encryptor
                import os
                
                encryptor = Encryptor()
                encryptor.generate_key_pair()
                
                # 保存公钥和私钥
                public_key_path = os.path.join(save_dir, 'public_key.pem')
                private_key_path = os.path.join(save_dir, 'private_key.pem')
                
                encryptor.save_public_key(public_key_path)
                encryptor.save_private_key(private_key_path)
                
                self.custom_key_path = public_key_path
                self.key_path_label.setText(public_key_path)
                
                QMessageBox.information(
                    self,
                    '成功',
                    f'密钥对已生成:\n公钥: {public_key_path}\n私钥: {private_key_path}\n\n请妥善保管私钥!'
                )
            except Exception as e:
                QMessageBox.critical(self, '错误', f'生成密钥失败: {e}')
    
    def preview_anonymization(self):
        """预览脱敏效果"""
        QMessageBox.information(self, '预览', '预览功能将在主窗口中实现')
    
    def get_selected_level(self) -> str:
        """获取选择的脱敏级别"""
        level_id = self.level_buttons.checkedId()
        level_map = {
            1: 'level1_basic',
            2: 'level2_standard',
            3: 'level3_strict',
            4: 'level4_encrypted'
        }
        return level_map.get(level_id, 'level1_basic')
    
    def get_custom_key_path(self) -> Optional[str]:
        """获取自定义公钥路径"""
        return self.custom_key_path if self.level_buttons.checkedId() == 4 else None
