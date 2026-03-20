"""
测试脚本 - 验证核心功能
"""
import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        from core.dicom_parser import DicomParser
        print("✓ DicomParser 导入成功")
    except Exception as e:
        print(f"✗ DicomParser 导入失败: {e}")
        return False
    
    try:
        from core.image_processor import ImageProcessor
        print("✓ ImageProcessor 导入成功")
    except Exception as e:
        print(f"✗ ImageProcessor 导入失败: {e}")
        return False
    
    try:
        from core.anonymizer import Anonymizer
        print("✓ Anonymizer 导入成功")
    except Exception as e:
        print(f"✗ Anonymizer 导入失败: {e}")
        return False
    
    try:
        from core.encryptor import Encryptor
        print("✓ Encryptor 导入成功")
    except Exception as e:
        print(f"✗ Encryptor 导入失败: {e}")
        return False
    
    try:
        from core.compressor import Compressor
        print("✓ Compressor 导入成功")
    except Exception as e:
        print(f"✗ Compressor 导入失败: {e}")
        return False
    
    try:
        from core.roi_manager import ROIManager
        print("✓ ROIManager 导入成功")
    except Exception as e:
        print(f"✗ ROIManager 导入失败: {e}")
        return False
    
    try:
        from utils.config import config_manager
        print("✓ ConfigManager 导入成功")
    except Exception as e:
        print(f"✗ ConfigManager 导入失败: {e}")
        return False
    
    return True


def test_config_loading():
    """测试配置加载"""
    print("\n测试配置加载...")
    
    from utils.config import config_manager
    
    # 测试脱敏配置
    levels = ['level1_basic', 'level2_standard', 'level3_strict', 'level4_encrypted']
    for level in levels:
        config = config_manager.get_anonymize_level(level)
        if config:
            print(f"✓ {level} 配置加载成功")
        else:
            print(f"✗ {level} 配置加载失败")
            return False
    
    # 测试压缩配置
    presets = ['level1_lossless', 'level2_standard', 'level3_roi']
    for preset in presets:
        config = config_manager.get_compression_preset(preset)
        if config:
            print(f"✓ {preset} 配置加载成功")
        else:
            print(f"✗ {preset} 配置加载失败")
            return False
    
    return True


def test_encryption():
    """测试加密功能"""
    print("\n测试加密功能...")
    
    try:
        from core.encryptor import Encryptor
        
        encryptor = Encryptor()
        
        # 生成密钥对
        encryptor.generate_key_pair()
        print("✓ 密钥对生成成功")
        
        # 测试加密解密
        plaintext = "PatientName: 张三"
        ciphertext = encryptor.encrypt(plaintext)
        print(f"✓ 加密成功: {plaintext} -> {ciphertext[:50]}...")
        
        decrypted = encryptor.decrypt(ciphertext)
        print(f"✓ 解密成功: {decrypted}")
        
        if decrypted == plaintext:
            print("✓ 加密解密验证成功")
            return True
        else:
            print("✗ 加密解密验证失败")
            return False
            
    except Exception as e:
        print(f"✗ 加密测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_roi_manager():
    """测试ROI管理"""
    print("\n测试ROI管理...")
    
    try:
        from core.roi_manager import ROIManager
        
        manager = ROIManager()
        
        # 添加ROI
        manager.add_roi(10, 20, 100, 200, "TestROI")
        print(f"✓ 添加ROI成功，数量: {manager.get_roi_count()}")
        
        # 获取ROI
        rois = manager.get_rois()
        if len(rois) == 1:
            print(f"✓ 获取ROI成功: {rois[0]}")
        else:
            print("✗ 获取ROI失败")
            return False
        
        # 清除ROI
        manager.clear_rois()
        if manager.get_roi_count() == 0:
            print("✓ 清除ROI成功")
        else:
            print("✗ 清除ROI失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ ROI管理测试失败: {e}")
        return False


def test_ui_imports():
    """测试UI组件导入"""
    print("\n测试UI组件导入...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("✓ PyQt5 导入成功")
    except Exception as e:
        print(f"✗ PyQt5 导入失败: {e}")
        print("  请安装: pip install PyQt5")
        return False
    
    try:
        from ui.image_viewer import ImageViewer, WindowLevelWidget
        print("✓ ImageViewer 导入成功")
    except Exception as e:
        print(f"✗ ImageViewer 导入失败: {e}")
        return False
    
    try:
        from ui.tag_editor import TagEditor
        print("✓ TagEditor 导入成功")
    except Exception as e:
        print(f"✗ TagEditor 导入失败: {e}")
        return False
    
    try:
        from ui.anonymize_dialog import AnonymizeDialog
        print("✓ AnonymizeDialog 导入成功")
    except Exception as e:
        print(f"✗ AnonymizeDialog 导入失败: {e}")
        return False
    
    try:
        from ui.compress_dialog import CompressDialog
        print("✓ CompressDialog 导入成功")
    except Exception as e:
        print(f"✗ CompressDialog 导入失败: {e}")
        return False
    
    return True


def main():
    """主测试函数"""
    print("=" * 60)
    print("DICOM图像数据处理工具 - 功能测试")
    print("=" * 60)
    
    results = []
    
    # 运行测试
    results.append(("模块导入", test_imports()))
    results.append(("配置加载", test_config_loading()))
    results.append(("加密功能", test_encryption()))
    results.append(("ROI管理", test_roi_manager()))
    results.append(("UI组件", test_ui_imports()))
    
    # 输出结果
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    print("=" * 60)
    
    # 统计
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查依赖安装")
        return 1


if __name__ == '__main__':
    sys.exit(main())
