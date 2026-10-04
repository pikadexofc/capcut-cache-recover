---
title: "Reverse Engineering CapCut's Encrypted Video Cache (BDVE Type 1) and Building an Open-Source Solver"
published: true
description: "A deep dive into ByteDance's BDVE Type 1 periodic XOR obfuscation, why standard media demuxers fail with 'moov atom not found', and how to recover bitstream-exact MP4s in pure Python."
tags: reverseengineering, python, video, opensource
canonical_url: https://github.com/pikadexofc/export-capcut-pro-video-free
cover_image: https://raw.githubusercontent.com/pikadexofc/export-capcut-pro-video-free/main/assets/brand/colours.png
---

If you've ever inspected the local draft directory of CapCut or JianYing (ByteDance's video editors), you might have noticed video cache files taking up hundreds of megabytes in folders like `Resources/combination` or `Resources/videoAlg`.

Naturally, you might try opening one with VLC, QuickTime, or running:

```bash
ffmpeg -i 48C34141-8F08-4483-A597-073963B3DB0A_video.mp4 output.mp4
```

Only to be greeted by this demuxer error:

```text
[mov,mp4,m4a,3gp,3g2,mj2 @ 0x7fa2b00] moov atom not found
Invalid data found when processing input
```

The file size on disk is complete (e.g. 50 MB, 1 GB), yet neither VLC nor FFmpeg can parse even a single valid packet.

Here is the technical story of how I reverse-engineered ByteDance's proprietary **BDVE Type 1** obfuscation scheme and created **[CapCut Cache Recover](https://github.com/pikadexofc/export-capcut-pro-video-free)**—a 100% pure Python forensic stream recovery engine and graphical suite that restores original bitstreams with **0% re-encoding quality loss** in under 0.3 seconds.

---

### The Investigation: Dissecting the ByteStream

When inspecting the hex headers of an ISO Base Media File Format (MP4/MOV) container, you normally expect to see an initial `ftyp` box:

```text
Offset 0x00:  00 00 00 20 66 74 79 70 69 73 6F 6D ...
              [Size: 32 ] [ 'ftyp'    ] [ 'isom'     ]
```

However, examining a CapCut combination clip revealed unexpected bytes at offset 0:

```text
Offset 0x00:  3B 3B 3B 1B 5D 4F 42 4B ...
```

Notice the pattern: `3B 3B 3B`. If we compute a bitwise XOR with `0x3B`:

```text
3B ^ 3B = 0x00
3B ^ 3B = 0x00
3B ^ 3B = 0x00
1B ^ 3B = 0x20  (32 in decimal!)
5D ^ 3B = 0x66  ('f')
4F ^ 3B = 0x74  ('t')
42 ^ 3B = 0x79  ('y')
4B ^ 3B = 0x70  ('p')
```

The XOR mask is clearly `0x3B`! Decrypting the first 8 bytes reveals the standard `ftyp` header.

But ByteDance didn't just XOR the entire file with `0x3B`. Attempting a naive full-file XOR corrupted the file worse.

---

### Understanding BDVE Cryptor Type 1

ByteDance applies **periodic XOR slicing**:

1. **Periodic Cadence**: Every `step` bytes along the media payload (`mdat`), a slice of `length` bytes is scrambled with a single-byte `key`.
2. **Plaintext Gaps**: The bytes between slices remain unencrypted plaintext.
3. **The Proprietary Trailer**: At the very end of the file, ByteDance appends a 68-byte custom container containing a `bdve` box and a child `crpt` box:

```text
+-----------------------+--------+------------------------------------+
| Field                 | Size   | Value / Description                |
+-----------------------+--------+------------------------------------+
| Box Size              | 4B     | 0x00000044 (68 bytes)              |
| Box Type              | 4B     | 'bdve'                             |
| Sub-box Size          | 4B     | 0x0000003C (60 bytes)              |
| Sub-box Type          | 4B     | 'crpt'                             |
| Version               | 4B     | 0x00000001 (Type 1 Cryptor)        |
| Algorithm ID          | 4B     | 0x00000001 (Periodic XOR)          |
| Reserved / Salt       | 16B    | Implementation parameters          |
| Verification SHA-256  | 32B    | SHA-256(step || length || key)     |
+-----------------------+--------+------------------------------------+
```

The trailer stores a 32-byte cryptographic digest:

$$\text{digest} = \text{SHA-256}(\text{BigEndian32}(\text{step}) \parallel \text{BigEndian32}(\text{length}) \parallel \text{Uint8}(\text{key}))$$

---

### Solving the Modulo Constraints

The search space for arbitrary 32-bit `step` and `length` integers is too large for brute force ($2^{64}$). However, we can use the structure of H.264 video streams to solve for `step` and `length` mathematically in milliseconds:

1. **Locate the `moov` atom**: By scanning backward from the `bdve` trailer, we identify the plaintext sample table boxes (`stsz`, `stsc`, `stco`/`co64`).
2. **Extract Sample Chunk Offsets**: The sample table gives us the exact byte offsets where H.264 NAL units (Network Abstraction Layer) are located in the file.
3. **NAL Unit Scoring**: A valid H.264 NAL header begins with a 4-byte start code (`0x00000001`) followed by a NAL type byte (e.g., SPS=7, PPS=8, IDR Slice=5). If a sample offset is in an encrypted block, its bytes will only match NAL signatures when XOR'd with the key.
4. **Modulo Arithmetic**: Slices are encrypted at offsets:
   $$\text{offset} \pmod{\text{step}} < \text{length}$$
   Every verified encrypted offset imposes:
   $$\text{length} > (\text{offset} \pmod{\text{step}})$$
   Every verified plaintext offset imposes:
   $$\text{length} \le (\text{offset} \pmod{\text{step}})$$

Testing candidate step intervals (derived from common chunk boundaries like 49,435 or 65,536) rapidly narrows the candidate set to a single integer pair `(step, length)`. We then verify against the 32-byte trailer SHA-256 digest.

When the digest matches, we have mathematical certainty of the exact cryptographic parameters.

---

### Pure Bitstream Inversion (Zero Re-Encoding Loss)

Once `(step, length, key)` are known:
1. We read the source file in chunks.
2. For each byte range where `pos % step < length`, we XOR the slice with `key`.
3. We truncate the 68-byte proprietary `bdve` trailer.
4. We write out the clean MP4 file.

**Throughput**: Because this is purely bitwise inversion with zero transcoding, throughput exceeds **100 MB/s** on standard hardware. A 500 MB video decrypts in ~4 seconds.

Most importantly, the original AVC/H.264 NAL units and AAC LC audio packets are bit-for-bit identical to CapCut's rendered output. There is **zero generational compression loss**, zero color space shift, and zero dropped frames.

---

### Building the Tool: Ergonomics & Polish

I packaged the engine into an open-source tool: **[CapCut Cache Recover](https://github.com/pikadexofc/export-capcut-pro-video-free)**.

Key features include:
1. **Interactive Terminal Selector**: Auto-indexes recent CapCut drafts and lets you navigate with arrow keys (`↑ / ↓`) in PowerShell or Command Prompt.
2. **Native Windows Explorer "Save As" (Ctrl+S style)**: Lets you pick the exact output folder and filename via a standard file dialog.
3. **CapCut Project Metadata Resolution**: Parses `draft_meta_info.json` and `draft_content.json` to extract your real project and clip names (`shining motion u - Compound clip16.mp4`) instead of cryptic GUIDs (`48C34141-8F08-4483...mp4`).
4. **Desktop GUI**: Native 4-tab dark obsidian visual suite (`#0B0F14`) with Drag & Drop and keyboard accelerators.
5. **Standalone Windows Executable**: A 12 MB portable binary requiring zero Python installation.

---

### Getting Started

You can install it via PowerShell in 5 seconds:

```powershell
irm https://raw.githubusercontent.com/pikadexofc/export-capcut-pro-video-free/main/install.ps1 | iex
```

Or clone the source code on GitHub:

```bash
git clone https://github.com/pikadexofc/export-capcut-pro-video-free.git
cd export-capcut-pro-video-free
python -m pip install -e .
```

* **GitHub Repository**: [pikadexofc/export-capcut-pro-video-free](https://github.com/pikadexofc/export-capcut-pro-video-free)
* **Latest Binary Release**: [v1.0.1 on GitHub Releases](https://github.com/pikadexofc/export-capcut-pro-video-free/releases/tag/v1.0.1)

---

*Engineered by **Md. Zobaed Islam Shanto** • Founded under **PixelPie Media**.*  
*If this utility saved your project, consider supporting development: [⚡ Fund the Production](https://mdzobaedislamshanto.supportkori.shop/).*
