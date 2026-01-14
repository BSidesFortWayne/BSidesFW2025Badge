#!/usr/bin/env python3
"""
BSides FW 2025 Badge Simulator

Unified simulator with binary protocol and enhanced GUI always enabled.

Usage:
    ./simulator.py                    # Run simulator
    ./simulator.py --setup            # Run first-time setup wizard
    ./simulator.py -p ../src          # Specify project directory
"""

import shutil
import subprocess
import argparse
import socket
import json
import os
import sys
import threading
import struct
import hashlib
from pathlib import Path
from typing import Optional, Tuple

# Defer GUI imports until needed to allow --help to work without dependencies
HAS_ENHANCED = None
HAS_BINARY = None
HAS_LOGGER = None

def check_dependencies():
    """Check if required dependencies are available"""
    global HAS_ENHANCED, HAS_BINARY, HAS_LOGGER
    
    # Check if files exist
    script_dir = Path(__file__).parent
    
    HAS_ENHANCED = (script_dir / 'gui.py').exists()
    HAS_BINARY = True  # Binary protocol always integrated
    HAS_LOGGER = (script_dir / 'logger.py').exists()


def load_config(config_path: str = 'config.json') -> dict:
    """Load configuration from file"""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='BSides FW 2025 Badge Simulator - Unified Version',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run simulator (binary + enhanced always enabled)
  %(prog)s --setup                  # Run first-time setup wizard
  %(prog)s -p ../src                # Specify project directory
  %(prog)s -v                       # Verbose output
  %(prog)s --config my.json         # Custom config file
        """
    )
    
    # Setup
    parser.add_argument('--setup', action='store_true',
                       help='Run interactive setup wizard')
    
    # Configuration
    config_group = parser.add_argument_group('configuration')
    config_group.add_argument('-p', '--project', type=str,
                             help='Project directory containing main.py')
    config_group.add_argument('-m', '--micropython', type=str,
                             help='MicroPython executable path')
    config_group.add_argument('-c', '--config', type=str, default='config.json',
                             help='Configuration file (default: config.json)')
    config_group.add_argument('--port', type=int,
                             help='JSON protocol socket port (default: 4455)')
    config_group.add_argument('--binary-port', type=int,
                             help='Binary protocol socket port (default: 4456)')
    
    # Debugging
    debug_group = parser.add_argument_group('debugging')
    debug_group.add_argument('-v', '--verbose', action='store_true',
                            help='Verbose output')
    debug_group.add_argument('--no-logs', action='store_true',
                            help='Disable logging to files')
    debug_group.add_argument('--no-gui', action='store_true',
                            help='Run without GUI (testing mode)')
    
    return parser.parse_args()


def validate_paths(project_path: str, micropython_path: str) -> Tuple[bool, str]:
    """Validate required paths exist. Returns (success, error_message)"""
    
    # Check project directory
    project_main = os.path.join(project_path, 'main.py')
    if not os.path.exists(project_main):
        return False, f'No main.py found in project directory: {project_path}'
    
    # Check MicroPython executable
    if shutil.which(micropython_path) is None:
        return False, f'MicroPython executable not found: {micropython_path}\nTry: apt install micropython, or uv run micropython'
    
    # Check libraries directory
    if not os.path.exists('libraries'):
        return False, 'libraries/ directory not found\nMake sure you run from simulator/ directory'
    
    return True, ''


def setup_project_directory(project_path: str):
    """Copy project files and overlay simulator libraries
    
    Uses smart caching to avoid re-copying unchanged files.
    """
    print('Setting up project directory...')
    
    # Get simulator directory (where this script lives)
    simulator_dir = Path(__file__).parent.resolve()
    
    # Resolve all paths relative to simulator directory
    src_dir = simulator_dir / 'src'
    libraries_dir = simulator_dir / 'libraries'
    project_path = Path(project_path).resolve()
    cache_file = simulator_dir / '.src_cache.json'
    
    # Verify project path exists
    if not project_path.exists():
        raise FileNotFoundError(f'Project path does not exist: {project_path}')
    
    # Check if we can use cached copy
    use_cache = False
    if src_dir.exists() and cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Verify cache is still valid
            if cache_data.get('project_path') == str(project_path):
                # Check hash of all Python files to detect changes
                cached_hash = cache_data.get('file_hash', '')
                
                # Calculate current hash of all Python files
                import hashlib
                hasher = hashlib.sha256()
                for py_file in sorted(project_path.rglob('*.py')):
                    if py_file.is_file():
                        hasher.update(str(py_file.relative_to(project_path)).encode())
                        hasher.update(str(py_file.stat().st_mtime).encode())
                current_hash = hasher.hexdigest()
                
                # If hashes match, use cache
                if current_hash == cached_hash:
                    print('✓ Using cached project files (no changes detected)')
                    use_cache = True
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            pass
    
    if not use_cache:
        # Clean old src directory
        if src_dir.exists():
            print('Cleaning old project copy...')
            # Use ignore_errors to handle permission issues with runtime-created files
            shutil.rmtree(src_dir, ignore_errors=True)
            # If directory still exists (some files couldn't be deleted), try harder
            if src_dir.exists():
                import stat
                def handle_remove_readonly(func, path, exc):
                    """Error handler for Windows/permission issues"""
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                shutil.rmtree(src_dir, onerror=handle_remove_readonly)
        
        # Copy project files
        print(f'Copying project from {project_path}')
        shutil.copytree(project_path, src_dir)
        
        # Calculate and save cache info with file hash
        import hashlib
        hasher = hashlib.sha256()
        for py_file in sorted(project_path.rglob('*.py')):
            if py_file.is_file():
                hasher.update(str(py_file.relative_to(project_path)).encode())
                hasher.update(str(py_file.stat().st_mtime).encode())
        
        with open(cache_file, 'w') as f:
            json.dump({
                'project_path': str(project_path),
                'file_hash': hasher.hexdigest()
            }, f)
        
        print('✓ Project files copied')
    
    # Always overlay simulator libraries (shims) - these rarely change
    print(f'Overlaying simulator libraries from {libraries_dir}')
    shutil.copytree(libraries_dir, src_dir, dirs_exist_ok=True)
    
    print('✓ Binary protocol drivers installed for maximum performance')
    
    # Set environment variable for simulator detection
    os.environ['BADGE_SIMULATOR'] = '1'
    print('Set BADGE_SIMULATOR=1 environment variable')


def create_socket_server(host: str, port: int, name: str = 'socket') -> Optional[socket.socket]:
    """Create and bind socket server"""
    print(f'Creating {name} server on {host}:{port}')
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen()
        print(f'✓ {name} server listening on {host}:{port}')
        return sock
    except OSError as e:
        print(f'✗ Failed to bind {name} socket: {e}')
        print(f'  Port {port} may be in use. Try a different port.')
        return None


def start_micropython(micropython_path: str, heap_size: str = '8M') -> Optional[subprocess.Popen]:
    """Start MicroPython process"""
    print(f'Starting MicroPython: {micropython_path}')
    
    # Resolve src directory relative to simulator script
    simulator_dir = Path(__file__).parent.resolve()
    src_dir = simulator_dir / 'src'
    
    # Create a boot_then_main.py script that runs boot.py then main.py
    boot_main_script = src_dir / '_boot_then_main.py'
    boot_main_content = '''# Auto-generated script to run boot.py then main.py
# This replicates the hardware behavior where boot.py runs first

# Execute boot.py in the global namespace
with open('boot.py', 'r') as f:
    exec(f.read(), globals())

# Execute main.py in the same global namespace (so it has access to variables from boot.py)
with open('main.py', 'r') as f:
    exec(f.read(), globals())
'''
    
    try:
        with open(boot_main_script, 'w') as f:
            f.write(boot_main_content)
        print('✓ Created boot sequence script')
    except Exception as e:
        print(f'✗ Failed to create boot sequence script: {e}')
        return None
    
    try:
        process = subprocess.Popen(
            [micropython_path, '-X', f'heapsize={heap_size}', '_boot_then_main.py'],
            cwd=str(src_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        print(f'✓ MicroPython process started (PID: {process.pid})')
        print('✓ Running boot.py → main.py sequence (hardware behavior)')
        return process
        
    except FileNotFoundError:
        print(f'✗ Failed to start MicroPython: {micropython_path}')
        print(f'  Check that micropython is installed')
        return None
    except Exception as e:
        print(f'✗ Unexpected error starting MicroPython: {e}')
        return None


def handle_json_protocol(conn: socket.socket, gui_instance, micropython_process, logger=None):
    """Handle JSON protocol communication"""
    buffer = b''
    
    while gui_instance.running:
        try:
            # Receive data in chunks with larger buffer for framebuffer data
            chunk = conn.recv(65536)
            if not chunk:
                print("Connection closed by MicroPython")
                break
            
            buffer += chunk
            
            # Try to parse JSON - keep accumulating if incomplete
            try:
                data = json.loads(buffer.decode('utf-8'))
                buffer = b''  # Clear buffer on successful parse
                
                # Log command if logger available
                if logger and hasattr(logger, 'log_command'):
                    logger.log_command(data)
                
                # Handle command
                resp = gui_instance.handle_command(data)
                
                # Send response
                data_to_send = {'status': 'ok', 'resp': resp}
                conn.send(json.dumps(data_to_send).encode())
                
            except json.JSONDecodeError:
                # Incomplete JSON, continue accumulating
                # Sanity check for buffer overflow
                if len(buffer) > 10 * 1024 * 1024:  # 10MB limit
                    print(f"ERROR: Buffer overflow: {len(buffer)} bytes")
                    buffer = b''
                continue
                
        except (BrokenPipeError, ConnectionResetError):
            print("JSON connection closed")
            break
        except Exception as e:
            import traceback
            print(f"Error in JSON receive loop: {type(e).__name__}: {e}")
            traceback.print_exc()
            break
    
    micropython_process.terminate()


def handle_external_commands(server_socket: socket.socket, gui_instance, logger=None):
    """Handle external command connections (screenshot tool, regression tests, etc.)
    
    This accepts multiple short-lived connections from external tools.
    Each connection sends a single command and receives a response.
    """
    while gui_instance.running:
        try:
            # Accept new connection
            conn, addr = server_socket.accept()
            
            if logger:
                logger.log_info(f'External command connection from {addr}')
            
            # Handle this connection in a separate thread
            thread = threading.Thread(
                target=_handle_single_external_command,
                args=(conn, addr, gui_instance, logger),
                daemon=True
            )
            thread.start()
            
        except Exception as e:
            if gui_instance.running:  # Only log if we didn't intentionally stop
                print(f"Error accepting external connection: {e}")
                break


def _handle_single_external_command(conn: socket.socket, addr, gui_instance, logger=None):
    """Handle a single external command connection"""
    try:
        # Set timeout for receiving command
        conn.settimeout(5.0)
        
        # Receive command
        buffer = b''
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            buffer += chunk
            
            try:
                command = json.loads(buffer.decode('utf-8'))
                break
            except json.JSONDecodeError:
                # Need more data
                if len(buffer) > 100000:  # Sanity check
                    print(f"External command too large from {addr}")
                    conn.close()
                    return
                continue
        
        if not buffer:
            conn.close()
            return
        
        # Log command
        if logger and hasattr(logger, 'log_command'):
            logger.log_command(command)
        
        # Handle command
        resp = gui_instance.handle_command(command)
        
        # Send response
        response = {'status': 'ok', 'resp': resp}
        conn.sendall(json.dumps(response).encode('utf-8'))
        
        # Close connection after response
        conn.close()
        
        if logger:
            logger.log_info(f'External command completed from {addr}')
            
    except Exception as e:
        print(f"Error handling external command from {addr}: {e}")
        try:
            error_response = {'status': 'error', 'error': str(e)}
            conn.sendall(json.dumps(error_response).encode('utf-8'))
        except:
            pass
        finally:
            conn.close()


def handle_binary_protocol(conn: socket.socket, binary_handler, gui_instance, micropython_process):
    """Handle binary protocol communication"""
    MAGIC = b'\xEB\x01'
    
    while gui_instance.running:
        try:
            # Read magic bytes
            magic = conn.recv(2)
            if not magic or magic != MAGIC:
                if magic:
                    print(f"Invalid magic bytes: {magic.hex()}")
                break
            
            # Read command ID
            cmd_id_bytes = conn.recv(1)
            if not cmd_id_bytes:
                break
            cmd_id = cmd_id_bytes[0]
            
            # Read payload length
            length_bytes = conn.recv(4)
            if not length_bytes or len(length_bytes) < 4:
                break
            length = struct.unpack('<I', length_bytes)[0]
            
            # Read payload
            payload = b''
            while len(payload) < length:
                chunk = conn.recv(min(length - len(payload), 65536))
                if not chunk:
                    raise ConnectionError("Connection closed during payload read")
                payload += chunk
            
            # Process command
            status, response_data = binary_handler.handle_command(cmd_id, payload)
            
            # Send response
            if response_data:
                response = bytes([status]) + struct.pack('<I', len(response_data)) + response_data
            else:
                response = bytes([status]) + struct.pack('<I', 0)
            
            conn.sendall(response)
            
        except (BrokenPipeError, ConnectionResetError):
            print("Binary connection closed")
            break
        except Exception as e:
            print(f"Error in binary handler: {e}")
            break
    
    micropython_process.terminate()


def main():
    """Main entry point"""
    
    # Parse arguments
    args = parse_args()
    
    # Change to simulator directory to ensure relative paths work
    simulator_dir = Path(__file__).parent.resolve()
    os.chdir(simulator_dir)
    print(f'Working directory: {simulator_dir}')
    print()
    
    # Handle setup wizard
    if args.setup:
        from setup_wizard import run_setup_wizard
        return run_setup_wizard()
    
    # Check dependencies
    check_dependencies()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line args
    if args.project:
        config['project_path'] = args.project
    if args.micropython:
        config['micropython_path'] = args.micropython
    if args.port:
        config['socket_port'] = args.port
    if args.verbose:
        config.setdefault('debug', {})['verbose'] = True
    if args.no_logs:
        config.setdefault('logging', {})['enabled'] = False
    
    # Binary and enhanced are always enabled
    if not HAS_ENHANCED:
        print('Error: GUI module not found (gui.py)')
        print('Run from the simulator/ directory')
        return 1
    
    # Get final configuration
    project_path = config.get('project_path', '../src')
    micropython_path = config.get('micropython_path', 'micropython')
    socket_host = config.get('socket_host', '127.0.0.1')
    socket_port = config.get('socket_port', 4455)
    binary_port = args.binary_port or config.get('binary_port', 4456)
    
    # Print banner
    print('=' * 60)
    print('BSides FW 2025 Badge Simulator')
    print('=' * 60)
    print('Features: Binary Protocol + Hardware Controls')
    print()
    
    # Create logger if available
    logger = None
    if HAS_LOGGER and not args.no_logs:
        from logger import create_logger
        logger = create_logger(config)
        if logger:
            logger.log_startup(
                project_path=project_path,
                micropython_path=micropython_path,
                socket=f'{socket_host}:{socket_port}',
                config_file=args.config
            )
    
    # Validate paths
    valid, error_msg = validate_paths(project_path, micropython_path)
    if not valid:
        print(f'✗ Validation failed: {error_msg}')
        return 1
    
    print('✓ Validation passed')
    print()
    
    # Setup project directory
    try:
        setup_project_directory(project_path)
    except Exception as e:
        print(f'✗ Failed to setup project directory: {e}')
        return 1
    
    print()
    
    # Create socket servers
    json_socket = create_socket_server(socket_host, socket_port, 'JSON protocol')
    if not json_socket:
        return 1
    
    binary_socket = create_socket_server(socket_host, binary_port, 'Binary protocol')
    if not binary_socket:
        json_socket.close()
        return 1
    
    # Create external command server (for screenshot tool, regression tests, etc.)
    external_port = socket_port + 10  # e.g., 4465 if JSON is 4455
    external_socket = create_socket_server(socket_host, external_port, 'External commands')
    if not external_socket:
        print('  Warning: External command port unavailable')
        external_socket = None  # Continue without it
    
    print()
    
    # Start MicroPython
    micropython_process = start_micropython(micropython_path)
    if not micropython_process:
        json_socket.close()
        if binary_socket:
            binary_socket.close()
        return 1
    
    print()
    
    # Wait for JSON connection
    print('Waiting for MicroPython to connect...')
    try:
        json_socket.settimeout(10.0)
        json_conn, addr = json_socket.accept()
        json_socket.settimeout(None)
        print(f'✓ JSON protocol connected from {addr}')
    except socket.timeout:
        print('✗ Timeout waiting for MicroPython connection')
        print('  MicroPython may have crashed during startup')
        micropython_process.terminate()
        json_socket.close()
        if binary_socket:
            binary_socket.close()
        return 1
    
    # Wait for binary connection
    try:
        binary_socket.settimeout(10.0)
        binary_conn, addr = binary_socket.accept()
        binary_socket.settimeout(None)
        print(f'✓ Binary protocol connected from {addr}')
    except socket.timeout:
        print('✗ Timeout waiting for binary protocol connection')
        micropython_process.terminate()
        json_socket.close()
        binary_socket.close()
        return 1
    
    print()
    
    # Create GUI instance
    print('Initializing GUI...')
    import gui
    
    gui_instance = gui.GUIEnhanced(config, logger)
    print('✓ Enhanced GUI initialized (hardware controls enabled)')
    
    # Create binary handler
    binary_handler = gui.BinaryProtocolHandler(gui_instance)
    print('✓ Binary protocol handler initialized')
    
    print()
    print('=' * 60)
    print('Simulator running! Close window to exit.')
    print('=' * 60)
    print()
    
    # Start communication threads
    json_thread = threading.Thread(
        target=handle_json_protocol,
        args=(json_conn, gui_instance, micropython_process, logger),
        daemon=True
    )
    json_thread.start()
    
    binary_thread = threading.Thread(
        target=handle_binary_protocol,
        args=(binary_conn, binary_handler, gui_instance, micropython_process),
        daemon=True
    )
    binary_thread.start()
    
    # Start external command server if available
    if external_socket:
        external_thread = threading.Thread(
            target=handle_external_commands,
            args=(external_socket, gui_instance, logger),
            daemon=True
        )
        external_thread.start()
    
    # Stream MicroPython output if logger available
    if logger and hasattr(logger, 'log_micropython'):
        def stream_output(stream, stream_name):
            for line in stream:
                logger.log_micropython(line, stream_name)
                # Also add to GUI log window
                if stream_name == 'stderr':
                    gui_instance.add_log_message(line.strip(), 'ERROR')
                else:
                    gui_instance.add_log_message(line.strip(), 'INFO')
        
        stdout_thread = threading.Thread(
            target=stream_output,
            args=(micropython_process.stdout, 'stdout'),
            daemon=True
        )
        stderr_thread = threading.Thread(
            target=stream_output,
            args=(micropython_process.stderr, 'stderr'),
            daemon=True
        )
        stdout_thread.start()
        stderr_thread.start()
    elif not logger:
        # No logger, but still stream to GUI
        def stream_output_gui_only(stream, stream_name):
            for line in stream:
                if stream_name == 'stderr':
                    gui_instance.add_log_message(line.strip(), 'ERROR')
                else:
                    gui_instance.add_log_message(line.strip(), 'INFO')
        
        stdout_thread = threading.Thread(
            target=stream_output_gui_only,
            args=(micropython_process.stdout, 'stdout'),
            daemon=True
        )
        stderr_thread = threading.Thread(
            target=stream_output_gui_only,
            args=(micropython_process.stderr, 'stderr'),
            daemon=True
        )
        stdout_thread.start()
        stderr_thread.start()
    
    # Run GUI (blocks until closed)
    try:
        gui_instance.gameloop()
    except KeyboardInterrupt:
        print('\nKeyboard interrupt received')
    except Exception as e:
        print(f'\n✗ GUI error: {e}')
        import traceback
        traceback.print_exc()
    
    # Cleanup
    print('\nShutting down simulator...')
    micropython_process.terminate()
    
    try:
        micropython_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        print('MicroPython did not terminate, killing...')
        micropython_process.kill()
    
    json_socket.close()
    binary_socket.close()
    
    print('Simulator stopped')
    return 0


if __name__ == '__main__':
    sys.exit(main())
