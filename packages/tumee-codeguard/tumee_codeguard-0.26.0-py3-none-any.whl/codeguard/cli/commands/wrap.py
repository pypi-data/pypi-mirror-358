#!/usr/bin/env python3
"""
process-wrap - Universal process interceptor for monitoring subprocess launches
Usage: process-wrap [options] <command> [command-args...]

Example: process-wrap code .
"""
import argparse
import atexit
import json
import os
import queue
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path


class ProcessWrapper:
    def __init__(self, log_file=None, output_format="text", verbose=False):
        self.log_file = log_file or tempfile.mktemp(suffix=".json", prefix="process-wrap-")
        self.output_format = output_format
        self.verbose = verbose
        self.interceptor_dir = Path(tempfile.mkdtemp(prefix="process-wrap-interceptors-"))
        self.start_time = time.time()
        self.process_count = 0
        self.output_queue = queue.Queue()
        self.shutdown = threading.Event()

        # Ensure interceptors exist
        self._create_interceptors()

        # Start output thread
        self.output_thread = threading.Thread(target=self._output_worker)
        self.output_thread.daemon = True
        self.output_thread.start()

        # Cleanup on exit
        atexit.register(self.cleanup)

    def _create_interceptors(self):
        """Create the Node.js and Python interceptor files."""

        # Node.js interceptor
        node_interceptor = self.interceptor_dir / "node_interceptor.js"
        with open(node_interceptor, "w") as f:
            f.write(self._get_node_interceptor_code())

        # Python interceptor
        python_interceptor = self.interceptor_dir / "python_interceptor.py"
        with open(python_interceptor, "w") as f:
            f.write(self._get_python_interceptor_code())

    def _get_node_interceptor_code(self):
        return f"""
// Node.js Process Interceptor
const {{ spawn, exec, execFile, execSync, spawnSync, fork }} = require('child_process');
const fs = require('fs');
const path = require('path');
const {{ performance }} = require('perf_hooks');

const LOG_FILE = '{self.log_file}';
const START_TIME = {self.start_time};

// Create write stream for logging
const logStream = fs.createWriteStream(LOG_FILE, {{ flags: 'a' }});

function getCallerLocation() {{
    const err = new Error();
    const stack = err.stack.split('\\n');
    // Find first stack frame not in this file
    for (let i = 3; i < stack.length; i++) {{
        const frame = stack[i];
        if (!frame.includes('node_interceptor.js') && 
            !frame.includes('child_process.js') &&
            !frame.includes('internal/')) {{
            const match = frame.match(/at (.*) \\((.*):(\\d+):(\\d+)\\)/);
            if (match) {{
                return {{
                    function: match[1],
                    file: match[2],
                    line: parseInt(match[3]),
                    column: parseInt(match[4])
                }};
            }}
            // Handle anonymous function
            const match2 = frame.match(/at (.*):(\\d+):(\\d+)/);
            if (match2) {{
                return {{
                    function: '<anonymous>',
                    file: match2[1],
                    line: parseInt(match2[2]),
                    column: parseInt(match2[3])
                }};
            }}
        }}
    }}
    return null;
}}

function logEvent(event) {{
    const timestamp = performance.now() / 1000 + START_TIME;
    const logEntry = JSON.stringify({{
        timestamp,
        relative_time: performance.now() / 1000,
        pid: process.pid,
        ppid: process.ppid,
        ...event
    }}) + '\\n';
    
    logStream.write(logEntry);
    
    // Also send to parent if verbose
    if (process.env.PROCESS_WRAP_VERBOSE === 'true') {{
        process.stderr.write(`[process-wrap] ${{event.type}}: ${{event.command || event.file}}\\n`);
    }}
}}

// Patch spawn
const originalSpawn = spawn;
require('child_process').spawn = function(command, args, options) {{
    const caller = getCallerLocation();
    logEvent({{
        type: 'spawn',
        command,
        args: args || [],
        options: {{
            cwd: options?.cwd,
            env: options?.env ? Object.keys(options.env).length : undefined,
            shell: options?.shell
        }},
        caller
    }});
    
    const child = originalSpawn.apply(this, arguments);
    
    child.on('exit', (code, signal) => {{
        logEvent({{
            type: 'exit',
            command,
            pid: child.pid,
            exitCode: code,
            signal
        }});
    }});
    
    return child;
}};

// Patch exec
const originalExec = exec;
require('child_process').exec = function(command, options, callback) {{
    const caller = getCallerLocation();
    logEvent({{
        type: 'exec',
        command,
        options: {{
            cwd: options?.cwd,
            env: options?.env ? Object.keys(options.env).length : undefined,
            shell: options?.shell
        }},
        caller
    }});
    
    return originalExec.apply(this, arguments);
}};

// Patch execFile
const originalExecFile = execFile;
require('child_process').execFile = function(file, args, options, callback) {{
    const caller = getCallerLocation();
    logEvent({{
        type: 'execFile',
        file,
        args: args || [],
        options: {{
            cwd: options?.cwd,
            env: options?.env ? Object.keys(options.env).length : undefined
        }},
        caller
    }});
    
    return originalExecFile.apply(this, arguments);
}};

// Patch fork
const originalFork = fork;
require('child_process').fork = function(modulePath, args, options) {{
    const caller = getCallerLocation();
    logEvent({{
        type: 'fork',
        modulePath,
        args: args || [],
        options: {{
            cwd: options?.cwd,
            env: options?.env ? Object.keys(options.env).length : undefined
        }},
        caller
    }});
    
    return originalFork.apply(this, arguments);
}};

// Patch sync methods
const originalSpawnSync = spawnSync;
require('child_process').spawnSync = function(command, args, options) {{
    const caller = getCallerLocation();
    const startTime = performance.now();
    
    logEvent({{
        type: 'spawnSync',
        command,
        args: args || [],
        options: {{
            cwd: options?.cwd,
            env: options?.env ? Object.keys(options.env).length : undefined,
            shell: options?.shell
        }},
        caller
    }});
    
    const result = originalSpawnSync.apply(this, arguments);
    
    logEvent({{
        type: 'spawnSync-complete',
        command,
        duration: (performance.now() - startTime) / 1000,
        exitCode: result.status,
        signal: result.signal
    }});
    
    return result;
}};

const originalExecSync = execSync;
require('child_process').execSync = function(command, options) {{
    const caller = getCallerLocation();
    const startTime = performance.now();
    
    logEvent({{
        type: 'execSync',
        command,
        options: {{
            cwd: options?.cwd,
            env: options?.env ? Object.keys(options.env).length : undefined
        }},
        caller
    }});
    
    try {{
        const result = originalExecSync.apply(this, arguments);
        logEvent({{
            type: 'execSync-complete',
            command,
            duration: (performance.now() - startTime) / 1000,
            success: true
        }});
        return result;
    }} catch (err) {{
        logEvent({{
            type: 'execSync-complete',
            command,
            duration: (performance.now() - startTime) / 1000,
            success: false,
            error: err.message
        }});
        throw err;
    }}
}};

// Log that interceptor is active
logEvent({{
    type: 'interceptor-loaded',
    process: process.argv[1],
    node_version: process.version
}});
"""

    def _get_python_interceptor_code(self):
        return f'''
# Python Process Interceptor
import subprocess
import sys
import os
import json
import time
import functools
import traceback

LOG_FILE = '{self.log_file}'
START_TIME = {self.start_time}

def get_caller_location():
    """Get information about who called subprocess."""
    stack = traceback.extract_stack()
    # Find first frame not in this file or subprocess module
    for frame in reversed(stack[:-2]):  # Skip current and subprocess frames
        if 'python_interceptor.py' not in frame.filename and 'subprocess.py' not in frame.filename:
            return {{
                'file': frame.filename,
                'line': frame.lineno,
                'function': frame.name,
                'code': frame.line
            }}
    return None

def log_event(event):
    """Log an event to the audit file."""
    event['timestamp'] = time.time()
    event['relative_time'] = time.time() - START_TIME
    event['pid'] = os.getpid()
    event['ppid'] = os.getppid()
    
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(event) + '\\n')
        
        if os.environ.get('PROCESS_WRAP_VERBOSE') == 'true':
            cmd = event.get('args', event.get('cmd', ''))
            if isinstance(cmd, list) and cmd:
                cmd = cmd[0]
            sys.stderr.write(f"[process-wrap] {{event['type']}}: {{cmd}}\\n")
            sys.stderr.flush()
    except:
        pass  # Don't break the program if logging fails

# Store original functions
_original_popen = subprocess.Popen
_original_run = subprocess.run
_original_call = subprocess.call
_original_check_call = subprocess.check_call
_original_check_output = subprocess.check_output

class InterceptedPopen(_original_popen):
    """Wrapped Popen class that logs process creation."""
    def __init__(self, args, **kwargs):
        # Log the creation
        caller = get_caller_location()
        log_event({{
            'type': 'Popen',
            'args': args if isinstance(args, list) else [args],
            'kwargs': {{
                'cwd': kwargs.get('cwd'),
                'env': len(kwargs['env']) if 'env' in kwargs and kwargs['env'] else None,
                'shell': kwargs.get('shell', False)
            }},
            'caller': caller
        }})
        
        # Store for exit logging
        self._wrap_command = args[0] if isinstance(args, list) and args else str(args)
        self._wrap_start_time = time.time()
        
        # Call original
        super().__init__(args, **kwargs)
    
    def wait(self, timeout=None):
        """Override wait to log exit."""
        result = super().wait(timeout)
        
        log_event({{
            'type': 'exit',
            'command': self._wrap_command,
            'pid': self.pid,
            'exitCode': result,
            'duration': time.time() - self._wrap_start_time
        }})
        
        return result

# Monkey patch subprocess
subprocess.Popen = InterceptedPopen

# Wrap other convenience functions
@functools.wraps(_original_run)
def wrapped_run(*args, **kwargs):
    if args:
        log_event({{
            'type': 'run',
            'args': args[0] if isinstance(args[0], list) else [args[0]],
            'caller': get_caller_location()
        }})
    return _original_run(*args, **kwargs)

subprocess.run = wrapped_run

# Log that interceptor is active
log_event({{
    'type': 'interceptor-loaded',
    'python_version': sys.version,
    'script': sys.argv[0] if sys.argv else None
}})
'''

    def _output_worker(self):
        """Worker thread to process output."""
        while not self.shutdown.is_set():
            try:
                # Read new events from log file
                if os.path.exists(self.log_file):
                    with open(self.log_file, "r") as f:
                        # Seek to end if this is first read
                        if not hasattr(self, "_log_position"):
                            self._log_position = 0

                        f.seek(self._log_position)
                        for line in f:
                            if line.strip():
                                try:
                                    event = json.loads(line)
                                    self._format_output(event)
                                except json.JSONDecodeError:
                                    pass

                        self._log_position = f.tell()

                time.sleep(0.1)  # Poll interval
            except:
                pass

    def _format_output(self, event):
        """Format and display output based on format setting."""
        if self.output_format == "json":
            print(json.dumps(event))
        elif self.output_format == "compact":
            event_type = event.get("type", "unknown")
            if event_type in [
                "spawn",
                "exec",
                "execFile",
                "fork",
                "Popen",
                "run",
                "spawnSync",
                "execSync",
            ]:
                cmd = event.get("command") or event.get("file") or event.get("args", [""])[0]
                caller = event.get("caller", {})
                location = f"{caller.get('file', '?')}:{caller.get('line', '?')}" if caller else "?"
                print(f"[{event['relative_time']:.3f}s] {event_type}: {cmd} (from {location})")
            elif event_type == "exit":
                print(
                    f"[{event['relative_time']:.3f}s] Process {event.get('pid')} exited: {event.get('exitCode')}"
                )

    def wrap_command(self, cmd_args):
        """Wrap and execute a command with interception."""
        # Detect if it's a Node.js app
        cmd = cmd_args[0]

        # VS Code might be a shell script that launches node/electron
        # We need to ensure our interceptor propagates to child processes
        env = os.environ.copy()

        # For Node.js/Electron apps
        node_options = env.get("NODE_OPTIONS", "")
        if node_options:
            node_options += " "
        node_options += f"--require {self.interceptor_dir}/node_interceptor.js"
        env["NODE_OPTIONS"] = node_options

        # For Python apps
        python_path = env.get("PYTHONPATH", "")
        if python_path:
            python_path = f"{self.interceptor_dir}:{python_path}"
        else:
            python_path = str(self.interceptor_dir)
        env["PYTHONPATH"] = python_path
        env["PYTHONSTARTUP"] = str(self.interceptor_dir / "python_interceptor.py")

        # Pass verbosity flag
        if self.verbose:
            env["PROCESS_WRAP_VERBOSE"] = "true"

        # Log the main command
        with open(self.log_file, "w") as f:
            f.write(
                json.dumps(
                    {
                        "type": "wrapper-start",
                        "command": cmd_args,
                        "timestamp": self.start_time,
                        "relative_time": 0,
                    }
                )
                + "\n"
            )

        if self.output_format != "json":
            print(f"🔍 process-wrap: Intercepting '{' '.join(cmd_args)}'")
            print(f"📁 Log file: {self.log_file}")
            print(f"{'─' * 60}")

        # Run the command
        try:
            proc = subprocess.Popen(cmd_args, env=env)

            # Handle Ctrl+C gracefully
            def signal_handler(sig, frame):
                proc.terminate()
                self.cleanup()
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)

            # Wait for process to complete
            exit_code = proc.wait()

            return exit_code

        except FileNotFoundError:
            print(f"❌ Command not found: {cmd}", file=sys.stderr)
            return 127
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            return 1

    def cleanup(self):
        """Cleanup on exit."""
        self.shutdown.set()
        if self.output_thread.is_alive():
            self.output_thread.join(timeout=1)

        # Clean up interceptor directory
        try:
            import shutil

            shutil.rmtree(self.interceptor_dir)
        except:
            pass

        if self.output_format != "json" and os.path.exists(self.log_file):
            # Show summary
            try:
                with open(self.log_file, "r") as f:
                    events = [json.loads(line) for line in f if line.strip()]

                process_events = [
                    e
                    for e in events
                    if e["type"] in ["spawn", "exec", "fork", "Popen", "spawnSync", "execSync"]
                ]
                print(f"\n{'─' * 60}")
                print(f"📊 Summary: {len(process_events)} processes spawned")
                print(f"⏱️  Total time: {time.time() - self.start_time:.3f}s")
                print(f"📁 Full log: {self.log_file}")

                # Show top commands
                from collections import Counter

                commands = []
                for e in process_events:
                    cmd = (
                        e.get("command")
                        or e.get("file")
                        or (e.get("args", [""])[0] if e.get("args") else "")
                    )
                    if cmd:
                        commands.append(os.path.basename(str(cmd).split()[0]))

                if commands:
                    print(f"\nTop commands:")
                    for cmd, count in Counter(commands).most_common(5):
                        print(f"  {cmd}: {count}")

            except:
                pass


def main():
    parser = argparse.ArgumentParser(
        description="process-wrap - Monitor subprocess launches from any program",
        usage="process-wrap [options] <command> [args...]",
    )

    parser.add_argument(
        "-o",
        "--output",
        choices=["text", "compact", "json"],
        default="compact",
        help="Output format (default: compact)",
    )
    parser.add_argument("-l", "--log-file", help="Log file path (default: auto-generated)")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show all process launches in real-time"
    )
    parser.add_argument("--keep-log", action="store_true", help="Keep log file after exit")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run and monitor")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Create wrapper
    wrapper = ProcessWrapper(
        log_file=args.log_file, output_format=args.output, verbose=args.verbose
    )

    # Run command
    exit_code = wrapper.wrap_command(args.command)

    # Cleanup
    wrapper.cleanup()

    # Remove log file unless asked to keep it
    if not args.keep_log and not args.log_file and os.path.exists(wrapper.log_file):
        try:
            os.unlink(wrapper.log_file)
        except:
            pass

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
