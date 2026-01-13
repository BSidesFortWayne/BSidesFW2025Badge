# Dev Container + Native Simulator Guide

## TL;DR - Recommended Workflow

✅ **Edit code in VS Code dev container** (consistent environment)  
✅ **Run simulator in native terminal** (reliable GUI)

## Why This Hybrid Approach?

### Dev Container Benefits
- ✅ Consistent Python/MicroPython environment
- ✅ Pre-configured linting and formatting
- ✅ No system package conflicts
- ✅ Works on Linux, macOS, Windows

### Native Simulator Benefits
- ✅ Direct display access (no X11 forwarding needed)
- ✅ Better performance
- ✅ No display permission issues
- ✅ Simpler setup

## Setup Steps

### 1. Open Project in Dev Container

1. Open VS Code
2. Install "Dev Containers" extension
3. Open this project folder
4. Click "Reopen in Container" (or Ctrl+Shift+P → "Dev Containers: Reopen in Container")
5. Wait for container setup (first time takes 5-10 min)

### 2. Set Up Native Simulator

Open a **separate native terminal** (NOT the VS Code integrated terminal):

```bash
# One-time setup
cd /path/to/BSidesFW2025Badge/simulator/
uv run ./setup_wizard.py

# This installs pygame, pygame-gui, and other GUI dependencies natively
```

### 3. Daily Workflow

**Terminal 1 (Native):**
```bash
cd /path/to/BSidesFW2025Badge/simulator/
uv run ./run.sh
```
This runs the pygame GUI simulator with full display access.

**VS Code (Dev Container):**
- Edit files in `src/apps/`, `src/lib/`, etc.
- Use integrated terminal for non-GUI tasks:
  ```bash
  uv run pytest tests/          # Run unit tests
  uv run ruff check src/        # Lint code
  ```

Changes you make in the container are immediately reflected in the native terminal since they share the same filesystem.

## File Changes Flow

```
You edit in VS Code (container)
         ↓
Changes written to workspace (shared volume)
         ↓
Native simulator sees changes instantly
         ↓
Simulator auto-copies src/ to simulator/src/
         ↓
Restart simulator to see changes
```

## What to Run Where

| Task | Location |
|------|----------|
| Code editing | VS Code (container) |
| Linting/formatting | Container terminal |
| Unit tests (pytest) | Container terminal |
| **Pygame GUI simulator** | **Native terminal** |
| Hardware deployment (mpremote) | Native terminal |
| Web browser config UI | Either (ports forwarded) |

## FAQ

### Can I run the simulator in the container?

Technically yes, but it's not recommended:
- Requires X11 forwarding configuration
- Different setup for Linux/macOS/Windows
- Display permission issues are common
- Performance overhead

See [.devcontainer/README.md](../.devcontainer/README.md) for advanced container GUI setup.

### Do I need both uv installations?

Yes:
- **Container uv:** Manages dev container Python packages
- **Native uv:** Manages native Python packages (pygame, etc.)

They don't conflict since they operate in different environments.

### Why not just run everything natively?

You can! The dev container is optional. It provides:
- Consistent environment across team members
- No system package conflicts
- Easy onboarding for new contributors

But if you prefer native development, that works fine too.

### What if I don't have VS Code?

You can use the dev container without VS Code:

```bash
# Build the container
docker build -t bsides-dev .devcontainer/

# Run it
docker run -it --rm \
  -v $(pwd):/workspace \
  --network=host \
  bsides-dev bash

# Then edit files with your preferred editor natively
```

## Troubleshooting

### "Simulator not finding new app"

The simulator copies `src/` to `simulator/src/` at startup:
1. Make your changes in `src/apps/my_app.py`
2. Restart the simulator
3. It will automatically copy and detect changes

### "Container Python version different from native"

This is fine! The container uses Python 3.12, your native might be different.
- Container Python is for tooling (linting, type checking)
- Native Python is for the simulator
- **MicroPython** (which runs your app code) is separate from both

### "Changes not reflected in simulator"

Remember to edit files in `src/`, not `simulator/src/`:
- ✅ Edit: `src/apps/my_app.py`
- ❌ Don't edit: `simulator/src/apps/my_app.py` (gets overwritten)

## Performance Tips

### Native Terminal Setup

For best performance, configure your native terminal to match container settings:

```bash
# Install Python dev dependencies natively
cd /path/to/BSidesFW2025Badge
uv sync

# Now you have access to:
uv run ruff check src/        # Linting
uv run pytest tests/          # Testing  
uv run mpremote connect ...   # Hardware deployment
```

This way you can do everything natively if you prefer, while still having the container available for consistency.

## Summary

The hybrid approach gives you the best of both worlds:

| Aspect | Hybrid Approach | Container-Only | Native-Only |
|--------|----------------|----------------|-------------|
| Code editing consistency | ✅ | ✅ | ⚠️ |
| GUI reliability | ✅ | ❌ | ✅ |
| Team consistency | ✅ | ✅ | ❌ |
| Setup complexity | Medium | High | Low |
| Performance | ✅ | ⚠️ | ✅ |

**Recommendation:** Use the hybrid approach for development, especially in team settings.
