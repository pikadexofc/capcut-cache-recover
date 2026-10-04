"""Modern, zero-dependency Dark Mode GUI for Export Capcut Pro Video Free."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import __version__
from .cryptor import recover_file, DecodeError
from .scanner import find_encrypted_videos, get_default_draft_paths
from .validator import validate_mp4


class ExportCapcutProGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Export Capcut Pro Video Free v" + __version__)
        self.root.geometry("640x580")
        self.root.minsize(560, 480)
        self.root.configure(bg="#121417")

        self.apply_theme()
        self.build_ui()

    def apply_theme(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Color palette
        self.bg_dark = "#121417"
        self.card_bg = "#1b1e23"
        self.border_color = "#2d333b"
        self.accent_blue = "#0070f3"
        self.accent_hover = "#005bb5"
        self.accent_green = "#10b981"
        self.text_main = "#f0f6fc"
        self.text_dim = "#8b949e"

        style.configure("TProgressbar", thickness=8, troughcolor="#21262d", background=self.accent_blue)
        style.configure("TScrollbar", troughcolor=self.bg_dark, background="#30363d")

    def build_ui(self):
        # Header Container
        header_frame = tk.Frame(self.root, bg=self.bg_dark, pady=16)
        header_frame.pack(fill=tk.X, padx=20)

        title_lbl = tk.Label(
            header_frame,
            text="🎬 Export Capcut Pro Video Free",
            font=("Segoe UI", 16, "bold"),
            fg=self.text_main,
            bg=self.bg_dark,
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            header_frame,
            text="Unlock, decrypt, and export unplayable CapCut & JianYing draft cache videos with 0% loss.",
            font=("Segoe UI", 9),
            fg=self.text_dim,
            bg=self.bg_dark,
        )
        subtitle_lbl.pack(anchor="w", pady=(2, 0))

        # Main Card
        card = tk.Frame(self.root, bg=self.card_bg, highlightbackground=self.border_color, highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))

        # Action 1: Auto Scan Button
        action_box = tk.Frame(card, bg=self.card_bg, pady=14, padx=16)
        action_box.pack(fill=tk.X)

        self.auto_btn = tk.Button(
            action_box,
            text="⚡ 1-Click Auto Scan & Export All Drafts",
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_blue,
            fg="#ffffff",
            activebackground=self.accent_hover,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.start_auto_scan,
        )
        self.auto_btn.pack(fill=tk.X)

        # Divider
        div_frame = tk.Frame(card, bg=self.card_bg, pady=5)
        div_frame.pack(fill=tk.X, padx=16)
        tk.Label(div_frame, text="— OR SELECT INDIVIDUAL FILE —", font=("Segoe UI", 8, "bold"), fg=self.text_dim, bg=self.card_bg).pack()

        # File Select Row
        file_box = tk.Frame(card, bg=self.card_bg, padx=16, pady=6)
        file_box.pack(fill=tk.X)

        self.file_entry = tk.Entry(
            file_box,
            font=("Segoe UI", 9),
            bg="#0d1117",
            fg=self.text_main,
            insertbackground=self.text_main,
            relief=tk.FLAT,
            highlightbackground=self.border_color,
            highlightthickness=1,
        )
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 8))

        browse_btn = tk.Button(
            file_box,
            text="Browse...",
            font=("Segoe UI", 9, "bold"),
            bg="#21262d",
            fg=self.text_main,
            activebackground="#30363d",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.browse_file,
        )
        browse_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.export_single_btn = tk.Button(
            file_box,
            text="Export Video",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_green,
            fg="#ffffff",
            activebackground="#059669",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=14,
            pady=4,
            cursor="hand2",
            command=self.start_single_export,
        )
        self.export_single_btn.pack(side=tk.LEFT)

        # Progress bar
        self.prog_bar = ttk.Progressbar(card, mode="indeterminate", style="TProgressbar")
        self.prog_bar.pack(fill=tk.X, padx=16, pady=(10, 6))

        # Log Window
        log_box = tk.Frame(card, bg=self.card_bg, padx=16, pady=4)
        log_box.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            log_box,
            bg="#0d1117",
            fg=self.text_main,
            font=("Consolas", 8),
            relief=tk.FLAT,
            highlightbackground=self.border_color,
            highlightthickness=1,
            wrap=tk.WORD,
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = ttk.Scrollbar(log_box, orient=tk.VERTICAL, command=self.log_text.yview, style="TScrollbar")
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scroll.set)

        # Bottom Bar Container
        bottom_bar = tk.Frame(self.root, bg=self.bg_dark)
        bottom_bar.pack(fill=tk.X, padx=20, pady=(0, 16))

        self.status_lbl = tk.Label(bottom_bar, text="Ready.", font=("Segoe UI", 9), fg=self.text_dim, bg=self.bg_dark)
        self.status_lbl.pack(side=tk.LEFT)

        self.open_folder_btn = tk.Button(
            bottom_bar,
            text="📂 Open Output Folder",
            font=("Segoe UI", 8, "bold"),
            bg="#21262d",
            fg=self.text_main,
            activebackground="#30363d",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            state=tk.DISABLED,
            command=self.open_output_folder,
        )
        self.open_folder_btn.pack(side=tk.RIGHT)

        self.last_output_dir = None
        self.log("Ready. Drop a video or click 'Auto Scan & Export All Drafts' to begin.")

    def log(self, message: str):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select CapCut Draft Video",
            filetypes=[("Video / Cache Files", "*.mp4;*.mov;*.tmp;*.cache"), ("All Files", "*.*")],
        )
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)

    def open_output_folder(self):
        if self.last_output_dir and Path(self.last_output_dir).exists():
            if sys.platform.startswith("win"):
                os.startfile(self.last_output_dir)
            elif sys.platform == "darwin":
                subprocess.run(["open", str(self.last_output_dir)])
            else:
                subprocess.run(["xdg-open", str(self.last_output_dir)])

    def set_busy(self, is_busy: bool, message: str = ""):
        if is_busy:
            self.prog_bar.start(10)
            self.auto_btn.config(state=tk.DISABLED)
            self.export_single_btn.config(state=tk.DISABLED)
            self.status_lbl.config(text=message, fg=self.accent_blue)
        else:
            self.prog_bar.stop()
            self.auto_btn.config(state=tk.NORMAL)
            self.export_single_btn.config(state=tk.NORMAL)
            self.status_lbl.config(text=message or "Ready.", fg=self.text_dim)

    def start_single_export(self):
        file_str = self.file_entry.get().strip()
        if not file_str:
            messagebox.showwarning("No File", "Please select a CapCut video file first.")
            return

        src = Path(file_str)
        if not src.exists():
            messagebox.showerror("Not Found", f"File does not exist:\n{src}")
            return

        dest = src.parent / f"{src.stem}_exported.mp4"
        self.last_output_dir = src.parent
        self.open_folder_btn.config(state=tk.NORMAL)

        def worker():
            self.set_busy(True, f"Exporting {src.name}...")
            self.log(f"[*] Exporting: {src.name}")
            try:
                params = recover_file(src, dest, log=lambda m: self.log(f"    {m}"))
                self.log(f"[+] Decryption complete! (Key: 0x{params.key:02X}, Step: {params.step})")
                val = validate_mp4(dest)
                if val.is_valid:
                    self.log(f"[+] Verified MP4: {val.duration_seconds}s | {val.video_width}x{val.video_height}")
                self.log(f"[SUCCESS] Exported video:\n    {dest}")
                self.set_busy(False, "Export complete!")
                # Open the video or folder
                if messagebox.askyesno("Success", f"Video exported successfully!\n\nLocation: {dest.name}\n\nWould you like to play it now?"):
                    if sys.platform.startswith("win"):
                        os.startfile(dest)
                    elif sys.platform == "darwin":
                        subprocess.run(["open", str(dest)])
            except Exception as e:
                self.log(f"[-] Export error: {e}")
                self.set_busy(False, "Error during export.")
                messagebox.showerror("Export Failed", str(e))

        threading.Thread(target=worker, daemon=True).start()

    def start_auto_scan(self):
        draft_paths = get_default_draft_paths()
        if not draft_paths:
            messagebox.showinfo("No Drafts", "No standard CapCut or JianYing draft folders detected.")
            return

        out_dir = Path.home() / "Desktop" / "Exported_CapCut_Videos"
        out_dir.mkdir(parents=True, exist_ok=True)
        self.last_output_dir = out_dir
        self.open_folder_btn.config(state=tk.NORMAL)

        def worker():
            self.set_busy(True, "Scanning CapCut drafts...")
            self.log(f"[*] Scanning {len(draft_paths)} draft root location(s)...")

            all_candidates = []
            for p in draft_paths:
                self.log(f"    Scanning: {p}")
                candidates = list(find_encrypted_videos(p))
                all_candidates.extend(candidates)

            if not all_candidates:
                self.log("[*] No BDVE-encrypted draft videos pending export.")
                self.set_busy(False, "No encrypted videos found.")
                messagebox.showinfo("Done", "No encrypted draft cache videos found.")
                return

            self.log(f"[+] Found {len(all_candidates)} encrypted video(s)! Exporting to Desktop...")
            success_count = 0
            for i, src in enumerate(all_candidates, 1):
                dest = out_dir / f"{src.stem.replace('_video', '')}_exported.mp4"
                self.log(f"[{i}/{len(all_candidates)}] Processing: {src.name}...")
                try:
                    recover_file(src, dest)
                    val = validate_mp4(dest)
                    if val.is_valid:
                        self.log(f"    [OK] {val.duration_seconds}s | {val.video_width}x{val.video_height}")
                    success_count += 1
                except Exception as err:
                    self.log(f"    [FAIL] {err}")

            self.log(f"\n[DONE] Successfully exported {success_count}/{len(all_candidates)} videos to:\n    {out_dir}")
            self.set_busy(False, f"Exported {success_count} videos!")
            messagebox.showinfo("Finished", f"Successfully exported {success_count} video(s) to:\n{out_dir}")

        threading.Thread(target=worker, daemon=True).start()


def launch_gui():
    root = tk.Tk()
    app = ExportCapcutProGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
