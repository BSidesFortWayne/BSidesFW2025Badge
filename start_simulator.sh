#!/usr/bin/env bash
#
# Quick start script - helps users choose the right mode
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

clear
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║     BSides FW 2025 Badge Simulator - Quick Start          ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo -e "${GREEN}The simulator now has AUTOMATIC setup!${NC}"
echo ""
echo "Just run:"
echo ""
echo -e "  ${BLUE}cd simulator/  
echo -e "  ./run.sh${NC}"
echo ""
echo "The script automatically:"
echo "  • Detects MicroPython → uses Native Mode (fastest)"
echo "  • If not found → tries to install it (brew/apt/dnf/pacman)"
echo "  • If install fails → offers Hybrid Mode with Docker"
echo "  • Installs pygame if needed"
echo "  • Handles everything for you!"
echo ""
echo "────────────────────────────────────────────────────────"
echo ""
read -p "Run simulator now? [Y/n]: " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    cd "$SCRIPT_DIR/simulator"
    exec ./run.sh
else
    echo ""
    echo "To run later:"
    echo "  cd simulator/"
    echo "  ./run.sh"
    echo ""
fi
