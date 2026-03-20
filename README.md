# DICOM图像数据处理工具

一个专业的Windows桌面端DICOM图像数据处理工具，用于临床数据预处理。

## 功能特性

### 核心功能
- **文件解析**: 支持标准DICOM文件读取(.dcm)
- **图像显示**: 灰度/彩色图像渲染，支持窗宽窗位调节
- **标签显示**: 树形结构显示所有标签，支持搜索和编辑

### 高级功能

#### 1. 多级别敏感信息脱敏

**级别1 - 基础脱敏**
- 患者姓名、ID、出生日期

**级别2 - 标准脱敏 (HIPAA)**
- 基础字段 + 地址、电话、机构、科室、检查日期等

**级别3 - 严格脱敏**
- 完全匿名化，所有UID重新生成，日期差值化处理

**级别4 - 加密脱敏**
- RSA非对称加密，用户可导入自己的公钥
- 可逆保护，支持私钥解密恢复

#### 2. 多级别数据压缩

**级别1 - 无损压缩**
- JPEG Lossless, JPEG 2000 Lossless
- 压缩比: 2-4x
- 适用: 诊断用途

**级别2 - 标准压缩**
- JPEG Baseline, JPEG 2000
- 压缩比: 8-15x, 质量: 90%+
- 适用: 临床审查

**级别3 - ROI压缩**
- JPEG 2000有损压缩
- 用户可绘制ROI区域
- ROI高质量压缩，非ROI高压缩比
- 压缩比: 20-40x
- 适用: 数据存档/远程会诊

## 安装

### 系统要求
- Windows 10/11
- Python 3.9+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
cd dicom-tool/src
python main.py
```

## 项目结构

```
dicom-tool/
├── src/
│   ├── main.py                 # 应用入口
│   ├── main_window.py          # 主窗口
│   ├── core/
│   │   ├── dicom_parser.py     # DICOM解析
│   │   ├── image_processor.py  # 图像处理
│   │   ├── anonymizer.py       # 脱敏处理
│   │   ├── encryptor.py        # 加密处理
│   │   ├── compressor.py       # 压缩处理
│   │   └── roi_manager.py      # ROI管理
│   ├── ui/
│   │   ├── image_viewer.py     # 图像查看器
│   │   ├── tag_editor.py       # 标签编辑器
│   │   ├── anonymize_dialog.py # 脱敏对话框
│   │   ├── compress_dialog.py  # 压缩对话框
│   │   ├── roi_editor.py       # ROI编辑器
│   │   └── key_manager.py      # 密钥管理
│   └── utils/
│       ├── config.py           # 配置管理
│       └── helpers.py          # 工具函数
├── requirements.txt
├── README.md
└── config/
    ├── anonymize_rules.json    # 脱敏规则配置
    └── compression_presets.json # 压缩预设配置
```

## 开发计划

- [x] 阶段1: 搭建项目框架和基础UI
- [x] 阶段2: 实现DICOM文件解析和图像显示
- [x] 阶段3: 实现标签显示和编辑
- [x] 阶段4: 实现多级别脱敏功能
- [x] 阶段5: 实现多级别压缩功能
- [x] 阶段6: 测试和优化

## 已完成功能

### 核心功能
- ✅ DICOM文件解析与显示
- ✅ 图像窗宽窗位调节
- ✅ 标签查看与编辑
- ✅ 文件保存功能

### 脱敏功能
- ✅ 级别1: 基础脱敏
- ✅ 级别2: 标准脱敏 (HIPAA)
- ✅ 级别3: 严格脱敏
- ✅ 级别4: RSA加密脱敏

### 压缩功能
- ✅ 级别1: JPEG/JPEG 2000 无损压缩
- ✅ 级别2: JPEG/JPEG 2000 有损压缩
- ✅ 级别3: JPEG 2000 ROI压缩
- ✅ JPEG压缩实现 (_compress_jpeg)
- ✅ JPEG 2000压缩实现 (_compress_jpeg2000)
- ✅ ROI预处理功能

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请提交Issue。
