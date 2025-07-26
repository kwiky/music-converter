# FLAC to Opus Album Converter

A Python script designed to efficiently convert FLAC audio files to Opus format while maintaining your music collection's organization structure.

## 🎵 Overview

This tool scans your music collection for albums containing FLAC files, allows you to select multiple albums for batch conversion, and automatically converts them to high-quality Opus format (stereo, 160kbps). After successful conversion, original FLAC files and macOS metadata files are automatically cleaned up.

## 📁 Collection Structure

The script is designed to work with the following music collection structure:

```
Music Root/
├── A/                                    # Artist names starting with 'A'
│   └── Artist Name - [YEAR] Album Name/
│       ├── 01-Track Name.flac
│       ├── 02-Track Name.flac
│       └── cover.jpg
├── B/                                    # Artist names starting with 'B'
│   └── Another Artist - [2023] Album/
└── ...
```

## ✨ Features

- **🔍 Smart Discovery**: Automatically scans your entire music collection to find albums with FLAC files
- **📋 Interactive Selection**: Choose multiple albums using flexible selection formats (`1,3,5` or `1-5` or `all`)
- **🎧 High-Quality Conversion**: Converts to Opus format at 160kbps in stereo
- **⚡ Multi-threaded**: Uses 4 concurrent threads for faster conversion
- **🧹 Automatic Cleanup**: Removes original FLAC files and macOS metadata files (`._*`) after successful conversion
- **📊 Disk Space Monitoring**: Shows disk usage before and after conversions
- **🔄 Continuous Workflow**: Option to convert additional albums in the same session
- **⚠️ Error Handling**: Keeps original files if any conversion fails
- **📈 Progress Tracking**: Detailed progress and results for each album

## 🛠️ Requirements

### System Requirements
- Python 3.6+
- macOS, Linux, or Windows

### Dependencies
- **opus-tools**: Required for FLAC to Opus conversion

#### Installation on macOS:
```bash
brew install opus-tools
```

#### Installation on Ubuntu/Debian:
```bash
sudo apt install opus-tools
```

## 🚀 Usage

### Quick Start

1. **Navigate to your music directory**:
   ```bash
   cd "~/my_music"
   ```

2. **Run the script**:
   ```bash
   ./convert_flac_to_opus.sh
   ```
   
   Or directly with Python:
   ```bash
   python3 flac_to_opus_converter.py
   ```

### Selection Examples

When prompted to select albums, you can use:

- **Individual albums**: `1,3,5` - Selects albums 1, 3, and 5
- **Range selection**: `1-10` - Selects albums 1 through 10  
- **Mixed selection**: `1,5-8,12` - Selects album 1, albums 5-8, and album 12
- **All albums**: `all` - Selects all albums with FLAC files

### Sample Session

```
FLAC to Opus Album Converter
========================================
Found opus encoder: opusenc

Scanning for albums with FLAC files...

Found 25 albums with FLAC files:

#    FLAC Files   Album Path
--------------------------------------------------------------------------------
1    12           A/Artist Name - [2023] Album Name
2    8            B/Band Name - [2022] Another Album
3    15           C/Composer - [2021] Classical Work

📊 Disk Space Information:
   Total: 512.0 GB
   Used:  328.5 GB (64.2%)
   Free:  183.5 GB

Select albums to convert (1-25):
Examples: '1,3,5' or '1-5' or '1,3-7,10' or 'all'
Selection: 1,2

Selected 2 albums:
  - A/Artist Name - [2023] Album Name (12 FLAC files)
  - B/Band Name - [2022] Another Album (8 FLAC files)

Proceed with conversion? (Y/n): 

============================================================
STARTING CONVERSION PROCESS
============================================================

[1/2] Processing: A/Artist Name - [2023] Album Name
Converting 12 FLAC files to Opus...
  ✓ Converted: 01-Track.flac
  ✓ Converted: 02-Track.flac
  ...
  Results: 12 converted, 0 failed, 0 skipped
  Deleting original FLAC files...
    Deleted: 01-Track.flac
    Deleted: 02-Track.flac
    ...
  Cleaning up macOS metadata files...
    Deleted: ._01-Track.flac
    Deleted: ._02-Track.flac

============================================================
CONVERSION COMPLETE
============================================================
Successfully processed: 2/2 albums

📊 Disk Space Information:
   Total: 512.0 GB
   Used:  312.1 GB (61.0%)
   Free:  199.9 GB

Would you like to convert more albums? (Y/n): n
```

## 🔧 Technical Details

### Audio Conversion Settings
- **Format**: Opus
- **Bitrate**: 160 kbps
- **Channels**: Stereo (downmixed from multi-channel if needed)
- **Quality**: High-quality compression optimized for music

### File Management
- **Safety**: Original FLAC files are only deleted after successful conversion
- **Cleanup**: Automatically removes macOS metadata files (`._*` pattern)
- **Error Handling**: If any file fails to convert, all FLAC files in that album are preserved

### Performance
- **Multi-threading**: Up to 4 concurrent conversions per album
- **Memory Efficient**: Processes one album at a time
- **Progress Tracking**: Real-time feedback on conversion progress

## 📋 Supported Formats

### Input Formats
- FLAC (primary target)
- The script specifically looks for `.flac` files

### Output Format
- Opus (`.opus` extension)
- 160 kbps stereo quality

## 🛡️ Safety Features

- **Non-destructive by default**: Original files kept until conversion succeeds
- **Verification**: Only deletes FLAC files after successful Opus creation
- **Error resilience**: Failed conversions don't affect successful ones
- **User confirmation**: Always asks before proceeding with conversions

## 📝 Files Included

- `flac_to_opus_converter.py` - Main Python script
- `convert_flac_to_opus.sh` - Shell wrapper script for easy execution
- `README.md` - This documentation file

## 🐛 Troubleshooting

### Common Issues

**"opusenc not found" error:**
- Install opus-tools using your system's package manager
- Ensure `opusenc` is in your system PATH

**"Permission denied" errors:**
- Make sure scripts are executable: `chmod +x *.sh *.py`
- Check file permissions in your music directory

**Disk space issues:**
- Monitor the disk space information shown by the script
- Ensure sufficient free space for temporary files during conversion

### Getting Help

If you encounter issues:
1. Check that all dependencies are installed
2. Verify your music collection follows the expected structure
3. Ensure you have write permissions to the music directory

## 📊 Performance Notes

- **Speed**: Conversion speed depends on your CPU and disk I/O
- **Space**: Opus files are typically 60-80% smaller than FLAC
- **Quality**: 160kbps Opus provides excellent quality for most music
- **Efficiency**: Multi-threading maximizes modern CPU usage

---

*This tool is designed specifically for the organized music collection structure described above and optimized for batch conversion workflows.*