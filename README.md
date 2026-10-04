<div align="center">
  <a href="https://github.com/pikadexofc">
    <img src="assets/brand/logo.png" alt="PixelPie Media Logo" width="240" />
  </a>
  <br /><br />
  <h1>Export Capcut Pro Video Free 🎬🔓</h1>
  <p><strong>A precision cryptographic recovery and export engine that decrypts, unlocks, and exports unplayable CapCut & JianYing draft cache videos with zero re-encoding loss.</strong></p>

  <p>
    <a href="https://github.com/pikadexofc/export-capcut-pro-video-free/actions">
      <img src="https://img.shields.io/github/actions/workflow/status/pikadexofc/export-capcut-pro-video-free/ci.yml?branch=main&label=CI&style=flat-square&color=fa7b1e&labelColor=0d1117" alt="CI Status" />
    </a>
    <a href="https://github.com/pikadexofc/export-capcut-pro-video-free/releases">
      <img src="https://img.shields.io/badge/Release-v1.0.0-fa7b1e?style=flat-square&labelColor=0d1117" alt="Version 1.0.0" />
    </a>
    <a href="https://opensource.org/licenses/MIT">
      <img src="https://img.shields.io/badge/License-MIT-fa7b1e?style=flat-square&labelColor=0d1117" alt="License MIT" />
    </a>
    <img src="https://img.shields.io/badge/Dependencies-0%20(Pure%20Python)-10b981?style=flat-square&labelColor=0d1117" alt="Zero Dependencies" />
    <img src="https://img.shields.io/badge/Privacy-100%25%20Local-10b981?style=flat-square&labelColor=0d1117" alt="100% Local" />
  </p>
</div>

<div align="center">
  <img src="assets/brand/colours.png" alt="PixelPie Media Palette" width="100%" height="6" />
</div>

---

## ⚡ Quick Install (Windows PowerShell)

Run this one-liner in PowerShell to download, configure the desktop drag-and-drop launcher, and register system-wide CLI commands automatically:

```powershell
irm https://raw.githubusercontent.com/pikadexofc/export-capcut-pro-video-free/main/install.ps1 | iex
```

---

## 💎 The Three Core Pillars

* **Zero Re-Encoding Loss**: Unlike screen recorders or transcoders that degrade bitrates and introduce generational compression artifacts, this engine mathematically inverts the XOR obfuscation in-place. The exact original H.264 NAL units and AAC audio frames are preserved bit-for-bit.
* **Zero-Friction Ergonomics**: Engineered for video editors and creators. Features a **1-second Windows Drag & Drop launcher**, an **auto-scanning dark-mode desktop GUI**, and an **interactive CLI** that auto-discovers CapCut draft folders without typing paths.
* **100% Local & Offline**: Operates purely within your local machine sandbox using Python's standard library. Zero cloud uploads, zero telemetry, and zero third-party software dependencies.

---

## 🖱️ Three Ways to Use

### Method 1: Instant Windows Drag & Drop (Easiest)
1. Drag any unplayable video file (`*_video.mp4`, `.mov`, `.tmp`, or cache block) onto **`Export-CapCut-Free.bat`** on your Desktop.
2. The engine instantly decrypts the file, checks container atoms, and outputs a clean MP4 right next to the original file.

### Method 2: Modern Dark-Mode GUI (Visual App)
Double-click **`Export-CapCut-Free.bat`** or run:
```bash
export-capcut-gui
```
* **⚡ 1-Click Auto Scan**: Recursively searches all local and external drives for CapCut / JianYing draft cache folders and exports every video to your Desktop.
* **📁 Single File Export**: Browse to any draft clip and click **Export Video**. Includes an option to auto-play upon completion.
* **📂 Open Output Folder**: Instant button to reveal exported files in File Explorer.

### Method 3: Smart Interactive CLI
Run without arguments to access the guided menu:
```bash
export-capcut-pro-video-free
```
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
export-capcut-pro-video-free "D:\capcut cache\draft\video.mp4" -o exported.mp4

# Auto-detect and export all CapCut drafts across all drives
export-capcut-pro-video-free --auto

# Recursively scan a custom directory
export-capcut-pro-video-free --scan "D:\custom_cache" -o "C:\ExportedVideos"
```

---

## 🔍 The Problem & Cryptographic Root Cause

When CapCut or JianYing (ByteDance) caches draft timelines, combination effects, or Pro feature previews, the files are written with full size on disk (e.g. 30MB–1GB+), but attempting to open them in VLC, Premiere, DaVinci Resolve, QuickTime, or FFmpeg yields:

```text
[mov,mp4,m4a,3gp,3g2,mj2 @ 0x...] moov atom not found
Invalid data found when processing input
```

### Why Standard Media Demuxers Fail

ByteDance applies **BDVE (ByteDance Video Encryption) Cryptor Type 1** to scratch and cache media:
1. **Periodic XOR Masking**: CapCut periodically applies a single-byte XOR mask across slices of the media payload (`mdat`). Every `step` bytes, a block of `length` bytes is scrambled with a `key`.
2. **Proprietary Trailer Box**: A 68-byte custom `bdve` container with a child `crpt` box is appended to the tail of the MP4 file. This box stores the encryption format version and a 32-byte SHA-256 digest:
   $$\text{target} = \text{SHA-256}(\text{step}_{4\text{B}} \parallel \text{length}_{4\text{B}} \parallel \text{key}_{1\text{B}})$$
3. **Container Failure**: Because standard players cannot locate the `moov` atom header through the scrambled blocks and unexpected trailer bytes, playback fails immediately.

---

## 🔬 How the Cryptanalysis Engine Works

```
+-----------------------------------------------------------------------------------+
|  Raw Cache File (BDVE Obfuscated)                                                 |
|    ├── ftyp / free [XOR masked with key]                                          |
|    ├── mdat [Periodic XOR: step bytes cadence, length bytes encrypted]            |
|    ├── moov [Plaintext metadata: stsz, stsc, stco sample tables]                  |
|    └── bdve trailer (68B) [crpt box: contains target SHA-256 digest]              |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|  Parameter Constraint Solver (capcut_cache_recover/cryptor.py)                    |
|    1. Parse moov atom candidate offsets & extract H.264 video sample offsets      |
|    2. Score H.264 NAL units (SPS, PPS, IDR slices) under XOR vs raw state         |
|    3. Establish mathematical modulo constraint system:                            |
|          low = max(pos % step + 1),  high = min(pos % step)                       |
|    4. Verify candidates: SHA-256(step || length || key) == target_sha256         |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|  Decryption & Container Normalization                                             |
|    1. Bitwise in-place XOR inversion across matched slice offsets                 |
|    2. Strip 68-byte proprietary 'bdve' trailer                                    |
|    3. Zero-reencode MP4 output with 100% original AVC + AAC bitstreams           |
+-----------------------------------------------------------------------------------+
```

---

## ⚙️ Technical Specifications

| Attribute | Specification |
| :--- | :--- |
| **Engine Core** | Pure Python 3.9+ (`pathlib`, `struct`, `hashlib`) |
| **Cryptor Target** | ByteDance BDVE Type 1 (Periodic XOR Masking) |
| **Throughput** | ~100 MB/s single-threaded bitwise stream inversion |
| **Re-encoding** | **0% (Bitstream-exact original copy)** |
| **Container Support** | MP4, MOV, ISO Base Media File Format |
| **Codecs Supported** | H.264 / AVC, H.265 / HEVC, AAC LC, MP3 |
| **Platforms** | Windows 10/11, macOS (Apple Silicon & Intel), Linux |
| **GUI Framework** | Native Tkinter (Zero external GUI frameworks needed) |

---

## 🛠️ Python Programmatic API

Embed the engine directly into automated editing pipelines or microservices:

```python
from pathlib import Path
from capcut_cache_recover import recover_file
from capcut_cache_recover.validator import validate_mp4

src = Path("D:/capcut cache/draft_video.mp4")
dest = Path("C:/Exported/output.mp4")

# Export and decrypt
params = recover_file(src, dest)
print(f"Decrypted: key=0x{params.key:02X}, step={params.step}, length={params.length}")

# Validate MP4 atoms
result = validate_mp4(dest)
if result.is_valid:
    print(f"Valid Video: {result.duration_seconds}s | {result.video_width}x{result.video_height}")
```

---

## 🧪 Verification & Test Suite

The repository includes automated unit tests covering cryptographic parameter derivation, synthetic container detection, and atom validation:

```bash
python -m unittest discover -s tests -v
```

All pushes and pull requests are verified via continuous integration matrix testing across Ubuntu, macOS, and Windows.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) © 2026 Shanto ([@pikadexofc](https://github.com/pikadexofc)).

---

<div align="center">
  <a href="https://github.com/pikadexofc">
    <img src="assets/brand/logo.png" alt="PixelPie Media Logo" width="160" />
  </a>
  <p style="margin-top: 8px;"><b>Export Capcut Pro Video Free</b> is engineered and maintained by <b>PixelPie Media</b>.</p>
  <p><i>Precision software engineering, spatial design, and local-first privacy systems.</i></p>
  <br />
  <img src="assets/brand/colours.png" alt="PixelPie Media Palette" width="100%" height="6" />
</div>
