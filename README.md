# SnapTidy

<div align="center">
  
  <p align="center">
    <img src="logo.png" alt="SnapTidy logo" width="280"/>
  </p>

  **Organize your photo library with ease.**
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![Python Version](https://img.shields.io/badge/python-3.7%2B-brightgreen)](https://www.python.org/downloads/)
  [![Homebrew](https://img.shields.io/badge/homebrew-available-orange)](https://brew.sh/)

  [🇺🇸 English](README.md) | [🇰🇷 한국어](README-ko.md)
</div>

## 🔍 What is SnapTidy?

**SnapTidy** is a powerful tool for organizing complex directories and removing duplicate files - especially optimized for photos and other media files. Tired of having the same photo downloaded multiple times or photos scattered across dozens of folders? Clean them up easily with SnapTidy.

## 🚀 Quick Start

### For Most Users: GUI Interface (Recommended)

SnapTidy includes a beautiful and intuitive GUI application that makes photo organization effortless!

```bash
# Launch the GUI
snaptidy-gui
```

**Features:**
- 📁 **Drag & Drop**: Simply drag folders into the interface
- ⚙️ **Visual Settings**: Adjust sensitivity, threads, and options with sliders
- 📊 **Real-time Progress**: See exactly what's happening during operations
- 🎨 **Modern Design**: Professional appearance that matches your OS
- 🔄 **Recovery System**: One-click recovery script generation
- 📋 **Logging Mode**: Safe operations with complete recovery capability
- 📱 **Responsive UI**: Scroll support for smaller windows

### For Power Users: Command Line Interface

Advanced users can use the CLI for automation and scripting:

```bash
# Flatten all files into a single directory
snaptidy flatten

# Remove duplicate photos (including similar ones!)
snaptidy dedup --sensitivity 0.9

# Organize photos by shooting date
snaptidy organize --date-format yearmonth
```

## ✨ Key Features

### 📁 Directory Flattening
- Move all files from subdirectories to the current directory
- **Option: Copy all files to a separate 'flattened' folder**
- Smart automatic handling of filename conflicts
- Solve complex nested folder structures with a single command

### 🔍 Smart Duplicate Removal
- Find exact duplicate files using SHA256 hash comparison
- Detect similar photos even if they've been resized or slightly modified
- Adjustable sensitivity level for visual similarity detection
- Always keep the highest quality version of each file
- **New: Move duplicates to a folder instead of deleting them**

### 📅 Date-Based Organization
- Extract creation dates from EXIF data and file metadata
- Automatic folder organization by year or year+month
- Organize photo collections based on when they were taken
- **New: Handle files without date metadata**

### 🔄 Recovery System
- **Complete operation logging** to CSV files for full recovery
- **Recovery script generation** to restore files to their original locations
- **Safe mode** that prevents file deletion and forces move operations
- **Automatic recovery button** in GUI when log files are available

## 🖥️ GUI Usage (For Most Users)

### Launch and Setup
1. **Install SnapTidy** (see installation section below)
2. **Launch GUI**: Run `snaptidy-gui` in your terminal
3. **Select Folder**: Use the folder selector or drag & drop a folder
4. **Configure Settings**: Adjust options using the intuitive controls
5. **Run Operations**: Click individual operation buttons or "Run All"

### GUI Features
- **Modern Interface**: Clean, professional design with drag-and-drop support
- **Visual Progress**: Real-time progress bars and status updates
- **Easy Configuration**: Intuitive controls for all SnapTidy options
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Recovery System**: Built-in recovery button when log files are available
- **Scroll Support**: Handles small window sizes gracefully

### Recovery Workflow
1. **Enable Logging Mode**: Check "📋 작업 로그 기록 (복구 가능)" in GUI
2. **Run Operations**: Execute flatten, dedup, or organize operations
3. **Generate Recovery Script**: Click "🔄 복구" button when available
4. **Execute Recovery**: Run the generated `snaptidy_recovery.py` script

### Safety Features
- **Complete Recoverability**: All operations logged when logging mode is enabled
- **No Data Loss**: File deletion is disabled in logging mode
- **Smart Recovery**: Automatic detection of available log files
- **User Confirmation**: Clear warnings and confirmations before destructive operations

## 💻 CLI Usage (For Power Users)

### Basic Commands

```bash
# Flatten subdirectories into the current directory
snaptidy flatten --path /path/to/folder

# Find and remove duplicate files
snaptidy dedup --path /path/to/folder --sensitivity 0.9

# Organize files by shooting date
snaptidy organize --path /path/to/folder --date-format yearmonth
```

### Advanced Options

| Option | Description |
|--------|-------------|
| `--path` | Target directory (default: current directory) |
| `--dry-run` | Show what would happen without making changes |
| `--log` | Save operation log to file |
| `--logging` | Enable CSV logging for recovery |
| `--sensitivity` | Visual similarity threshold (0.0-1.0) |
| `--threads` | Number of concurrent threads to use |
| `--date-format` | Date-based organization format (`year` or `yearmonth`) |
| `--copy` | Copy files instead of moving (flatten only) |
| `--output` | Output directory for copied files (flatten only) |
| `--duplicates-folder` | Move duplicates to this folder instead of deleting |
| `--unclassified-folder` | Move files without date metadata to this folder |

### New Options

#### Directory Flattening
```bash
# Move all files to the current directory (default)
snaptidy flatten --path /path/to/folder

# Copy all files to a new 'flattened' folder (recommended when you have plenty of disk space)
snaptidy flatten --path /path/to/folder --copy

# Copy all files to a specified folder
snaptidy flatten --path /path/to/folder --copy --output /path/to/output_folder
```

#### Duplicate Handling
```bash
# Delete duplicates (default)
snaptidy dedup --path /path/to/folder

# Move duplicates to a specified folder
snaptidy dedup --path /path/to/folder --duplicates-folder /path/to/duplicates
```

#### Unclassified File Handling
```bash
# Move files without date metadata to 'unclassified' folder
snaptidy organize --path /path/to/folder --unclassified-folder /path/to/unclassified
```

### Disk Space Safety
- When using the `--copy` option, SnapTidy checks available disk space before copying. If space is insufficient, the operation is aborted with a warning.

## 📊 Examples

### Before Organization:
```
Photos/
├── Download/
│   ├── IMG_0123.jpg
│   ├── IMG_0123 (1).jpg (duplicate)
│   └── vacation/
│       ├── IMG_0456.jpg
│       └── IMG_0789.jpg
├── Backup/
│   └── old_photos/
│       ├── IMG_0456.jpg (duplicate)
│       └── IMG_1010.jpg
└── IMG_2000.jpg
```

### After Deduplication and Organization:
```
Photos/
├── 202101/
│   ├── IMG_0123.jpg
│   └── IMG_0789.jpg
├── 202102/
│   └── IMG_1010.jpg 
├── 202112/
│   └── IMG_2000.jpg
└── duplicates/
    ├── IMG_0123 (1).jpg
    └── IMG_0456.jpg
```

## 🚀 Installation

### Using Homebrew (Recommended)

```bash
brew tap yourname/tap
brew install snaptidy
```

### Install from Source

```bash
git clone https://github.com/yourname/snaptidy.git
cd snaptidy
pip install .
```

## 🧩 Technical Overview

SnapTidy is developed in Python and uses the following core technologies:

- **File Hashing**: `hashlib` for accurate duplicate detection
- **Image Analysis**: `imagehash` and `Pillow` for visual image comparison
- **Video Processing**: `opencv-python` and `ffmpeg` for video similarity
- **Metadata Extraction**: `exifread` and `hachoir` for file information parsing
- **Performance Optimization**: `concurrent.futures` for multi-threading
- **GUI Framework**: `PyQt6` for modern cross-platform interface

## 🤝 Contributing

Contributions are always welcome! Check out the [issues page](https://github.com/yourname/snaptidy/issues) for open tasks or submit your ideas.

## 📜 License

SnapTidy is provided under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <i>Made with ❤️ for people who hate messy photo libraries</i>
</div>
