# BSides FW 2025 Badge Simulator

A high-performance simulator for developing and testing badge applications without physical hardware.

## 🚀 Quick Start

### One Command Setup

```bash
cd simulator/
./run.sh
```

**That's it!** The script automatically:
- ✅ Detects if MicroPython is available → uses **Native Mode** (fastest)
- ✅ If not, offers to install MicroPython (brew/apt/dnf/pacman)
- ✅ Falls back to **Hybrid Mode** with Docker if needed
- ✅ Installs pygame if needed
- ✅ Prompts before any installations

### Manual Mode Selection (Optional)

```bash
./run.sh --native    # Force native mode (requires MicroPython)
./run.sh --docker    # Force hybrid/Docker mode
./run.sh --setup     # Run interactive setup wizard (deprecated - auto setup recommended)
```

---

## Modes Explained

The script automatically chooses the best mode for your system:

### ⚡ Native Mode (Auto-selected if MicroPython available)
**Everything runs natively** - fastest performance
- MicroPython and pygame run natively on your system
- Best performance for development
- Requires: MicroPython, pygame

### 🐳 Hybrid Mode (Auto-selected if no MicroPython)
**MicroPython in Docker, GUI native** - easiest setup
- No MicroPython installation needed
- Works everywhere
- Requires: Docker, pygame

You can force a specific mode with `--native` or `--docker` flags if needed.

---
- ✅ **Binary protocol** - 10-20x faster rendering
- ✅ **Hardware controls** - Mock sensors and peripherals
- ✅ **Dual displays** - Both 240x240 circular screens
- ✅ **Button emulation** - Keyboard keys 0-7

## Features

### High Performance Binary Protocol
- ⚡ 10-20x faster than JSON protocol
- ⚡ `blit_buffer(240x240)` in ~5ms vs ~100ms
- ⚡ Eliminates screen artifacting
- ✨ Smooth 60 FPS rendering

### Hardware Control Panel
The right panel lets you mock hardware:
- 🎮 **Accelerometer** (X/Y/Z axes + shake button)
- 🔋 **Battery** voltage slider
- ⚡ **Charge** state toggle
- 📡 **WiFi** state simulation
- 🔵 **Bluetooth** state simulation

### Log Panel
The bottom panel shows real-time logs:
- 📝 Last 100 log messages
- 🔵 **Blue**: INFO messages
- 🟠 **Orange**: WARNING messages
- 🔴 **Red**: ERROR messages
- ⏱️ Timestamps on all entries
- 👁️ Toggle visibility with "▼ Hide Log Panel" button

### Keyboard Controls

| Key | Hardware Button | Description |
|-----|----------------|-------------|
| `0` | SW5 | Boot/Reset |
| `1` | SW1 | Button A (top) |
| `2` | SW2 | Button B (top) |
| `3` | SW3 | Button C (top) |
| `4` | SW4 | Button D (top) |
| `7` | SW7 | Game button 1 |
| `8` | SW8 | Game button 2 |
| `9` | SW9 | Game button 3 |

### Mouse Controls

**Clickable Button Areas:**
- Click directly on the badge button images to trigger presses
- Semi-transparent circles show clickable areas
- Buttons highlight **green** when pressed
- Works alongside keyboard controls

## Requirements

The auto setup handles installation, but here's what you need:

**Python Packages (auto-installed if needed):**
- pygame
- pillow
- pygame-gui

**MicroPython (auto-detected or auto-installed):**
The script will offer to install MicroPython if not found. Manual installation:

```bash
# Linux (Debian/Ubuntu)
sudo apt update && sudo apt install micropython

# Linux (Fedora)
sudo dnf install micropython

# macOS (Homebrew)
brew install micropython

# Windows - Use WSL, then follow Linux instructions:
wsl --install
```

**Docker (fallback if MicroPython unavailable):**
If MicroPython install fails or is declined, the script will use Docker automatically.

> **Note:** Just run `./run.sh` - it handles everything!

## Usage

### Running the Simulator

```bash
# Run with auto-detection (recommended)
./run.sh

# With custom project directory
./run.sh -p /path/to/your/project

# Verbose output for debugging
./run.sh -v

# Force specific mode
./run.sh --native    # Requires MicroPython
./run.sh --docker    # Requires Docker

# See all options
./run.sh --help
```

## Configuration

The simulator auto-configures itself. Advanced users can customize `config.json`:

```json
{
  "project_path": "../src",
  "micropython_path": "micropython",
  "socket_port": 4455,
  "binary_port": 4456,
  "logging": {
    "enabled": true,
    "output_dir": "logs"
  },
  "gui": {
    "show_fps": true,
    "target_fps": 60
  }
}
```

> **Note:** Config is optional - the script uses sensible defaults.

## How It Works

```
┌─────────────────┐           ┌──────────────────┐
│  Badge App      │           │  Pygame GUI      │
│  (MicroPython)  │◄─────────►│                  │
│                 │  Binary/  │  • Display       │
│  Fake Drivers   │   JSON    │  • Controls      │
│  (Shims)        │           │  • LEDs          │
└─────────────────┘           └──────────────────┘
   Port: N/A          127.0.0.1:4455/4456
```

1. **Setup**: Copies `src/` to `simulator/src/`
2. **Overlay**: Installs hardware shims (fake drivers)
3. **Boot Sequence**: Runs `boot.py` then `main.py` (matches hardware behavior)
4. **Launch**: Starts MicroPython with your badge code
5. **IPC**: Socket communication for commands
6. **Render**: Pygame displays the badge screens

### Boot Sequence

The simulator replicates the **exact hardware boot sequence**:
- Runs `boot.py` first (sets up displays, hardware)
- Then runs `main.py` (starts controller and apps)
- Variables from `boot.py` (like `displays`) are available in `main.py`
- This matches real hardware behavior where boot.py runs on power-up

## Development Workflow

### IMPORTANT: Edit Files in `src/`, Not `simulator/src/`

The simulator **copies** your project files to `simulator/src/` at startup.

- ✅ **DO**: Edit files in `src/apps/`, `src/lib/`, etc.
- ❌ **DON'T**: Edit files in `simulator/src/` (changes will be lost)
- After editing `src/`, restart the simulator to pick up changes

### Testing Your App

```bash
# 1. Create/edit your app
vim src/apps/my_app.py

# 2. Run simulator
cd simulator/
uv run ./run.sh

# 3. Navigate to your app using buttons
# 4. Check logs/ for errors
```

### Performance Testing

For apps using `blit_buffer()` and framebuffers:

```python
# Your app (src/apps/my_app.py)
import framebuf
import gc9a01

# Create framebuffer
buf = bytearray(240 * 240 * 2)
fb = framebuf.FrameBuffer(buf, 240, 240, framebuf.RGB565)

# Draw to framebuffer
fb.fill(0xF800)  # Red
fb.rect(10, 10, 100, 100, 0xFFFF)

# Blit to display (FAST with binary protocol)
display.blit_buffer(buf, 0, 0, 240, 240)
```

The binary protocol makes this 10-20x faster than the old JSON protocol.

## Troubleshooting

### "No MicroPython found"

```bash
# Install system package
sudo apt install micropython

# Or check PATH
which micropython
```

### "pygame not found"

```bash
pip install pygame pillow pygame-gui
```

### Port already in use

```bash
# Change ports
uv run ./run.sh --port 4460 --binary-port 4461

# Or kill existing process
pkill -f simulator.py
```

### MicroPython crashes on startup

```bash
# Check logs
cat logs/simulator_*.log

# Run verbose
uv run ./run.sh -v

# Verify your code works
cd ../src
uv run micropython main.py
```

### Black screens / No display

- Check that your app draws to displays
- Verify MicroPython output for errors
- Ensure `blit_buffer()` or drawing commands are being called

### Low FPS

The binary protocol should give you 60 FPS. If not:
- Check CPU usage
- Look for Python exceptions in logs
- Verify your app isn't blocking with `time.sleep()`

## File Structure

```
simulator/
├── simulator.py          # Main entry point
├── run.sh               # Launcher script
├── setup_wizard.py      # Interactive setup
├── gui_enhanced.py      # Enhanced GUI (hardware controls)
├── gui_binary.py        # Binary protocol handler
├── logger.py            # Logging utilities
├── config.json          # Configuration (created by setup)
├── libraries/           # Hardware shims (fake drivers)
│   ├── gc9a01.py        # Display driver shim
│   ├── gc9a01_binary.py # Binary protocol display driver
│   ├── pca9535.py       # Button controller shim
│   ├── machine.py       # machine module shim
│   └── ...              # Other hardware shims
├── fonts/               # Bitmap fonts for GUI
├── logs/                # Log output (created at runtime)
└── src/                 # Project copy (created at runtime)
```

## Performance Comparison

| Operation | Old (JSON) | New (Binary) | Speedup |
|-----------|-----------|--------------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) - Complete architecture, protocols, and design decisions
- [BUTTON_MAPPING.md](BUTTON_MAPPING.md) - Hardware button reference
- [REGRESSION_TEST_GUIDE.md](REGRESSION_TEST_GUIDE.md) - Automated testing guide
- [SCREENSHOT_GUIDE.md](SCREENSHOT_GUIDE.md) - Screenshot tool usage
| Single pixel | ~0.5ms | ~0.1ms | **5x** |

**The binary protocol is essential for smooth animations.**

## Additional Documentation

- `BUTTON_MAPPING.md` - Hardware button reference
- `../docs/SIMULATOR_*.md` - Architecture docs
- `Advanced Features

### Screenshot Capture

Capture screenshots from the running simulator:

```bash
# Basic screenshot (badge displays only)
python simulator/take_screenshot.py --output my_badge.png

# Include control panel and log window
python simulator/take_screenshot.py --output full_sim.png --include-controls
```

Screenshots are saved to the `screenshots/` directory by default.

See [SCREENSHOT_GUIDE.md](SCREENSHOT_GUIDE.md) for more details.

### Regression Testing

Automated testing for badge apps:

```bash
# Run a regression test
python simulator/regression_test.py demo_regression_test.py

# Tests can:
# - Navigate apps
# - Trigger button sequences
# - Capture screenshots
# - Compare against baselines
```

See [REGRESSION_TEST_GUIDE.md](REGRESSION_TEST_GUIDE.md) for more details.

## FAQ

**Q: How do I start the simulator?**  
A: Just run `./run.sh` - it handles everything automatically!

**Q: Do I need to install anything first?**  
A: No! The script detects what's missing and offers to install it.

**Q: Which mode should I use?**  
A: Just run `./run.sh` - it automatically picks the best mode for your system.

**Q: Do I need to run setup every time?**  
A: No, only the first run for installations. After that, just use `./run.sh`.

**Q: Can I use this for WiFi/Bluetooth features?**  
A: WiFi and Bluetooth state can be mocked, but actual network functionality is not simulated.

**Q: Is this 100% accurate to real hardware?**  
A: Very close, but not perfect. Always test critical features on real hardware before deployment.

**Q: Can I run multiple simulators at once?**  
A: Yes, but use different ports:
```bash
./run.sh --port 4460 --binary-port 4461
```

**Q: Why are my changes to `simulator/src/` not persisting?**  
A: `simulator/src/` is auto-generated at startup. Always edit files in `../src/` instead.

## Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: See `../docs/` directory
- **Logs**: Check `logs/` for detailed error information

---

**Made with ❤️ for BSides FW 2025**
