#!/usr/bin/env bash
#
# BSides FW 2025 Badge Simulator - Smart Auto-Setup
#
# This script automatically detects your environment and chooses the best mode:
# - Native mode if MicroPython is available
# - Hybrid mode (Docker) if MicroPython is not available
# - Auto-installs dependencies as needed
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Mode tracking
MODE=""
USE_DOCKER=0
MICROPYTHON_CONTAINER_NAME="bsides-badge-micropython-$$"

# Cleanup function
cleanup() {
    if [ $USE_DOCKER -eq 1 ] && [ -n "$MICROPYTHON_CONTAINER_NAME" ]; then
        echo ""
        echo -e "${BLUE}Cleaning up...${NC}"
        docker stop "$MICROPYTHON_CONTAINER_NAME" &>/dev/null || true
        docker rm "$MICROPYTHON_CONTAINER_NAME" &>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

print_banner() {
    echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  BSides FW 2025 Badge Simulator               ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${GREEN}▶${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

show_help() {
    echo "Usage: ./run.sh [options]"
    echo ""
    echo "The script automatically detects your environment and chooses:"
    echo "  • Native mode if MicroPython is available"
    echo "  • Hybrid mode (Docker) if MicroPython is not available"
    echo ""
    echo "Options:"
    echo "  --setup              Force run setup wizard"
    echo "  --native             Force native mode (requires MicroPython)"
    echo "  --docker             Force hybrid/Docker mode"
    echo "  -p PATH              Project directory (default: ../src)"
    echo "  -v                   Verbose output"
    echo "  --help               Show this help"
    echo ""
    echo "Advanced:"
    echo "  --port PORT          JSON protocol port (default: 4455)"
    echo "  --binary-port PORT   Binary protocol port (default: 4456)"
    echo ""
    echo "Examples:"
    echo "  ./run.sh             # Auto-detect and run"
    echo "  ./run.sh --docker    # Force Docker mode"
    echo "  ./run.sh --native    # Force native mode"
    echo ""
}

check_micropython() {
    # Try various MicroPython locations
    if command -v micropython &>/dev/null; then
        return 0
    elif [ -f "$HOME/.local/bin/micropython" ]; then
        return 0
    elif [ -f "$(pwd)/bin/micropython" ]; then
        return 0
    fi
    return 1
}

check_docker() {
    command -v docker &>/dev/null && docker info &>/dev/null
}

check_pygame() {
    python3 -c "import pygame" 2>/dev/null
}

install_pygame() {
    print_step "Installing pygame dependencies..."
    
    if command -v uv &>/dev/null; then
        uv pip install pygame pygame-gui Pillow || pip3 install pygame pygame-gui Pillow
    else
        pip3 install pygame pygame-gui Pillow
    fi
}

install_micropython() {
    print_step "Attempting to install MicroPython..."
    
    # Detect package manager and try installation
    if command -v brew &>/dev/null; then
        echo "  Using Homebrew..."
        if brew install micropython; then
            print_info "MicroPython installed successfully via Homebrew"
            return 0
        fi
    elif command -v apt-get &>/dev/null; then
        echo "  Using apt..."
        if sudo apt-get update && sudo apt-get install -y micropython; then
            print_info "MicroPython installed successfully via apt"
            return 0
        fi
    elif command -v dnf &>/dev/null; then
        echo "  Using dnf..."
        if sudo dnf install -y micropython; then
            print_info "MicroPython installed successfully via dnf"
            return 0
        fi
    elif command -v pacman &>/dev/null; then
        echo "  Using pacman..."
        if sudo pacman -S --noconfirm micropython; then
            print_info "MicroPython installed successfully via pacman"
            return 0
        fi
    else
        print_warning "No supported package manager found (brew, apt, dnf, pacman)"
        return 1
    fi
    
    return 1
}

offer_micropython_install() {
    echo ""
    print_warning "MicroPython not found on your system"
    echo ""
    
    # Try automatic installation
    echo "Attempting automatic installation..."
    echo ""
    
    if [ -t 0 ]; then  # Interactive terminal
        read -p "Try to install MicroPython now? [Y/n]: " -n 1 -r
        echo ""
        
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            if install_micropython; then
                echo ""
                print_info "MicroPython installed! Will use Native Mode."
                return 2  # Signal to retry MicroPython check
            fi
            
            print_warning "Automatic installation failed"
        fi
    fi
    
    # If installation failed or declined, offer Docker
    echo ""
    echo "Fallback options:"
    echo ""
    echo -e "${GREEN}1) Use Hybrid Mode with Docker${NC}"
    echo "   • MicroPython runs in Docker (no install needed)"
    echo "   • Pygame GUI runs natively (reliable display)"
    echo ""
    echo -e "${BLUE}2) Install MicroPython Manually${NC}"
    echo "   • Linux:   sudo apt install micropython"
    echo "   • macOS:   brew install micropython"
    echo "   • Windows: Use WSL, then: sudo apt install micropython"
    echo ""
    
    if check_docker; then
        print_info "Docker is available ✓"
        echo ""
        read -p "Use Hybrid Mode with Docker? [Y/n]: " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            echo ""
            echo "Please install MicroPython manually and try again."
            exit 1
        else
            return 0  # Use Docker
        fi
    else
        print_error "Docker is not available either"
        echo ""
        echo "Please install one of:"
        echo "  • MicroPython (for Native Mode - fastest)"
        echo "  • Docker (for Hybrid Mode - easiest)"
        echo ""
        exit 1
    fi
}

build_docker_image() {
    print_step "Building MicroPython Docker image..."
    
    if [ ! -f "Dockerfile.micropython" ]; then
        print_error "Dockerfile.micropython not found!"
        exit 1
    fi
    
    docker build -t bsides-badge-micropython -f Dockerfile.micropython .. || {
        print_error "Failed to build Docker image"
        exit 1
    }
}

start_micropython_container() {
    print_step "Starting MicroPython container..."
    
    # Stop any existing container with same name
    docker stop "$MICROPYTHON_CONTAINER_NAME" &>/dev/null || true
    docker rm "$MICROPYTHON_CONTAINER_NAME" &>/dev/null || true
    
    # Start container
    docker run -d \
        --name "$MICROPYTHON_CONTAINER_NAME" \
        --network host \
        -v "$(cd .. && pwd)/src:/workspace/src:ro" \
        bsides-badge-micropython \
        micropython -c "
import sys
sys.path.append('/workspace')
import src.main
" || {
        print_error "Failed to start MicroPython container"
        docker logs "$MICROPYTHON_CONTAINER_NAME" 2>&1 | head -20
        exit 1
    }
    
    # Give it a moment to start
    sleep 2
    
    # Verify it's running
    if ! docker ps --format '{{.Names}}' | grep -q "^${MICROPYTHON_CONTAINER_NAME}$"; then
        print_error "MicroPython container failed to start!"
        echo ""
        echo "Container logs:"
        docker logs "$MICROPYTHON_CONTAINER_NAME"
        exit 1
    fi
    
    print_info "MicroPython running in container (logs: docker logs $MICROPYTHON_CONTAINER_NAME)"
}

run_native_mode() {
    print_step "Running in NATIVE mode"
    print_info "MicroPython and pygame both running natively"
    echo ""
    
    # Run with uv if available, otherwise direct python
    if command -v uv &>/dev/null; then
        exec uv run python3 simulator.py "$@"
    else
        exec python3 simulator.py "$@"
    fi
}

run_hybrid_mode() {
    print_step "Running in HYBRID mode"
    print_info "MicroPython in Docker, pygame GUI native"
    echo ""
    
    # Build image if needed
    if ! docker images | grep -q "bsides-badge-micropython"; then
        build_docker_image
    fi
    
    # Start MicroPython container
    start_micropython_container
    
    echo ""
    print_info "Starting pygame GUI (native)..."
    echo ""
    
    # Run GUI natively
    if command -v uv &>/dev/null; then
        uv run python3 gui.py "$@"
    else
        python3 gui.py "$@"
    fi
}

# Main logic
main() {
    print_banner
    
    # Parse arguments
    FORCE_MODE=""
    FORCE_SETUP=0
    EXTRA_ARGS=()
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --setup)
                FORCE_SETUP=1
                shift
                ;;
            --native)
                FORCE_MODE="native"
                shift
                ;;
            --docker)
                FORCE_MODE="docker"
                shift
                ;;
            *)
                EXTRA_ARGS+=("$1")
                shift
                ;;
        esac
    done
    
    # Run setup wizard if requested
    if [ $FORCE_SETUP -eq 1 ]; then
        print_step "Running setup wizard..."
        exec uv run python3 setup_wizard.py
    fi
    
    # Check pygame (needed for both modes)
    if ! check_pygame; then
        print_warning "Pygame not installed"
        
        if [ -t 0 ]; then  # Interactive terminal
            read -p "Install pygame now? [Y/n]: " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                install_pygame
            fi
        else
            install_pygame
        fi
        
        # Verify installation
        if ! check_pygame; then
            print_error "Pygame installation failed"
            exit 1
        fi
    fi
    
    # Determine mode
    if [ "$FORCE_MODE" = "native" ]; then
        # Forced native mode
        if ! check_micropython; then
            print_error "Native mode requested but MicroPython not found!"
            echo ""
            echo "Install MicroPython:"
            echo "  Linux:   sudo apt install micropython"
            echo "  macOS:   brew install micropython"
            echo "  Windows: Use WSL, then: sudo apt install micropython"
            exit 1
        fi
        MODE="native"
        
    elif [ "$FORCE_MODE" = "docker" ]; then
        # Forced Docker mode
        if ! check_docker; then
            print_error "Docker mode requested but Docker not available!"
            echo ""
            echo "Install Docker: https://docs.docker.com/get-docker/"
            exit 1
        fi
        MODE="docker"
        USE_DOCKER=1
        
    else
        # Auto-detect mode
        if check_micropython; then
            MODE="native"
            print_info "Auto-detected: MicroPython available → using NATIVE mode"
        else
            # Try to install MicroPython or use Docker
            install_result=$(offer_micropython_install)
            result_code=$?
            
            if [ $result_code -eq 2 ]; then
                # MicroPython was installed, retry check
                if check_micropython; then
                    MODE="native"
                    print_info "Using newly installed MicroPython → NATIVE mode"
                else
                    print_error "MicroPython installation reported success but not found in PATH"
                    echo "You may need to restart your shell or add it to PATH manually"
                    exit 1
                fi
            elif [ $result_code -eq 0 ]; then
                # User chose Docker
                MODE="docker"
                USE_DOCKER=1
                print_info "Using HYBRID mode (MicroPython in Docker)"
            else
                print_error "Unable to determine mode"
                exit 1
            fi
        fi
    fi
    
    echo ""
    
    # Run appropriate mode
    if [ "$MODE" = "native" ]; then
        run_native_mode "${EXTRA_ARGS[@]}"
    elif [ "$MODE" = "docker" ]; then
        run_hybrid_mode "${EXTRA_ARGS[@]}"
    else
        print_error "Unable to determine mode"
        exit 1
    fi
}

# Run main
main "$@"
