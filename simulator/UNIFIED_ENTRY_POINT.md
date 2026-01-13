# Unified Simulator Entry Point - Release Notes

## 🎯 Summary

**One command to rule them all:** `./run.sh` now automatically detects your environment and sets up everything for you.

## What Changed

### Before (Manual Mode Selection)
```bash
# Users had to choose and use separate scripts:
./run.sh --setup     # Native mode setup
# Hybrid mode was separate script (now removed)
./start_simulator.sh # Interactive menu
```

### After (Automatic Detection)
```bash
# Just one command:
cd simulator/
./run.sh

# Automatically:
# ✓ Detects MicroPython availability
# ✓ Chooses best mode (Native or Hybrid)  
# ✓ Installs pygame if needed
# ✓ Prompts before any installations
```

## How It Works

### Detection Logic

1. **Check pygame** (needed for both modes)
   - If missing → offer to install
   
2. **Check MicroPython**
   - ✅ Available → Use **Native Mode** (fastest)
   - ❌ Not available → Try to install it
   
3. **Try Install MicroPython** (if not found)
   - Detect package manager (brew, apt, dnf, pacman)
   - Attempt automatic installation with user confirmation
   - ✅ Success → Use **Native Mode**
   - ❌ Failed/Declined → Check Docker
   
4. **Check Docker** (if MicroPython install failed)
   - ✅ Available → Use **Hybrid Mode** (easiest)
   - ❌ Not available → Error (need one or the other)

### User Experience

```
╔════════════════════════════════════════════════╗
║  BSides FW 2025 Badge Simulator               ║
╚════════════════════════════════════════════════╝

ℹ Auto-detected: MicroPython available → using NATIVE mode

▶ Running in NATIVE mode
ℹ MicroPython and pygame both running natively

[Simulator starts]
```

Or if no MicroPython:

```
╔════════════════════════════════════════════════╗
║  BSides FW 2025 Badge Simulator               ║
╚════════════════════════════════════════════════╝

⚠ MicroPython not found on your system

Attempting automatic installation...

Try to install MicroPython now? [Y/n]: y

▶ Attempting to install MicroPython...
  Using Homebrew...
ℹ MicroPython installed successfully via Homebrew

ℹ MicroPython installed! Will use Native Mode.
ℹ Using newly installed MicroPython → NATIVE mode

▶ Running in NATIVE mode
[Simulator starts]
```

Or if installation fails/declined:

```
⚠ Automatic installation failed

Fallback options:

1) Use Hybrid Mode with Docker
   • MicroPython runs in Docker (no install needed)
   • Pygame GUI runs natively (reliable display)

2) Install MicroPython Manually
   • Linux:   sudo apt install micropython
   • macOS:   brew install micropython
   • Windows: Use WSL, then: sudo apt install micropython

ℹ Docker is available ✓

Use Hybrid Mode with Docker? [Y/n]:
```

## Manual Overrides

Users can still force a specific mode:

```bash
./run.sh --native    # Force native (requires MicroPython)
./run.sh --docker    # Force hybrid (requires Docker)
./run.sh --setup     # Run interactive setup wizard
./run.sh --help      # Show all options
```

## Benefits

### For New Users
- ✅ **Zero configuration** - just run it
- ✅ **Automatic fallback** - uses Docker if no MicroPython
- ✅ **Clear prompts** - explains what it's doing
- ✅ **No wrong choices** - script picks the best option

### For Experienced Users
- ✅ **Smart detection** - uses native if available (fastest)
- ✅ **Manual override** - can force specific mode
- ✅ **Non-interactive** - respects CI/automation
- ✅ **Backward compatible** - old flags still work

### For Teams
- ✅ **Consistent command** - everyone runs same thing
- ✅ **Adapts to environment** - works on any setup
- ✅ **Self-documenting** - clear output about what's happening
- ✅ **No decision paralysis** - automatic mode selection

## Technical Details

### Environment Detection

**MicroPython Search Path:**
1. `command -v micropython` (system PATH)
2. `$HOME/.local/bin/micropython` (user install)
3. `$(pwd)/bin/micropython` (local install)

**Docker Detection:**
- Checks `docker` command exists
- Verifies Docker daemon is running (`docker info`)

**Pygame Detection:**
- Attempts `python3 -c "import pygame"`

### Container Management

When using Hybrid Mode:
- Container name: `bsides-badge-micropython-$$` (unique per process)
- Automatic cleanup on exit (trap EXIT INT TERM)
- Logs available: `docker logs bsides-badge-micropython-<pid>`

### Installation Prompts

All installations require confirmation:
```bash
Install pygame now? [Y/n]:
Use Hybrid Mode with Docker? [Y/n]:
```

Non-interactive mode (CI/automation) gets sensible defaults.

## Migration Guide

### From Old Scripts

**Old:**
```bash
./run.sh                     # Native mode only
./start_simulator.sh         # Interactive menu
# (Hybrid mode was separate)
```

**New:**
```bash
./run.sh                     # Auto-detects (all modes in one)
./run.sh --docker            # Explicit hybrid
./run.sh --native            # Explicit native
```

### Backward Compatibility

All functionality consolidated into `run.sh`:
- Hybrid mode: `./run.sh --docker`
- Native mode: `./run.sh --native` or `./run.sh`
- Setup wizard: `./run.sh --setup`

## Files Changed

### Modified
- `simulator/run.sh` - Complete rewrite with smart detection and all modes
- `start_simulator.sh` - Simplified to redirect to unified script
- `simulator/README.md` - Updated quick start section
- `README.md` - Simplified simulator instructions
- `SIMULATOR_MODES.md` - Updated command reference

### Removed
- `simulator/run_hybrid.sh` - Functionality merged into `run.sh`

## Examples

### First-Time User (No MicroPython)
```bash
$ cd simulator/
$ ./run.sh

╔════════════════════════════════════════════════╗
║  BSides FW 2025 Badge Simulator               ║
╚════════════════════════════════════════════════╝

▶ Installing pygame dependencies...
✓ pygame installed successfully

⚠ MicroPython not found on your system

Use Hybrid Mode with Docker? [Y/n]: y

▶ Building MicroPython Docker image...
▶ Starting MicroPython container...
ℹ MicroPython running in container

▶ Running in HYBRID mode
ℹ MicroPython in Docker, pygame GUI native

[Simulator GUI launches]
```

### Experienced User (Has MicroPython)
```bash
$ cd simulator/
$ ./run.sh

╔════════════════════════════════════════════════╗
║  BSides FW 2025 Badge Simulator               ║
╚════════════════════════════════════════════════╝

ℹ Auto-detected: MicroPython available → using NATIVE mode

▶ Running in NATIVE mode
ℹ MicroPython and pygame both running natively

[Simulator launches immediately]
```

### Forcing a Mode
```bash
$ ./run.sh --docker

╔════════════════════════════════════════════════╗
║  BSides FW 2025 Badge Simulator               ║
╚════════════════════════════════════════════════╝

▶ Building MicroPython Docker image...
[etc...]
```

## Testing

To test the detection logic without running:

```bash
# Check what would be detected
which micropython || echo "Would use Docker mode"

# Force specific modes to test
./run.sh --native    # Test native path
./run.sh --docker    # Test Docker path
```

## Troubleshooting

### "MicroPython not found"
The script will offer Docker mode automatically.
Accept to use Hybrid Mode, or install MicroPython.

### "Docker not available"
Install Docker or install MicroPython natively.

### "Pygame not found"
Script will offer to install it automatically.

### Container won't start
Check Docker logs:
```bash
docker logs bsides-badge-micropython-<pid>
```

## Future Enhancements

Possible additions:
- [ ] Auto-rebuild Docker image if Dockerfile changes
- [ ] Cache mode selection for faster subsequent runs
- [ ] Detect container image age and suggest rebuild
- [ ] Performance profiling to recommend mode
- [ ] WSL detection for Windows users

## Summary

The simulator is now truly "zero-config":

1. Clone repo
2. `cd simulator/`
3. `./run.sh`
4. Done!

No need to understand modes, make decisions, or install specific dependencies. The script handles everything automatically while still allowing expert users to override when needed.
