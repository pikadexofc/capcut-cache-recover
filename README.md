# Export Capcut Pro Video Free 🎬🔓

[![CI](https://github.com/pikadexofc/export-capcut-pro-video-free/actions/workflows/ci.yml/badge.svg)](https://github.com/pikadexofc/export-capcut-pro-video-free/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)]()

> **Export Capcut Pro Video Free** is a high-performance open-source recovery and export engine to decrypt, unlock, and export unplayable **CapCut** and **JianYing** draft cache videos (`moov atom not found` / ByteDance `BDVE` Cryptor Type 1). Zero re-encoding, 100% original bitstream quality.

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

## The Solution: Export Capcut Pro Video Free

**Export Capcut Pro Video Free** mathematically solves the exact `(step, length, key)` tuple by:
1. Parsing the raw MP4 container structures and locating valid H.264 NAL units (SPS, PPS, IDR slices).
2. Setting up a constraint satisfaction solver on the modulo offsets:
   $$\text{low} = \max(\text{remainder} + 1), \quad \text{high} = \min(\text{remainder})$$
3. Verifying the derived parameters against the file's embedded SHA-256 footer hash.
4. Performing a zero-copy periodic bitwise XOR inversion and stripping the proprietary `bdve` trailer.

**Result**: 100% clean, standard MP4 video rendered without paying or needing CapCut's export gate.

---

## ✨ Features

- ⚡ **Lightning Fast**: Exports a 30 MB 1080p video in under **0.3 seconds**.
- 💎 **Zero Quality Loss**: Inverts the bitwise scrambling directly. No re-encoding, zero compression artifacts, identical audio/video bitrates.
- 🔍 **Auto-Scan & Batch Export**: Recursively searches your disks and draft folders for all encrypted clips.
- 📦 **Zero Third-Party Dependencies**: Written entirely in pure Python standard library (`pathlib`, `struct`, `hashlib`, `argparse`).
- 🛡️ **Built-in MP4 Validator**: Verifies `ftyp`, `mdat`, `moov`, video resolution, and audio tracks automatically without needing FFmpeg installed.
- 🤖 **Background Daemon Support**: Ships with an autonomous watcher daemon to monitor CapCut folders and auto-export clips as they render.

---

## 🚀 Quick Start

### 1. Installation

Clone the repository:
```bash
git clone https://github.com/pikadexofc/export-capcut-pro-video-free.git
cd export-capcut-pro-video-free
```

(Optional) Install in editable mode:
```bash
pip install -e .
```

### 2. Basic CLI Usage

#### Export a Single Video Free
```bash
python -m capcut_cache_recover.cli "D:\path\to\encrypted_video.mp4" -o exported.mp4
# Or after pip install:
export-capcut-pro-video-free "D:\path\to\encrypted_video.mp4" -o exported.mp4
```

#### Automatically Detect and Export All CapCut Drafts
```bash
export-capcut-pro-video-free --auto
```
*Automatically searches standard CapCut and JianYing draft paths on Windows & macOS.*

#### Scan a Specific Directory
```bash
export-capcut-pro-video-free --scan "D:\capcut cache\CapCut Drafts" -o "C:\ExportedVideos"
```

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
