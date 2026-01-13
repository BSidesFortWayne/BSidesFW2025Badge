# Simulator Mode Comparison

Quick reference for choosing the right simulator mode for your needs.

## TL;DR

- **Just want it to work?** → Run `cd simulator/ && ./run.sh` (auto-detects everything)
- **Have MicroPython installed?** → Auto-uses **Native Mode** (fastest)
- **No MicroPython?** → Auto-uses **Hybrid Mode** (Docker)
- **Just coding (no GUI)?** → Use **Dev Container**

## The Three Modes

### 🐳 Hybrid Mode (Recommended)

**What:** MicroPython in Docker + Pygame GUI native

```bash
./start_simulator.sh   # Interactive (deprecated, just use run.sh)
# or
cd simulator/
./run.sh              # Auto mode (recommended)
./run.sh --docker     # Force hybrid mode
```

| Aspect | Rating | Notes |
|--------|--------|-------|
| Setup Difficulty | ⭐ Easy | Just needs Docker installed |
| GUI Reliability | ⭐⭐⭐ Excellent | Native display = no issues |
| Performance | ⭐⭐ Good | Slight socket overhead |
| Cross-platform | ⭐⭐⭐ Excellent | Works everywhere |
| MicroPython install | ✅ Not needed | Runs in container |

**Best for:**
- First-time users
- Users on macOS/Windows (where MicroPython install is complex)
- Teams wanting consistent MicroPython versions
- When you don't want to install MicroPython natively

📖 [Full Guide](simulator/HYBRID_MODE.md)

---

### ⚡ Native Mode

**What:** Everything runs directly on your system

```bash
cd simulator/
uv run ./run.sh --setup  # First time
uv run ./run.sh          # Daily use
```

| Aspect | Rating | Notes |
|--------|--------|-------|
| Setup Difficulty | ⭐⭐ Moderate | Requires MicroPython install |
| GUI Reliability | ⭐⭐⭐ Excellent | Native display |
| Performance | ⭐⭐⭐ Best | Zero overhead |
| Cross-platform | ⭐⭐ Good | Platform-specific MicroPython |
| MicroPython install | ❌ Required | System package manager |

**Best for:**
- Users who already have MicroPython installed
- Maximum performance needs
- Linux users (easiest MicroPython install)
- When you want minimal dependencies

📖 [Main README](simulator/README.md)

---

### 📝 Dev Container Mode

**What:** VS Code container for code editing

```bash
# In VS Code: "Reopen in Container"
# Then run simulator in DIFFERENT mode (Hybrid or Native)
```

| Aspect | Rating | Notes |
|--------|--------|-------|
| Setup Difficulty | ⭐ Easy | VS Code handles it |
| GUI Reliability | ❌ Poor | X11 forwarding issues |
| Performance | ⚠️ N/A | Don't run GUI here |
| Cross-platform | ⭐⭐⭐ Excellent | Containerized |
| **Use case** | Code editing | **NOT for GUI** |

**Best for:**
- VS Code users
- Code editing, linting, type checking
- Team consistency
- **NOT for running the pygame GUI**

📖 [Dev Container Guide](simulator/DEV_CONTAINER_GUIDE.md)

---

## Decision Tree

```
Do you want to run the pygame GUI simulator?
│
├─ YES
│  │
│  └─ Do you have Docker installed?
│     │
│     ├─ YES → Use HYBRID MODE ✅
│     │
│     └─ NO → Do you have MicroPython installed?
│        │
│        ├─ YES → Use NATIVE MODE ✅
│        │
│        └─ NO → Install Docker, use HYBRID MODE ✅
│
└─ NO (just editing code)
   │
   └─ Use DEV CONTAINER MODE ✅
```

## Feature Comparison

| Feature | Hybrid | Native | Dev Container |
|---------|--------|--------|---------------|
| **Requirements** |
| Docker | ✅ Required | ❌ | ✅ Required |
| MicroPython | ❌ | ✅ Required | ❌ |
| Pygame | ✅ Native | ✅ Native | ❌ (X11 issues) |
| VS Code | ❌ Optional | ❌ Optional | ✅ Required |
| **Performance** |
| Display Speed | Fast | Fastest | Slow (X11) |
| Socket Overhead | Minimal | None | Minimal |
| Memory Usage | ~150MB | ~100MB | ~200MB |
| **Reliability** |
| GUI Display | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| Cross-platform | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Setup Success | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Development** |
| Code Editing | Any editor | Any editor | VS Code |
| Hot Reload | Restart sim | Restart sim | Restart sim |
| Debugging | Standard | Standard | VS Code tools |
| **Best For** |
| Primary Use | Most users | Power users | Code editing |
| Platform | All | Linux best | All |
| Team Setup | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

## Setup Commands Reference

### Auto Mode (Recommended)
```bash
cd simulator/
./run.sh    # Automatically detects and configures
```

The script automatically:
- Detects MicroPython → uses Native Mode
- If not found → tries to install MicroPython (brew/apt/dnf/pacman)
- If installation fails → offers Hybrid Mode (Docker)
- Installs pygame if needed

### Force Specific Mode
```bash
cd simulator/
./run.sh --native    # Force native (requires MicroPython)
./run.sh --docker    # Force hybrid (requires Docker)
./run.sh --setup     # Run setup wizard
```

### Dev Container Mode
```bash
# In VS Code
Ctrl+Shift+P → "Dev Containers: Reopen in Container"

# Don't run GUI here! Use ./run.sh in separate terminal
```

Requirements: VS Code, Docker, Dev Containers extension

## Migration Between Modes

### From Native → Hybrid
```bash
# Keep native setup, just install Docker
# Both can coexist without conflicts
./start_simulator.sh  # Choose option 1
```

### From Dev Container → Hybrid
```bash
# Exit container, run in native terminal
cd /path/to/project
./start_simulator.sh  # Choose option 1
```

### From Hybrid → Native
```bash
# Install MicroPython natively
sudo apt install micropython  # Linux
brew install micropython      # macOS

# Run setup
cd simulator/
uv run ./run.sh --setup
```

All modes can coexist - no need to uninstall anything!

## Common Questions

**Q: Which mode is fastest?**  
A: Native mode has the best performance, but Hybrid is nearly as fast.

**Q: Which mode is easiest to set up?**  
A: Hybrid mode - just needs Docker, no MicroPython installation.

**Q: Can I switch between modes?**  
A: Yes! All modes can coexist. Just run the one you want.

**Q: Why not use Dev Container for GUI?**  
A: X11 forwarding is complex and unreliable. Native display is much better.

**Q: Do I need VS Code?**  
A: No! Only Dev Container mode requires VS Code. Hybrid and Native work with any editor.

**Q: What about Windows?**  
A: Hybrid mode works great on Windows. Native mode needs WSL.

**Q: Can I develop on one machine, test on another?**  
A: Yes! The simulator listens on network ports. Change `socket_host` in config.

## Summary Recommendation

```
┌─────────────────────────────────────────────────────┐
│  FOR MOST USERS: Use Hybrid Mode                   │
│                                                     │
│  • Easy setup (just Docker)                        │
│  • Reliable GUI                                    │
│  • Works everywhere                                │
│  • No MicroPython install hassles                  │
│                                                     │
│  Run: ./start_simulator.sh                         │
└─────────────────────────────────────────────────────┘
```

## Getting Help

- **Hybrid Mode:** [HYBRID_MODE.md](simulator/HYBRID_MODE.md)
- **Native Mode:** [README.md](simulator/README.md)
- **Dev Container:** [DEV_CONTAINER_GUIDE.md](simulator/DEV_CONTAINER_GUIDE.md)
- **General Setup:** Run `./start_simulator.sh` for interactive help
