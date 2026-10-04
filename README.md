<div align="center">
  <a href="https://github.com/pikadexofc">
    <img src="assets/brand/logo.png" alt="PixelPie Media Logo" width="240" />
  </a>
  <br /><br />
  <h1>CapCut Cache Recover 🎬🛠️</h1>
  <p><strong>A precision forensic stream repair and data recovery engine to restore corrupted or unfinalized CapCut & JianYing local draft video caches with bitstream-exact fidelity.</strong></p>

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

## 💡 How It Works: Technical Overview

1. **Why Draft Videos Fail to Play**: When CapCut or JianYing writes temporary editing caches and compound clip previews, it applies a fast byte-level periodic XOR obfuscation across slices of the media payload (`mdat`) and appends a 68-byte proprietary `bdve` container trailer. Standard video players (VLC, Windows Media Player, QuickTime) see the obfuscated file headers and fail with `moov atom not found` or corrupted container errors.
2. **How the Recovery Engine Restores It**: **CapCut Cache Recover** derives the exact mathematical periodic scrambling constraint parameters (`step`, `length`, `key`) in milliseconds, reverses the XOR transformation in-place, and restores standard ISO Base Media File Format atoms.
3. **Bitstream-Exact Restoration (Zero Re-Encoding Loss)**: The video is never re-compressed or transcoded. Your original 4K/1080p video frames (AVC/H.264, HEVC) and AAC audio stream are salvaged bit-for-bit with 100% original fidelity intact.

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
* **⚡ Quick Export**: Select any individual cache clip, restore in 0.3s, verify MP4 atoms, and optionally preview the video immediately.
* **📁 Draft Library**: One-click automatic detection of all CapCut & JianYing projects across your drives with file size, draft project name, and caching timestamps.
* **📦 Batch Queue**: Queue custom folders or multiple clips for automated bulk recovery.
* **ℹ️ About & Production**: Architecture specifications, developer credits to **Md. Zobaed Islam Shanto**, and a direct **⚡ Fund the Production** button.

### Method 3: Interactive CLI & Arrow-Key Selector
Run without arguments in PowerShell or CMD to automatically scan and interactively browse your recent projects:
```bash
export-capcut-pro-video-free
```
```text
========================================================================
   CAPCUT CACHE RECOVER  -  INTERACTIVE DRAFT SELECTOR
   Use [UP / DOWN] arrow keys to navigate, [ENTER] to recover, [Q] to quit
========================================================================

Detected 14 recent CapCut & JianYing draft video cache(s):

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
# Recover a single video and choose destination via Windows Explorer Save As dialog
export-capcut-pro-video-free "D:\capcut cache\draft\video.mp4" --save-as

# Recover a single video directly to a specific destination
export-capcut-pro-video-free "D:\capcut cache\draft\video.mp4" -o "C:\MyVideos\recovered.mp4"

# Auto-detect and recover all CapCut drafts across all drives
export-capcut-pro-video-free --auto

# Recursively scan a custom directory
export-capcut-pro-video-free --scan "D:\custom_cache" -o "C:\RecoveredVideos"
```

---

## 📱 Mobile Support (Android & Termux)

### Termux (Android CLI)
Install and run natively on Android in Termux with one command:
```bash
pkg install curl -y && curl -sL https://raw.githubusercontent.com/pikadexofc/export-capcut-pro-video-free/main/install-termux.sh | bash
```

---

## 🐍 Python Developer API

Integrate the recovery engine directly into your own video pipelines:

```python
from capcut_cache_recover.core import recover_file
from capcut_cache_recover.atom import validate_mp4

src = r"C:\Users\User\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\Draft\Resources\combination\clip_video.mp4"
dest = r"C:\Recovered\clip_recovered.mp4"

# Recover stream
params = recover_file(src, dest)
print(f"Recovered: key=0x{params.key:02X}, step={params.step}, length={params.length}")

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

## ⚖️ Legal Disclaimer & Safe Harbor Compliance

1. **Forensic Research & Data Recovery Only**: This software is an independent research project and data recovery tool created strictly to assist video editors, forensic researchers, and content creators in recovering their own locally stored, corrupted, or unfinalized media cache streams generated during desktop editing crashes or interrupted export sessions.
2. **No Circumvention or Piracy**: This software does NOT alter, modify, hook, tamper with, crack, or bypass ByteDance's licensing, subscription validation, or authentication mechanisms. It operates exclusively on locally stored cache files created on the user's local machine.
3. **User Ownership**: Users are solely responsible for ensuring they possess lawful ownership or copyright authorization over any video files, media clips, or assets they process with this software.
4. **Trademarks**: "CapCut" and "JianYing" are registered trademarks of ByteDance Ltd. This open-source utility is not affiliated with, endorsed by, sponsored by, or connected to ByteDance Ltd. or its subsidiaries.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) © 2026 Shanto ([@pikadexofc](https://github.com/pikadexofc)).

---

<div align="center">
  <a href="https://github.com/pikadexofc">
    <img src="assets/brand/logo.png" alt="PixelPie Media Logo" width="180" />
  </a>
  <p style="margin-top: 10px;">
    <b>CapCut Cache Recover</b> is engineered and maintained by <b>PixelPie Media</b>.<br/>
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
