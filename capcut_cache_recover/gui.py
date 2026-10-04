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

from . import __version__, __tool_name__
from .cryptor import recover_file, DecodeError
from .scanner import find_encrypted_videos, get_default_draft_paths
from .validator import validate_mp4


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
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Export Capcut Pro Video Free  •  PixelPie Media")
        self.root.geometry("820x640")
        self.root.minsize(720, 560)
        self.root.configure(bg="#0d1117")

        # Global State
        self.default_output_dir = Path.home() / "Desktop" / "Exported_CapCut_Videos"
        self.last_exported_file: Path | None = None
        self.draft_items: list[Path] = []
        self.is_busy = False

        self.apply_theme()
        self.build_ui()
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

        # Notebook / Tabs
        self.style.configure(
            "TNotebook",
            background=self.bg_root,
            borderwidth=0,
        )
        self.style.configure(
            "TNotebook.Tab",
            background=self.bg_card,
            foreground=self.text_muted,
            padding=[16, 8],
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", self.bg_subtle), ("active", "#1c2128")],
            foreground=[("selected", self.accent_orange), ("active", self.text_main)],
        )

        # Progressbar
        self.style.configure(
            "Orange.Horizontal.TProgressbar",
            troughcolor=self.bg_card,
            background=self.accent_orange,
            thickness=6,
            borderwidth=0,
        )

        # Treeview for Draft Library
        self.style.configure(
            "Drafts.Treeview",
            background=self.bg_card,
            foreground=self.text_main,
            fieldbackground=self.bg_card,
            borderwidth=0,
            rowheight=26,
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
            text="🎬 Export Capcut Pro Video Free",
            font=("Segoe UI", 16, "bold"),
            fg=self.text_main,
            bg=self.bg_root,
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            header_left,
            text="Precision Cryptographic Video Recovery & Bitstream Export • By PixelPie Media",
            font=("Segoe UI", 9),
            fg=self.text_muted,
            bg=self.bg_root,
        )
        subtitle_lbl.pack(anchor="w", pady=(2, 0))

        # Header Right - Fund Button
        header_right = tk.Frame(top_bar, bg=self.bg_root)
        header_right.pack(side=tk.RIGHT)

        fund_btn = tk.Button(
            header_right,
            text="⚡ Fund the Production",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_orange,
            fg="#ffffff",
            activebackground=self.accent_orange_hover,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=lambda: webbrowser.open(SUPPORT_URL),
        )
        fund_btn.pack(side=tk.RIGHT)

        # 2. MAIN TABBED NAVIGATION
        self.notebook = ttk.Notebook(self.root, style="TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        # Tab Frames
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

        # 3. GLOBAL PROGRESS BAR
        self.prog_bar = ttk.Progressbar(self.root, mode="indeterminate", style="Orange.Horizontal.TProgressbar")
        self.prog_bar.pack(fill=tk.X, padx=20, pady=(0, 6))

        # 4. BOTTOM STATUS FOOTER BAR
        footer = tk.Frame(self.root, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1, pady=8, padx=16)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_lbl = tk.Label(footer, text="Ready. Drag & drop a video or choose an action.", font=("Segoe UI", 9), fg=self.text_muted, bg=self.bg_card)
        self.status_lbl.pack(side=tk.LEFT)

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

    # -------------------------------------------------------------
    # TAB 1: QUICK EXPORT
    # -------------------------------------------------------------
    def setup_quick_tab(self):
        container = tk.Frame(self.tab_quick, bg=self.bg_root, pady=10)
        container.pack(fill=tk.BOTH, expand=True)

        # Dropzone / Selector Card
        drop_card = tk.Frame(container, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1, pady=20, padx=20)
        drop_card.pack(fill=tk.X, pady=(0, 12))

        icon_lbl = tk.Label(drop_card, text="🎬", font=("Segoe UI Emoji", 28), fg=self.accent_orange, bg=self.bg_card)
        icon_lbl.pack()

        drop_title = tk.Label(
            drop_card,
            text="Select Any Unplayable CapCut Cache Video",
            font=("Segoe UI", 12, "bold"),
            fg=self.text_main,
            bg=self.bg_card,
        )
        drop_title.pack(pady=(4, 2))

        drop_sub = tk.Label(
            drop_card,
            text="Supports combination videos, draft cache fragments, and Pro preview blocks (*_video.mp4, .mov, .tmp)",
            font=("Segoe UI", 9),
            fg=self.text_muted,
            bg=self.bg_card,
        )
        drop_sub.pack(pady=(0, 12))

        btn_row = tk.Frame(drop_card, bg=self.bg_card)
        btn_row.pack()

        browse_btn = tk.Button(
            btn_row,
            text="📂 Choose File...",
            font=("Segoe UI", 9, "bold"),
            bg=self.bg_subtle,
            fg=self.text_main,
            activebackground=self.border_color,
            relief=tk.FLAT,
            padx=16,
            pady=7,
            cursor="hand2",
            command=self.browse_single_file,
        )
        browse_btn.pack(side=tk.LEFT, padx=6)

        self.export_btn = tk.Button(
            btn_row,
            text="🚀 Export Video Free",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_green,
            fg="#ffffff",
            activebackground=self.accent_green_hover,
            relief=tk.FLAT,
            padx=20,
            pady=7,
            cursor="hand2",
            command=self.export_single_file,
        )
        self.export_btn.pack(side=tk.LEFT, padx=6)

        # Input & Output path labels
        paths_frame = tk.Frame(drop_card, bg=self.bg_card, pady=8)
        paths_frame.pack(fill=tk.X, pady=(10, 0))

        self.file_path_var = tk.StringVar(value="No file selected.")
        path_display = tk.Label(
            paths_frame,
            textvariable=self.file_path_var,
            font=("Consolas", 8),
            fg=self.text_highlight,
            bg="#0d1117",
            padx=8,
            pady=5,
            anchor="w",
            relief=tk.FLAT,
        )
        path_display.pack(fill=tk.X)

        # Console Log Box
        log_frame = tk.Frame(container, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1)
        log_frame.pack(fill=tk.BOTH, expand=True)

        log_head = tk.Frame(log_frame, bg=self.bg_subtle, padx=12, pady=6)
        log_head.pack(fill=tk.X)
        tk.Label(log_head, text="Live Engine Telemetry", font=("Segoe UI", 8, "bold"), fg=self.text_main, bg=self.bg_subtle).pack(side=tk.LEFT)

        self.quick_log_text = tk.Text(
            log_frame,
            bg="#0d1117",
            fg=self.text_main,
            font=("Consolas", 8),
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=10,
            pady=10,
        )
        self.quick_log_text.pack(fill=tk.BOTH, expand=True)

    # -------------------------------------------------------------
    # TAB 2: DRAFT LIBRARY (AUTO-SCAN)
    # -------------------------------------------------------------
    def setup_library_tab(self):
        container = tk.Frame(self.tab_library, bg=self.bg_root, pady=10)
        container.pack(fill=tk.BOTH, expand=True)

        toolbar = tk.Frame(container, bg=self.bg_card, highlightbackground=self.border_color, highlightthickness=1, padx=12, pady=8)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        scan_btn = tk.Button(
            toolbar,
            text="🔄 Scan Draft Folders",
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

        export_all_btn = tk.Button(
            toolbar,
            text="⚡ Export All Detected Drafts",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_orange,
            fg="#ffffff",
            activebackground=self.accent_orange_hover,
            relief=tk.FLAT,
            padx=16,
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

        columns = ("name", "project", "size", "modified")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Drafts.Treeview")
        self.tree.heading("name", text="File Name")
        self.tree.heading("project", text="Draft Project")
        self.tree.heading("size", text="Size")
        self.tree.heading("modified", text="Date Cached")

        self.tree.column("name", width=220)
        self.tree.column("project", width=180)
        self.tree.column("size", width=90, anchor="e")
        self.tree.column("modified", width=140, anchor="center")

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

        # Batch listbox
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
            "Export Capcut Pro Video Free is a zero-friction reverse-engineering utility\n"
            "designed to unlock and decrypt unplayable CapCut & JianYing draft cache videos.\n\n"
            "• Primary Developer:  Md. Zobaed Islam Shanto\n"
            "• Organization:       PixelPie Media\n"
            "• Core Architecture:  BDVE Type 1 Periodic XOR Cryptanalysis Solver\n"
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

        # GitHub Link
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
            self.file_path_var.set(fn)
            self.log(f"Selected: {Path(fn).name}")

    def export_single_file(self):
        file_str = self.file_path_var.get().strip()
        if not file_str or file_str == "No file selected.":
            messagebox.showwarning("Select Video", "Please select a CapCut cache video file first.")
            return

        src = Path(file_str)
        if not src.exists():
            messagebox.showerror("Error", f"File does not exist:\n{src}")
            return

        self.default_output_dir.mkdir(parents=True, exist_ok=True)
        dest = self.default_output_dir / f"{src.stem.replace('_video', '')}_exported.mp4"

        def worker():
            self.set_busy(True, f"Exporting {src.name}...")
            self.log(f"Starting export for: {src.name} ({format_size(src.stat().st_size)})")
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
                self.log(f"[SUCCESS] Video exported cleanly to:\n    {dest}")

                if messagebox.askyesno("Export Complete", f"Successfully exported:\n{dest.name}\n\nWould you like to play it now?"):
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
                project_name = vf.parent.parent.name if vf.parent.name == "combination" else vf.parent.name
                size_str = format_size(vf.stat().st_size)
                mtime_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(vf.stat().st_mtime))
                self.tree.insert("", tk.END, values=(vf.name, project_name, size_str, mtime_str), tags=(str(vf),))

            self.lib_count_lbl.config(text=f"{len(found_files)} drafts detected")
            self.set_busy(False, f"Indexed {len(found_files)} draft videos.")
            self.log(f"Scan complete. Found {len(found_files)} encrypted clips.")

        threading.Thread(target=worker, daemon=True).start()

    def export_all_library_items(self):
        if not self.draft_items:
            messagebox.showinfo("No Drafts", "No draft clips currently in library. Click 'Scan Draft Folders' first.")
            return

        out_dir = self.default_output_dir
        out_dir.mkdir(parents=True, exist_ok=True)

        def worker():
            self.set_busy(True, f"Bulk exporting {len(self.draft_items)} drafts...")
            success_count = 0
            for i, src in enumerate(self.draft_items, 1):
                dest = out_dir / f"{src.stem.replace('_video', '')}_exported.mp4"
                self.log(f"[{i}/{len(self.draft_items)}] Exporting {src.name}...")
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
                dest = out_dir / f"{src.stem}_exported.mp4"
                self.log(f"[{i}/{len(items)}] Processing: {src.name}")
                try:
                    recover_file(src, dest)
                except Exception as e:
                    self.log(f"[-] Error on {src.name}: {e}")

            self.set_busy(False, "Queue completed.")
            messagebox.showinfo("Queue Finished", f"Finished processing {len(items)} videos!")

        threading.Thread(target=worker, daemon=True).start()

    def refresh_stats(self):
        self.log(f"System ready. Default output: {self.default_output_dir}")


def launch_gui():
    root = tk.Tk()
    app = ExportCapcutProApp(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
