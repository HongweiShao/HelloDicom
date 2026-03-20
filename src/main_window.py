"""
主窗口模块
"""
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QAction, QFileDialog, QToolBar, QStatusBar, QLabel,
    QMessageBox, QTabWidget, QTextEdit, QDialog, QPushButton
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from pathlib import Path


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.current_file = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('DICOM图像数据处理工具')
        self.setGeometry(0, 0, 1400, 900)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 创建中心部件
        self.create_central_widget()
        
        # 创建状态栏
        self.create_status_bar()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        open_action = QAction('打开(&O)', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction('保存(&S)', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction('另存为...', self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具(&T)')
        
        anonymize_action = QAction('敏感信息脱敏', self)
        anonymize_action.triggered.connect(self.show_anonymize_dialog)
        tools_menu.addAction(anonymize_action)
        
        compress_action = QAction('数据压缩', self)
        compress_action.triggered.connect(self.show_compress_dialog)
        tools_menu.addAction(compress_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar('主工具栏')
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        # 打开文件
        open_action = QAction('打开', self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        # 保存文件
        save_action = QAction('保存', self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # 脱敏
        anonymize_action = QAction('脱敏', self)
        anonymize_action.triggered.connect(self.show_anonymize_dialog)
        toolbar.addAction(anonymize_action)
        
        # 压缩
        compress_action = QAction('压缩', self)
        compress_action.triggered.connect(self.show_compress_dialog)
        toolbar.addAction(compress_action)
    
    def create_central_widget(self):
        """创建中心部件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧：图像显示区域
        from ui.image_viewer import ImageViewer, WindowLevelWidget
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 图像查看器
        self.image_viewer = ImageViewer()
        left_layout.addWidget(self.image_viewer, stretch=1)
        
        # 窗宽窗位控制
        self.window_level_widget = WindowLevelWidget()
        self.window_level_widget.window_level_changed.connect(self.on_window_level_changed)
        left_layout.addWidget(self.window_level_widget)
        
        # 缩放控制按钮
        zoom_layout = QHBoxLayout()
        
        zoom_in_btn = QPushButton('放大')
        zoom_in_btn.clicked.connect(self.image_viewer.zoom_in)
        zoom_layout.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton('缩小')
        zoom_out_btn.clicked.connect(self.image_viewer.zoom_out)
        zoom_layout.addWidget(zoom_out_btn)
        
        fit_btn = QPushButton('适应窗口')
        fit_btn.clicked.connect(self.image_viewer.fit_to_window)
        zoom_layout.addWidget(fit_btn)
        
        reset_btn = QPushButton('重置')
        reset_btn.clicked.connect(self.reset_image_view)
        zoom_layout.addWidget(reset_btn)
        
        left_layout.addLayout(zoom_layout)
        
        splitter.addWidget(left_panel)
        
        # 右侧：标签显示区域
        right_panel = QTabWidget()
        splitter.addWidget(right_panel)
        
        # 标签编辑器标签页
        from ui.tag_editor import TagEditor
        self.tag_editor = TagEditor()
        self.tag_editor.tag_modified.connect(self.on_tag_modified)
        right_panel.addTab(self.tag_editor, 'DICOM标签')
        
        # 元数据标签页
        self.metadata_view = QTextEdit()
        self.metadata_view.setReadOnly(True)
        right_panel.addTab(self.metadata_view, '文件信息')
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.file_info_label = QLabel('未加载文件')
        self.status_bar.addPermanentWidget(self.file_info_label)
    
    def open_file(self):
        """打开DICOM文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '选择DICOM文件',
            '',
            'DICOM文件 (*.dcm);;所有文件 (*.*)'
        )
        
        if file_path:
            self.current_file = file_path
            self.load_dicom_file(file_path)
    
    def load_dicom_file(self, file_path: str):
        """加载DICOM文件"""
        try:
            from core.dicom_parser import DicomParser
            
            self.parser = DicomParser(file_path)
            
            # 显示图像
            pixel_array = self.parser.get_pixel_array()
            if pixel_array is not None:
                # 自动计算窗宽窗位
                from core.image_processor import ImageProcessor
                processor = ImageProcessor()
                center, width = processor.auto_window_level(pixel_array)
                
                self.image_viewer.set_image(pixel_array, center, width)
                self.window_level_widget.set_values(center, width)
                
                self.image_viewer.fit_to_window()
            
            # 显示元数据
            metadata_text = "文件信息:\n"
            for key, value in self.parser.metadata.items():
                metadata_text += f"{key}: {value}\n"
            self.metadata_view.setText(metadata_text)
            
            # 显示标签
            tags = self.parser.get_all_tags()
            self.tag_editor.load_tags(tags)
            
            # 更新状态栏
            file_name = Path(file_path).name
            file_size = self.parser.get_file_size()
            from utils.helpers import bytes_to_readable
            self.file_info_label.setText(
                f"已加载: {file_name} | 大小: {bytes_to_readable(file_size)}"
            )
            
            self.status_bar.showMessage('文件加载成功', 3000)
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载文件失败: {e}')
            import traceback
            traceback.print_exc()
    
    def save_file(self):
        """保存DICOM文件"""
        if not hasattr(self, 'parser') or not self.parser:
            QMessageBox.warning(self, '警告', '没有已加载的文件')
            return
        
        # 弹出文件保存对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            '保存DICOM文件',
            '',
            'DICOM文件 (*.dcm);;所有文件 (*.*)'
        )
        
        if file_path:
            # 确保文件扩展名
            if not file_path.lower().endswith('.dcm'):
                file_path += '.dcm'
            
            try:
                # 保存文件
                success = self.parser.save(file_path)
                
                if success:
                    # 更新当前文件路径
                    self.current_file = file_path
                    
                    # 更新状态栏
                    from pathlib import Path
                    from utils.helpers import bytes_to_readable
                    file_name = Path(file_path).name
                    file_size = self.parser.get_file_size()
                    self.file_info_label.setText(
                        f"已保存: {file_name} | 大小: {bytes_to_readable(file_size)}"
                    )
                    
                    self.status_bar.showMessage('文件保存成功', 3000)
                    QMessageBox.information(self, '成功', f'文件已保存到:\n{file_path}')
                else:
                    QMessageBox.critical(self, '错误', '保存文件失败')
                    
            except Exception as e:
                QMessageBox.critical(self, '错误', f'保存文件失败: {e}')
                import traceback
                traceback.print_exc()
    
    def save_file_as(self):
        """另存为"""
        self.save_file()
    
    def on_window_level_changed(self, center: float, width: float):
        """窗宽窗位改变回调"""
        if hasattr(self, 'parser') and self.parser:
            pixel_array = self.parser.get_pixel_array()
            if pixel_array is not None:
                self.image_viewer.update_window_level(center, width)
    
    def reset_image_view(self):
        """重置图像视图"""
        self.image_viewer.reset_zoom()
        if hasattr(self, 'parser') and self.parser:
            pixel_array = self.parser.get_pixel_array()
            if pixel_array is not None:
                from core.image_processor import ImageProcessor
                processor = ImageProcessor()
                center, width = processor.auto_window_level(pixel_array)
                self.window_level_widget.set_values(center, width)
                self.image_viewer.update_window_level(center, width)
    
    def show_anonymize_dialog(self):
        """显示脱敏对话框"""
        if not hasattr(self, 'parser') or not self.parser:
            QMessageBox.warning(self, '警告', '请先加载DICOM文件')
            return
        
        from ui.anonymize_dialog import AnonymizeDialog
        
        dialog = AnonymizeDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            level = dialog.get_selected_level()
            custom_key = dialog.get_custom_key_path()
            
            try:
                from core.anonymizer import Anonymizer
                
                anonymizer = Anonymizer()
                success = anonymizer.anonymize(self.parser.dataset, level, custom_key)
                
                if success:
                    # 刷新标签显示
                    tags = self.parser.get_all_tags()
                    self.tag_editor.load_tags(tags)
                    
                    self.status_bar.showMessage(f'脱敏成功 - 级别: {level}', 5000)
                    QMessageBox.information(self, '成功', '敏感信息脱敏完成！')
                else:
                    QMessageBox.warning(self, '警告', '脱敏失败')
                    
            except Exception as e:
                QMessageBox.critical(self, '错误', f'脱敏失败: {e}')
                import traceback
                traceback.print_exc()
    
    def show_compress_dialog(self):
        """显示压缩对话框"""
        if not hasattr(self, 'parser') or not self.parser:
            QMessageBox.warning(self, '警告', '请先加载DICOM文件')
            return
        
        from ui.compress_dialog import CompressDialog
        
        dialog = CompressDialog(self)
        
        # 如果有ROI，传递给对话框
        if hasattr(self.image_viewer, 'rois'):
            dialog.set_rois(self.image_viewer.roi_rects)
        
        if dialog.exec_() == QDialog.Accepted:
            level = dialog.get_selected_level()
            quality = dialog.get_quality()
            rois = dialog.get_rois()
            
            try:
                from core.compressor import Compressor
                
                compressor = Compressor()
                success = compressor.compress(self.parser.dataset, level, rois, quality)
                
                if success:
                    # 更新文件大小显示
                    file_size = self.parser.get_file_size()
                    from utils.helpers import bytes_to_readable
                    
                    self.status_bar.showMessage(
                        f'压缩成功 - 级别: {level}, 质量: {quality}%', 
                        5000
                    )
                    
                    QMessageBox.information(
                        self, 
                        '成功', 
                        f'数据压缩完成！\n级别: {level}\n质量: {quality}%'
                    )
                else:
                    QMessageBox.warning(self, '警告', '压缩失败')
                    
            except Exception as e:
                QMessageBox.critical(self, '错误', f'压缩失败: {e}')
                import traceback
                traceback.print_exc()
    
    def on_tag_modified(self, tag_id: str, old_value: str, new_value: str):
        """标签修改回调"""
        if hasattr(self, 'parser') and self.parser:
            # 更新parser中的标签值
            self.parser.set_tag_value(tag_id, new_value)
            self.status_bar.showMessage(f'标签 {tag_id} 已更新', 3000)
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            '关于',
            'DICOM图像数据处理工具\n\n'
            '版本: 1.0.0\n\n'
            '功能:\n'
            '- DICOM文件解析\n'
            '- 图像显示\n'
            '- 标签查看\n'
            '- 多级别敏感信息脱敏\n'
            '- 多级别数据压缩\n\n'
            '用于临床数据预处理'
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
