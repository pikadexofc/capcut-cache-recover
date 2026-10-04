"""MP4 Container validation module.

Validates atoms, headers, video/audio tracks, and duration without requiring external tools like ffmpeg.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .cryptor import iter_boxes, find_child, find_path, read_u32


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    duration_seconds: float
    has_video: bool
    has_audio: bool
    video_width: int
    video_height: int
    error: Optional[str] = None


def validate_mp4(file_path: Path) -> ValidationResult:
    """Parses and validates an MP4 file's container structure."""
    if not file_path.exists():
        return ValidationResult(False, 0.0, False, False, 0, 0, f"File does not exist: {file_path}")

    try:
        data = file_path.read_bytes()
    except Exception as e:
        return ValidationResult(False, 0.0, False, False, 0, 0, f"Read error: {e}")

    if len(data) < 32:
        return ValidationResult(False, 0.0, False, False, 0, 0, "File too small to be a valid MP4 container.")

    has_ftyp = False
    has_moov = False
    has_mdat = False
    moov_box = None

    for box in iter_boxes(data, 0, len(data)):
        if box.type == b"ftyp":
            has_ftyp = True
        elif box.type == b"moov":
            has_moov = True
            moov_box = box
        elif box.type == b"mdat":
            has_mdat = True

    if not has_ftyp:
        return ValidationResult(False, 0.0, False, False, 0, 0, "Missing 'ftyp' atom. Not a valid MP4/MOV container.")
    if not has_moov:
        return ValidationResult(False, 0.0, False, False, 0, 0, "Missing 'moov' atom. Index was never finalized or was truncated.")
    if not has_mdat:
        return ValidationResult(False, 0.0, False, False, 0, 0, "Missing 'mdat' atom. Container has no media data payload.")

    assert moov_box is not None
    duration = 0.0
    has_video = False
    has_audio = False
    width = 0
    height = 0

    # Read mvhd for duration
    mvhd = find_child(data, moov_box, b"mvhd")
    if mvhd is not None:
        offset = mvhd.content_start
        version = data[offset]
        if version == 0:
            timescale = read_u32(data, offset + 12)
            duration_ticks = read_u32(data, offset + 16)
        else:
            timescale = read_u32(data, offset + 20)
            duration_ticks = int.from_bytes(data[offset + 24 : offset + 32], "big")
        if timescale > 0:
            duration = duration_ticks / timescale

    # Inspect tracks
    for trak in iter_boxes(data, moov_box.content_start, moov_box.end):
        if trak.type != b"trak":
            continue

        hdlr = find_path(data, trak, (b"mdia", b"hdlr"))
        if hdlr is not None:
            handler = data[hdlr.content_start + 8 : hdlr.content_start + 12]
            if handler == b"vide":
                has_video = True
                tkhd = find_child(data, trak, b"tkhd")
                if tkhd is not None:
                    # Width and height in 16.16 fixed point at end of tkhd
                    w_raw = int.from_bytes(data[tkhd.end - 8 : tkhd.end - 4], "big")
                    h_raw = int.from_bytes(data[tkhd.end - 4 : tkhd.end], "big")
                    width = w_raw >> 16
                    height = h_raw >> 16
            elif handler == b"soun":
                has_audio = True

    return ValidationResult(
        is_valid=True,
        duration_seconds=round(duration, 2),
        has_video=has_video,
        has_audio=has_audio,
        video_width=width,
        video_height=height,
    )
