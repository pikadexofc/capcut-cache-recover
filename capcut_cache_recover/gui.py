"""Export Capcut Pro Video Free - Flagship Desktop Application.

Engineered by PixelPie Media • Founded by Md. Zobaed Islam Shanto.
High-performance, zero-friction cryptographic video recovery and export engine.
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import List, Optional
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Native Drag & Drop Support
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except ImportError:
    HAS_DND = False

from . import __version__, __tool_name__
from .cryptor import recover_file, DecodeError
from .scanner import (
    find_encrypted_videos,
    get_default_draft_paths,
    discover_capcut_projects,
    get_project_encrypted_clips,
    CapCutProject,
)
from .validator import validate_mp4
from .metadata import resolve_capcut_metadata, ProjectMetadata


SUPPORT_URL = "https://mdzobaedislamshanto.supportkori.shop/"
GITHUB_URL = "https://github.com/pikadexofc/export-capcut-pro-video-free"
PIXELPIE_URL = "https://github.com/pikadexofc"


def format_size(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:3.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} TB"


class ExportCapcutProApp:
    def __init__(self, root: tk.Tk, initial_file: str | None = None):
        self.root = root
        self.root.title("CapCut Cache Recover  •  PixelPie Media")
        self.root.geometry("880x690")
        self.root.minsize(780, 600)
        self.root.configure(bg="#0d1117")

        # Global State
        self.default_output_dir = Path.home() / "Desktop" / "Exported_CapCut_Videos"
        self.last_exported_file: Path | None = None
        self.draft_items: list[Path] = []
        self.discovered_projects: list[CapCutProject] = []
        self.current_project_clips: list[Path] = []
        self.library_raw_data: list[tuple[str, str, str, str, Path]] = []
        self.current_meta: ProjectMetadata | None = None
        self.is_busy = False

        self.apply_theme()
        self.build_ui()
        self.enable_drag_and_drop()

        if initial_file:
            self.load_file(Path(initial_file))
        else:
            self.refresh_stats()

        # Kick off automatic project discovery in background immediately
        threading.Thread(target=self.start_background_discovery, daemon=True).start()

    def apply_theme(self):
        # PixelPie Media Dark Palette
        self.bg_root = "#0d1117"
        self.bg_card = "#161b22"
        self.bg_subtle = "#21262d"
        self.border_color = "#30363d"
        self.accent_orange = "#FA7B1E"
        self.accent_orange_hover = "#E06810"
        self.accent_green = "#238636"
        self.accent_green_hover = "#2ea043"
        self.text_main = "#f0f6fc"
        self.text_muted = "#8b949e"
        self.text_highlight = "#58a6ff"

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("TNotebook", background=self.bg_root, borderwidth=0)
        self.style.configure(
            "TNotebook.Tab",
            background=self.bg_card,
            foreground=self.text_muted,
            padding=[18, 8],
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", self.bg_subtle), ("active", "#1c2128")],
            foreground=[("selected", self.accent_orange), ("active", self.text_main)],
        )

        self.style.configure(
            "Orange.Horizontal.TProgressbar",
            troughcolor=self.bg_card,
            background=self.accent_orange,
            thickness=6,
            borderwidth=0,
        )

        self.style.configure(
            "Drafts.Treeview",
            background=self.bg_card,
            foreground=self.text_main,
            fieldbackground=self.bg_card,
            borderwidth=0,
            rowheight=28,
            font=("Segoe UI", 9),
        )
        self.style.configure(
            "Drafts.Treeview.Heading",
            background=self.bg_subtle,
            foreground=self.text_main,
            borderwidth=0,
            font=("Segoe UI", 9, "bold"),
        )
        self.style.map(
            "Drafts.Treeview",
            background=[("selected", "#1f3a5f")],
            foreground=[("selected", "#ffffff")],
        )

    def build_ui(self):
        # 1. TOP HEADER BRAND BAR
        top_bar = tk.Frame(self.root, bg=self.bg_root, pady=12, padx=20)
        top_bar.pack(fill=tk.X)

        header_left = tk.Frame(top_bar, bg=self.bg_root)
        header_left.pack(side=tk.LEFT)

        title_lbl = tk.Label(
            header_left,
            text="CapCut Cache Recover",
            font=("Segoe UI", 15, "bold"),
            fg=self.text_main,
            bg=self.bg_root,
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            header_left,
            text="Precision Cryptographic BDVE Recovery & Bitstream Export • By PixelPie Media",
            font=("Segoe UI", 9),
            fg=self.text_muted,
            bg=self.bg_root,
        )
        subtitle_lbl.pack(anchor="w", pady=(2, 0))

        # Header Right - Clean System & Version Badge
        header_right = tk.Frame(top_bar, bg=self.bg_root)
        header_right.pack(side=tk.RIGHT)

        ver_badge = tk.Frame(header_right, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1, padx=10, pady=4)
        ver_badge.pack(side=tk.RIGHT)

        tk.Label(
            ver_badge,
            text="v" + __version__ + "  •  100% Free & Open Source",
            font=("Segoe UI", 8, "bold"),
            fg=self.accent_orange,
            bg=self.bg_card,
        ).pack()

        # 2. MAIN TABBED NAVIGATION
        self.notebook = ttk.Notebook(self.root, style="TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        self.tab_quick = tk.Frame(self.notebook, bg=self.bg_root)
        self.tab_library = tk.Frame(self.notebook, bg=self.bg_root)
        self.tab_batch = tk.Frame(self.notebook, bg=self.bg_root)
        self.tab_about = tk.Frame(self.notebook, bg=self.bg_root)

        self.notebook.add(self.tab_quick, text="  ⚡ Quick Export  ")
        self.notebook.add(self.tab_library, text="  📁 Projects & Library  ")
        self.notebook.add(self.tab_batch, text="  📦 Batch Queue  ")
        self.notebook.add(self.tab_about, text="  ℹ️ About & Credits  ")

        self.setup_quick_tab()
        self.setup_library_tab()
        self.setup_batch_tab()
        self.setup_about_tab()

        # Keyboard Accelerators
        self.root.bind("<Control-o>", lambda e: self.browse_single_file())
        self.root.bind("<Control-O>", lambda e: self.browse_single_file())
        self.root.bind("<Control-s>", lambda e: self.export_single_file(prompt_save_as=True))
        self.root.bind("<Control-S>", lambda e: self.export_single_file(prompt_save_as=True))
        self.root.bind("<Control-r>", lambda e: self.start_background_discovery())
        self.root.bind("<Control-R>", lambda e: self.start_background_discovery())

        # 3. GLOBAL PROGRESS BAR
        self.prog_bar = ttk.Progressbar(self.root, mode="indeterminate", style="Orange.Horizontal.TProgressbar")
        self.prog_bar.pack(fill=tk.X, padx=20, pady=(0, 6))

        # 4. BOTTOM STATUS FOOTER BAR
        footer = tk.Frame(self.root, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1, pady=8, padx=16)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_lbl = tk.Label(footer, text="Ready. Auto-detecting CapCut projects...", font=("Segoe UI", 9), fg=self.text_muted, bg=self.bg_card)
        self.status_lbl.pack(side=tk.LEFT)

        shortcuts_hint = tk.Label(footer, text="Ctrl+O: Open  │  Ctrl+S: Save As  │  Ctrl+R: Refresh", font=("Consolas", 8), fg=self.text_muted, bg=self.bg_card)
        shortcuts_hint.pack(side=tk.LEFT, padx=20)

        footer_actions = tk.Frame(footer, bg=self.bg_card)
        footer_actions.pack(side=tk.RIGHT)

        self.open_output_btn = tk.Button(
            footer_actions,
            text="📂 Open Output Folder",
            font=("Segoe UI", 8, "bold"),
            bg=self.bg_subtle,
            fg=self.text_main,
            activebackground=self.border_color,
            relief=tk.FLAT,
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.open_output_dir,
        )
        self.open_output_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.play_last_btn = tk.Button(
            footer_actions,
            text="▶ Play Video",
            font=("Segoe UI", 8, "bold"),
            bg=self.accent_green,
            fg="#ffffff",
            activebackground=self.accent_green_hover,
            relief=tk.FLAT,
            padx=10,
            pady=3,
            state=tk.DISABLED,
            cursor="hand2",
            command=self.play_last_exported,
        )
        self.play_last_btn.pack(side=tk.LEFT)

    def enable_drag_and_drop(self):
        """Binds OS-level drag and drop to the window and dropcard."""
        if HAS_DND:
            try:
                self.root.drop_target_register(DND_FILES)
                self.root.dnd_bind("<<Drop>>", self.on_drop_event)
                self.drop_card.drop_target_register(DND_FILES)
                self.drop_card.dnd_bind("<<Drop>>", self.on_drop_event)
                self.drop_card.dnd_bind("<<DragEnter>>", self.on_drag_enter)
                self.drop_card.dnd_bind("<<DragLeave>>", self.on_drag_leave)
                self.log("[+] Native Drag & Drop active. Drop files anywhere on this window.")
            except Exception as e:
                self.log(f"[-] Drag & Drop registration notice: {e}")
        else:
            self.log("[*] Standard file picker active.")

    def on_drag_enter(self, event):
        self.drop_card.configure(highlightbackground=self.accent_orange, highlightthickness=2)
        self.drop_title.configure(text="✨ Release to Load Video Now!", fg=self.accent_orange)

    def on_drag_leave(self, event):
        self.drop_card.configure(highlightbackground=self.border_color, highlightthickness=1)
        self.drop_title.configure(text="Drag & Drop Video Here (or Click to Browse)", fg=self.text_main)

    def on_drop_event(self, event):
        self.on_drag_leave(None)
        raw_data = event.data
        if not raw_data:
            return

        clean_path = raw_data.strip("{}").strip('"').strip("'")
        if "}" in clean_path:
            clean_path = clean_path.split("}")[0].strip("{")

        dropped = Path(clean_path)
        if dropped.exists():
            self.load_file(dropped)

    def load_file(self, file_path: Path):
        self.file_path_var.set(str(file_path))
        self.drop_card.configure(highlightbackground=self.accent_green, highlightthickness=1)

        # Resolve Real Project Name & Clip Name!
        meta = resolve_capcut_metadata(file_path)
        self.current_meta = meta

        self.project_name_var.set(f"📁 Project: {meta.project_name}")
        self.clip_name_var.set(f"🎬 Material: {meta.clip_name or 'Main Media'}")
        self.suggested_name_var.set(f"💾 Will Export As: {meta.suggested_filename}")

        size_str = format_size(file_path.stat().st_size)
        self.drop_title.configure(text=f"Ready to Export: {meta.get_display_title()} ({size_str})", fg=self.text_main)
        self.log(f"[+] Loaded clip: {file_path.name}")
        self.log(f"    - Project:  {meta.project_name}")
        if meta.clip_name:
            self.log(f"    - Clip:     {meta.clip_name}")
        self.log(f"    - Target:   {meta.suggested_filename}")

    # -------------------------------------------------------------
    # TAB 1: QUICK EXPORT (WITH AUTO-DISCOVERED PROJECTS BAR)
    # -------------------------------------------------------------
    def setup_quick_tab(self):
        container = tk.Frame(self.tab_quick, bg=self.bg_root, pady=6)
        container.pack(fill=tk.BOTH, expand=True)

        # AUTO-DISCOVERED PROJECTS QUICK BAR
        proj_panel = tk.Frame(container, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1, pady=8, padx=14)
        proj_panel.pack(fill=tk.X, pady=(0, 8))

        proj_top = tk.Frame(proj_panel, bg=self.bg_card)
        proj_top.pack(fill=tk.X, pady=(0, 6))

        self.proj_badge_lbl = tk.Label(
            proj_top,
            text="⚡ Auto-Discovered CapCut Projects: (Detecting...)",
            font=("Segoe UI", 9, "bold"),
            fg=self.accent_orange,
            bg=self.bg_card,
        )
        self.proj_badge_lbl.pack(side=tk.LEFT)

        rescan_proj_btn = tk.Button(
            proj_top,
            text="🔄 Refresh Projects",
            font=("Segoe UI", 8, "bold"),
            bg=self.bg_subtle,
            fg=self.text_main,
            activebackground=self.border_color,
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.start_background_discovery,
        )
        rescan_proj_btn.pack(side=tk.RIGHT)

        # Dropdown selection row
        sel_row = tk.Frame(proj_panel, bg=self.bg_card)
        sel_row.pack(fill=tk.X, pady=(0, 6))

        tk.Label(sel_row, text="Project:", font=("Segoe UI", 9), fg=self.text_muted, bg=self.bg_card).pack(side=tk.LEFT, padx=(0, 6))

        self.project_var = tk.StringVar(value="Scanning CapCut projects...")
        self.project_combo = ttk.Combobox(sel_row, textvariable=self.project_var, state="readonly", width=38)
        self.project_combo.pack(side=tk.LEFT, padx=(0, 8))
        self.project_combo.bind("<<ComboboxSelected>>", self.on_project_combo_selected)

        tk.Label(sel_row, text="Clip:", font=("Segoe UI", 9), fg=self.text_muted, bg=self.bg_card).pack(side=tk.LEFT, padx=(0, 6))

        self.clip_var = tk.StringVar(value="Select Clip...")
        self.clip_combo = ttk.Combobox(sel_row, textvariable=self.clip_var, state="readonly", width=28)
        self.clip_combo.pack(side=tk.LEFT, padx=(0, 8))
        self.clip_combo.bind("<<ComboboxSelected>>", self.on_clip_combo_selected)

        self.load_proj_clip_btn = tk.Button(
            sel_row,
            text="⚡ Load Clip",
            font=("Segoe UI", 8, "bold"),
            bg=self.accent_orange,
            fg="#ffffff",
            activebackground=self.accent_orange_hover,
            relief=tk.FLAT,
            padx=10,
            pady=2,
            cursor="hand2",
            command=self.load_selected_project_clip,
        )
        self.load_proj_clip_btn.pack(side=tk.LEFT)

        # Quick project chips container
        self.chips_frame = tk.Frame(proj_panel, bg=self.bg_card)
        self.chips_frame.pack(fill=tk.X)

        tk.Label(self.chips_frame, text="Recent:", font=("Segoe UI", 8), fg=self.text_muted, bg=self.bg_card).pack(side=tk.LEFT, padx=(0, 6))
        self.chips_inner = tk.Frame(self.chips_frame, bg=self.bg_card)
        self.chips_inner.pack(side=tk.LEFT, fill=tk.X)

        # Dropzone / Selector Card
        self.drop_card = tk.Frame(container, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1, pady=12, padx=20)
        self.drop_card.pack(fill=tk.X, pady=(0, 8))

        icon_lbl = tk.Label(self.drop_card, text="🎬", font=("Segoe UI Emoji", 22), fg=self.accent_orange, bg=self.bg_card)
        icon_lbl.pack()

        self.drop_title = tk.Label(
            self.drop_card,
            text="Drag & Drop Video Here (or Click to Browse)",
            font=("Segoe UI", 12, "bold"),
            fg=self.text_main,
            bg=self.bg_card,
        )
        self.drop_title.pack(pady=(2, 2))

        drop_sub = tk.Label(
            self.drop_card,
            text="Or select any project above. Accepts *_video.mp4, combination clips, and draft cache streams.",
            font=("Segoe UI", 8),
            fg=self.text_muted,
            bg=self.bg_card,
        )
        drop_sub.pack(pady=(0, 8))

        btn_row = tk.Frame(self.drop_card, bg=self.bg_card)
        btn_row.pack()

        browse_btn = tk.Button(
            btn_row,
            text="📂 Choose File... (Ctrl+O)",
            font=("Segoe UI", 9, "bold"),
            bg=self.bg_subtle,
            fg=self.text_main,
            activebackground=self.border_color,
            relief=tk.FLAT,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self.browse_single_file,
        )
        browse_btn.pack(side=tk.LEFT, padx=6)

        self.export_btn = tk.Button(
            btn_row,
            text="💾 Save As & Export... (Ctrl+S)",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_green,
            fg="#ffffff",
            activebackground=self.accent_green_hover,
            relief=tk.FLAT,
            padx=18,
            pady=5,
            cursor="hand2",
            command=lambda: self.export_single_file(prompt_save_as=True),
        )
        self.export_btn.pack(side=tk.LEFT, padx=6)

        self.quick_export_btn = tk.Button(
            btn_row,
            text="⚡ 1-Click Desktop",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_orange,
            fg="#ffffff",
            activebackground=self.accent_orange_hover,
            relief=tk.FLAT,
            padx=14,
            pady=5,
            cursor="hand2",
            command=lambda: self.export_single_file(prompt_save_as=False),
        )
        self.quick_export_btn.pack(side=tk.LEFT, padx=6)

        # Smart Metadata Info Badges
        meta_frame = tk.Frame(self.drop_card, bg=self.bg_subtle, pady=6, padx=12, highlightbackground=self.border_color, highlightthickness=1)
        meta_frame.pack(fill=tk.X, pady=(10, 0))

        self.project_name_var = tk.StringVar(value="📁 Project: Auto-detecting upon selection...")
        self.clip_name_var = tk.StringVar(value="🎬 Material: —")
        self.suggested_name_var = tk.StringVar(value="💾 Output Filename: —")

        tk.Label(meta_frame, textvariable=self.project_name_var, font=("Segoe UI", 9, "bold"), fg=self.accent_orange, bg=self.bg_subtle, anchor="w").pack(fill=tk.X)
        tk.Label(meta_frame, textvariable=self.clip_name_var, font=("Segoe UI", 8), fg=self.text_main, bg=self.bg_subtle, anchor="w").pack(fill=tk.X)
        tk.Label(meta_frame, textvariable=self.suggested_name_var, font=("Consolas", 8), fg=self.text_highlight, bg=self.bg_subtle, anchor="w", pady=(1, 0)).pack(fill=tk.X)

        self.file_path_var = tk.StringVar(value="No file selected.")

        # Console Log Box
        log_frame = tk.Frame(container, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1)
        log_frame.pack(fill=tk.BOTH, expand=True)

        log_head = tk.Frame(log_frame, bg=self.bg_subtle, padx=12, pady=5)
        log_head.pack(fill=tk.X)
        tk.Label(log_head, text="Engine Activity Log", font=("Segoe UI", 8, "bold"), fg=self.text_main, bg=self.bg_subtle).pack(side=tk.LEFT)

        self.quick_log_text = tk.Text(
            log_frame,
            bg="#0d1117",
            fg=self.text_main,
            font=("Consolas", 8),
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=10,
            pady=6,
        )
        self.quick_log_text.pack(fill=tk.BOTH, expand=True)

    # -------------------------------------------------------------
    # TAB 2: PROJECTS & DRAFTS LIBRARY (AUTO-INDEXED + LIVE FILTER)
    # -------------------------------------------------------------
    def setup_library_tab(self):
        container = tk.Frame(self.tab_library, bg=self.bg_root, pady=8)
        container.pack(fill=tk.BOTH, expand=True)

        toolbar = tk.Frame(container, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1, padx=12, pady=6)
        toolbar.pack(fill=tk.X, pady=(0, 8))

        scan_btn = tk.Button(
            toolbar,
            text="🔄 Rescan (Ctrl+R)",
            font=("Segoe UI", 9, "bold"),
            bg=self.bg_subtle,
            fg=self.text_main,
            activebackground=self.border_color,
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.start_background_discovery,
        )
        scan_btn.pack(side=tk.LEFT, padx=(0, 8))

        # Real-time search filter box
        filter_box = tk.Frame(toolbar, bg=self.bg_card)
        filter_box.pack(side=tk.LEFT, padx=(4, 10))

        tk.Label(filter_box, text="🔍 Filter:", font=("Segoe UI", 8), fg=self.text_muted, bg=self.bg_card).pack(side=tk.LEFT, padx=(0, 4))
        self.lib_filter_var = tk.StringVar()
        self.lib_filter_entry = tk.Entry(
            filter_box,
            textvariable=self.lib_filter_var,
            bg=self.bg_subtle,
            fg=self.text_main,
            insertbackground=self.text_main,
            relief=tk.FLAT,
            font=("Segoe UI", 9),
            width=24,
        )
        self.lib_filter_entry.pack(side=tk.LEFT, ipady=2)
        self.lib_filter_var.trace_add("write", lambda *_: self.filter_library_table())

        export_selected_btn = tk.Button(
            toolbar,
            text="💾 Save As & Export...",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_green,
            fg="#ffffff",
            activebackground=self.accent_green_hover,
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.export_selected_library_item,
        )
        export_selected_btn.pack(side=tk.LEFT, padx=(0, 6))

        load_to_quick_btn = tk.Button(
            toolbar,
            text="⚡ Load to Quick",
            font=("Segoe UI", 9),
            bg=self.bg_subtle,
            fg=self.text_highlight,
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.load_selected_to_quick,
        )
        load_to_quick_btn.pack(side=tk.LEFT, padx=(0, 6))

        export_all_btn = tk.Button(
            toolbar,
            text="⚡ Bulk Export All",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_orange,
            fg="#ffffff",
            activebackground=self.accent_orange_hover,
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.export_all_library_items,
        )
        export_all_btn.pack(side=tk.LEFT)

        self.lib_count_lbl = tk.Label(toolbar, text="Discovering...", font=("Segoe UI", 9), fg=self.text_muted, bg=self.bg_card)
        self.lib_count_lbl.pack(side=tk.RIGHT)

        # Treeview Table
        tree_frame = tk.Frame(container, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("project", "clip", "size", "modified")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Drafts.Treeview")
        self.tree.heading("project", text="CapCut Project Name")
        self.tree.heading("clip", text="Material Clip Title")
        self.tree.heading("size", text="Size")
        self.tree.heading("modified", text="Date Cached")

        self.tree.column("project", width=240)
        self.tree.column("clip", width=220)
        self.tree.column("size", width=90, anchor="e")
        self.tree.column("modified", width=140, anchor="center")

        self.tree.bind("<Double-1>", lambda e: self.export_selected_library_item())

        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # -------------------------------------------------------------
    # TAB 3: BATCH QUEUE
    # -------------------------------------------------------------
    def setup_batch_tab(self):
        container = tk.Frame(self.tab_batch, bg=self.bg_root, pady=10)
        container.pack(fill=tk.BOTH, expand=True)

        batch_toolbar = tk.Frame(container, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1, padx=12, pady=8)
        batch_toolbar.pack(fill=tk.X, pady=(0, 10))

        add_folder_btn = tk.Button(
            batch_toolbar,
            text="📁 Add Folder to Queue...",
            font=("Segoe UI", 9, "bold"),
            bg=self.bg_subtle,
            fg=self.text_main,
            relief=tk.FLAT,
            padx=12,
            pady=5,
            cursor="hand2",
            command=self.batch_add_folder,
        )
        add_folder_btn.pack(side=tk.LEFT, padx=(0, 8))

        clear_btn = tk.Button(
            batch_toolbar,
            text="🗑 Clear Queue",
            font=("Segoe UI", 9),
            bg=self.bg_subtle,
            fg=self.text_muted,
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.batch_clear,
        )
        clear_btn.pack(side=tk.LEFT)

        self.batch_start_btn = tk.Button(
            batch_toolbar,
            text="🚀 Process Queue",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_green,
            fg="#ffffff",
            relief=tk.FLAT,
            padx=16,
            pady=5,
            cursor="hand2",
            command=self.batch_process,
        )
        self.batch_start_btn.pack(side=tk.RIGHT)

        list_frame = tk.Frame(container, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.batch_listbox = tk.Listbox(
            list_frame,
            bg="#0d1117",
            fg=self.text_main,
            selectbackground=self.accent_orange,
            selectforeground="#ffffff",
            font=("Consolas", 9),
            relief=tk.FLAT,
            highlightthickness=0,
        )
        self.batch_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.batch_listbox.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.batch_listbox.config(yscrollcommand=scroll.set)

    # -------------------------------------------------------------
    # TAB 4: ABOUT & PRODUCTION
    # -------------------------------------------------------------
    def setup_about_tab(self):
        container = tk.Frame(self.tab_about, bg=self.bg_root, pady=16, padx=20)
        container.pack(fill=tk.BOTH, expand=True)

        about_card = tk.Frame(container, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1, pady=16, padx=20)
        about_card.pack(fill=tk.X, pady=(0, 14))

        tk.Label(about_card, text="CapCut Cache Recover", font=("Segoe UI", 16, "bold"), fg=self.text_main, bg=self.bg_card).pack(anchor="w")
        tk.Label(
            about_card,
            text="Autonomous ByteDance Video Cryptor (BDVE Type 1) Stream Recovery Engine",
            font=("Segoe UI", 9),
            fg=self.text_highlight,
            bg=self.bg_card,
        ).pack(anchor="w", pady=(2, 10))

        desc = (
            "CapCut Cache Recover is an open-source forensic recovery utility engineered to salvage and repair\n"
            "unplayable CapCut & JianYing draft cache videos and bitstreams without quality loss.\n\n"
            "Key Innovations:\n"
            "• Direct Bitstream XOR Inversion: Decrypts 50MB video in under 0.3s without re-encoding.\n"
            "• Automatic CapCut Project Discovery: Reads master project databases across drives.\n"
            "• Interoperability & Forensic Research: Built under 17 U.S.C. § 1201(f) reverse engineering exemptions.\n"
        )
        tk.Label(about_card, text=desc, font=("Segoe UI", 9), fg=self.text_main, bg=self.bg_card, justify=tk.LEFT).pack(anchor="w", pady=(0, 12))

        btn_box = tk.Frame(about_card, bg=self.bg_card)
        btn_box.pack(anchor="w")

        fund_btn = tk.Button(
            btn_box,
            text="⚡ Fund the Production →",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_orange,
            fg="#ffffff",
            activebackground=self.accent_orange_hover,
            relief=tk.FLAT,
            padx=14,
            pady=5,
            cursor="hand2",
            command=lambda: webbrowser.open(SUPPORT_URL),
        )
        fund_btn.pack(side=tk.LEFT, padx=(0, 8))

        github_btn = tk.Button(
            btn_box,
            text="View Source on GitHub (★ Star)",
            font=("Segoe UI", 9),
            bg=self.bg_subtle,
            fg=self.text_highlight,
            relief=tk.FLAT,
            padx=12,
            pady=5,
            cursor="hand2",
            command=lambda: webbrowser.open(GITHUB_URL),
        )
        github_btn.pack(side=tk.LEFT)

    # -------------------------------------------------------------
    # BACKGROUND AUTO-DISCOVERY & PROJECT MANAGEMENT
    # -------------------------------------------------------------
    def start_background_discovery(self):
        """Dispatches autonomous discovery of all projects and draft clips across disks."""
        def worker():
            self.set_busy(True, "Auto-discovering CapCut projects and draft streams...")
            self.log("[*] Starting CapCut project discovery scan...")

            # 1. Discover all projects
            projects = discover_capcut_projects()
            self.discovered_projects = projects
            self.log(f"[+] Discovered {len(projects)} CapCut projects across disk roots.")

            # Update UI dropdown and chips on main thread
            self.root.after(0, self.update_projects_ui)

            # 2. Progressively index clips for library table
            found_clips: list[Path] = []
            seen: set[str] = set()

            for proj in projects:
                clips = get_project_encrypted_clips(proj.folder)
                for c in clips:
                    c_key = str(c.resolve()).lower()
                    if c_key not in seen:
                        seen.add(c_key)
                        found_clips.append(c)

            # Fallback across all draft roots
            for r in get_default_draft_paths():
                for v in find_encrypted_videos(r):
                    v_key = str(v.resolve()).lower()
                    if v_key not in seen:
                        seen.add(v_key)
                        found_clips.append(v)

            self.draft_items = found_clips
            self.root.after(0, lambda: self.populate_library_table(found_clips))
            self.set_busy(False, f"Indexed {len(projects)} projects • {len(found_clips)} draft clips ready.")
            self.log(f"[+] Total {len(found_clips)} encrypted video clips ready for immediate export.")

        threading.Thread(target=worker, daemon=True).start()

    def update_projects_ui(self):
        """Updates the Project Combobox and Quick Chips with discovered projects."""
        count = len(self.discovered_projects)
        self.proj_badge_lbl.config(
            text=f"⚡ Auto-Discovered: {count} CapCut Projects (Ready)",
            fg=self.text_highlight if count > 0 else self.accent_orange,
        )
        self.status_lbl.config(text=f"● {count} CapCut Projects Auto-Detected  │  Ready.")

        if not self.discovered_projects:
            self.project_combo["values"] = ["No CapCut projects found"]
            return

        combo_values = []
        for p in self.discovered_projects:
            date_str = time.strftime("%b %d", time.localtime(p.modified_time)) if p.modified_time else ""
            combo_values.append(f"{p.name}  [{date_str}]")

        self.project_combo["values"] = combo_values
        self.project_combo.current(0)
        self.on_project_combo_selected(None)

        # Update Quick Project Chips (top 4 recent projects)
        for child in self.chips_inner.winfo_children():
            child.destroy()

        for proj in self.discovered_projects[:4]:
            btn = tk.Button(
                self.chips_inner,
                text=f"⚡ {proj.name[:20]}",
                font=("Segoe UI", 8),
                bg=self.bg_subtle,
                fg=self.text_main,
                activebackground=self.border_color,
                relief=tk.FLAT,
                padx=6,
                pady=1,
                cursor="hand2",
                command=lambda p=proj: self.select_project_direct(p),
            )
            btn.pack(side=tk.LEFT, padx=3)

    def select_project_direct(self, proj: CapCutProject):
        """Directly selects a project from a quick chip."""
        for i, p in enumerate(self.discovered_projects):
            if p.folder == proj.folder:
                self.project_combo.current(i)
                self.on_project_combo_selected(None)
                break

    def on_project_combo_selected(self, event):
        """Called when a user chooses a project from the combobox."""
        idx = self.project_combo.current()
        if idx < 0 or idx >= len(self.discovered_projects):
            return

        proj = self.discovered_projects[idx]
        clips = get_project_encrypted_clips(proj.folder)
        self.current_project_clips = clips

        if not clips:
            self.clip_combo["values"] = ["No encrypted clips in this draft"]
            self.clip_combo.current(0)
            self.log(f"[*] Project '{proj.name}' selected. No encrypted cache streams found (media may be already exported).")
            return

        clip_labels = []
        for c in clips:
            meta = resolve_capcut_metadata(c)
            size_s = format_size(c.stat().st_size)
            clip_labels.append(f"{meta.clip_name or c.name} ({size_s})")

        self.clip_combo["values"] = clip_labels
        self.clip_combo.current(0)
        # Automatically load first clip
        self.load_file(clips[0])

    def on_clip_combo_selected(self, event):
        idx = self.clip_combo.current()
        if 0 <= idx < len(self.current_project_clips):
            self.load_file(self.current_project_clips[idx])

    def load_selected_project_clip(self):
        idx = self.clip_combo.current()
        if 0 <= idx < len(self.current_project_clips):
            self.load_file(self.current_project_clips[idx])

    def populate_library_table(self, found_files: list[Path]):
        """Populates the Projects & Drafts library table with resolved names."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.library_raw_data = []
        for vf in found_files:
            try:
                meta = resolve_capcut_metadata(vf)
                size_str = format_size(vf.stat().st_size)
                mtime_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(vf.stat().st_mtime))
                proj_name = meta.project_name
                clip_name = meta.clip_name or vf.name
                item_tuple = (proj_name, clip_name, size_str, mtime_str, vf)
                self.library_raw_data.append(item_tuple)
                self.tree.insert("", tk.END, values=(proj_name, clip_name, size_str, mtime_str), tags=(str(vf),))
            except Exception:
                continue

        count = len(self.library_raw_data)
        self.lib_count_lbl.config(text=f"{len(self.discovered_projects)} projects • {count} clips ready")

    def filter_library_table(self):
        """Filters the library table rows in real time based on user query."""
        query = self.lib_filter_var.get().strip().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)

        for proj, clip, size, mtime, vf in self.library_raw_data:
            if not query or query in proj.lower() or query in clip.lower() or query in str(vf).lower():
                self.tree.insert("", tk.END, values=(proj, clip, size, mtime), tags=(str(vf),))

    def load_selected_to_quick(self):
        """Loads selected row from library into Quick Export tab."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Draft", "Please select a draft video from the table first.")
            return

        item_tags = self.tree.item(selected[0], "tags")
        if item_tags:
            src = Path(item_tags[0])
            if src.exists():
                self.load_file(src)
                self.notebook.select(self.tab_quick)

    # -------------------------------------------------------------
    # LOGIC & WORKERS
    # -------------------------------------------------------------
    def log(self, message: str):
        self.quick_log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.quick_log_text.see(tk.END)

    def set_busy(self, busy: bool, message: str = ""):
        self.is_busy = busy
        if busy:
            self.prog_bar.start(10)
            self.export_btn.config(state=tk.DISABLED)
            self.status_lbl.config(text=message, fg=self.accent_orange)
        else:
            self.prog_bar.stop()
            self.export_btn.config(state=tk.NORMAL)
            self.status_lbl.config(text=message or "Ready.", fg=self.text_muted)

    def open_output_dir(self):
        dest = self.default_output_dir
        dest.mkdir(parents=True, exist_ok=True)
        if sys.platform.startswith("win"):
            os.startfile(dest)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(dest)])
        else:
            subprocess.run(["xdg-open", str(dest)])

    def play_last_exported(self):
        if self.last_exported_file and self.last_exported_file.exists():
            if sys.platform.startswith("win"):
                os.startfile(self.last_exported_file)
            elif sys.platform == "darwin":
                subprocess.run(["open", str(self.last_exported_file)])
            else:
                subprocess.run(["xdg-open", str(self.last_exported_file)])

    def browse_single_file(self):
        fn = filedialog.askopenfilename(
            title="Select CapCut Video",
            filetypes=[("Video / Cache Files", "*.mp4;*.mov;*.tmp;*.cache;*.mp4_temp"), ("All Files", "*.*")],
        )
        if fn:
            self.load_file(Path(fn))

    def export_single_file(self, prompt_save_as: bool = True):
        file_str = self.file_path_var.get().strip()
        if not file_str or file_str == "No file selected.":
            messagebox.showwarning("Select Video", "Please select a project or drag a CapCut cache video file first.")
            return

        src = Path(file_str)
        if not src.exists():
            messagebox.showerror("Error", f"File does not exist:\n{src}")
            return

        self.default_output_dir.mkdir(parents=True, exist_ok=True)
        target_name = self.current_meta.suggested_filename if self.current_meta else f"{src.stem}_exported.mp4"

        if prompt_save_as:
            chosen_path = filedialog.asksaveasfilename(
                parent=self.root,
                title="Save Exported Video As...",
                initialdir=str(self.default_output_dir),
                initialfile=target_name,
                defaultextension=".mp4",
                filetypes=[("MP4 Video (*.mp4)", "*.mp4"), ("All Files (*.*)", "*.*")],
            )
            if not chosen_path:
                self.log("[-] Export cancelled by user.")
                return
            dest = Path(chosen_path)
        else:
            dest = self.default_output_dir / target_name

        def worker():
            self.set_busy(True, f"Exporting {dest.name}...")
            self.log(f"Starting export: {src.name} -> {dest.name}")
            try:
                start_t = time.perf_counter()
                params = recover_file(src, dest, log=lambda m: self.log(f"  {m}"))
                elapsed = time.perf_counter() - start_t
                self.log(f"[+] Decrypted in {elapsed:.2f}s! Key: 0x{params.key:02X}, Step: {params.step:,} B")

                val = validate_mp4(dest)
                if val.is_valid:
                    self.log(f"[+] MP4 Container: PASS ({val.duration_seconds}s | {val.video_width}x{val.video_height})")

                self.last_exported_file = dest
                self.play_last_btn.config(state=tk.NORMAL)
                self.set_busy(False, f"Exported: {dest.name}")
                self.log(f"[SUCCESS] Clean video ready at:\n    {dest}")

                if messagebox.askyesno("Export Complete", f"Successfully exported:\n{dest.name}\n\nPlay video now?"):
                    self.play_last_exported()

            except Exception as e:
                self.log(f"[-] Error: {e}")
                self.set_busy(False, "Export failed.")
                messagebox.showerror("Export Failed", str(e))

        threading.Thread(target=worker, daemon=True).start()

    def export_selected_library_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Draft", "Please select a draft video from the library table first.")
            return

        item_tags = self.tree.item(selected[0], "tags")
        if not item_tags:
            return

        src = Path(item_tags[0])
        if not src.exists():
            messagebox.showerror("Not Found", f"File no longer exists:\n{src}")
            return

        meta = resolve_capcut_metadata(src)
        self.default_output_dir.mkdir(parents=True, exist_ok=True)

        chosen_path = filedialog.asksaveasfilename(
            parent=self.root,
            title=f"Save As - {meta.get_display_title()}",
            initialdir=str(self.default_output_dir),
            initialfile=meta.suggested_filename,
            defaultextension=".mp4",
            filetypes=[("MP4 Video (*.mp4)", "*.mp4"), ("All Files (*.*)", "*.*")],
        )
        if not chosen_path:
            return

        dest = Path(chosen_path)
        dest.parent.mkdir(parents=True, exist_ok=True)

        def worker():
            self.set_busy(True, f"Exporting {dest.name}...")
            self.log(f"Exporting library clip: {meta.get_display_title()} -> {dest.name}")
            try:
                start_t = time.perf_counter()
                params = recover_file(src, dest, log=lambda m: self.log(f"  {m}"))
                elapsed = time.perf_counter() - start_t
                self.log(f"[+] Decrypted in {elapsed:.2f}s! Key: 0x{params.key:02X}")
                self.last_exported_file = dest
                self.play_last_btn.config(state=tk.NORMAL)
                self.set_busy(False, f"Exported: {dest.name}")

                if messagebox.askyesno("Export Complete", f"Successfully exported:\n{dest.name}\n\nPlay video now?"):
                    self.play_last_exported()
            except Exception as e:
                self.log(f"[-] Error: {e}")
                self.set_busy(False, "Export failed.")
                messagebox.showerror("Export Failed", str(e))

        threading.Thread(target=worker, daemon=True).start()

    def export_all_library_items(self):
        if not self.draft_items:
            messagebox.showinfo("No Drafts", "No draft clips currently in library. Click 'Rescan' first.")
            return

        out_dir = self.default_output_dir
        out_dir.mkdir(parents=True, exist_ok=True)

        def worker():
            self.set_busy(True, f"Bulk exporting {len(self.draft_items)} drafts with clean project names...")
            success_count = 0
            for i, src in enumerate(self.draft_items, 1):
                meta = resolve_capcut_metadata(src)
                dest = out_dir / meta.suggested_filename
                self.log(f"[{i}/{len(self.draft_items)}] Exporting {meta.project_name} -> {dest.name}...")
                try:
                    recover_file(src, dest)
                    success_count += 1
                except Exception as err:
                    self.log(f"[-] Failed {src.name}: {err}")

            self.set_busy(False, f"Bulk export finished: {success_count}/{len(self.draft_items)} exported.")
            messagebox.showinfo("Done", f"Successfully exported {success_count} video(s) to:\n{out_dir}")

        threading.Thread(target=worker, daemon=True).start()

    def batch_add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder to Scan for CapCut Videos")
        if folder:
            p = Path(folder)
            candidates = list(find_encrypted_videos(p))
            for c in candidates:
                self.batch_listbox.insert(tk.END, str(c))
            self.log(f"Added {len(candidates)} file(s) from '{p.name}' to queue.")

    def batch_clear(self):
        self.batch_listbox.delete(0, tk.END)

    def batch_process(self):
        items = [Path(self.batch_listbox.get(i)) for i in range(self.batch_listbox.size())]
        if not items:
            messagebox.showwarning("Empty", "Queue is empty. Add a folder first.")
            return

        out_dir = self.default_output_dir
        out_dir.mkdir(parents=True, exist_ok=True)

        def worker():
            self.set_busy(True, f"Processing queue of {len(items)} items...")
            for i, src in enumerate(items, 1):
                meta = resolve_capcut_metadata(src)
                dest = out_dir / meta.suggested_filename
                self.log(f"[{i}/{len(items)}] Processing: {meta.get_display_title()}")
                try:
                    recover_file(src, dest)
                except Exception as e:
                    self.log(f"[-] Error on {src.name}: {e}")

            self.set_busy(False, "Queue completed.")
            messagebox.showinfo("Queue Finished", f"Finished processing {len(items)} videos!")

        threading.Thread(target=worker, daemon=True).start()

    def refresh_stats(self):
        self.log(f"System ready. Default output: {self.default_output_dir}")


def launch_gui(initial_file: str | None = None):
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = ExportCapcutProApp(root, initial_file=initial_file)
    root.mainloop()


if __name__ == "__main__":
    init_f = sys.argv[1] if len(sys.argv) > 1 else None
    launch_gui(init_f)
