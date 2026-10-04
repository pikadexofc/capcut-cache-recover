"""Background Watcher Daemon for CapCut Cache Recovery.

Monitors configured CapCut / JianYing draft cache folders and automatically
recovers incoming encrypted combination videos in the background at zero token cost.
"""

import sys
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from capcut_cache_recover.scanner import get_default_draft_paths, find_encrypted_videos
from capcut_cache_recover.cryptor import recover_file


def run_watcher(poll_interval: int = 15):
    print(f"[*] CapCut Cache Recovery Watcher Daemon started. Polling every {poll_interval}s...")
    seen_files = set()

    while True:
        try:
            draft_paths = get_default_draft_paths()
            for root in draft_paths:
                for candidate in find_encrypted_videos(root):
                    if candidate in seen_files:
                        continue
                    seen_files.add(candidate)
                    dest = candidate.parent / f"{candidate.stem}_auto_recovered.mp4"
                    print(f"[*] Detected new encrypted file: {candidate.name}")
                    try:
                        recover_file(candidate, dest)
                        print(f"[+] Auto-recovered: {dest}")
                    except Exception as err:
                        print(f"[-] Auto-recovery error on {candidate}: {err}")
        except KeyboardInterrupt:
            print("\n[*] Daemon stopped by user.")
            break
        except Exception as e:
            print(f"[!] Daemon cycle exception: {e}")

        time.sleep(poll_interval)


if __name__ == "__main__":
    run_watcher()
