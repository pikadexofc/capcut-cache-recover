"""Command Line Interface for Export Capcut Pro Video Free."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __version__, __tool_name__
from .cryptor import recover_file, DecodeError
from .scanner import find_encrypted_videos, get_default_draft_paths
from .validator import validate_mp4


BANNER = r"""
========================================================================
   EXPORT CAPCUT PRO VIDEO FREE  -  v""" + __version__ + r"""
   Unlock, Decrypt & Export Protected CapCut & JianYing Draft Videos
========================================================================
"""


def format_size(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:3.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} TB"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="export-capcut-pro-video-free",
        description="Export Capcut Pro Video Free: Recover and export unplayable CapCut & JianYing draft cache videos (BDVE Cryptor Type 1).",
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="Path to encrypted CapCut video file or directory to export.",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output destination path for exported video or output directory for batch scans.",
    )
    parser.add_argument(
        "--scan",
        type=Path,
        help="Scan a specific directory recursively for all BDVE encrypted draft videos to export.",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Automatically locate CapCut & JianYing draft directories and export all encrypted clips.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        default=True,
        help="Perform MP4 container validation after export (default: True).",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable detailed debug logging during cryptor parameter discovery.",
    )

    args = parser.parse_args(argv)

    print(BANNER)

    logger = (lambda msg: print(f"  [+] {msg}")) if args.verbose else (lambda _: None)

    # 1. AUTO SCAN MODE
    if args.auto:
        draft_paths = get_default_draft_paths()
        if not draft_paths:
            print("[-] No standard CapCut or JianYing draft folders detected.")
            return 1

        print(f"[*] Found {len(draft_paths)} draft root location(s):")
        for p in draft_paths:
            print(f"    - {p}")

        all_candidates = []
        for p in draft_paths:
            print(f"[*] Scanning {p}...")
            candidates = list(find_encrypted_videos(p))
            print(f"    Found {len(candidates)} encrypted video(s)")
            all_candidates.extend(candidates)

        if not all_candidates:
            print("[*] No BDVE-encrypted videos currently pending export.")
            return 0

        out_dir = args.output or Path.cwd() / "exported_capcut_videos"
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"[*] Exporting {len(all_candidates)} video(s) into: {out_dir}")

        success_count = 0
        for i, src in enumerate(all_candidates, 1):
            stem = src.stem.replace("_video", "") + "_exported.mp4"
            dest = out_dir / stem
            print(f"\n[{i}/{len(all_candidates)}] Processing: {src.name} ({format_size(src.stat().st_size)})")
            try:
                recover_file(src, dest, log=logger)
                if args.verify:
                    val = validate_mp4(dest)
                    if val.is_valid:
                        print(f"    [OK] Duration: {val.duration_seconds}s | {val.video_width}x{val.video_height}")
                success_count += 1
            except Exception as e:
                print(f"    [FAIL] Error: {e}")

        print(f"\n[DONE] Successfully exported {success_count}/{len(all_candidates)} videos.")
        return 0

    # 2. SCAN FOLDER MODE
    if args.scan:
        scan_dir = args.scan
        if not scan_dir.exists():
            print(f"[-] Directory does not exist: {scan_dir}")
            return 1

        candidates = list(find_encrypted_videos(scan_dir))
        print(f"[*] Scanned '{scan_dir}' and found {len(candidates)} BDVE encrypted video(s).")
        if not candidates:
            return 0

        out_dir = args.output or scan_dir / "exported"
        out_dir.mkdir(parents=True, exist_ok=True)

        success_count = 0
        for i, src in enumerate(candidates, 1):
            dest = out_dir / f"{src.stem}_exported.mp4"
            print(f"\n[{i}/{len(candidates)}] Processing: {src.name}")
            try:
                recover_file(src, dest, log=logger)
                success_count += 1
            except Exception as e:
                print(f"    [FAIL] Error: {e}")

        print(f"\n[DONE] Successfully exported {success_count}/{len(candidates)} videos.")
        return 0

    # 3. SINGLE FILE MODE
    if args.input:
        src = args.input
        if not src.exists():
            print(f"[-] Input file not found: {src}")
            return 1

        if src.is_dir():
            print(f"[*] Input is a directory. Switching to scan mode on '{src}'...")
            candidates = list(find_encrypted_videos(src))
            print(f"[*] Found {len(candidates)} encrypted files.")
            out_dir = args.output or src / "exported"
            out_dir.mkdir(parents=True, exist_ok=True)
            for s in candidates:
                d = out_dir / f"{s.stem}_exported.mp4"
                print(f"[*] Exporting {s.name} -> {d.name}")
                recover_file(s, d, log=logger)
            return 0

        # Output path derivation
        if args.output:
            dest = args.output
            if dest.is_dir():
                dest = dest / f"{src.stem}_exported.mp4"
        else:
            dest = src.parent / f"{src.stem}_exported.mp4"

        print(f"[*] Source file:      {src} ({format_size(src.stat().st_size)})")
        print(f"[*] Destination:      {dest}")

        start_time = time.perf_counter()
        try:
            params = recover_file(src, dest, log=logger)
            elapsed = time.perf_counter() - start_time
            print(f"[+] Decryption and export completed in {elapsed:.2f}s!")
            print(f"    - Key:      0x{params.key:02X}")
            print(f"    - Step:     {params.step:,} bytes")
            print(f"    - Length:   {params.length:,} bytes")

            if args.verify:
                print("[*] Validating MP4 container integrity...")
                val = validate_mp4(dest)
                if val.is_valid:
                    print("[+] Container Check: PASS (100% valid MP4)")
                    print(f"    - Duration:    {val.duration_seconds}s")
                    print(f"    - Video Track: {'Yes' if val.has_video else 'No'} ({val.video_width}x{val.video_height})")
                    print(f"    - Audio Track: {'Yes' if val.has_audio else 'No'}")
                else:
                    print(f"[-] Container Check Warning: {val.error}")

            print(f"\n[SUCCESS] Your exported video is ready at:\n  {dest.resolve()}")
            return 0

        except DecodeError as e:
            print(f"[-] Export failed: {e}")
            return 1
        except Exception as e:
            print(f"[-] Unexpected error: {e}")
            return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
