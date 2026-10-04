"""CapCut & JianYing Metadata Resolution Engine.

Extracts real project names and material clip titles from CapCut draft JSONs
(draft_meta_info.json, draft_content.json, root_meta_info.json).
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class ProjectMetadata:
    project_name: str
    clip_name: Optional[str] = None
    suggested_filename: str = ""

    def get_display_title(self) -> str:
        if self.clip_name and self.clip_name != self.project_name:
            return f"{self.project_name} - {self.clip_name}"
        return self.project_name


def sanitize_filename(name: str) -> str:
    """Removes invalid filename characters across operating systems."""
    return re.sub(r'[<>:"/\\|?*]', "_", name).strip()


def resolve_capcut_metadata(video_path: Path) -> ProjectMetadata:
    """Intelligently resolves project name and clip title from CapCut draft directory structure."""
    video_path = video_path.resolve()
    guid = video_path.stem.replace("_video", "").upper()

    project_name: Optional[str] = None
    clip_name: Optional[str] = None

    # Step 1: Traverse upward to find draft root folder
    current = video_path.parent
    draft_folder: Optional[Path] = None

    for _ in range(5):
        if (current / "draft_meta_info.json").exists() or (current / "draft_content.json").exists():
            draft_folder = current
            break
        if current.parent == current:
            break
        current = current.parent

    # Step 2: Read draft_meta_info.json
    if draft_folder:
        meta_info_path = draft_folder / "draft_meta_info.json"
        if meta_info_path.exists():
            try:
                with open(meta_info_path, "r", encoding="utf-8") as f:
                    meta_data = json.load(f)
                    if isinstance(meta_data, dict):
                        project_name = meta_data.get("draft_name") or meta_data.get("name")
            except Exception:
                pass

        # Step 3: Search draft_content.json for material clip name
        content_json_path = draft_folder / "draft_content.json"
        if content_json_path.exists():
            try:
                with open(content_json_path, "r", encoding="utf-8") as f:
                    content_data = json.load(f)
                    if isinstance(content_data, dict):
                        # If project name wasn't in meta, check content name
                        if not project_name:
                            project_name = content_data.get("name")

                        # Search materials for this video GUID
                        materials = content_data.get("materials", {})
                        if isinstance(materials, dict):
                            for cat in ("videos", "combines", "drafts"):
                                items = materials.get(cat, [])
                                if isinstance(items, list):
                                    for item in items:
                                        if isinstance(item, dict):
                                            item_str = json.dumps(item)
                                            if guid in item_str or video_path.name in item_str:
                                                clip_name = item.get("material_name") or item.get("name")
                                                if clip_name:
                                                    break
                                if clip_name:
                                    break
            except Exception:
                pass

    # Step 4: Fallback to CapCut global root_meta_info.json in AppData if needed
    if not project_name:
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            master_meta = Path(local_app_data) / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft" / "root_meta_info.json"
            if master_meta.exists():
                try:
                    with open(master_meta, "r", encoding="utf-8") as f:
                        master_data = json.load(f)
                        all_drafts = master_data.get("all_draft_store", [])
                        for d in all_drafts:
                            # Match draft path or folder name
                            d_path = str(d.get("draft_root_path", ""))
                            if draft_folder and str(draft_folder).lower().startswith(d_path.lower()):
                                if d.get("draft_name"):
                                    project_name = d.get("draft_name")
                                    break
                except Exception:
                    pass

    # Step 5: Final fallbacks
    if not project_name and draft_folder:
        project_name = draft_folder.name
    elif not project_name:
        project_name = video_path.stem

    clean_project = sanitize_filename(project_name)
    clean_clip = sanitize_filename(clip_name) if clip_name else None

    if clean_clip and clean_clip.lower() != clean_project.lower():
        suggested = f"{clean_project} - {clean_clip}.mp4"
    else:
        suggested = f"{clean_project}_exported.mp4"

    return ProjectMetadata(
        project_name=clean_project,
        clip_name=clean_clip,
        suggested_filename=suggested,
    )
