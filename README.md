# SnapTidy

<div align="center">
  
  <p align="center">
    <img src="logo.png" alt="SnapTidy logo" width="280"/>
  </p>

  **Clean up your photo library with a single command.**
  
  [![라이선스: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![Python 버전](https://img.shields.io/badge/python-3.7%2B-brightgreen)](https://www.python.org/downloads/)
  [![Homebrew](https://img.shields.io/badge/homebrew-available-orange)](https://brew.sh/)

  [🇺🇸 English](README.md) | [🇰🇷 한국어](README-ko.md)
</div>

## 🔍 What is SnapTidy?

**SnapTidy** is a powerful CLI tool that helps you organize messy directories and remove duplicate files - especially for photos and other media files. Ever downloaded the same photo multiple times or have photos spread across dozens of folders? SnapTidy makes cleaning up a breeze.

```bash
# Flatten all files into one directory
snaptidy flatten

# Remove duplicate photos (even similar ones!)
snaptidy dedup --sensitivity 0.9

# Organize photos by date taken
snaptidy organize --date-format yearmonth
```

## ✨ Key Features

### 📁 Flatten Directories
- Move all files from subdirectories into the current directory
- Automatically handle filename conflicts with smart renaming
- Get rid of complex nested folder structures with one command

### 🔍 Smart Deduplication
- Find and remove exact duplicates using SHA256 hash comparison
- Detect similar photos even if they've been resized or slightly modified
- Choose your sensitivity level for perceptual similarity detection
- Always keeps the highest quality version of each file

### 📅 Date-Based Organization
- Extract creation dates from EXIF data and file metadata
- Automatically sort files into folders by year or year+month
- Restore order to your photo collection based on when the photos were taken

### ⚙️ Flexible Configuration
- Preview changes with `--dry-run` before applying them
- Tune performance with multi-threading support
- Customize organization with multiple date format options

## 🚀 Installation

### Using Homebrew (recommended)

```bash
brew tap yourname/tap
brew install snaptidy
```

### From Source

```bash
git clone https://github.com/yourname/snaptidy.git
cd snaptidy
pip install .
```

## 📋 Usage

```bash
# General usage
snaptidy [command] [options]

# Get help
snaptidy --help
snaptidy [command] --help
```

### Basic Commands

```bash
# Flatten all files from subdirectories into current directory
snaptidy flatten --path /path/to/folder

# Find and remove duplicate files
snaptidy dedup --path /path/to/folder --sensitivity 0.9

# Organize files by date taken
snaptidy organize --path /path/to/folder --date-format yearmonth
```

### Options

| Option | Description |
|--------|-------------|
| `--path` | Target directory (default: current directory) |
| `--dry-run` | Show what would happen without making changes |
| `--log` | Save operation log to a file |
| `--sensitivity` | Perceptual similarity threshold (0.0-1.0) |
| `--threads` | Number of concurrent threads to use |
| `--date-format` | Format for organizing by date (`year` or `yearmonth`) |

## 📊 Examples

### Before:
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

### After deduplication and organization:
```
Photos/
├── 202101/
│   ├── IMG_0123.jpg
│   └── IMG_0789.jpg
├── 202102/
│   └── IMG_1010.jpg 
└── 202112/
    └── IMG_2000.jpg
```

## 🧩 Technical Overview

SnapTidy is built with Python and uses these core technologies:

- **File Hashing**: `hashlib` for exact duplicate detection
- **Image Analysis**: `imagehash` and `Pillow` for perceptual image comparison
- **Video Processing**: `opencv-python` and `ffmpeg` for video similarity
- **Metadata Extraction**: `exifread` and `hachoir` for parsing file information
- **Performance**: `concurrent.futures` for multi-threading

## 🤝 Contributing

Contributions are welcome! Check out the [issues page](https://github.com/yourname/snaptidy/issues) for open tasks or submit your own ideas.

## 📜 License

SnapTidy is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <i>Made with ❤️ for people who hate messy photo libraries</i>
</div>
