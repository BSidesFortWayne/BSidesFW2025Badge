#!/usr/bin/env python3
"""
BSides FW 2025 Badge Simulator - Setup Wizard

Interactive setup for first-time users to configure the simulator.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path


def print_header(text: str):
    """Print a formatted header"""
    print()
    print('=' * 60)
    print(text)
    print('=' * 60)
    print()


def print_step(step_num: int, total: int, text: str):
    """Print a step indicator"""
    print(f'\n[Step {step_num}/{total}] {text}')
    print('-' * 60)


def ask_yes_no(question: str, default: bool = True) -> bool:
    """Ask a yes/no question"""
    default_str = 'Y/n' if default else 'y/N'
    response = input(f'{question} [{default_str}]: ').strip().lower()
    
    if not response:
        return default
    return response in ['y', 'yes']


def ask_choice(question: str, choices: list, default: int = 0) -> int:
    """Ask user to choose from a list"""
    print(f'\n{question}')
    for i, choice in enumerate(choices):
        marker = ' (default)' if i == default else ''
        print(f'  {i + 1}. {choice}{marker}')
    
    while True:
        response = input(f'\nChoice [1-{len(choices)}]: ').strip()
        if not response:
            return default
        
        try:
            choice_idx = int(response) - 1
            if 0 <= choice_idx < len(choices):
                return choice_idx
        except ValueError:
            pass
        
        print(f'Invalid choice. Please enter a number between 1 and {len(choices)}.')


def ask_text(question: str, default: str = '') -> str:
    """Ask for text input"""
    if default:
        response = input(f'{question} [{default}]: ').strip()
        return response if response else default
    else:
        while True:
            response = input(f'{question}: ').strip()
            if response:
                return response
            print('This field is required.')


def check_dependency(name: str, import_name: str = None, command: str = None) -> bool:
    """Check if a dependency is installed"""
    if import_name:
        try:
            __import__(import_name)
            return True
        except ImportError:
            return False
    
    if command:
        return shutil.which(command) is not None
    
    return False


def get_platform_info():
    """Detect current platform"""
    import platform
    system = platform.system().lower()
    return system


def is_running_in_container():
    """Detect if running inside a container (Docker/devcontainer)"""
    # Check for VS Code devcontainer environment variable
    if os.getenv('REMOTE_CONTAINERS') or os.getenv('CODESPACES'):
        return True
    
    # Check for .dockerenv file
    if os.path.exists('/.dockerenv'):
        return True
    
    # Check cgroup for docker/containerd
    try:
        with open('/proc/1/cgroup', 'r') as f:
            if any(keyword in line for line in f for keyword in ['docker', 'containerd', 'lxc']):
                return True
    except:
        pass
    
    return False


def install_micropython_instructions():
    """Show platform-specific MicroPython installation instructions"""
    system = get_platform_info()
    
    print('\nMicroPython Installation Options:')
    print('=' * 60)
    
    if system == 'linux':
        print('\nOption 1: System Package Manager (Recommended)')
        print('  Debian/Ubuntu: sudo apt update && sudo apt install micropython')
        print('  Fedora:        sudo dnf install micropython')
        print('  Arch:          sudo pacman -S micropython')
        
    elif system == 'darwin':
        print('\nOption 1: Homebrew (Recommended)')
        print('  brew install micropython')
        print('\nOption 2: MacPorts')
        print('  sudo port install micropython')
        
    elif system == 'windows':
        print('\nOption 1: Windows Support via WSL')
        print('  1. Install WSL: wsl --install')
        print('  2. Open Ubuntu/WSL terminal')
        print('  3. Run: sudo apt install micropython')
    
    print('\nOption 2: Auto-Installer (Downloads pre-built binary)')
    print('  python3 install_micropython.py')
    
    print('\nOption 3: Build from Source')
    print('  https://github.com/micropython/micropython/wiki/Getting-Started')
    print('=' * 60)


def install_dependency(name: str, package: str, pip: bool = True) -> bool:
    """Attempt to install a dependency"""
    if pip:
        print(f'Installing {name}...')
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
            print(f'✓ {name} installed successfully')
            return True
        except subprocess.CalledProcessError:
            print(f'✗ Failed to install {name}')
            return False
    else:
        print(f'Please install {name} manually:')
        print(f'  $ {package}')
        return False


def run_setup_wizard() -> int:
    """Run the interactive setup wizard"""
    
    print_header('BSides FW 2025 Badge Simulator - Setup Wizard')
    
    # Check if running in container
    if is_running_in_container():
        print('⚠  CONTAINER ENVIRONMENT DETECTED')
        print('=' * 60)
        print()
        print('You appear to be running inside a Docker/dev container.')
        print()
        print('IMPORTANT: The pygame GUI simulator requires display access,')
        print('which is complex and unreliable in containers.')
        print()
        print('RECOMMENDED OPTIONS:')
        print()
        print('  1. HYBRID MODE (Best) - MicroPython in Docker, GUI native')
        print('     • No MicroPython installation needed')
        print('     • Reliable GUI display')
        print('     • Run: ./run.sh --docker (in native terminal)')
        print('     • See: HYBRID_MODE.md')
        print()
        print('  2. NATIVE MODE - Everything runs natively')
        print('     • Fastest performance')
        print('     • Run this wizard natively')
        print('     • Requires MicroPython installation')
        print()
        print('WHY? Because:')
        print('  • X11 forwarding requires host-side configuration')
        print('  • Display permissions often fail in containers')
        print('  • macOS/Windows require extra tools (XQuartz/VcXsrv)')
        print('  • Native/hybrid execution is faster and more reliable')
        print()
        print('=' * 60)
        print()
        
        if not ask_yes_no('Continue anyway (not recommended)?', default=False):
            print()
            print('Setup cancelled.')
            print()
            print('Recommended next steps:')
            print()
            print('  Option 1 - Hybrid Mode (Easiest):')
            print('    1. Open a native terminal')
            print('    2. cd simulator/')
            print('    3. ./run.sh --docker')
            print()
            print('  Option 2 - Native Mode:')
            print('    1. Exit the container (or open a native terminal)')
            print('    2. cd simulator/')
            print('    3. uv run ./setup_wizard.py')
            print()
            return 0
    
    print('Welcome! This wizard will help you set up the simulator.')
    print()
    print('The simulator allows you to develop and test badge apps without')
    print('physical hardware. It runs your app code in MicroPython and displays')
    print('the output in a pygame window.')
    print()
    
    if not ask_yes_no('Continue with setup?'):
        print('Setup cancelled.')
        return 0
    
    # Step 1: Check dependencies
    print_step(1, 5, 'Checking Dependencies')
    
    dependencies = {
        'Python 3.8+': {'check': sys.version_info >= (3, 8), 'required': True},
        'pygame': {'import': 'pygame', 'package': 'pygame', 'required': True},
        'Pillow': {'import': 'PIL', 'package': 'Pillow', 'required': True},
        'MicroPython': {'command': 'micropython', 'required': True},
        'pygame-gui': {'import': 'pygame_gui', 'package': 'pygame-gui', 'required': False,
                      'note': 'Required for enhanced mode with hardware controls'},
    }
    
    missing_required = []
    missing_optional = []
    
    for name, dep in dependencies.items():
        if 'check' in dep:
            has_dep = dep['check']
        elif 'import' in dep:
            has_dep = check_dependency(name, import_name=dep['import'])
        elif 'command' in dep:
            has_dep = check_dependency(name, command=dep['command'])
        else:
            has_dep = False
        
        status = '✓' if has_dep else '✗'
        note = f" ({dep['note']})" if 'note' in dep and not has_dep else ''
        print(f'{status} {name}{note}')
        
        if not has_dep:
            if dep['required']:
                missing_required.append((name, dep))
            else:
                missing_optional.append((name, dep))
    
    # Offer to install missing dependencies
    if missing_required or missing_optional:
        print()
        if missing_required:
            print('⚠ Some required dependencies are missing!')
            
            if ask_yes_no('Attempt to install missing dependencies?'):
                for name, dep in missing_required:
                    if 'package' in dep:
                        install_dependency(name, dep['package'])
                    elif 'command' in dep:
                        print(f'\n{name} must be installed manually:')
                        if name == 'MicroPython':
                            install_micropython_instructions()
                            
                            if ask_yes_no('\nRun auto-installer now?'):
                                print('\nLaunching MicroPython auto-installer...\n')
                                try:
                                    result = subprocess.run([sys.executable, 'install_micropython.py'])
                                    if result.returncode == 0:
                                        print('\n✓ MicroPython installation successful!')
                                    else:
                                        print('\n⚠ Please install MicroPython manually using the options above.')
                                except Exception as e:
                                    print(f'\n✗ Auto-installer failed: {e}')
                                    print('Please install MicroPython manually using the options above.')
                        input('\nPress Enter when ready...')
        
        if missing_optional:
            print()
            print('Optional dependencies missing:')
            for name, dep in missing_optional:
                print(f'  - {name}: {dep.get("note", "")}')
            
            if ask_yes_no('Install optional dependencies?'):
                for name, dep in missing_optional:
                    if 'package' in dep:
                        install_dependency(name, dep['package'])
    else:
        print('\n✓ All dependencies are installed!')
    
    # Step 2: Select project directory
    print_step(2, 5, 'Project Configuration')
    
    # Try to auto-detect src directory
    default_project = '../src'
    if os.path.exists(default_project) and os.path.exists(os.path.join(default_project, 'main.py')):
        print(f'✓ Found project directory: {default_project}')
        project_path = default_project
    else:
        print('Could not auto-detect project directory.')
        project_path = ask_text('Enter path to project directory (containing main.py)',
                               default='../src')
    
    while not os.path.exists(o
        'micropython',
        str(Path.home() / '.local' / 'bin' / 'micropython'),
        str(Path.cwd() / 'bin' / 'micropython'),
    ]
    micropython_path = None
    
    for candidate in micropython_candidates:
        if shutil.which(candidate) or (Path(candidate).exists() and Path(candidate).is_file()):
            print(f'✓ Found MicroPython: {candidate}')
            micropython_path = candidate
            break
    
    if not micropython_path:
        print('Could not auto-detect MicroPython.')
        print('\nIf you just installed it, you may need to:')
        print('  1. Restart your shell')
        print('  2. Source your shell config (e.g., source ~/.bashrc)')
        print('  3. Use the full path')
        print(un micropython']
    micropython_path = None
    
    for candidate in micropython_candidates:
        if shutil.which(candidate.split()[0]):
            print(f'✓ Found MicroPython: {candidate}')
            micropython_path = candidate
            break
    
    if not micropython_path:
        print('Could not auto-detect MicroPython.')
        micropython_path = ask_text('Enter MicroPython command or path',
                                   default='micropython')
    
    print(f'✓ Using MicroPython: {micropython_path}')
    
    # Step 4: Confirm features
    print_step(4, 5, 'Simulator Features')
    
    print('\nThe unified simulator includes all features by default:')
    print()
    print('  \u2713 Binary protocol (10-20x faster than JSON)')
    print('  \u2713 Hardware control panel (mock accelerometer, battery, WiFi, Bluetooth)')
    print('  \u2713 Dual circular display rendering')
    print('  \u2713 Keyboard button controls')
    print('  \u2713 Structured logging')
    print()
    print('These can be disabled with --json-only or --no-enhanced flags if needed.')
    print()
    
    # Step 5: Save configuration
    print_step(5, 5, 'Save Configuration')
    
    config = {
        'project_path': project_path,
        'micropython_path': micropython_path,
        'socket_port': 4455,
        'socket_host': '127.0.0.1',
        'binary_protocol': True,
        'binary_port': 4456,
        'enhanced_gui': True,
        'logging': {
            'enabled': True,
            'output_dir': 'logs',
            'log_micropython': True,
            'log_gui_commands': False,
            'log_button_polling': False,
            'structured_output': True
        },
        'gui': {
            'window_title': 'BSides FW 2025 Badge Simulator',
            'show_fps': True,
            'target_fps': 60,
            'show_led_positions': True
        },
        'debug': {
            'verbose': False,
            'print_commands': False,
            'print_startup': True
        }
    }
    
    config_path = 'config.json'
    
    # Backup existing config
    if os.path.exists(config_path):
        if ask_yes_no(f'{config_path} already exists. Backup existing config?'):
            backup_path = f'{config_path}.backup'
            shutil.copy(config_path, backup_path)
            print(f'✓ Backed up to {backup_path}')
    
    # Save configuration
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f'✓ Configuration saved to {config_path}')
    
    # Summary
    print_header('Setup Complete!')
    
    print('Configuration Summary:')
    print(f'  Project: {project_path}')
    print(f'  MicroPython: {micropython_path}')
    print(f'  Features: All enabled (Binary Protocol + Hardware Controls)')
    print()
    print('To run the simulator:')
    print('  ./run.sh')
    print()
    print('Or directly:')
    print('  ./simulator.py')
    print()
    print('To disable features:')
    print('  ./simulator.py --json-only       # Disable binary protocol')
    print('  ./simulator.py --no-enhanced     # Disable hardware controls')
    print()
    print('For help:')
    print('  ./simulator.py --help')
    print()
    
    if ask_yes_no('Run simulator now?'):
        print()
        print('Starting simulator...')
        print()
        
        # Import and run main
        import simulator
        sys.argv = ['simulator.py']
        sys.argv.extend(['-p', project_path, '-m', micropython_path])
        
        return simulator.main()
    
    return 0


if __name__ == '__main__':
    sys.exit(run_setup_wizard())
