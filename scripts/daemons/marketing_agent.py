"""Zero-Token Autonomous Marketing & Content Generation Daemon.

Powered by PixelPie Media & Zero-Token Multi-LLM Fleet (Groq/Gemini/Mistral).
Generates high-converting blog posts, Reddit technical writeups, and social distribution assets
at 0 agent context token cost.
"""

import os
import sys
import time
from pathlib import Path

# Add project daemons directory to sys.path
DAEMONS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DAEMONS_DIR))

try:
    from llm_client import generate_text
except ImportError:
    generate_text = None


PROMPTS = [
    {
        "platform": "reddit_r_videoediting",
        "title": "Reverse-engineering CapCut's BDVE draft cache encryption: How to recover unplayable MP4s",
        "prompt": "Write an educational, first-principles technical breakdown for r/VideoEditing and r/reverseengineering explaining how ByteDance obfuscates draft cache videos using periodic XOR masking (BDVE Type 1) and trailer metadata, and how our open-source tool 'Export Capcut Pro Video Free' (by PixelPie Media) mathematically derives parameters to restore the bitstream in 0.3s without re-encoding."
    },
    {
        "platform": "dev_to_article",
        "title": "How I Solved CapCut's 'moov atom not found' Bug with 50 Lines of Python",
        "prompt": "Write a viral dev.to / Hashnode blog post with code snippets showing how to reverse-engineer MP4 atom structures (ftyp, mdat, moov, crpt) and decrypt ByteDance cache videos. Mention the GitHub repo: https://github.com/pikadexofc/export-capcut-pro-video-free and developer Md. Zobaed Islam Shanto."
    },
    {
        "platform": "twitter_thread",
        "title": "Viral X Thread: Exporting CapCut Pro Videos Free",
        "prompt": "Write a punchy, 5-tweet viral thread explaining how to export CapCut Pro draft cache videos 100% free with 0% quality loss using our standalone open-source app. Include hashtags #CapCut #VideoEditing #OpenSource and link to releases."
    }
]


def run_marketing_sprint():
    out_dir = DAEMONS_DIR / "generated_marketing"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[*] Starting Zero-Token Marketing Generation Sprint. Output: {out_dir}")

    for item in PROMPTS:
        target_file = out_dir / f"{item['platform']}.md"
        print(f"[*] Generating content for: {item['platform']}...")
        if generate_text:
            try:
                res = generate_text(item["prompt"])
                content = res if isinstance(res, str) else str(res)
                target_file.write_text(content, encoding="utf-8")
                print(f"[+] Wrote: {target_file.name} ({len(content)} chars)")
            except Exception as e:
                print(f"[-] LLM generation fallback on {item['platform']}: {e}")
        else:
            print("[-] llm_client not initialized, writing template.")


if __name__ == "__main__":
    run_marketing_sprint()
