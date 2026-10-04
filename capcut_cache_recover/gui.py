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
from .scanner import find_encrypted_videos, get_default_draft_paths
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
        self.root.geometry("840x650")
        self.root.minsize(740, 580)
        self.root.configure(bg="#0d1117")

        # Global State
        self.default_output_dir = Path.home() / "Desktop" / "Exported_CapCut_Videos"
        self.last_exported_file: Path | None = None
        self.draft_items: list[Path] = []
        self.current_meta: ProjectMetadata | None = None
        self.is_busy = False

        self.apply_theme()
        self.build_ui()
        self.enable_drag_and_drop()

        if initial_file:
            self.load_file(Path(initial_file))
        else:
            self.refresh_stats()

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
        # 1. TOP HEADER BRAND BAR (Clean, Non-Slop, No Cheap Top Buttons)
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
        self.notebook.add(self.tab_library, text="  📁 Draft Library  ")
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
        self.root.bind("<Control-r>", lambda e: self.populate_draft_library())
        self.root.bind("<Control-R>", lambda e: self.populate_draft_library())

        # 3. GLOBAL PROGRESS BAR
        self.prog_bar = ttk.Progressbar(self.root, mode="indeterminate", style="Orange.Horizontal.TProgressbar")
        self.prog_bar.pack(fill=tk.X, padx=20, pady=(0, 6))

        # 4. BOTTOM STATUS FOOTER BAR
        footer = tk.Frame(self.root, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1, pady=8, padx=16)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_lbl = tk.Label(footer, text="Ready. Drag & drop video or press Ctrl+O.", font=("Segoe UI", 9), fg=self.text_muted, bg=self.bg_card)
        self.status_lbl.pack(side=tk.LEFT)

        shortcuts_hint = tk.Label(footer, text="Ctrl+O: Open  │  Ctrl+S: Save As  │  Ctrl+R: Scan", font=("Consolas", 8), fg=self.text_muted, bg=self.bg_card)
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

        # Clean Windows path formatting (e.g. {C:\path with spaces\video.mp4})
        clean_path = raw_data.strip("{}").strip('"').strip("'")
        # If multiple files dropped, take the first one
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
        self.log(f"[+] Loaded: {file_path.name}")
        self.log(f"    - Detected Project: {meta.project_name}")
        if meta.clip_name:
            self.log(f"    - Detected Clip:    {meta.clip_name}")
        self.log(f"    - Clean Target:     {meta.suggested_filename}")

    # -------------------------------------------------------------
    # TAB 1: QUICK EXPORT
    # -------------------------------------------------------------
    def setup_quick_tab(self):
        container = tk.Frame(self.tab_quick, bg=self.bg_root, pady=10)
        container.pack(fill=tk.BOTH, expand=True)

        # Dropzone / Selector Card
        self.drop_card = tk.Frame(container, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1, pady=16, padx=20)
        self.drop_card.pack(fill=tk.X, pady=(0, 10))

        icon_lbl = tk.Label(self.drop_card, text="🎬", font=("Segoe UI Emoji", 26), fg=self.accent_orange, bg=self.bg_card)
        icon_lbl.pack()

        self.drop_title = tk.Label(
            self.drop_card,
            text="Drag & Drop Video Here (or Click to Browse)",
            font=("Segoe UI", 12, "bold"),
            fg=self.text_main,
            bg=self.bg_card,
        )
        self.drop_title.pack(pady=(4, 2))

        drop_sub = tk.Label(
            self.drop_card,
            text="Drop any combination clip, draft cache fragment, or Pro preview (*_video.mp4, .mov, .tmp)",
            font=("Segoe UI", 9),
            fg=self.text_muted,
            bg=self.bg_card,
        )
        drop_sub.pack(pady=(0, 10))

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
            pady=6,
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
            pady=6,
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
            pady=6,
            cursor="hand2",
            command=lambda: self.export_single_file(prompt_save_as=False),
        )
        self.quick_export_btn.pack(side=tk.LEFT, padx=6)

        # Smart Metadata Info Badges
        meta_frame = tk.Frame(self.drop_card, bg=self.bg_subtle, pady=8, padx=12, highlightbackground=self.border_color, highlightthickness=1)
        meta_frame.pack(fill=tk.X, pady=(12, 0))

        self.project_name_var = tk.StringVar(value="📁 Project: Auto-detecting upon selection...")
        self.clip_name_var = tk.StringVar(value="🎬 Material: —")
        self.suggested_name_var = tk.StringVar(value="💾 Output Filename: —")

        tk.Label(meta_frame, textvariable=self.project_name_var, font=("Segoe UI", 9, "bold"), fg=self.accent_orange, bg=self.bg_subtle, anchor="w").pack(fill=tk.X)
        tk.Label(meta_frame, textvariable=self.clip_name_var, font=("Segoe UI", 8), fg=self.text_main, bg=self.bg_subtle, anchor="w").pack(fill=tk.X)
        tk.Label(meta_frame, textvariable=self.suggested_name_var, font=("Consolas", 8), fg=self.text_highlight, bg=self.bg_subtle, anchor="w", pady=(2, 0)).pack(fill=tk.X)

        self.file_path_var = tk.StringVar(value="No file selected.")

        # Console Log Box
        log_frame = tk.Frame(container, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1)
        log_frame.pack(fill=tk.BOTH, expand=True)

        log_head = tk.Frame(log_frame, bg=self.bg_subtle, padx=12, pady=6)
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
            pady=8,
        )
        self.quick_log_text.pack(fill=tk.BOTH, expand=True)

    # -------------------------------------------------------------
    # TAB 2: DRAFT LIBRARY (AUTO-SCAN WITH REAL PROJECT NAMES)
    # -------------------------------------------------------------
    def setup_library_tab(self):
        container = tk.Frame(self.tab_library, bg=self.bg_root, pady=10)
        container.pack(fill=tk.BOTH, expand=True)

        toolbar = tk.Frame(container, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1, padx=12, pady=8)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        scan_btn = tk.Button(
            toolbar,
            text="🔄 Scan Drafts (Ctrl+R)",
            font=("Segoe UI", 9, "bold"),
            bg=self.bg_subtle,
            fg=self.text_main,
            activebackground=self.border_color,
            relief=tk.FLAT,
            padx=12,
            pady=5,
            cursor="hand2",
            command=self.populate_draft_library,
        )
        scan_btn.pack(side=tk.LEFT, padx=(0, 8))

        export_selected_btn = tk.Button(
            toolbar,
            text="💾 Save As & Export Selected...",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_green,
            fg="#ffffff",
            activebackground=self.accent_green_hover,
            relief=tk.FLAT,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self.export_selected_library_item,
        )
        export_selected_btn.pack(side=tk.LEFT, padx=(0, 8))

        export_all_btn = tk.Button(
            toolbar,
            text="⚡ Bulk Export All to Desktop",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_orange,
            fg="#ffffff",
            activebackground=self.accent_orange_hover,
            relief=tk.FLAT,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self.export_all_library_items,
        )
        export_all_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.lib_count_lbl = tk.Label(toolbar, text="0 drafts indexed", font=("Segoe UI", 9), fg=self.text_muted, bg=self.bg_card)
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

        self.tree.column("project", width=220)
        self.tree.column("clip", width=180)
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

        about_card = tk.Frame(container, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1, pady=24, padx=24)
        about_card.pack(fill=tk.BOTH, expand=True)

        tk.Label(about_card, text="PIXELPIE MEDIA", font=("Segoe UI", 14, "bold"), fg=self.accent_orange, bg=self.bg_card).pack(anchor="w")
        tk.Label(about_card, text="Precision Software Engineering & Systems Design", font=("Segoe UI", 9), fg=self.text_muted, bg=self.bg_card).pack(anchor="w", pady=(0, 16))

        info_text = (
            "CapCut Cache Recover is a zero-friction forensic recovery utility\n"
            "designed to salvage and repair unplayable CapCut & JianYing draft cache videos.\n\n"
            "• Primary Developer:  Md. Zobaed Islam Shanto\n"
            "• Organization:       PixelPie Media\n"
            "• Core Architecture:  BDVE Type 1 Periodic XOR Cryptanalysis Solver\n"
            "• Project Resolution: Real CapCut Project Name & Clip Title Extraction\n"
            "• License:            MIT License (100% Free & Open Source)\n"
            "• Telemetry:          0% (Zero analytics, 100% offline local execution)\n"
        )
        tk.Label(about_card, text=info_text, font=("Consolas", 9), justify=tk.LEFT, fg=self.text_main, bg=self.bg_card).pack(anchor="w", pady=(0, 20))

        # Fund the Production Highlight Box
        support_box = tk.Frame(about_card, bg=self.bg_subtle, padx=16, pady=14, highlightbackground=self.accent_orange, highlightthickness=1)
        support_box.pack(fill=tk.X, pady=(0, 16))

        tk.Label(
            support_box,
            text="⚡ Fund the Production",
            font=("Segoe UI", 11, "bold"),
            fg=self.accent_orange,
            bg=self.bg_subtle,
        ).pack(anchor="w")

        tk.Label(
            support_box,
            text="Help support independent software development, maintenance, and free open-source releases.",
            font=("Segoe UI", 9),
            fg=self.text_main,
            bg=self.bg_subtle,
        ).pack(anchor="w", pady=(2, 8))

        fund_now_btn = tk.Button(
            support_box,
            text="Fund the Production →",
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
        fund_now_btn.pack(anchor="w")

        link_btn = tk.Button(
            about_card,
            text="View Source on GitHub (★ Star)",
            font=("Segoe UI", 9),
            bg=self.bg_subtle,
            fg=self.text_highlight,
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
            command=lambda: webbrowser.open(GITHUB_URL),
        )
        link_btn.pack(anchor="w")

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
            filetypes=[("Video / Cache Files", "*.mp4;*.mov;*.tmp;*.cache"), ("All Files", "*.*")],
        )
        if fn:
            self.load_file(Path(fn))

    def export_single_file(self, prompt_save_as: bool = True):
        file_str = self.file_path_var.get().strip()
        if not file_str or file_str == "No file selected.":
            messagebox.showwarning("Select Video", "Please select or drag a CapCut cache video file first.")
            return

        src = Path(file_str)
        if not src.exists():
            messagebox.showerror("Error", f"File does not exist:\n{src}")
            return

        self.default_output_dir.mkdir(parents=True, exist_ok=True)
        target_name = self.current_meta.suggested_filename if self.current_meta else f"{src.stem}_exported.mp4"

        if prompt_save_as:
            # Native Windows Explorer 'Save As' Dialog (Ctrl+S style)
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
            self.log(f"Starting export for: {src.name} -> {dest.name}")
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
                val = validate_mp4(dest)
                if val.is_valid:
                    self.log(f"[+] Validation PASS ({val.duration_seconds}s)")
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

    def populate_draft_library(self):
        def worker():
            self.set_busy(True, "Scanning CapCut draft folders...")
            for row in self.tree.get_children():
                self.tree.delete(row)

            draft_paths = get_default_draft_paths()
            found_files = []
            for dp in draft_paths:
                self.log(f"Scanning draft root: {dp}")
                for v in find_encrypted_videos(dp):
                    found_files.append(v)

            self.draft_items = found_files
            for vf in found_files:
                meta = resolve_capcut_metadata(vf)
                size_str = format_size(vf.stat().st_size)
                mtime_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(vf.stat().st_mtime))
                self.tree.insert("", tk.END, values=(meta.project_name, meta.clip_name or vf.name, size_str, mtime_str), tags=(str(vf),))

            self.lib_count_lbl.config(text=f"{len(found_files)} drafts detected")
            self.set_busy(False, f"Indexed {len(found_files)} draft videos.")
            self.log(f"Scan complete. Found {len(found_files)} clips with resolved project names.")

        threading.Thread(target=worker, daemon=True).start()

    def export_all_library_items(self):
        if not self.draft_items:
            messagebox.showinfo("No Drafts", "No draft clips currently in library. Click 'Scan Draft Folders' first.")
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
