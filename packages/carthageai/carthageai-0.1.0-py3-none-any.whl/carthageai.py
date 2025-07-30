#!/usr/bin/env python3

import json
import os
import re
import argparse
import readline
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import time
import ssl
import socket
import sys
import hashlib
from openai import OpenAI
from openai import APIConnectionError, RateLimitError, APIStatusError

# UI Components
try:
    from rich import print
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn
    from rich.table import Table
    from rich.console import Console
    from rich.style import Style
    from rich.text import Text
    from rich.syntax import Syntax
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    console = None

# --- Config ---
CONFIG_DIR = Path(__file__).parent.resolve()
CONFIG_FILE = CONFIG_DIR / "config.json"
CHAT_DIR = CONFIG_DIR / "sessions"
DEBUG_LOG = CONFIG_DIR / "debug.log"

# Timeout settings
REQUEST_TIMEOUT = 30  # seconds
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30
MAX_FILE_SIZE = 100000  # 100KB

# Available Models
MODELS = {
    "openai": ["gpt-4", "gpt-3.5-turbo"],
    "deepseek": ["deepseek-chat", "deepseek-reasoner"]
}

# Colors and Styles
THEME = {
    "primary": "bold blue",
    "secondary": "cyan",
    "success": "bold green",
    "warning": "yellow",
    "error": "bold red",
    "prompt": "bold magenta",
    "ai": "bright_white",
    "user": "bright_green",
    "code": "on black",
    "file_ref": "bold yellow"
}

class CarthageAI:
    def __init__(self):
        # Initialize all attributes first
        self.debug_log = None
        self.clients = {}
        self.chat_history = []
        self.current_session = None
        self.current_model = "gpt-4"
        self.current_provider = "openai"
        self.start_time = datetime.now()
        
        # Check directory permissions first
        self._verify_directory_permissions()
        
        # Initialize components
        self._setup_logging()
        self.config = self._load_config()
        self._init_clients()
        self._init_readline()
        self._verify_ssl()

    def _verify_directory_permissions(self):
        """Verify we can write to the script directory"""
        try:
            # Test creating directories
            os.makedirs(CHAT_DIR, exist_ok=True)
            
            # Test writing a file
            test_file = CONFIG_DIR / "permission_test.tmp"
            with open(test_file, 'w') as f:
                f.write("test")
            os.unlink(test_file)
            
        except PermissionError as e:
            self._print_panel("⚠ Permission Error", 
                f"Cannot write to {CONFIG_DIR}\n"
                f"Try: chmod 755 '{CONFIG_DIR}'\n"
                "Do NOT use sudo!", "error")
            sys.exit(1)
        except Exception as e:
            self._print_panel("⚠ Error", f"Directory check failed: {str(e)}", "error")
            sys.exit(1)

    def _check_apis(self):
        """Manual API connection check (called via !check)"""
        results = []
        for provider, client in self.clients.items():
            try:
                # Test with a simple request
                if provider == "openai":
                    models = client.models.list(timeout=5)
                    status = "✅ Working" if models else "⚠️ No response"
                elif provider == "deepseek":
                    models = client.models.list(timeout=5)
                    status = "✅ Working" if models else "⚠️ No response"
                else:
                    status = "⚠️ Unknown provider"
                
                results.append(f"{provider.upper()}: {status}")
            except APIConnectionError as e:
                results.append(f"{provider.upper()}: 🔌 Connection failed")
            except RateLimitError:
                results.append(f"{provider.upper()}: 🚦 Rate limited")
            except APIStatusError as e:
                results.append(f"{provider.upper()}: ⚠️ API error ({e.status_code})")
            except Exception as e:
                results.append(f"{provider.upper()}: ❌ Failed ({str(e)})")
        
        self._print_panel("🔌 API Check Results", "\n".join(results), "primary")

    def _init_readline(self):
        """Initialize readline for command history"""
        if sys.stdin.isatty():
            readline.parse_and_bind("tab: complete")
            histfile = os.path.join(os.path.expanduser("~"), ".carthageai_history")
            try:
                readline.read_history_file(histfile)
            except FileNotFoundError:
                pass
            import atexit
            atexit.register(readline.write_history_file, histfile)

    def _verify_ssl(self):
        """Check SSL configuration"""
        try:
            ssl_version = ssl.OPENSSL_VERSION
            self._log("INFO", f"SSL Version: {ssl_version}")
        except Exception as e:
            self._log("ERROR", f"SSL Check Failed: {str(e)}")

    def _log(self, level: str, message: str):
        """Log messages with timestamp"""
        if self.debug_log:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level}] {message}\n"
            self.debug_log.write(log_entry)
            self.debug_log.flush()

    def _setup_logging(self):
        """Initialize debug logging"""
        self.debug_log = open(DEBUG_LOG, "a")
        self._log("DEBUG", "CarthageAI initialized")

    def _init_clients(self):
        """Initialize API clients"""
        self.clients = {
            "openai": OpenAI(api_key=self.config.get("openai_key")),
            "deepseek": OpenAI(
                api_key=self.config.get("deepseek_key", "default"),
                base_url="https://api.deepseek.com/v1"
            )
        }

    def _get_client(self):
        """Get client for current provider"""
        return self.clients[self.current_provider]

    def _load_config(self) -> Dict:
        """Load or create config file with API keys."""
        if not CONFIG_FILE.exists():
            self._print_header()
            self._print_panel("🔑 CarthageAI First-Time Setup", 
                            "Welcome! Let's configure your API keys", 
                            "primary")
            
            config = {
                "openai_key": self._prompt_input("OpenAI API Key: ", password=True),
                "deepseek_key": self._prompt_input("DeepSeek API Key (optional): ", password=True)
            }
            
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f)
                
            self._print_panel("✓ Configuration Saved", 
                            f"Settings stored in {CONFIG_FILE}", 
                            "success")
            return config
            
        with open(CONFIG_FILE) as f:
            return json.load(f)

    def _print_header(self):
        """Display application header"""
        if RICH_AVAILABLE:
            header = Text("CarthageAI", style="bold blue")
            subtitle = Text("AI Terminal Assistant with DeepSeek Support", style="dim")
            console.print(Panel(header, subtitle=subtitle, border_style="blue"))
        else:
            print("=== CarthageAI ===")

    def _print_panel(self, title: str, content: str, style: str = "primary"):
        """Print a styled panel"""
        if RICH_AVAILABLE:
            console.print(Panel(content, title=title, style=THEME.get(style, "")))
        else:
            print(f"{title}\n{'-'*len(title)}\n{content}\n")

    def _prompt_input(self, prompt: str, password: bool = False) -> str:
        """Get user input with optional password masking"""
        if RICH_AVAILABLE:
            style = Style(color="magenta", bold=True)
            prompt_text = Text(prompt, style=style)
            if password:
                import getpass
                return getpass.getpass(prompt)
            return console.input(prompt_text)
        return input(prompt)

    def _show_loading(self, message: str = "Thinking..."):
        """Display a loading indicator"""
        if RICH_AVAILABLE:
            with Progress(SpinnerColumn(), transient=True) as progress:
                task = progress.add_task(f"[{THEME['secondary']}]{message}", total=None)
                while not progress.finished:
                    time.sleep(0.1)
        else:
            print(message)

    def _parse_file_references(self, text: str) -> Tuple[str, List[str]]:
        """Extract @file references from text, ignoring email patterns"""
        file_refs = re.findall(r'(?<!\w)@([^\s@]+)', text)
        cleaned_text = re.sub(r'(?<!\w)@([^\s@]+)', '', text).strip()
        return cleaned_text, file_refs

    def _read_file_content(self, file_path: str) -> Optional[str]:
        """Safely read file content with validation"""
        try:
            full_path = Path(file_path).expanduser().resolve()
            
            if not full_path.exists():
                self._print_panel("⚠ Error", f"File not found: {file_path}", "error")
                return None

            if full_path.is_dir():
                self._print_panel("⚠ Error", f"Path is a directory: {file_path}", "error")
                return None

            if full_path.stat().st_size > MAX_FILE_SIZE:
                self._print_panel("⚠ Error", 
                                f"File too large ({full_path.stat().st_size} > {MAX_FILE_SIZE} bytes)", 
                                "error")
                return None

            with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()

        except Exception as e:
            self._print_panel("⚠ Error", f"Could not read file: {str(e)}", "error")
            return None

    def _format_file_prompt(self, question: str, files: Dict[str, str]) -> str:
        """Format file content into AI prompt"""
        prompt = ""
        for file_path, content in files.items():
            file_ext = os.path.splitext(file_path)[1].lower()
            lexer_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.sh': 'bash',
                '.json': 'json',
                '.md': 'markdown',
                '.txt': 'text',
                '.php': 'php',
                '.html': 'html',
                '.css': 'css'
            }
            lexer = lexer_map.get(file_ext, 'text')

            if RICH_AVAILABLE:
                console.print(Panel(
                    Syntax(content, lexer),
                    title=f"📄 {os.path.basename(file_path)}",
                    border_style=THEME["file_ref"]
                ))

            prompt += f"File: {file_path}\nContent:\n```{lexer}\n{content}\n```\n\n"

        prompt += f"Question: {question}"
        return prompt

    def _process_file_references(self, user_input: str) -> Tuple[str, Dict[str, str]]:
        """Handle @file references in user input"""
        question, file_refs = self._parse_file_references(user_input)
        files = {}
        
        for file_ref in file_refs:
            content = self._read_file_content(file_ref)
            if content is not None:
                files[file_ref] = content

        if RICH_AVAILABLE and files:
            console.print(Panel(
                f"Found {len(files)} file(s) to analyze",
                style=THEME["success"]
            ))

        return question, files

    def _call_ai(self, prompt: str) -> str:
        """Make API call using official OpenAI package"""
        self._show_loading()
        
        try:
            response = self._get_client().chat.completions.create(
                model=self.current_model.split('/')[-1],
                messages=[{"role": "user", "content": prompt}],
                timeout=REQUEST_TIMEOUT
            )
            return response.choices[0].message.content
            
        except APIConnectionError as e:
            error_msg = f"Connection error: {e.__cause__}"
            self._log("ERROR", error_msg)
            return f"Error: {error_msg}. Check your internet connection."
            
        except RateLimitError:
            error_msg = "Rate limit exceeded. Please wait before making more requests."
            self._log("ERROR", error_msg)
            return f"Error: {error_msg}"
            
        except APIStatusError as e:
            error_msg = f"API error [{e.status_code}]: {e.message}"
            self._log("ERROR", error_msg)
            return f"Error: {error_msg}"
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self._log("CRITICAL", error_msg)
            return f"Critical Error: {error_msg}. Please check debug.log"

    def _save_session(self):
        """Save chat history to a JSON file."""
        if not self.current_session:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.current_session = f"session_{timestamp}.json"
            
        with open(CHAT_DIR / self.current_session, "w") as f:
            json.dump({
                "model": self.current_model,
                "history": self.chat_history,
                "description": f"Session with {len(self.chat_history)} messages"
            }, f, indent=2)
            
        self._print_panel("✓ Session Saved", 
                         f"Saved as {self.current_session}", 
                         "success")

    def _load_session(self, session_id: str):
        """Load a previous chat session."""
        session_file = CHAT_DIR / f"{session_id}.json"
        if session_file.exists():
            try:
                with open(session_file) as f:
                    data = json.load(f)
                self.chat_history = data.get("history", [])
                self.current_model = data.get("model", self.current_model)
                self.current_session = f"{session_id}.json"
                self._print_panel("✓ Session Loaded", 
                                 f"Loaded {len(self.chat_history)} messages from {session_id}", 
                                 "success")
            except Exception as e:
                error_msg = f"Error loading session: {str(e)}"
                self._log("ERROR", error_msg)
                self._print_panel("⚠ Error", error_msg, "error")
        else:
            error_msg = f"Session {session_id} not found!"
            self._log("ERROR", error_msg)
            self._print_panel("⚠ Error", error_msg, "error")

    def _list_sessions(self):
        """List all available sessions"""
        sessions = list(CHAT_DIR.glob("*.json"))
        
        if not sessions:
            self._print_panel("No Sessions Found", 
                             "You don't have any saved sessions yet", 
                             "warning")
            return
            
        if RICH_AVAILABLE:
            table = Table(title="Saved Sessions", border_style="blue")
            table.add_column("ID", style="cyan")
            table.add_column("Description")
            table.add_column("Last Modified")
            table.add_column("Messages")
            table.add_column("Model")
            
            for session in sorted(sessions, key=lambda x: x.stat().st_mtime, reverse=True):
                with open(session) as f:
                    data = json.load(f)
                    messages = len(data.get("history", []))
                    model = data.get("model", "unknown")
                    desc = data.get("description", "No description")
                mod_time = datetime.fromtimestamp(session.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                table.add_row(session.stem, desc, mod_time, str(messages), model)
                
            console.print(table)
        else:
            print("Saved sessions:")
            for session in sessions:
                print(f"- {session.stem}")

    def _print_response(self, text: str):
        """Print AI response with rich formatting"""
        if RICH_AVAILABLE:
            text = re.sub(r'```(\w+)?\n(.*?)```', 
                         lambda m: f"\n[on black]{m.group(2)}[/]\n" if m.group(2) else "", 
                         text, flags=re.DOTALL)
            
            panel = Panel(
                Markdown(text),
                title=f"🤖 CarthageAI ({self.current_model})",
                title_align="left",
                border_style=THEME["ai"],
                style=THEME["ai"]
            )
            console.print(panel)
        else:
            print(f"AI ({self.current_model}): {text}")

    def _print_help(self):
        """Display help information"""
        help_text = f"""
        [bold]Available Commands:[/bold]
        [green]General:[/green]
        !help       - Show this help
        !save       - Save current conversation
        !exit       - End session
        !new        - Start new chat
        !files      - List available sessions
        !load <id>  - Load a previous session
        !model      - Switch AI model (current: {self.current_model})
        !debug      - Check system info
        !check      - Test API connections

        [green]File Analysis:[/green]
        @file.ext    - Reference a file in your question
        Example: "What's wrong with @test.php?"
        
        [green]Sysadmin Tools:[/green]
        !portcheck <host> <port> - Check open port
        !ping <host>      - Network connectivity test
        !diskspace       - Show disk usage
        !findproc <name> - Find running processes
        !sudocheck       - List sudo users
        !sshcheck        - Audit SSH config

        [green]Shortcuts:[/green]
        Up/Down arrows - Command history
        Ctrl+C         - Cancel input
        """
        
        if RICH_AVAILABLE:
            console.print(Panel(help_text, title="Help", border_style=THEME["secondary"]))
        else:
            print(help_text)

    def _switch_model(self):
        """Switch between available AI models"""
        available_models = []
        
        if self.config.get("openai_key"):
            available_models.extend([f"openai/{m}" for m in MODELS["openai"]])
        if self.config.get("deepseek_key"):
            available_models.extend([f"deepseek/{m}" for m in MODELS["deepseek"]])
        
        if not available_models:
            self._print_panel("⚠ Error", "No API keys configured for any model!", "error")
            return
        
        self._print_panel("Available Models", "\n".join(f"- {m}" for m in available_models), "secondary")
        new_model = self._prompt_input(f"Select model (current: {self.current_model}): ")
        
        if new_model in available_models:
            self.current_provider, self.current_model = new_model.split('/')
            self._print_panel("✓ Model Changed", f"Now using: {new_model}", "success")
        else:
            self._print_panel("⚠ Error", "Invalid model selection", "error")

    def _check_port(self, host: str, port: int):
        """Check if a port is open"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                result = s.connect_ex((host, port))
                status = "OPEN" if result == 0 else "CLOSED"
                self._print_panel("🔌 Port Check", 
                                f"Host: {host}\nPort: {port}\nStatus: {status}", 
                                "success" if status == "OPEN" else "warning")
        except Exception as e:
            self._print_panel("⚠ Error", f"Port check failed: {str(e)}", "error")

    def _ping_host(self, host: str):
        """Ping a network host"""
        try:
            result = subprocess.run(
                ["ping", "-c", "4", host],
                capture_output=True,
                text=True
            )
            self._print_panel("📶 Ping Results", result.stdout, "secondary")
        except Exception as e:
            self._print_panel("⚠ Error", f"Ping failed: {str(e)}", "error")

    def _get_disk_usage(self) -> str:
        """Get disk usage information"""
        try:
            result = subprocess.run(
                ["df", "-h"],
                capture_output=True,
                text=True
            )
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"

    def _find_process(self, name: str):
        """Find running processes by name"""
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True
            )
            matches = [line for line in result.stdout.split('\n') if name in line]
            
            if matches:
                self._print_panel(f"🔄 Processes: {name}", "\n".join(matches), "secondary")
            else:
                self._print_panel("⚠ Not Found", f"No processes matching '{name}'", "warning")
        except Exception as e:
            self._print_panel("⚠ Error", f"Process search failed: {str(e)}", "error")

    def _check_sudo_users(self):
        """List users with sudo privileges"""
        try:
            result = subprocess.run(
                ["grep", "-Po", '^sudo.+:\\K.*$', "/etc/group"],
                capture_output=True,
                text=True
            )
            users = result.stdout.strip().split(',')
            self._print_panel("🛡 Sudo Users", "\n".join(users) if users else "No sudo users", "secondary")
        except Exception as e:
            self._print_panel("⚠ Error", f"Sudo check failed: {str(e)}", "error")

    def _check_ssh_config(self):
        """Audit SSH server configuration"""
        try:
            with open("/etc/ssh/sshd_config", "r") as f:
                content = f.read()
            
            checks = {
                "PermitRootLogin": "Should be 'no'",
                "PasswordAuthentication": "Should be 'no'",
                "Protocol": "Should be '2'"
            }
            
            results = []
            for key, recommendation in checks.items():
                match = re.search(f"^{key}\\s+(.+)", content, re.MULTILINE)
                value = match.group(1) if match else "Not set"
                results.append(f"{key}: {value} ({recommendation})")
            
            self._print_panel("🔐 SSH Audit", "\n".join(results), "secondary")
        except Exception as e:
            self._print_panel("⚠ Error", f"SSH check failed: {str(e)}", "error")

    def _handle_command(self, user_input: str) -> bool:
        """Handle special commands, returns True if should continue"""
        if user_input.lower() in ('exit', 'quit'):
            return False
        elif user_input.lower() == '!help':
            self._print_help()
        elif user_input.lower() == '!save':
            self._save_session()
        elif user_input.lower() == '!files':
            self._list_sessions()
        elif user_input.lower().startswith('!load '):
            session_id = user_input[6:].strip()
            self._load_session(session_id)
        elif user_input.lower() == '!new':
            self.chat_history = []
            self.current_session = None
            self.start_time = datetime.now()
            self._print_panel("✓ New Session", "Started fresh conversation", "success")
        elif user_input.lower() == '!model':
            self._switch_model()
        elif user_input.lower() == '!debug':
            self._print_panel("💽 Disk Space", self._get_disk_usage(), "secondary")
        elif user_input.lower() == '!check':
            self._check_apis()
        elif user_input.lower().startswith('!portcheck '):
            parts = user_input[11:].split()
            if len(parts) == 2:
                self._check_port(parts[0], int(parts[1]))
            else:
                self._print_panel("⚠ Error", "Usage: !portcheck <host> <port>", "error")
        elif user_input.lower().startswith('!ping '):
            self._ping_host(user_input[6:].strip())
        elif user_input.lower() == '!diskspace':
            self._print_panel("💽 Disk Space", self._get_disk_usage(), "secondary")
        elif user_input.lower().startswith('!findproc '):
            self._find_process(user_input[10:].strip())
        elif user_input.lower() == '!sudocheck':
            self._check_sudo_users()
        elif user_input.lower() == '!sshcheck':
            self._check_ssh_config()
        else:
            question, files = self._process_file_references(user_input)
            if files:
                prompt = self._format_file_prompt(question, files)
            else:
                prompt = user_input

            response = self._call_ai(prompt)
            self._print_response(response)
            self.chat_history.append({
                "timestamp": datetime.now().isoformat(),
                "user": user_input,
                "ai": response,
                "model": self.current_model
            })
            
        return True

    def run_cli(self):
        """Main CLI interface"""
        self._print_header()
        
        parser = argparse.ArgumentParser(description="CarthageAI - AI Terminal Assistant")
        parser.add_argument("query", nargs="?", help="Direct question for AI")
        parser.add_argument("--file", help="Analyze a file's content")
        parser.add_argument("--model", help="AI model to use")
        parser.add_argument("--session", help="Load a previous session")
        parser.add_argument("--list-sessions", action="store_true", help="List saved sessions")
        args = parser.parse_args()

        if args.list_sessions:
            self._list_sessions()
            return

        if args.session:
            self._load_session(args.session)

        if args.model:
            if '/' in args.model:
                provider, model = args.model.split('/')
                if provider in self.clients:
                    self.current_provider = provider
                    self.current_model = model
                    self._print_panel("✓ Model Set", f"Using: {args.model}", "success")
                else:
                    self._print_panel("⚠ Error", f"Invalid provider: {provider}", "error")
                    return
            else:
                self._print_panel("⚠ Error", "Specify model as provider/model (e.g. deepseek/deepseek-chat)", "error")
                return

        if args.query:
            prompt = args.query
            if args.file:
                content = self._read_file_content(args.file)
                if content:
                    prompt = self._format_file_prompt(prompt, {args.file: content})

            response = self._call_ai(prompt)
            self._print_response(response)
            self.chat_history.append({
                "timestamp": datetime.now().isoformat(),
                "user": prompt,
                "ai": response,
                "model": self.current_model
            })
            self._save_session()
        else:
            self._print_panel("💬 Interactive Mode", 
                            "Type !help for commands or @file to analyze files - https://github.com/alaadotcom", 
                            "primary")
            
            while True:
                try:
                    user_input = self._prompt_input("\nYou: ")
                    if not self._handle_command(user_input):
                        break
                except KeyboardInterrupt:
                    self._print_panel("⚠ Exit", "Use !save to preserve history", "warning")
                    break
                except Exception as e:
                    self._print_panel("⚠ Error", str(e), "error")

if __name__ == "__main__":
    try:
        ai = CarthageAI()
        ai.run_cli()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)