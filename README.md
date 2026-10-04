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
      <img src="https://img.shields.io/badge/Release-v1.0.1-fa7b1e?style=flat-square&labelColor=0d1117" alt="Version 1.0.1" />
    </a>
    <a href="https://opensource.org/licenses/MIT">
      <img src="https://img.shields.io/badge/License-MIT-fa7b1e?style=flat-square&labelColor=0d1117" alt="License MIT" />
    </a>
    <a href="https://mdzobaedislamshanto.supportkori.shop/">
      <img src="https://img.shields.io/badge/⚡%20Fund%20the%20Production-PixelPie%20Media-fa7b1e?style=flat-square&logo=shopware&logoColor=white" alt="Fund the Production" />
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

## 💡 How It Works: Simple & Clear Overview

1. **Why Draft Videos Fail to Play**: When CapCut or JianYing creates temporary draft caches and Pro combination previews, it applies a fast byte-level periodic XOR scramble across slices of the file and attaches a proprietary container trailer. Standard video players (VLC, Windows Media Player, Premiere Pro) see these scrambled headers and report `moov atom not found` or corrupted stream errors.
2. **How the Tool Restores It**: **Export Capcut Pro Video Free** derives the exact mathematical periodic scrambling constraint in milliseconds, reverses the XOR transformation in-place, and normalizes the standard MP4 atoms.
3. **Bitstream-Exact Export (Zero Quality Loss)**: The video is never re-compressed or transcoded. Your original 4K/1080p video frames (AVC/H.264, HEVC) and AAC audio stream are preserved bit-for-bit with 100% original fidelity intact.

---

## 💎 The Four Core Pillars

* **Zero Re-Encoding Loss**: Unlike screen recorders or transcoders that degrade bitrates and introduce generational compression artifacts, this engine mathematically inverts the XOR obfuscation in-place. The exact original H.264 NAL units and AAC audio frames are preserved bit-for-bit.
* **🧠 Smart Project & Clip Name Detection**: CapCut draft caches use opaque GUIDs (e.g. `48C34141-8F08-4483-A597-073963B3DB0A_video.mp4`). Our engine automatically inspects draft project metadata (`draft_meta_info.json`, `draft_content.json`, and CapCut AppData catalogs) to extract your actual CapCut Project Name and timeline clip title, automatically exporting clean human-readable files (e.g., `shining motion u - Compound clip16.mp4`).
* **Zero-Friction Ergonomics**: Engineered for video editors and creators. Features a **native Drag & Drop window**, an **auto-scanning dark-mode desktop GUI**, and an **interactive CLI** that auto-discovers CapCut draft folders without typing paths.
* **100% Local & Offline**: Operates purely within your local machine sandbox using Python's standard library. Zero cloud uploads, zero telemetry, and zero third-party software dependencies.

---

## 🖱️ Three Ways to Use

### Method 1: Instant Windows Drag & Drop (Easiest)
1. Drag any unplayable video file (`*_video.mp4`, `.mov`, `.tmp`, or cache block) onto **`Export-CapCut-Free.bat`** on your Desktop.
2. The engine instantly decrypts the file, checks container atoms, and outputs a clean MP4 right next to the original file.

### Method 2: Modern Dark-Mode GUI (Flagship Visual App)
Double-click **`Export-CapCut-Free.bat`** on your Desktop or run:
```bash
export-capcut-gui
```
The application provides four dedicated workspaces:
* **⚡ Quick Export**: Select any individual cache clip, decrypt in 0.3s, verify MP4 atoms, and optionally auto-play the video immediately.
* **📁 Draft Library**: One-click automatic detection of all CapCut & JianYing projects across your drives with file size, draft project name, and caching timestamps.
* **📦 Batch Queue**: Queue custom folders or multiple clips for automated bulk export.
* **ℹ️ About & Production**: Full architecture specs, developer credits to **Md. Zobaed Islam Shanto**, and a direct **⚡ Fund the Production** button.

### Method 3: Interactive CLI & Arrow-Key Selector
Run without arguments in PowerShell or CMD to automatically scan and interactively browse your recent projects:
```bash
export-capcut-pro-video-free
```
```text
========================================================================
   EXPORT CAPCUT PRO VIDEO FREE  -  INTERACTIVE DRAFT SELECTOR
   Use [UP / DOWN] arrow keys to navigate, [ENTER] to export, [Q] to quit
========================================================================

Detected 14 recent protected CapCut & JianYing draft video(s):

 ▶ [ 1] shining motion u - Compound clip16    43.7 MB  │  1 hr ago    
   [ 2] shining motion u - Compound clip16    28.1 MB  │  1 hr ago    
   [ 3] shining motion u                      28.1 MB  │  1 hr ago    
   [ 4] unn drone m - 547e2aa258e6639f0cb     18.4 MB  │  3 days ago  

------------------------------------------------------------------------
Selected: shining motion u
Material: Compound clip16
Save As:  shining motion u - Compound clip16.mp4
------------------------------------------------------------------------
Press [Enter] to choose destination in Windows Explorer dialog.
```

When you hit `[Enter]`, a **native Windows Explorer "Save As" pop-out dialog (`Ctrl+S` style)** automatically opens, pre-filled with the auto-resolved project name, letting you save your clean MP4 anywhere you want with 100% control!

Or pass flags directly:
```bash
# Export a single video and choose destination via Windows Explorer Save As dialog
export-capcut-pro-video-free "D:\capcut cache\draft\video.mp4" --save-as

# Export a single video directly to a specific destination
export-capcut-pro-video-free "D:\capcut cache\draft\video.mp4" -o "C:\MyVideos\final.mp4"

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
    <img src="assets/brand/logo.png" alt="PixelPie Media Logo" width="180" />
  </a>
  <p style="margin-top: 10px;">
    <b>Export Capcut Pro Video Free</b> is engineered and maintained by <b>PixelPie Media</b>.<br/>
    <i>Founded and developed by <a href="https://github.com/pikadexofc">Md. Zobaed Islam Shanto</a>.</i>
  </p>
  <p>
    <a href="https://mdzobaedislamshanto.supportkori.shop/">
      <img src="https://img.shields.io/badge/⚡%20Fund%20the%20Production-SupportKori-fa7b1e?style=for-the-badge&logo=shopware&logoColor=white" alt="Fund the Production" />
    </a>
  </p>
  <br />
  <img src="assets/brand/colours.png" alt="PixelPie Media Palette" width="100%" height="6" />
</div>
