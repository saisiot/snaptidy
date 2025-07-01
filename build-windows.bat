@echo off
echo Building SnapTidy for Windows...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

REM Build CLI executable
echo Building CLI executable...
pyinstaller snaptidy-cli-windows.spec --clean

REM Build GUI executable
echo Building GUI executable...
pyinstaller snaptidy-gui-windows.spec --clean

REM Create release directory
if not exist "release\v0.1.0b1\gui-windows-x64" mkdir "release\v0.1.0b1\gui-windows-x64"

REM Copy GUI files
echo Copying GUI files...
copy "dist\snaptidy-gui.exe" "release\v0.1.0b1\gui-windows-x64\"
copy "logo.png" "release\v0.1.0b1\gui-windows-x64\"
copy "README.md" "release\v0.1.0b1\gui-windows-x64\"
copy "README-ko.md" "release\v0.1.0b1\gui-windows-x64\"
copy "LICENSE" "release\v0.1.0b1\gui-windows-x64\"
copy "CHANGELOG.md" "release\v0.1.0b1\gui-windows-x64\"

REM Create CLI directory
if not exist "release\v0.1.0b1\cli-windows-x64" mkdir "release\v0.1.0b1\cli-windows-x64"

REM Copy CLI files
echo Copying CLI files...
copy "dist\snaptidy.exe" "release\v0.1.0b1\cli-windows-x64\"
copy "README.md" "release\v0.1.0b1\cli-windows-x64\"
copy "README-ko.md" "release\v0.1.0b1\cli-windows-x64\"
copy "LICENSE" "release\v0.1.0b1\cli-windows-x64\"
copy "CHANGELOG.md" "release\v0.1.0b1\cli-windows-x64\"

REM Create complete package directory
if not exist "release\v0.1.0b1\complete-windows-x64" mkdir "release\v0.1.0b1\complete-windows-x64"

REM Copy all files to complete package
echo Copying files to complete package...
xcopy "release\v0.1.0b1\gui-windows-x64\*" "release\v0.1.0b1\complete-windows-x64\" /E /Y
copy "release\v0.1.0b1\cli-windows-x64\snaptidy.exe" "release\v0.1.0b1\complete-windows-x64\"

echo Build completed successfully!
echo.
echo Files created:
echo - release\v0.1.0b1\gui-windows-x64\ (GUI only)
echo - release\v0.1.0b1\cli-windows-x64\ (CLI only)
echo - release\v0.1.0b1\complete-windows-x64\ (Complete package)
echo.
pause 