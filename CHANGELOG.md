# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-XX

### Added
- **Complete SnapTidy system** with both GUI and CLI interfaces
- **CSV logging system** with recovery script generation for full recoverability
- **Safe mode** with file deletion prevention and move-only operations
- **Modern PyQt6 GUI** with drag-and-drop interface and real-time progress tracking
- **Smart duplicate detection** using SHA256 hashing and visual similarity comparison
- **Date-based file organization** with EXIF metadata extraction
- **Disk space safety checks** when copying files
- **Cross-platform support** (Windows, macOS, Linux)
- **Comprehensive CLI** with advanced options for power users
- **Recovery system** with automatic log file detection and script generation
- **User-friendly documentation** with separate sections for GUI and CLI users

### Features
- **Directory Flattening**: Move or copy files from nested directories to a single location
- **Duplicate Removal**: Find and remove exact duplicates or visually similar files
- **Date Organization**: Organize files by year or year+month based on creation date
- **Logging Mode**: Complete operation tracking with CSV logs and recovery scripts
- **Safety Options**: Move duplicates to folders instead of deletion
- **Unclassified File Handling**: Store files without date metadata in separate folders

### Technical
- **Multi-threading support** for improved performance
- **Configurable sensitivity** for visual similarity detection
- **Automatic filename conflict resolution**
- **Real-time progress tracking** in GUI
- **Responsive UI** with scroll support for smaller windows
- **Modular architecture** with separate modules for each operation

### Documentation
- **User-type separated README**: GUI-first for most users, CLI for power users
- **Bilingual support**: English and Korean documentation
- **Comprehensive examples** and usage scenarios
- **Safety guidelines** and best practices

### Beta Notes
This is the first beta release of SnapTidy. The core functionality is complete and tested, but user feedback is welcome for future improvements.

**Known Limitations:**
- GUI may require additional testing on different OS configurations
- Some edge cases in file organization may need refinement
- Performance optimization for very large directories is ongoing

**Next Steps:**
- User feedback collection and bug reports
- Performance optimization
- Additional file format support
- Enhanced GUI features based on user requests
