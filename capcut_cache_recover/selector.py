"""Interactive Terminal Selector & Windows Explorer Save-As Integration.

Provides automatic detection of recent CapCut draft cache files, interactive
arrow-key console navigation, and native Windows Explorer 'Save As' pop-out dialogs.
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .metadata import resolve_capcut_metadata, ProjectMetadata
from .scanner import find_encrypted_videos, get_default_draft_paths


@dataclass
class RecentDraftItem:
    path: Path
    meta: ProjectMetadata
    size_bytes: int
    mtime: float

    @property
    def formatted_size(self) -> str:
        s = float(self.size_bytes)
        for unit in ("B", "KB", "MB", "GB"):
            if abs(s) < 1024.0:
                return f"{s:3.1f} {unit}"
            s /= 1024.0
        return f"{s:.1f} TB"

    @property
    def formatted_time(self) -> str:
        now = time.time()
        diff = now - self.mtime
        if diff < 60:
            return "Just now"
        elif diff < 3600:
            return f"{int(diff // 60)} min ago"
        elif diff < 86400:
            return f"{int(diff // 3600)} hr ago"
        elif diff < 86400 * 7:
            return f"{int(diff // 86400)} days ago"
        else:
            return time.strftime("%b %d, %Y", time.localtime(self.mtime))


def scan_recent_drafts(limit: int = 12) -> list[RecentDraftItem]:
    """Scans all known CapCut & JianYing draft folders and returns items sorted by most recent."""
    roots = get_default_draft_paths()
    found_files: list[Path] = []
    for r in roots:
        found_files.extend(find_encrypted_videos(r))

    # Sort files by modification time descending
    items: list[RecentDraftItem] = []
    for fp in found_files:
        try:
            stat = fp.stat()
            meta = resolve_capcut_metadata(fp)
            items.append(RecentDraftItem(
                path=fp,
                meta=meta,
                size_bytes=stat.st_size,
                mtime=stat.st_mtime,
            ))
        except Exception:
            continue

    items.sort(key=lambda x: x.mtime, reverse=True)
    return items[:limit]


def prompt_windows_save_dialog(
    suggested_filename: str,
    initial_dir: Optional[Path] = None,
    title: str = "Save Exported Video As..."
) -> Optional[Path]:
    """Opens a native Windows Explorer 'Save As' pop-out dialog (Ctrl+S style).

    Pre-fills the auto-resolved CapCut project name and clip title, allowing
    the user to choose the exact destination directory and filename.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        root.focus_force()

        if initial_dir is None or not initial_dir.exists():
            initial_dir = Path.home() / "Desktop"

        selected = filedialog.asksaveasfilename(
            parent=root,
            title=title,
            initialdir=str(initial_dir),
            initialfile=suggested_filename,
            defaultextension=".mp4",
            filetypes=[("MP4 Video (*.mp4)", "*.mp4"), ("All Files (*.*)", "*.*")],
        )
        root.destroy()

        if selected:
            return Path(selected).resolve()
        return None
    except Exception:
        return None


def interactive_select_draft(items: list[RecentDraftItem]) -> Optional[RecentDraftItem]:
    """Renders an interactive terminal menu navigable with Up/Down arrow keys or numbers."""
    if not items:
        return None

    # Check for Windows console arrow key support via msvcrt
    has_msvcrt = False
    try:
        import msvcrt
        has_msvcrt = True
    except ImportError:
        pass

    if not sys.stdin.isatty() or not has_msvcrt:
        # Fallback to standard numbered prompt
        print("\nRecent CapCut Draft Videos:")
        for idx, item in enumerate(items, 1):
            title = item.meta.get_display_title()
            print(f"  [{idx:2d}] {title:<40} ({item.formatted_size:>8}, {item.formatted_time})")
        print("  [ 0] Cancel / Exit")
        try:
            choice = input("\nEnter selection number: ").strip()
            if choice.isdigit():
                val = int(choice)
                if 1 <= val <= len(items):
                    return items[val - 1]
        except (KeyboardInterrupt, EOFError):
            pass
        return None

    import msvcrt

    selected_index = 0
    total = len(items)

    def draw_menu():
        # Clear screen and draw menu header
        os.system("cls" if os.name == "nt" else "clear")
        print("========================================================================")
        print("   EXPORT CAPCUT PRO VIDEO FREE  -  INTERACTIVE DRAFT SELECTOR")
        print("   Use [UP / DOWN] arrow keys to navigate, [ENTER] to export, [Q] to quit")
        print("========================================================================\n")
        print(f"Detected {total} recent protected CapCut & JianYing draft video(s):\n")

        for idx, item in enumerate(items):
            is_active = (idx == selected_index)
            prefix = " ▶ " if is_active else "   "
            num_badge = f"[{idx + 1:2d}]"
            title = item.meta.get_display_title()
            if len(title) > 36:
                title = title[:33] + "..."

            line = f"{prefix}{num_badge} {title:<36}  {item.formatted_size:>8}  │  {item.formatted_time:<12}"
            if is_active:
                # Highlight active line using ANSI or bright markers
                print(f"\033[1;37;48;2;250;123;30m{line}\033[0m" if os.name != "nt" or "WT_SESSION" in os.environ or "TERM" in os.environ else f" >>> {line}")
            else:
                print(line)

        print("\n------------------------------------------------------------------------")
        active_item = items[selected_index]
        print(f"Selected: {active_item.meta.project_name}")
        if active_item.meta.clip_name:
            print(f"Material: {active_item.meta.clip_name}")
        print(f"Save As:  {active_item.meta.suggested_filename}")
        print("------------------------------------------------------------------------")
        print("Press [Enter] to choose destination in Windows Explorer dialog.")
        print("Press [1-9] for instant jump, or [Q] to cancel.")

    while True:
        draw_menu()
        key = msvcrt.getch()

        # Handle Extended Keys (Arrow Keys on Windows)
        if key in (b"\x00", b"\xe0"):
            sub_key = msvcrt.getch()
            if sub_key == b"H":  # Up Arrow
                selected_index = (selected_index - 1) % total
            elif sub_key == b"P":  # Down Arrow
                selected_index = (selected_index + 1) % total
            elif sub_key == b"G":  # Home
                selected_index = 0
            elif sub_key == b"O":  # End
                selected_index = total - 1
        elif key == b"\r":  # Enter
            return items[selected_index]
        elif key in (b"q", b"Q", b"\x1b"):  # Q or Escape
            return None
        elif key.isdigit():
            val = int(key.decode("latin-1"))
            if 1 <= val <= total:
                selected_index = val - 1
                return items[selected_index]
