# Export Capcut Pro Video Free 🎬🔓

[![CI](https://github.com/pikadexofc/export-capcut-pro-video-free/actions/workflows/ci.yml/badge.svg)](https://github.com/pikadexofc/export-capcut-pro-video-free/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)]()

> **Export Capcut Pro Video Free** is a zero-friction recovery and export engine to unlock and export unplayable **CapCut** and **JianYing** draft cache videos (`moov atom not found` / ByteDance `BDVE` Cryptor Type 1). Zero re-encoding, 100% original bitstream quality.

---

## ⚡ Zero-Friction Usage (Pick Your Favorite Way)

No complex terminal commands or video engineering knowledge needed.

### 🖱️ Method 1: Windows 1-Click Launcher & Drag-and-Drop (Easiest)

1. Clone or [download this repo](https://github.com/pikadexofc/export-capcut-pro-video-free/archive/refs/heads/main.zip).
2. **Drag & Drop**: Drag any unplayable CapCut video file and drop it directly onto **`Export-CapCut-Free.bat`**. It will instantly decrypt and open the exported video!
3. **Or Double-Click**: Double-click **`Export-CapCut-Free.bat`** to launch the Dark-Mode Visual App!

---

### 🎨 Method 2: Modern Dark-Mode GUI (Visual App)

Launch the visual desktop interface:

```bash
python -m capcut_cache_recover.gui
# Or after pip install:
export-capcut-gui
```

- **⚡ 1-Click Auto Scan**: Automatically finds all CapCut and JianYing draft cache folders and exports every video to your Desktop.
- **📁 Browse & Export**: Select any individual `.mp4` / `.mov` / `.tmp` video and export it with one click.
- **📂 Open Output Folder**: Instant button to view your rendered MP4s in File Explorer / Finder.

---

### 💻 Method 3: Smart Interactive CLI

Simply run without flags:
```bash
python -m capcut_cache_recover.cli
```
You will be prompted with a zero-friction interactive menu:
```text
[?] No arguments provided. Select an option:
    [1] ⚡ 1-Click Auto Scan & Export All CapCut Drafts Free (Recommended)
    [2] 🎬 Launch Modern Visual GUI
    [3] 📂 Enter a video file path manually
    [4] ❓ View Command Line Help
```

Or pass flags directly:
```bash
# Export a single video
python -m capcut_cache_recover.cli "D:\path\to\encrypted_video.mp4" -o exported.mp4

# Auto-detect and export all CapCut drafts
python -m capcut_cache_recover.cli --auto

# Scan a specific directory
python -m capcut_cache_recover.cli --scan "D:\capcut cache\CapCut Drafts" -o "C:\ExportedVideos"
```

---

## The Problem

Have you ever tried opening a video cached inside CapCut's drafts folder (e.g. `Resources/combination/*_video.mp4` or Pro feature preview scratch files) in VLC, Windows Media Player, QuickTime, Premiere, or FFmpeg, only to get blocked by errors like:

```text
[mov,mp4,m4a,3gp,3g2,mj2 @ 0x...] moov atom not found
Invalid data found when processing input
```

The file exists with its complete multi-megabyte size (e.g. 30MB+), but standard media players cannot open or export it.

### Why Does This Happen?

CapCut and JianYing (ByteDance) protect draft cache clips using a proprietary container obfuscation scheme known as **BDVE (ByteDance Video Encryption) Cryptor Type 1**:
1. **Periodic XOR Masking**: CapCut periodically applies a single-byte XOR mask across slices of the media payload (`mdat`). Every `step` bytes, a block of `length` bytes is scrambled with a `key`.
2. **Proprietary Trailer Box**: A 68-byte custom `bdve` container with a child `crpt` box is appended to the tail of the MP4 file. This box stores the encryption format version and a 32-byte SHA-256 digest:
   $$\text{target} = \text{SHA-256}(\text{step}_{4\text{B}} \parallel \text{length}_{4\text{B}} \parallel \text{key}_{1\text{B}})$$
3. **Container Failure**: Because standard players cannot locate the `moov` atom header through the scrambled blocks and unexpected trailer bytes, playback fails immediately.

---

## ✨ Key Features

- ⚡ **Lightning Fast**: Exports a 30 MB 1080p video in under **0.3 seconds**.
- 💎 **Zero Quality Loss**: Inverts the bitwise scrambling directly. No re-encoding, zero compression artifacts, identical audio/video bitrates.
- 🖱️ **Drag-and-Drop Launcher**: Includes a native Windows `.bat` launcher for 1-second drag-and-drop export.
- 🎨 **Modern Dark-Mode GUI**: Zero external GUI dependencies (built on standard Tkinter).
- 🔍 **Auto-Scan & Batch Export**: Recursively searches disks and draft folders for all encrypted clips.
- 📦 **Zero Third-Party Dependencies**: Written entirely in pure Python standard library (`pathlib`, `struct`, `hashlib`, `tkinter`).
- 🛡️ **Built-in MP4 Validator**: Verifies `ftyp`, `mdat`, `moov`, video resolution, and audio tracks automatically without needing FFmpeg installed.
- 🤖 **Background Daemon Support**: Ships with an autonomous watcher daemon to monitor CapCut folders and auto-export clips as they render.

---

## 💻 Python API Usage

You can also integrate **Export Capcut Pro Video Free** directly into your Python scripts or automation workflows:

```python
from pathlib import Path
from capcut_cache_recover import recover_file
from capcut_cache_recover.validator import validate_mp4

src = Path("encrypted_cache_video.mp4")
dest = Path("exported_video.mp4")

# Export and decrypt the file
params = recover_file(src, dest)
print(f"Exported with key=0x{params.key:02X}, step={params.step}, length={params.length}")

# Validate container integrity
validation = validate_mp4(dest)
if validation.is_valid:
    print(f"Valid MP4! Duration: {validation.duration_seconds}s | Resolution: {validation.video_width}x{validation.video_height}")
```

---

## 🔬 Technical Anatomy: BDVE Container Layout

```
+-----------------------------------------------------------------------+
|  MP4 Header (ftyp, free)  [Partially / fully masked with XOR key]     |
+-----------------------------------------------------------------------+
|  Media Data Payload (mdat)                                            |
|    - Block 0:  [0 : length]  -> XORed with key                        |
|    - Block 0:  [length : step] -> Plaintext unencrypted               |
|    - Block 1:  [step : step + length] -> XORed with key               |
|    - Block 1:  [step + length : 2*step] -> Plaintext unencrypted      |
|    ...                                                                |
+-----------------------------------------------------------------------+
|  Movie Box (moov)  [Plaintext or candidate offset]                    |
+-----------------------------------------------------------------------+
|  ByteDance Trailer Box (bdve) [68 Bytes]                              |
|    ├── Child Atom: 'crpt' (48 bytes)                                  |
|    │     ├── Cryptor Type: 0x00000001 (Type 1 Periodic XOR)           |
|    │     ├── Version:      0x00000003                                 |
|    │     └── SHA-256:      32-byte digest of (step || length || key)  |
|    └── Child Atom: 'size' (12 bytes) -> Total trailer size (68)       |
+-----------------------------------------------------------------------+
```

---

## 🧪 Running Tests

A comprehensive unit test suite is included:

```bash
python -m unittest discover -s tests -v
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) © 2026 Shanto ([@pikadexofc](https://github.com/pikadexofc)).
