"""Scanner module to discover CapCut & JianYing draft cache videos across disks."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Generator, List, Optional

from .cryptor import parse_bdve_footer


def get_default_draft_paths() -> List[Path]:
    """Returns typical CapCut & JianYing draft directory paths on the current operating system."""
    paths: List[Path] = []

    if sys.platform.startswith("win"):
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            paths.append(Path(local_app_data) / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft")
            paths.append(Path(local_app_data) / "JianyingPro" / "User Data" / "Projects" / "com.lveditor.draft")

        # Scan for common custom cache drives (C:, D:, E:)
        for drive in ("D:", "E:", "F:", "C:"):
            drive_path = Path(f"{drive}\\capcut cache\\CapCut Drafts")
            if drive_path.exists():
                paths.append(drive_path)
            custom_path = Path(f"{drive}\\CapCut Drafts")
            if custom_path.exists():
                paths.append(custom_path)
    elif sys.platform == "darwin":
        home = Path.home()
        paths.append(home / "Movies" / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft")
        paths.append(home / "Movies" / "JianyingPro" / "User Data" / "Projects" / "com.lveditor.draft")

    return [p for p in paths if p.exists()]


def is_bdve_file(file_path: Path) -> bool:
    """Quickly tests if a file contains the ByteDance BDVE cryptor footer."""
    try:
        size = file_path.stat().st_size
        if size < 68:
            return False
        with open(file_path, "rb") as f:
            f.seek(max(0, size - 256))
            tail = f.read(256)
            return parse_bdve_footer(tail) is not None
    except Exception:
        return False


def find_encrypted_videos(directory: Path) -> Generator[Path, None, None]:
    """Recursively walks a directory and yields all files with BDVE signatures."""
    if not directory.exists():
        return

    for root, _, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in {".mp4", ".mov", ".tmp", ".cache", ""}:
                file_path = Path(root) / file
                if is_bdve_file(file_path):
                    yield file_path
