"""
Structured logging for the simulator.
Provides consistent, parseable output for debugging and AI analysis.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class SimulatorLogger:
    """Structured logger for simulator events"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('logging', {})
        self.debug_config = config.get('debug', {})
        self.enabled = self.config.get('enabled', True)
        self.structured = self.config.get('structured_output', True)
        
        # Create log directory if needed
        if self.enabled:
            log_dir = Path(self.config.get('output_dir', 'logs'))
            log_dir.mkdir(exist_ok=True)
            
            # Create timestamped log file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.log_file = log_dir / f'simulator_{timestamp}.log'
            self.json_log_file = log_dir / f'simulator_{timestamp}.jsonl'
    
    def _write_to_file(self, message: str, json_obj: Optional[Dict] = None):
        """Write to log files"""
        if not self.enabled:
            return
        
        # Write text log
        with open(self.log_file, 'a') as f:
            f.write(f"{message}\n")
        
        # Write JSON log if structured
        if self.structured and json_obj:
            with open(self.json_log_file, 'a') as f:
                f.write(json.dumps(json_obj) + '\n')
    
    def log_event(self, event_type: str, **kwargs):
        """Log a structured event"""
        timestamp = datetime.now().isoformat()
        
        if self.structured:
            log_obj = {
                'timestamp': timestamp,
                'type': event_type,
                **kwargs
            }
            message = f"[{timestamp}] [{event_type.upper()}] {json.dumps(kwargs)}"
        else:
            message = f"[{timestamp}] [{event_type.upper()}] {' '.join(f'{k}={v}' for k, v in kwargs.items())}"
            log_obj = None
        
        # Print to console if verbose
        if self.debug_config.get('verbose', False):
            print(message)
        
        self._write_to_file(message, log_obj)
    
    def log_startup(self, **kwargs):
        """Log simulator startup"""
        if self.debug_config.get('print_startup', True):
            print(f"[SIMULATOR] Starting badge simulator...")
            for key, value in kwargs.items():
                print(f"[SIMULATOR]   {key}: {value}")
        self.log_event('startup', **kwargs)
    
    def log_micropython(self, line: str, stream: str = 'stdout'):
        """Log MicroPython output"""
        if not self.config.get('log_micropython', True):
            return
        
        # Don't print to console - messages are displayed in GUI log window
        # to avoid duplicate output
        
        self.log_event('micropython', stream=stream, line=line.rstrip())
    
    def log_command(self, command: Dict[str, Any]):
        """Log a command from MicroPython to GUI"""
        # Skip button polling spam unless enabled
        if command.get('module') == 'pca9535' and command.get('command') == 'get_inputs':
            if not self.config.get('log_button_polling', False):
                return
        
        if not self.config.get('log_gui_commands', False):
            return
        
        if self.debug_config.get('print_commands', False):
            print(f"[CMD] {command['module']}.{command['command']}")
        
        self.log_event('command', 
                      module=command.get('module'),
                      command=command.get('command'),
                      parameters=command.get('parameters', {}))
    
    def log_error(self, error_type: str, message: str, **kwargs):
        """Log an error"""
        print(f"[ERROR] {error_type}: {message}", file=sys.stderr)
        self.log_event('error', error_type=error_type, message=message, **kwargs)
    
    def log_info(self, message: str, **kwargs):
        """Log informational message"""
        print(f"[INFO] {message}")
        self.log_event('info', message=message, **kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log warning message"""
        print(f"[WARNING] {message}")
        self.log_event('warning', message=message, **kwargs)


def create_logger(config: Dict[str, Any]) -> SimulatorLogger:
    """Create a logger instance"""
    return SimulatorLogger(config)
