"""
测试DICOM压缩功能
"""
import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_compression():
    """测试压缩功能"""
    print("=" * 60)
    print("DICOM压缩功能测试")
    print("=" * 60)
    
    try:
        from core.compressor import Compressor
        from core.dicom_parser import DicomParser
        import numpy as np
        
        print("\n测试1: 创建测试DICOM数据集")
        # 创建一个简单的测试数据集
        from pydicom.dataset import Dataset, FileMetaDataset
        from pydicom.uid import generate_uid
        
        ds = Dataset()
        ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
        ds.SOPInstanceUID = generate_uid()
        ds.Modality = 'CT'
        ds.SeriesInstanceUID = generate_uid()
        ds.StudyInstanceUID = generate_uid()
        ds.PixelSpacing = [1.0, 1.0]
        ds.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
        ds.ImagePositionPatient = [0, 0, 0]
        ds.SamplesPerPixel = 1
        ds.Rows = 256
        ds.Columns = 256
        ds.BitsAllocated = 16
        ds.BitsStored = 16
        ds.HighBit = 15
        ds.PixelRepresentation = 0
        ds.PhotometricInterpretation = 'MONOCHROME2'
        
        # 创建测试像素数据
        pixel_data = np.random.randint(0, 4096, size=(256, 256), dtype=np.uint16)
        ds.PixelData = pixel_data.tobytes()
        
        print("✓ 测试数据集创建成功")
        print(f"  图像尺寸: {ds.Rows}x{ds.Columns}")
        print(f"  数据类型: {pixel_data.dtype}")
        print(f"  原始大小: {len(ds.PixelData)} 字节")
        
        print("\n测试2: 级别1无损压缩")
        compressor = Compressor()
        success = compressor.compress(ds, 'level1_lossless')
        if success:
            print("✓ 级别1无损压缩成功")
            print(f"  传输语法: {ds.file_meta.TransferSyntaxUID}")
            print(f"  压缩后大小: {len(ds.PixelData)} 字节")
        else:
            print("✗ 级别1无损压缩失败")
        
        print("\n测试3: 级别2标准压缩")
        # 重新创建数据集（因为已经被压缩）
        ds2 = Dataset()
        ds2.SOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
        ds2.SOPInstanceUID = generate_uid()
        ds2.Modality = 'CT'
        ds2.Rows = 256
        ds2.Columns = 256
        ds2.BitsAllocated = 16
        ds2.BitsStored = 16
        ds2.HighBit = 15
        ds2.PixelRepresentation = 0
        ds2.PhotometricInterpretation = 'MONOCHROME2'
        pixel_data2 = np.random.randint(0, 4096, size=(256, 256), dtype=np.uint16)
        ds2.PixelData = pixel_data2.tobytes()
        
        success = compressor.compress(ds2, 'level2_standard', quality=90)
        if success:
            print("✓ 级别2标准压缩成功")
            print(f"  传输语法: {ds2.file_meta.TransferSyntaxUID}")
            print(f"  压缩后大小: {len(ds2.PixelData)} 字节")
        else:
            print("✗ 级别2标准压缩失败")
        
        print("\n测试4: 级别3 ROI压缩")
        ds3 = Dataset()
        ds3.SOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
        ds3.SOPInstanceUID = generate_uid()
        ds3.Modality = 'CT'
        ds3.Rows = 256
        ds3.Columns = 256
        ds3.BitsAllocated = 16
        ds3.BitsStored = 16
        ds3.HighBit = 15
        ds3.PixelRepresentation = 0
        ds3.PhotometricInterpretation = 'MONOCHROME2'
        pixel_data3 = np.random.randint(0, 4096, size=(256, 256), dtype=np.uint16)
        ds3.PixelData = pixel_data3.tobytes()
        
        rois = [(50, 50, 150, 150)]  # ROI区域
        success = compressor.compress(ds3, 'level3_roi', rois=rois, quality=70)
        if success:
            print("✓ 级别3 ROI压缩成功")
            print(f"  传输语法: {ds3.file_meta.TransferSyntaxUID}")
            print(f"  压缩后大小: {len(ds3.PixelData)} 字节")
            print(f"  ROI区域: {rois}")
        else:
            print("✗ 级别3 ROI压缩失败")
        
        print("\n测试5: 保存压缩后的文件")
        try:
            # 保存测试文件
            test_output = Path('test_compressed.dcm')
            ds3.save_as(str(test_output))
            print(f"✓ 测试文件保存成功: {test_output}")
            print(f"  文件大小: {test_output.stat().st_size} 字节")
            
            # 尝试重新加载验证
            parser = DicomParser(str(test_output))
            print("✓ 压缩文件可以正常加载")
            
        except Exception as e:
            print(f"✗ 保存测试失败: {e}")
        
        print("\n" + "=" * 60)
        print("压缩功能测试完成")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_compression()
    sys.exit(0 if success else 1)
