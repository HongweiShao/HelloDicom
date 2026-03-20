# DICOM压缩功能优化说明

## 优化目标

确保压缩后的DICOM文件符合DICOM标准格式，能够被标准的DICOM查看器和处理软件正确读取。

## 主要优化内容

### 1. 使用pydicom的内置压缩功能

**之前的问题:**
```python
# 直接替换PixelData，不处理DICOM封装
compressed_data = self._compress_jpeg(pixel_array, quality=quality)
dataset.PixelData = compressed_data  # ❌ 不符合DICOM格式
```

**优化后的方案:**
```python
# 使用pydicom的compress方法，自动处理DICOM格式封装
dataset.compress(transfer_syntax_uid)  # ✓ 正确的DICOM格式
```

### 2. 8位转换处理

**实现方法:**
```python
def _convert_pixel_data_to_8bit(self, dataset: Dataset) -> bool:
    """将像素数据转换为8位"""
    pixel_array = dataset.pixel_array
    
    # 归一化到0-255
    min_val = pixel_array.min()
    max_val = pixel_array.max()
    normalized = ((pixel_array - min_val) / 
                 (max_val - min_val) * 255).astype(np.uint8)
    
    # 更新数据集
    dataset.PixelData = normalized.tobytes()
    
    # 更新相关属性
    dataset.BitsAllocated = 8
    dataset.BitsStored = 8
    dataset.HighBit = 7
    dataset.PixelRepresentation = 0
```

### 3. 传输语法支持

支持的DICOM传输语法：

| 传输语法 | UID | 描述 |
|---------|-----|------|
| JPEG Baseline | 1.2.840.10008.1.2.4.50 | JPEG有损压缩 |
| JPEG Extended | 1.2.840.10008.1.2.4.51 | JPEG有损扩展 |
| JPEG Lossless | 1.2.840.10008.1.2.4.57 | JPEG无损压缩 |
| JPEG Lossless SV1 | 1.2.840.10008.1.2.4.70 | JPEG无损SV1 |
| JPEG 2000 Lossless | 1.2.840.10008.1.2.4.90 | JPEG 2000无损 |
| JPEG 2000 | 1.2.840.10008.1.2.4.91 | JPEG 2000有损 |

### 4. ROI压缩优化

**实现策略:**
1. **ROI预处理**: 对非ROI区域应用高斯模糊
2. **pydicom压缩**: 使用标准compress方法
3. **格式保证**: 确保符合DICOM标准

**代码示例:**
```python
# 应用ROI预处理
processed_array = self._apply_roi_preprocessing(
    pixel_array, roi_mask, roi_quality, non_roi_quality
)

# 更新像素数据
dataset.PixelData = processed_array.tobytes()

# 使用pydicom的压缩功能
dataset.compress(target_syntax)
```

### 5. 错误处理和回退

**多层级回退机制:**

```
主要方法: pydicom.compress()
    ↓ 失败
备用方法: glymur (OpenJPEG)
    ↓ 失败
兜底方法: OpenCV cv2.imencode()
    ↓ 失败
最后保底: JPEG Baseline (最兼容格式)
```

## DICOM文件格式要求

### 压缩后的文件必须包含:

1. **文件元信息 (File Meta Information)**
   - TransferSyntaxUID: 压缩传输语法
   - SOPClassUID: SOP类UID
   - SOPInstanceUID: SOP实例UID

2. **像素数据 (Pixel Data)**
   - 正确封装的压缩数据
   - 符合传输语法规范

3. **像素属性 (Pixel Attributes)**
   - BitsAllocated: 每像素位数
   - BitsStored: 存储位数
   - HighBit: 最高位
   - PixelRepresentation: 像素表示(0=无符号, 1=有符号)

### pydicom.compress() 的优势:

1. **自动封装**: 自动处理DICOM格式的封装
2. **属性更新**: 自动更新相关属性
3. **标准兼容**: 生成的文件符合DICOM标准
4. **错误检查**: 内置格式验证

## 使用建议

### 级别1 - 无损压缩

**适用场景:**
- 诊断用途
- 需要保持原始图像质量
- 法律要求无损

**特点:**
- 压缩比: 2-4x
- 完全可逆
- 兼容性好

### 级别2 - 标准压缩

**适用场景:**
- 临床审查
- 日常诊断
- 数据传输

**特点:**
- 压缩比: 8-15x
- 质量损失小
- 速度较快

### 级别3 - ROI压缩

**适用场景:**
- 数据存档
- 远程会诊
- 带宽受限

**特点:**
- 压缩比: 20-40x
- ROI区域高质量
- 非ROI区域高压缩

## 依赖要求

### 必需依赖:
```bash
pip install pydicom>=2.4.4
pip install numpy>=1.24.0
```

### 推荐依赖 (提升压缩效果):
```bash
# JPEG压缩
pip install opencv-python>=4.8.0

# JPEG 2000压缩
pip install glymur>=0.12.0
# 还需要安装OpenJPEG
pip install pylibjpeg>=2.0.0
pip install pylibjpeg-libjpeg>=2.0.0
pip install gdcm>=3.0.22
```

## 测试验证

运行测试脚本验证压缩功能:

```bash
cd E:\Temp\dicom-tool
python test_compression.py
```

测试内容包括:
1. 创建测试DICOM数据集
2. 级别1无损压缩
3. 级别2标准压缩
4. 级别3 ROI压缩
5. 文件保存和重新加载验证

## 注意事项

1. **备份原文件**: 压缩前请备份原始DICOM文件
2. **质量选择**: 根据用途选择合适的质量参数
3. **兼容性**: 确保接收方支持所选的压缩格式
4. **ROI定义**: 准确定义ROI区域以获得最佳效果
5. **内存需求**: 大文件压缩可能需要较多内存

## 常见问题

### Q: 压缩后文件无法打开?
A: 检查是否使用了不支持的传输语法，建议使用JPEG Baseline作为最兼容选项。

### Q: 质量损失明显?
A: 尝试提高质量参数，或使用无损压缩。

### Q: 压缩比不理想?
A: 使用ROI压缩保护关键区域，非ROI区域可以获得更高压缩比。

### Q: ROI压缩后ROI区域模糊?
A: ROI预处理使用了模糊来提高压缩比，如需ROI高质量，可以调整ROI质量参数。

---

© 2026 DICOM图像数据处理工具
