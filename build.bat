@echo off
REM DICOM图像数据处理工具 - 构建脚本
REM 用于Windows平台打包

chcp 65001 >nul

echo ====================================
echo DICOM图像数据处理工具 - 构建脚本
echo ====================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.9+
    pause
    exit /b 1
)

REM 安装依赖
echo [步骤1] 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo [步骤2] 安装打包工具...
pip install pyinstaller
if errorlevel 1 (
    echo [错误] PyInstaller安装失败
    pause
    exit /b 1
)

echo.
echo [步骤3] 运行测试...
python test_basic.py
if errorlevel 1 (
    echo [警告] 部分测试失败，是否继续打包？(Y/N)
 REM   choice /C YN /N /M "请选择: "
 REM   if errorlevel 2 (
 REM       echo [取消] 用户取消打包
 REM       pause
 REM       exit /b 1
    )
)

echo.
echo [步骤4] 开始打包...
pyinstaller build.spec --clean
if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo ====================================
echo [成功] 打包完成！
echo ====================================
echo.
echo 可执行文件位置: dist\DICOM图像数据处理工具.exe
echo.
pause
