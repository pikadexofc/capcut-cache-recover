"""Standalone single-file unified launcher for CapCut Cache Recover.

Handles both GUI launch on double-click and Drag-and-Drop / CLI processing when arguments are passed.
"""

import sys
from capcut_cache_recover.cli import main
from capcut_cache_recover.gui import launch_gui

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.exit(main())
    else:
        launch_gui()
