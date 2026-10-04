"""Scanner module to discover CapCut & JianYing draft projects and cache videos across disks."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator, List, Optional, Set

from .cryptor import parse_bdve_footer


@dataclass
class CapCutProject:
    """Represents a discovered CapCut or JianYing editing project."""
    name: str
    folder: Path
    modified_time: float
    cover_image: Optional[Path] = None
    draft_id: str = ""
    duration_sec: float = 0.0
    encrypted_clips: List[Path] = field(default_factory=list)

    @property
    def display_name(self) -> str:
        return self.name or self.folder.name


def get_default_draft_paths() -> List[Path]:
    """Returns typical CapCut & JianYing draft directory paths on the current operating system,
    dynamically resolving active draft directories from registry and master root_meta_info.json files.
    """
    paths: List[Path] = []
    seen: Set[str] = set()

    def add_path(p: Path | str | None):
        if not p:
            return
        try:
            cand = Path(p).resolve()
            cand_str = str(cand).lower()
            if cand.exists() and cand_str not in seen:
                seen.add(cand_str)
                paths.append(cand)
        except Exception:
            pass

    if sys.platform.startswith("win"):
        local_app_data = os.environ.get("LOCALAPPDATA")
        user_profile = os.environ.get("USERPROFILE")
        home = Path.home()

        # 1. Inspect CapCut and Jianying master root_meta_info.json for active user draft roots
        if local_app_data:
            master_metas = [
                Path(local_app_data) / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft" / "root_meta_info.json",
                Path(local_app_data) / "JianyingPro" / "User Data" / "Projects" / "com.lveditor.draft" / "root_meta_info.json",
            ]
            for mm in master_metas:
                if mm.exists():
                    try:
                        with open(mm, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        # Extract draft_root_path and draft_fold_path roots
                        for draft in data.get("all_draft_store", []):
                            rp = draft.get("draft_root_path")
                            if rp:
                                add_path(rp)
                            fp = draft.get("draft_fold_path")
                            if fp:
                                add_path(Path(fp).parent)
                    except Exception:
                        pass

        # 2. Standard Windows user draft folders
        add_path(home / "CapCut Drafts")
        if user_profile:
            add_path(Path(user_profile) / "CapCut Drafts")
        if local_app_data:
            add_path(Path(local_app_data) / "CapCut Drafts")
            add_path(Path(local_app_data) / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft")
            add_path(Path(local_app_data) / "JianyingPro" / "User Data" / "Projects" / "com.lveditor.draft")
            add_path(Path(local_app_data) / "CapCut" / "User Data" / "Projects")
            add_path(Path(local_app_data) / "CapCut" / "User Data" / "Cache")

        add_path(home / "Videos" / "CapCut")
        add_path(home / "Documents" / "CapCut")

        # 3. Scan all available Windows drives (C:, D:, E:, F:, G:)
        for drive_letter in ("C", "D", "E", "F", "G"):
            drive = f"{drive_letter}:\\"
            if os.path.exists(drive):
                add_path(Path(f"{drive}capcut cache\\CapCut Drafts"))
                add_path(Path(f"{drive}CapCut Drafts"))
                add_path(Path(f"{drive}capcut cache"))
                add_path(Path(f"{drive}CapCut"))

    elif sys.platform == "darwin":
        home = Path.home()
        add_path(home / "Movies" / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft")
        add_path(home / "Movies" / "CapCut Drafts")
        add_path(home / "Movies" / "CapCut")
        add_path(home / "Movies" / "JianyingPro" / "User Data" / "Projects" / "com.lveditor.draft")

    elif "android" in sys.platform.lower() or os.path.exists("/data/data/com.termux") or os.path.exists("/storage/emulated/0"):
        base_storage = Path("/storage/emulated/0")
        termux_storage = Path.home() / "storage"

        android_roots = [
            base_storage / "Android/data/com.lemon.lvoverseas/files/newdrafts",
            base_storage / "Android/data/com.lemon.lvoverseas/files/draft",
            base_storage / "Android/data/com.jianying.mobile/files/newdrafts",
            base_storage / "DCIM/CapCut",
            base_storage / "Movies/CapCut",
            base_storage / "Download",
            termux_storage / "shared/Android/data/com.lemon.lvoverseas/files/newdrafts",
            termux_storage / "dcim/CapCut",
            termux_storage / "movies/CapCut",
            termux_storage / "downloads",
        ]
        for ar in android_roots:
            add_path(ar)

    return paths


def discover_capcut_projects() -> List[CapCutProject]:
    """Automatically locates and resolves all CapCut and JianYing projects with names,
    modification dates, cover thumbnails, and folder paths across the machine.
    """
    projects_map: dict[str, CapCutProject] = {}
    local_app_data = os.environ.get("LOCALAPPDATA")

    # 1. Parse master root_meta_info.json files (very fast, covers historical & custom paths)
    if local_app_data:
        master_metas = [
            Path(local_app_data) / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft" / "root_meta_info.json",
            Path(local_app_data) / "JianyingPro" / "User Data" / "Projects" / "com.lveditor.draft" / "root_meta_info.json",
        ]
        for mm in master_metas:
            if mm.exists():
                try:
                    with open(mm, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    for item in data.get("all_draft_store", []):
                        fold_str = item.get("draft_fold_path") or ""
                        if not fold_str:
                            continue
                        fold = Path(fold_str)
                        if fold.exists():
                            name = item.get("draft_name") or fold.name
                            mtime = float(item.get("tm_draft_modified", 0))
                            if mtime > 1e12:
                                mtime /= 1e6
                            elif mtime == 0:
                                try:
                                    mtime = fold.stat().st_mtime
                                except Exception:
                                    mtime = 0.0

                            cover_str = item.get("draft_cover")
                            cover = Path(cover_str) if cover_str and Path(cover_str).exists() else None
                            if not cover and (fold / "draft_cover.jpg").exists():
                                cover = fold / "draft_cover.jpg"

                            duration = float(item.get("tm_duration", 0)) / 1e6 if item.get("tm_duration") else 0.0
                            draft_id = item.get("draft_id", "")

                            key = str(fold.resolve()).lower()
                            projects_map[key] = CapCutProject(
                                name=name,
                                folder=fold,
                                modified_time=mtime,
                                cover_image=cover,
                                draft_id=draft_id,
                                duration_sec=duration,
                            )
                except Exception:
                    pass

    # 2. Inspect all candidate draft roots on disk for draft folders
    for root_dir in get_default_draft_paths():
        if not root_dir.exists():
            continue
        try:
            for item in root_dir.iterdir():
                if not item.is_dir():
                    continue
                key = str(item.resolve()).lower()
                if key in projects_map:
                    continue

                # Check if it has CapCut draft signatures
                has_content = (item / "draft_content.json").exists()
                has_meta = (item / "draft_meta_info.json").exists()
                if has_content or has_meta:
                    name = item.name
                    if has_meta:
                        try:
                            with open(item / "draft_meta_info.json", "r", encoding="utf-8") as f:
                                m_data = json.load(f)
                                name = m_data.get("draft_name") or m_data.get("name") or name
                        except Exception:
                            pass

                    cover = item / "draft_cover.jpg"
                    cover_path = cover if cover.exists() else None
                    try:
                        mtime = item.stat().st_mtime
                    except Exception:
                        mtime = 0.0

                    projects_map[key] = CapCutProject(
                        name=name,
                        folder=item,
                        modified_time=mtime,
                        cover_image=cover_path,
                    )
        except Exception:
            pass

    # Sort descending by modification time (most recent projects first)
    projects_list = list(projects_map.values())
    projects_list.sort(key=lambda p: p.modified_time, reverse=True)
    return projects_list


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


def get_project_encrypted_clips(project_folder: Path) -> List[Path]:
    """Discovers all BDVE encrypted video streams within a specific project folder,
    including resources, combinations, local caches, and draft_content.json references.
    """
    clips: List[Path] = []
    seen: Set[str] = set()

    def add_clip(p: Path):
        try:
            res = p.resolve()
            res_str = str(res).lower()
            if res_str not in seen and res.exists() and is_bdve_file(res):
                seen.add(res_str)
                clips.append(res)
        except Exception:
            pass

    # 1. Walk project folder for potential video files
    if project_folder.exists():
        for root, _, files in os.walk(project_folder):
            for f in files:
                f_lower = f.lower()
                ext = os.path.splitext(f_lower)[1]
                if ext in {".mp4", ".mov", ".tmp", ".cache", ".dat", ".mp4_temp", ".aac"} or "_video" in f_lower or "videoalg" in root.lower() or "combination" in root.lower():
                    add_clip(Path(root) / f)

    # 2. Check draft_content.json referenced paths if present
    content_json = project_folder / "draft_content.json"
    if content_json.exists():
        try:
            with open(content_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            materials = data.get("materials", {})
            for cat in ("videos", "combines", "audios"):
                for item in materials.get(cat, []):
                    p_str = item.get("path")
                    if p_str:
                        p_obj = Path(p_str)
                        add_clip(p_obj)
                        # Check base versions if .alpha.mp4, _RECOVERED.mp4, or _temp
                        clean_str = (
                            p_str.replace(".alpha.mp4", "")
                            .replace("_RECOVERED.mp4", ".mp4")
                            .replace(".mp4_temp", ".mp4")
                        )
                        if clean_str != p_str:
                            add_clip(Path(clean_str))
        except Exception:
            pass

    return clips


def find_encrypted_videos(directory: Path) -> Generator[Path, None, None]:
    """Recursively walks a directory and yields all files with BDVE signatures."""
    if not directory.exists():
        return

    # If the directory is itself a project, use project-aware extraction first
    if (directory / "draft_content.json").exists() or (directory / "draft_meta_info.json").exists():
        for clip in get_project_encrypted_clips(directory):
            yield clip
        return

    seen: Set[str] = set()
    for root, dirs, files in os.walk(directory):
        # Skip node_modules or git caches if any
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "$RECYCLE.BIN")]
        for file in files:
            file_lower = file.lower()
            ext = os.path.splitext(file_lower)[1]
            if (
                ext in {".mp4", ".mov", ".tmp", ".cache", ".dat", ".mp4_temp", ".aac", ""}
                or "_video" in file_lower
                or "videoalg" in root.lower()
                or "combination" in root.lower()
            ):
                file_path = Path(root) / file
                res_key = str(file_path).lower()
                if res_key not in seen and is_bdve_file(file_path):
                    seen.add(res_key)
                    yield file_path
