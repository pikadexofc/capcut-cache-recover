# Community Outreach & Social Distribution Drafts

---

## 1. Reddit: r/CapCut

**Target Subreddit**: [r/CapCut](https://www.reddit.com/r/CapCut/)  
**Flair**: Discussion / Tutorial / Help  
**Title**: How to export and recover your CapCut draft videos if Pro features lock you out (Free & Open Source)

**Post Body**:
Hey everyone,

If you've been working on a project in CapCut Desktop and accidentally used a Pro feature (or your trial ended) and CapCut refuses to let you export without paying:

CapCut **already renders your full video in full resolution** into your local draft folder while you're editing!

However, ByteDance intentionally encrypts these preview/cache files (`*_video.mp4` inside `Resources/combination` or `Resources/videoAlg`) using a periodic XOR scrambling scheme called **BDVE Cryptor Type 1**. If you try playing them in VLC or importing them into Premiere, you get `moov atom not found` or corrupted media errors.

I reverse-engineered the exact scrambling math and built a 100% free and open-source tool: **Export Capcut Pro Video Free**.

### What It Does:
- **0% Quality Loss**: Mathematically reverses the XOR scramble in milliseconds. It does NOT screen-record or re-encode; your original 4K/1080p bitstream and audio frames are 100% intact.
- **Smart Project Detection**: Automatically reads your draft files to detect your actual project name and clip title instead of weird random GUIDs like `48C34141-8F08-4483...mp4`.
- **Interactive Terminal + Desktop GUI**: Includes an interactive terminal arrow-key picker (`[↑ / ↓]`) and a full dark-mode desktop app with drag-and-drop.
- **Save Anywhere**: Lets you choose where to save via a standard Windows Explorer Save As dialog (`Ctrl+S` style).
- **100% Offline & Private**: Zero telemetry, zero uploads, runs completely on your local machine.

### Quick Install (PowerShell):
```powershell
irm https://raw.githubusercontent.com/pikadexofc/export-capcut-pro-video-free/main/install.ps1 | iex
```

Or download the standalone `.exe` (no Python needed) from GitHub Releases:  
🔗 **GitHub Repository & Releases**: https://github.com/pikadexofc/export-capcut-pro-video-free

Hope this helps anyone who got stuck or lost access to an important edit!

---

## 2. Reddit: r/VideoEditing

**Target Subreddit**: [r/VideoEditing](https://www.reddit.com/r/VideoEditing/)  
**Flair**: Technical / Tools  
**Title**: Reverse-engineering ByteDance's BDVE Type 1 video encryption: Recovering "moov atom not found" CapCut draft caches

**Post Body**:
Hi all,

I recently analyzed how CapCut / JianYing stores scratch media and combination clips on disk. 

When CapCut creates a cached draft or combination clip, the files often take up their full size on disk (e.g. 500 MB–1 GB), but fail to open in VLC or FFmpeg with:
`[mov,mp4 @ 0x...] moov atom not found`

### Cryptographic Breakdown:
ByteDance applies **BDVE Cryptor Type 1**:
1. It applies a periodic single-byte XOR mask across slices of the `mdat` container. Every `step` bytes, a block of `length` bytes is XOR'd with a `key`.
2. It appends a 68-byte custom trailer (`bdve` container with a `crpt` box) containing format metadata and a 32-byte SHA-256 verification hash:
   `SHA-256(step || length || key)`
3. Standard demuxers fail because the initial `ftyp` box and NAL headers are scrambled and the trailer confuses container atom parsers.

### Solution:
By reading the plaintext `moov` atom sample table offsets (`stco`/`co64`), scoring candidate H.264 NAL units (SPS, PPS, IDR slices), and establishing a modulo constraint solver, the exact `(step, length, key)` can be derived in ~0.2 seconds.

I packaged this into a pure Python solver and standalone Windows executable with both an interactive terminal interface and visual GUI:
https://github.com/pikadexofc/export-capcut-pro-video-free

Because it inverts the XOR in-place rather than transcoding through FFmpeg, throughput exceeds 100 MB/s and the original AVC/HEVC and AAC bitstreams remain mathematically bit-exact.

---

## 3. Hacker News: Show HN

**Title**: Show HN: Export Capcut Pro Video Free – Reverse-engineering CapCut's BDVE cryptor

**URL**: https://github.com/pikadexofc/export-capcut-pro-video-free

**Comment**:
ByteDance video editors (CapCut, JianYing) store rendered draft cache videos on disk, but protect them using an obfuscation scheme called BDVE Cryptor Type 1 (periodic XOR masking across slices with a 68-byte trailing metadata atom). Standard media demuxers (FFmpeg, VLC) fail with `moov atom not found`.

I built an open-source tool that analyzes H.264 NAL unit sample tables, solves the modulo constraint system to recover the periodic scrambling parameters in milliseconds, and restores clean, bitstream-exact MP4 files with zero transcoding loss.

Features:
- Pure Python core (zero dependencies).
- Standalone Windows binary (12 MB) and drag-and-drop launcher.
- Interactive console with arrow-key navigation (`↑ / ↓`) and native Windows Explorer "Save As" pop-out dialog.
- Automatically resolves CapCut project and timeline clip names from internal metadata.

Code & releases: https://github.com/pikadexofc/export-capcut-pro-video-free
