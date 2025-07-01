# SnapTidy Windows Build Script (PowerShell)

Write-Host "Building SnapTidy for Windows..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
pip install pyinstaller

# Build CLI executable
Write-Host "Building CLI executable..." -ForegroundColor Yellow
pyinstaller snaptidy-cli-windows.spec --clean

# Build GUI executable
Write-Host "Building GUI executable..." -ForegroundColor Yellow
pyinstaller snaptidy-gui-windows.spec --clean

# Create release directories
$releaseBase = "release\v0.1.0b1"
$guiDir = "$releaseBase\gui-windows-x64"
$cliDir = "$releaseBase\cli-windows-x64"
$completeDir = "$releaseBase\complete-windows-x64"

New-Item -ItemType Directory -Force -Path $guiDir | Out-Null
New-Item -ItemType Directory -Force -Path $cliDir | Out-Null
New-Item -ItemType Directory -Force -Path $completeDir | Out-Null

# Copy GUI files
Write-Host "Copying GUI files..." -ForegroundColor Yellow
Copy-Item "dist\snaptidy-gui.exe" $guiDir
Copy-Item "logo.png" $guiDir
Copy-Item "README.md" $guiDir
Copy-Item "README-ko.md" $guiDir
Copy-Item "LICENSE" $guiDir
Copy-Item "CHANGELOG.md" $guiDir

# Copy CLI files
Write-Host "Copying CLI files..." -ForegroundColor Yellow
Copy-Item "dist\snaptidy.exe" $cliDir
Copy-Item "README.md" $cliDir
Copy-Item "README-ko.md" $cliDir
Copy-Item "LICENSE" $cliDir
Copy-Item "CHANGELOG.md" $cliDir

# Copy all files to complete package
Write-Host "Copying files to complete package..." -ForegroundColor Yellow
Copy-Item "$guiDir\*" $completeDir -Recurse -Force
Copy-Item "$cliDir\snaptidy.exe" $completeDir

Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Files created:" -ForegroundColor Cyan
Write-Host "- $guiDir (GUI only)" -ForegroundColor White
Write-Host "- $cliDir (CLI only)" -ForegroundColor White
Write-Host "- $completeDir (Complete package)" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit" 