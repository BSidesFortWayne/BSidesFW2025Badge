# Hybrid Mode: Docker MicroPython + Native GUI

> **Note:** Hybrid mode is now automatically available via `./run.sh`. This document explains how it works internally.

## Overview

This approach gives you the best of both worlds:
- 🐳 **MicroPython runs in Docker** (no native installation needed)
- 🎮 **Pygame GUI runs natively** (reliable display, no X11 forwarding)
- 🔌 **They communicate via sockets** (ports 4455/4456)

## Quick Start

```bash
cd simulator/
./run.sh          # Automatically uses hybrid mode if MicroPython install fails
# or
./run.sh --docker # Force hybrid mode
```

## Why This Approach?

### Advantages
✅ No need to install MicroPython natively (can be tricky on some systems)  
✅ Consistent MicroPython environment across all platforms  
✅ GUI runs natively = reliable display, no X11 issues  
✅ Lightweight container (only ~100MB, no GUI dependencies)  
✅ Easy to update MicroPython version (just rebuild container)  
✅ Works on Linux, macOS, Windows  

### vs Full Dev Container
| Feature | Hybrid Mode | Full Dev Container |
|---------|-------------|-------------------|
| MicroPython consistency | ✅ | ✅ |
| GUI reliability | ✅ (native) | ❌ (X11 forwarding) |
| Setup complexity | Low | High (X11 setup) |
| Display performance | Fast | Slower (protocol overhead) |
| Resource usage | Low | Higher |

### vs Fully Native
| Feature | Hybrid Mode | Fully Native |
|---------|-------------|--------------|
| MicroPython installation | ✅ Easy | ❌ Platform-specific |
| MicroPython version control | ✅ Containerized | ⚠️ System-dependent |
| GUI reliability | ✅ | ✅ |
| No Docker needed | ❌ | ✅ |

## Quick Start

### Prerequisites
1. **Docker** installed and running
2. **Python 3.8+** installed natively (for pygame)

### Running

```bash
cd simulator/
./run.sh --docker    # Force hybrid mode
# or
./run.sh             # Auto-detects and may use hybrid if no MicroPython
```

The `run.sh` script now handles everything automatically:
1. ✅ Checks Docker is running
2. ✅ Installs pygame natively (if needed)
3. ✅ Builds lightweight MicroPython container
4. ✅ Starts MicroPython in container
5. ✅ Launches pygame GUI natively
6. ✅ Cleans up on exit

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Host Machine                                            │
│                                                         │
│  ┌──────────────────┐         ┌──────────────────┐    │
│  │ Docker Container │◄────────┤   Pygame GUI     │    │
│  │                  │ Socket  │   (Native)       │    │
│  │  MicroPython     │ 4455/6  │                  │    │
│  │  + Badge Code    │────────►│   Display        │    │
│  │                  │         │   Rendering      │    │
│  └──────────────────┘         └──────────────────┘    │
│         ▲                                              │
│         │                                              │
│         │ Volume Mount (src/ code)                     │
│         │                                              │
│  ┌──────┴────────────────────────────────────┐        │
│  │  /src/apps/                               │        │
│  │  /src/lib/                                │        │
│  │  /src/drivers/                            │        │
│  └───────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**MicroPython Container:**
- Runs your badge app code
- Executes controller and app logic
- Sends display commands via socket
- Sends LED, button state via socket
- No display/GUI code needed

**Native Pygame GUI:**
- Receives display commands
- Renders to screen
- Handles user input (keyboard → buttons)
- Mock hardware controls (accelerometer, battery, etc.)
- No MicroPython installation needed

### Communication Protocol

They use the existing binary protocol:
- Port 4455: JSON control messages
- Port 4456: Binary display data (fast blit_buffer)

Both run on `localhost`, so no network configuration needed.

## Development Workflow

### 1. Edit Code
Edit files in `src/apps/`, `src/lib/`, etc. using your favorite editor:
```bash
# Edit on host
vim ../src/apps/my_app.py
# or
code ../src/apps/my_app.py
```

### Restarting

The container mounts `src/` as read-only, so:
```bash
# Stop simulator (Ctrl+C)
# Restart to see changes
./run.sh --docker
```

### 3. View Logs
**MicroPython logs (container):**
```bash
docker logs bsides-badge-micropython -f
```

**GUI logs (native terminal):**
Visible in the terminal where you ran `./run.sh`

## Advanced Usage

### Using Docker Compose

For more control:
```bash
# Start MicroPython container
docker-compose up -d micropython

# Run GUI separately
uv run python3 gui.py

# Stop container
docker-compose down
```

### Custom Ports
```bash
# In config.json
{
  "socket_port": 4457,
  "binary_port": 4458
}

# Update docker-compose.yml ports if needed
```

### Debugging MicroPython

Access the container directly:
```bash
docker exec -it bsides-badge-micropython bash

# Inside container
micropython
>>> import src.main
```

### Rebuilding Container

After changing Docker configuration:
```bash
docker build -t bsides-badge-micropython -f Dockerfile.micropython ..

# Or with docker-compose
docker-compose build
```

## Troubleshooting

### "Cannot connect to Docker daemon"
**Solution:** Start Docker Desktop or the Docker daemon
```bash
# Linux
sudo systemctl start docker

# macOS/Windows
# Start Docker Desktop application
```

### "Connection refused" when starting GUI
**Problem:** MicroPython container not running or ports conflict

**Solution:**
```bash
# Check container status
docker ps | grep bsides-badge-micropython

# View container logs
docker logs bsides-badge-micropython

# Check if ports are in use
lsof -i :4455
lsof -i :4456

# Kill conflicting processes or change ports
```

### "pygame not found"
**Problem:** Native pygame not installed

**Solution:**
```bash
# Install with uv
uv pip install pygame pygame-gui Pillow

# Or with pip
pip3 install pygame pygame-gui Pillow
```

### Container keeps restarting
**Problem:** MicroPython code has an error

**Solution:**
```bash
# View logs
docker logs bsides-badge-micropython -f

# Check your app code in src/
# Fix errors and restart
```

### Changes not reflected
**Problem:** Container uses old code

**Solution:**
```bashand restart simulator
# Press Ctrl+C to stop
./run.sh --dockerpt handles this)
./run_hybrid.sh
```

### Performance issues
**Problem:** Display updates slow

**Solution:**
- Ensure binary protocol is enabled (default)
- Check network performance: `docker stats`
- Check logs for errors

## Comparison with Other Modes

### When to Use Hybrid Mode
✅ You want MicroPython in a consistent environment  
✅ You want reliable GUI display  
✅ You're comfortable with Docker  
✅ You want easy MicroPython version management  
✅ You're on macOS/Windows where native MicroPython is tricky  

### When to Use Fully Native
✅ You don't want Docker overhead  
✅ MicroPython is easy to install on your platform (Linux)  
✅ You want maximum performance  
✅ You want simpler architecture  

### When to Use Dev Container
✅ You only need code editing (no GUI)  
✅ You're doing non-GUI development  
✅ Team consistency is critical  
❌ Not recommended for GUI simulator  

## Resource Usage

**Disk Space:**
- Container image: ~100MB (slim Python + MicroPython)
- No GUI libraries in container

**Memory:**
- Container: ~50MB (just MicroPython)
- GUI: ~100MB (pygame + rendering)
- Total: ~150MB

**CPU:**
- Minimal overhead (socket communication is fast)
- Most CPU used by GUI rendering (same as native)

## Security Notes

- Source code mounted **read-only** in container
- Container runs with user permissions (not root)
- Network mode: host (for simple socket communication)
- No sensitive data in container

## FAQ

**Q: Do I need to rebuild the container after code changes?**  
A: No! The source code is mounted as a volume. Just restart the simulator.

**Q: Can I use this for hardware deployment?**  
A: No, this is simulator-only. For hardware deployment, use native `mpremote` or the dev container approach for USB access.

**Q: What MicroPython version is used?**  
A: Whatever's in the Debian repos (currently 1.19+). You can customize the Dockerfile to use a specific version.

**Q: Can I run multiple simulators?**  
A: Yes, but change ports and container names:
```bash
docker run --name bsides-badge-micropython-2 \
  -e SOCKET_PORT=4457 -e BINARY_PORT=4458 ...
```

**Q: Does this work on ARM Macs (M1/M2)?**  
A: Yes! Docker handles the architecture automatically.

## Migration Guide

### From Fully Native
```bash
# 1. Install Docker
# 2. No need to uninstall native MicroPython (won't conflict)
# 3. Run hybrid mode
cd simulator/
./run_hybrid.sh
```

### From Dev Container
```bash
# 1. Exit dev container
# 2. Run hybrid mode natively
cd simulator/
./run_hybrid.sh
```

Hybrid mode is a superset - it works alongside other approaches without conflicts.

## Summary

Hybrid mode combines the best aspects:
- **Easy setup** (no MicroPython installation)
- **Reliable GUI** (native display, no X11 issues)
- **Consistent environment** (containerized MicroPython)
- **Cross-platform** (works on Linux/macOS/Windows)
- **Lightweight** (small container, minimal overhead)

Perfect for developers who want a reliable simulator without complex native setup.
