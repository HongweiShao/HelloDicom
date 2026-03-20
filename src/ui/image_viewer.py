"""
图像查看器组件
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, 
    QPushButton, QScrollArea, QFrame, QSpinBox
)
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QPen
import numpy as np


class ImageViewer(QScrollArea):
    """图像查看器"""
    
    def __init__(self):
        super().__init__()
        
        self.image = None
        self.qpixmap = None
        self.scale_factor = 1.0
        self.min_scale = 0.1
        self.max_scale = 10.0
        
        # 窗宽窗位
        self.window_center = 127
        self.window_width = 256
        
        # 平移
        self.dragging = False
        self.last_pos = QPoint()
        
        # ROI绘制
        self.roi_enabled = False
        self.roi_start = None
        self.roi_end = None
        self.roi_rects = []
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        # 设置滚动区域属性
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignCenter)
        self.setBackgroundRole(QPalette.Dark)
        
        # 图像标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 400)
        self.setWidget(self.image_label)
        
        # 设置鼠标跟踪
        self.setMouseTracking(True)
    
    def set_image(self, pixel_array: np.ndarray, 
                  window_center: float = None, 
                  window_width: float = None):
        """
        设置图像
        
        Args:
            pixel_array: 像素数组
            window_center: 窗位
            window_width: 窗宽
        """
        from core.image_processor import ImageProcessor
        
        if pixel_array is None:
            return
        
        self.image = pixel_array
        
        # 应用窗宽窗位
        processor = ImageProcessor()
        
        if window_center is not None and window_width is not None:
            self.window_center = window_center
            self.window_width = window_width
            processor.current_window_center = window_center
            processor.current_window_width = window_width
        else:
            # 自动计算窗宽窗位
            self.window_center, self.window_width = processor.auto_window_level(pixel_array)
        
        # 应用窗宽窗位
        display_image = processor.apply_window_level(
            pixel_array, 
            self.window_center, 
            self.window_width
        )
        
        # 转换为RGB格式
        display_image = processor.convert_to_pixmap(display_image)
        
        # 转换为QImage
        height, width, channel = display_image.shape
        bytes_per_line = 3 * width
        qimage = QImage(
            display_image.data, 
            width, 
            height, 
            bytes_per_line, 
            QImage.Format_RGB888
        )
        
        self.qpixmap = QPixmap.fromImage(qimage)
        self.update_display()
    
    def update_display(self):
        """更新显示"""
        if self.qpixmap is None:
            return
        
        # 缩放图像
        scaled_pixmap = self.qpixmap.scaled(
            self.qpixmap.size() * self.scale_factor,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.resize(scaled_pixmap.size())
    
    def zoom_in(self):
        """放大"""
        if self.scale_factor < self.max_scale:
            self.scale_factor *= 1.2
            self.update_display()
    
    def zoom_out(self):
        """缩小"""
        if self.scale_factor > self.min_scale:
            self.scale_factor /= 1.2
            self.update_display()
    
    def reset_zoom(self):
        """重置缩放"""
        self.scale_factor = 1.0
        self.update_display()
    
    def fit_to_window(self):
        """适应窗口"""
        if self.qpixmap is None:
            return
        
        # 计算适应窗口的缩放比例
        viewport_size = self.viewport().size()
        pixmap_size = self.qpixmap.size()
        
        scale_w = viewport_size.width() / pixmap_size.width()
        scale_h = viewport_size.height() / pixmap_size.height()
        
        self.scale_factor = min(scale_w, scale_h)
        self.update_display()
    
    def update_window_level(self, center: float, width: float):
        """
        更新窗宽窗位
        
        Args:
            center: 窗位
            width: 窗宽
        """
        self.window_center = center
        self.window_width = width
        
        if self.image is not None:
            from core.image_processor import ImageProcessor
            processor = ImageProcessor()
            processor.current_window_center = center
            processor.current_window_width = width
            
            display_image = processor.apply_window_level(
                self.image, 
                center, 
                width
            )
            display_image = processor.convert_to_pixmap(display_image)
            
            height, width, channel = display_image.shape
            bytes_per_line = 3 * width
            qimage = QImage(
                display_image.data, 
                width, 
                height, 
                bytes_per_line, 
                QImage.Format_RGB888
            )
            
            self.qpixmap = QPixmap.fromImage(qimage)
            self.update_display()
    
    def enable_roi_drawing(self, enabled: bool):
        """
        启用/禁用ROI绘制
        
        Args:
            enabled: 是否启用
        """
        self.roi_enabled = enabled
        if enabled:
            self.setCursor(Qt.CrossCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
    
    def clear_rois(self):
        """清除所有ROI"""
        self.roi_rects = []
        self.update()
    
    def get_rois(self):
        """获取所有ROI区域"""
        return self.roi_rects
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            if self.roi_enabled:
                # 开始绘制ROI
                self.roi_start = event.pos()
            else:
                # 开始平移
                self.dragging = True
                self.last_pos = event.pos()
                self.setCursor(Qt.ClosedHandCursor)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.dragging:
            # 平移图像
            delta = event.pos() - self.last_pos
            self.last_pos = event.pos()
            
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()
            
            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())
        
        elif self.roi_enabled and self.roi_start is not None:
            # 绘制ROI
            self.roi_end = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            if self.roi_enabled and self.roi_start is not None and self.roi_end is not None:
                # 完成ROI绘制
                roi_rect = QRect(self.roi_start, self.roi_end).normalized()
                if roi_rect.width() > 10 and roi_rect.height() > 10:  # 最小ROI尺寸
                    self.roi_rects.append(roi_rect)
                self.roi_start = None
                self.roi_end = None
            else:
                # 结束平移
                self.dragging = False
                self.setCursor(Qt.ArrowCursor)
            
            self.update()
    
    def wheelEvent(self, event):
        """鼠标滚轮事件"""
        # 缩放
        delta = event.angleDelta().y()
        
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def paintEvent(self, event):
        """绘制事件"""
        super().paintEvent(event)
        
        if not self.roi_rects or self.qpixmap is None:
            return
        
        # 绘制ROI区域
        painter = QPainter(self.viewport())
        painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.DashLine))
        
        for rect in self.roi_rects:
            painter.drawRect(rect)
        
        # 绘制当前正在绘制的ROI
        if self.roi_start is not None and self.roi_end is not None:
            current_rect = QRect(self.roi_start, self.roi_end).normalized()
            painter.drawRect(current_rect)


class WindowLevelWidget(QWidget):
    """窗宽窗位控制组件"""
    
    window_level_changed = pyqtSignal(float, float)
    
    def __init__(self):
        super().__init__()
        
        self.window_center = 127
        self.window_width = 256
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 窗位控制
        center_layout = QHBoxLayout()
        center_layout.addWidget(QLabel('窗位:'))
        
        self.center_slider = QSlider(Qt.Horizontal)
        self.center_slider.setMinimum(-1000)
        self.center_slider.setMaximum(3000)
        self.center_slider.setValue(int(self.window_center))
        self.center_slider.valueChanged.connect(self.on_center_changed)
        center_layout.addWidget(self.center_slider)
        
        self.center_spin = QSpinBox()
        self.center_spin.setMinimum(-1000)
        self.center_spin.setMaximum(3000)
        self.center_spin.setValue(int(self.window_center))
        self.center_spin.valueChanged.connect(self.on_center_spin_changed)
        center_layout.addWidget(self.center_spin)
        
        layout.addLayout(center_layout)
        
        # 窗宽控制
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel('窗宽:'))
        
        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setMinimum(1)
        self.width_slider.setMaximum(4000)
        self.width_slider.setValue(int(self.window_width))
        self.width_slider.valueChanged.connect(self.on_width_changed)
        width_layout.addWidget(self.width_slider)
        
        self.width_spin = QSpinBox()
        self.width_spin.setMinimum(1)
        self.width_spin.setMaximum(4000)
        self.width_spin.setValue(int(self.window_width))
        self.width_spin.valueChanged.connect(self.on_width_spin_changed)
        width_layout.addWidget(self.width_spin)
        
        layout.addLayout(width_layout)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton('重置')
        reset_btn.clicked.connect(self.reset)
        button_layout.addWidget(reset_btn)
        
        auto_btn = QPushButton('自动')
        auto_btn.clicked.connect(self.auto_window_level)
        button_layout.addWidget(auto_btn)
        
        layout.addLayout(button_layout)
    
    def on_center_changed(self, value):
        """窗位滑块改变"""
        self.window_center = value
        self.center_spin.blockSignals(True)
        self.center_spin.setValue(value)
        self.center_spin.blockSignals(False)
        self.window_level_changed.emit(self.window_center, self.window_width)
    
    def on_center_spin_changed(self, value):
        """窗位数值框改变"""
        self.window_center = value
        self.center_slider.blockSignals(True)
        self.center_slider.setValue(value)
        self.center_slider.blockSignals(False)
        self.window_level_changed.emit(self.window_center, self.window_width)
    
    def on_width_changed(self, value):
        """窗宽滑块改变"""
        self.window_width = value
        self.width_spin.blockSignals(True)
        self.width_spin.setValue(value)
        self.width_spin.blockSignals(False)
        self.window_level_changed.emit(self.window_center, self.window_width)
    
    def on_width_spin_changed(self, value):
        """窗宽数值框改变"""
        self.window_width = value
        self.width_slider.blockSignals(True)
        self.width_slider.setValue(value)
        self.width_slider.blockSignals(False)
        self.window_level_changed.emit(self.window_center, self.window_width)
    
    def reset(self):
        """重置窗宽窗位"""
        self.window_center = 127
        self.window_width = 256
        self.center_slider.setValue(int(self.window_center))
        self.width_slider.setValue(int(self.window_width))
        self.window_level_changed.emit(self.window_center, self.window_width)
    
    def auto_window_level(self):
        """自动窗宽窗位 - 由外部调用时设置"""
        self.window_level_changed.emit(self.window_center, self.window_width)
    
    def set_values(self, center: float, width: float):
        """
        设置窗宽窗位值
        
        Args:
            center: 窗位
            width: 窗宽
        """
        self.window_center = center
        self.window_width = width
        self.center_slider.setValue(int(center))
        self.width_slider.setValue(int(width))


# 需要导入QPalette
from PyQt5.QtGui import QPalette
