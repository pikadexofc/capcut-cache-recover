#!/data/data/com.termux/files/usr/bin/bash
# install-termux.sh - 1-Line Termux Installer for CapCut Cache Recover
# Engineered by PixelPie Media • Founded by Md. Zobaed Islam Shanto

set -e

echo "=========================================================="
echo "   🎬 CapCut Cache Recover - Termux Mobile Setup"
echo "   PixelPie Media • Precision Software Engineering"
echo "=========================================================="
echo ""

# 1. Update packages and install python and git
echo "[1/4] Ensuring Python and Git are installed..."
pkg update -y
pkg install -y python git clang

# 2. Setup Termux Storage Access
echo "[2/4] Setting up storage permissions..."
termux-setup-storage || true

# 3. Clone or update repository
INSTALL_DIR="$HOME/capcut-cache-recover"
if [ -d "$INSTALL_DIR" ]; then
    echo "[3/4] Updating existing installation..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    echo "[3/4] Downloading CapCut Cache Recover..."
    git clone https://github.com/pikadexofc/export-capcut-pro-video-free.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# 4. Install python package
echo "[4/4] Registering mobile CLI commands..."
pip install -e .

# 5. Create handy alias in bashrc
BASHRC="$HOME/.bashrc"
ALIAS_CMD="alias capcut-recover='python -m capcut_cache_recover.cli'"
if ! grep -q "capcut-recover" "$BASHRC" 2>/dev/null; then
    echo "$ALIAS_CMD" >> "$BASHRC"
    echo "alias capcut-export='python -m capcut_cache_recover.cli'" >> "$BASHRC"
fi

echo ""
echo "=========================================================="
echo "  ✅ Termux Installation Complete!"
echo "=========================================================="
echo "Commands available:"
echo "  • capcut-cache-recover"
echo "  • capcut-recover"
echo ""
echo "Quick Test:"
echo "  capcut-recover --recent"
echo ""
echo "Your recovered videos will be saved directly to your phone storage!"
echo ""
