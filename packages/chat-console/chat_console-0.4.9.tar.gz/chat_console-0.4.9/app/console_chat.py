#!/usr/bin/env python3
"""
Pure Console Chat CLI - No Textual Dependencies
A true terminal interface following Dieter Rams principles
"""

import os
import sys
import asyncio
import argparse
import signal
import threading
import time
import random
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
import shutil

from .models import Message, Conversation
from .database import ChatDatabase
from .config import CONFIG, save_config
from .utils import resolve_model_id, generate_conversation_title
from .console_utils import console_streaming_response, apply_style_prefix
from .api.base import BaseModelClient

class ConsoleUI:
    """Pure console UI following Rams design principles with Gemini-inspired enhancements"""
    
    def __init__(self):
        self.width = min(shutil.get_terminal_size().columns, 120)
        self.height = shutil.get_terminal_size().lines
        self.db = ChatDatabase()
        self.current_conversation: Optional[Conversation] = None
        self.messages: List[Message] = []
        self.selected_model = resolve_model_id(CONFIG["default_model"])
        self.selected_style = CONFIG["default_style"]
        self.running = True
        self.generating = False
        self.input_mode = "text"  # "text" or "menu"
        self.multi_line_input = []
        self.input_history = []
        self.history_index = 0
        self.theme = self._load_theme()
        self.loading_phrases = [
            "Thinking deeply", "Crafting response", "Processing context",
            "Analyzing request", "Generating ideas", "Considering options",
            "Formulating answer", "Connecting concepts", "Refining thoughts"
        ]
        self.loading_phase_index = 0
        self.start_time = time.time()
        
        # Suppress verbose logging for console mode
        self._setup_console_logging()
    
    def _load_theme(self) -> Dict[str, str]:
        """Load color theme configuration"""
        try:
            # Try to import colorama for colors
            from colorama import Fore, Back, Style, init
            init(autoreset=True)
            
            # Default theme inspired by gemini-code-assist
            return {
                'primary': Fore.CYAN,
                'secondary': Fore.BLUE,
                'accent': Fore.MAGENTA,
                'success': Fore.GREEN,
                'warning': Fore.YELLOW,
                'error': Fore.RED,
                'muted': Fore.LIGHTBLACK_EX,
                'text': Fore.WHITE,
                'reset': Style.RESET_ALL,
                'bold': Style.BRIGHT,
                'dim': Style.DIM
            }
        except ImportError:
            # Fallback to no colors if colorama not available
            return {key: '' for key in [
                'primary', 'secondary', 'accent', 'success', 'warning', 
                'error', 'muted', 'text', 'reset', 'bold', 'dim'
            ]}
    
    def _setup_console_logging(self):
        """Setup logging to minimize disruption to console UI"""
        import logging
        
        # Set root logger to ERROR to suppress all INFO messages
        logging.getLogger().setLevel(logging.ERROR)
        
        # Suppress all app module logging
        logging.getLogger('app').setLevel(logging.ERROR)
        logging.getLogger('app.api').setLevel(logging.ERROR)
        logging.getLogger('app.api.base').setLevel(logging.ERROR)
        logging.getLogger('app.api.ollama').setLevel(logging.ERROR)
        logging.getLogger('app.utils').setLevel(logging.ERROR)
        logging.getLogger('app.console_utils').setLevel(logging.ERROR)
        
        # Suppress third-party library logging
        logging.getLogger('aiohttp').setLevel(logging.ERROR)
        logging.getLogger('urllib3').setLevel(logging.ERROR)
        logging.getLogger('httpx').setLevel(logging.ERROR)
        logging.getLogger('asyncio').setLevel(logging.ERROR)
        logging.getLogger('root').setLevel(logging.ERROR)
        
        # Completely disable all handlers to prevent any output
        logging.basicConfig(
            level=logging.CRITICAL,  # Only show CRITICAL messages
            format='',  # Empty format
            handlers=[logging.NullHandler()]  # Null handler suppresses all output
        )
        
        # Clear any existing handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # Add only NullHandler
        logging.root.addHandler(logging.NullHandler())
        
        # Redirect stdout/stderr for subprocess calls (if any)
        self._dev_null = open(os.devnull, 'w')
        
    def _suppress_output(self):
        """Context manager to suppress all output during sensitive operations"""
        import sys
        import contextlib
        
        @contextlib.contextmanager
        def suppress():
            with open(os.devnull, "w") as devnull:
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                try:
                    sys.stdout = devnull
                    sys.stderr = devnull
                    yield
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
        
        return suppress()
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_border_chars(self):
        """Get clean ASCII border characters"""
        return {
            'horizontal': '─',
            'vertical': '│',
            'top_left': '┌',
            'top_right': '┐',
            'bottom_left': '└',
            'bottom_right': '┘',
            'tee_down': '┬',
            'tee_up': '┴',
            'tee_right': '├',
            'tee_left': '┤'
        }
    
    def draw_border_line(self, width: int, position: str = 'top') -> str:
        """Draw a clean border line"""
        chars = self.get_border_chars()
        
        if position == 'top':
            return chars['top_left'] + chars['horizontal'] * (width - 2) + chars['top_right']
        elif position == 'bottom':
            return chars['bottom_left'] + chars['horizontal'] * (width - 2) + chars['bottom_right']
        elif position == 'middle':
            return chars['tee_right'] + chars['horizontal'] * (width - 2) + chars['tee_left']
        else:
            return chars['horizontal'] * width
    
    def draw_header(self) -> List[str]:
        """Draw the application header with colors"""
        from . import __version__
        chars = self.get_border_chars()
        
        lines = []
        
        # Top border with title and model info
        title = f" {self.theme['primary']}Chat Console{self.theme['reset']} v{__version__} "
        model_info = f" Model: {self.theme['accent']}{self.selected_model}{self.theme['reset']} "
        
        # Calculate spacing (without color codes for length calculation)
        title_plain = f" Chat Console v{__version__} "
        model_plain = f" Model: {self.selected_model} "
        used_space = len(title_plain) + len(model_plain)
        remaining = self.width - used_space - 2
        spacing = chars['horizontal'] * max(0, remaining)
        
        header_line = f"{self.theme['muted']}{chars['top_left']}{title}{spacing}{model_info}{chars['top_right']}{self.theme['reset']}"
        lines.append(header_line)
        
        # Conversation title
        conv_title = self.current_conversation.title if self.current_conversation else "New Conversation"
        title_content = f" {self.theme['secondary']}{conv_title}{self.theme['reset']} "
        padding_needed = self.width - 2 - len(conv_title) - 1
        title_line = f"{self.theme['muted']}{chars['vertical']}{title_content}{' ' * padding_needed}{chars['vertical']}{self.theme['reset']}"
        lines.append(title_line)
        
        # Separator
        separator = f"{self.theme['muted']}{self.draw_border_line(self.width, 'middle')}{self.theme['reset']}"
        lines.append(separator)
        
        return lines
    
    def draw_footer(self) -> List[str]:
        """Draw the footer with colorized controls"""
        chars = self.get_border_chars()
        
        # Colorize control keys
        controls = (f"{self.theme['accent']}[Tab]{self.theme['reset']} Menu Mode  "
                   f"{self.theme['accent']}[q]{self.theme['reset']} Quit  "
                   f"{self.theme['accent']}[n]{self.theme['reset']} New  "
                   f"{self.theme['accent']}[h]{self.theme['reset']} History  "
                   f"{self.theme['accent']}[s]{self.theme['reset']} Settings  "
                   f"{self.theme['accent']}[m]{self.theme['reset']} Models")
        
        # Calculate plain text length for padding
        controls_plain = "[Tab] Menu Mode  [q] Quit  [n] New  [h] History  [s] Settings  [m] Models"
        padding_needed = self.width - 2 - len(controls_plain) - 1
        
        footer_line = f"{self.theme['muted']}{chars['vertical']} {controls}{' ' * padding_needed}{chars['vertical']}{self.theme['reset']}"
        
        return [
            f"{self.theme['muted']}{self.draw_border_line(self.width, 'middle')}{self.theme['reset']}",
            footer_line,
            f"{self.theme['muted']}{self.draw_border_line(self.width, 'bottom')}{self.theme['reset']}"
        ]
    
    def format_message(self, message: Message) -> List[str]:
        """Enhanced message formatting with colors, code highlighting and better wrapping"""
        timestamp = datetime.now().strftime("%H:%M")
        chars = self.get_border_chars()
        
        # Calculate available width for content
        content_width = self.width - 10  # Account for borders and timestamp
        
        # Apply code highlighting if enabled
        highlighted_content = self._detect_and_highlight_code(message.content)
        
        # Use improved word wrapping
        lines = self._improved_word_wrap(highlighted_content, content_width)
        
        # Format lines with proper spacing and colors
        formatted_lines = []
        for i, line in enumerate(lines):
            if i == 0:
                # First line with colorized timestamp and role indicator
                if message.role == "user":
                    role_indicator = f"{self.theme['primary']}👤{self.theme['reset']}"
                    role_color = self.theme['primary']
                else:
                    role_indicator = f"{self.theme['accent']}🤖{self.theme['reset']}"
                    role_color = self.theme['accent']
                    
                prefix = f" {role_indicator} {self.theme['muted']}{timestamp}{self.theme['reset']} "
                
                # Calculate plain text length for proper alignment
                prefix_plain = f" 👤 {timestamp} "
                content_padding = content_width - len(prefix_plain) - len(line.replace(self.theme.get('accent', ''), '').replace(self.theme.get('reset', ''), ''))
                
                formatted_line = f"{self.theme['muted']}{chars['vertical']}{prefix}{line}{' ' * max(0, content_padding)}{chars['vertical']}{self.theme['reset']}"
            else:
                # Continuation lines with proper indentation
                prefix = "        "  # Align with content
                content_padding = content_width - len(prefix) - len(line.replace(self.theme.get('accent', ''), '').replace(self.theme.get('reset', ''), ''))
                formatted_line = f"{self.theme['muted']}{chars['vertical']}{prefix}{line}{' ' * max(0, content_padding)}{chars['vertical']}{self.theme['reset']}"
            formatted_lines.append(formatted_line)
        
        # Add empty line for spacing
        empty_line = f"{self.theme['muted']}{chars['vertical']}{' ' * (self.width - 2)}{chars['vertical']}{self.theme['reset']}"
        formatted_lines.append(empty_line)
        
        return formatted_lines
    
    def _detect_and_highlight_code(self, content: str) -> str:
        """Detect and highlight code blocks in content"""
        if not CONFIG.get("highlight_code", True):
            return content
            
        try:
            # Try to import colorama for terminal colors
            from colorama import Fore, Style, init
            init()  # Initialize colorama
            
            lines = content.split('\n')
            result_lines = []
            in_code_block = False
            
            for line in lines:
                # Detect code block markers
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    if in_code_block:
                        result_lines.append(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
                    else:
                        result_lines.append(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
                elif in_code_block:
                    # Highlight code content
                    result_lines.append(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
                elif '`' in line and line.count('`') >= 2:
                    # Inline code highlighting
                    import re
                    highlighted = re.sub(
                        r'`([^`]+)`', 
                        f'{Fore.GREEN}`\\1`{Style.RESET_ALL}', 
                        line
                    )
                    result_lines.append(highlighted)
                else:
                    result_lines.append(line)
            
            return '\n'.join(result_lines)
            
        except ImportError:
            # Colorama not available, return content as-is
            return content
        except Exception:
            # Any other error, return content as-is
            return content
    
    def _improved_word_wrap(self, text: str, width: int) -> List[str]:
        """Improved word wrapping that preserves code blocks and handles long lines"""
        lines = text.split('\n')
        wrapped_lines = []
        
        for line in lines:
            # Handle very long lines (like URLs or code)
            if len(line) > width:
                # If it looks like code or a URL, don't break it aggressively
                if (line.strip().startswith(('http', 'https', 'www', '  ', '\t')) or 
                    '```' in line or line.count('`') >= 2):
                    # Add as-is but truncate if necessary
                    if len(line) > width:
                        wrapped_lines.append(line[:width-3] + "...")
                    else:
                        wrapped_lines.append(line)
                else:
                    # Normal word wrapping
                    words = line.split()
                    current_line = ""
                    
                    for word in words:
                        if len(current_line) + len(word) + 1 <= width:
                            if current_line:
                                current_line += " "
                            current_line += word
                        else:
                            if current_line:
                                wrapped_lines.append(current_line)
                            current_line = word
                    
                    if current_line:
                        wrapped_lines.append(current_line)
            else:
                # Line fits, add as-is
                wrapped_lines.append(line)
        
        return wrapped_lines or [""]
    
    def draw_ascii_welcome(self) -> List[str]:
        """Draw ASCII art welcome screen"""
        chars = self.get_border_chars()
        lines = []
        
        # ASCII art that scales with terminal width
        if self.width >= 80:
            ascii_art = [
                "    ┌─┐┬ ┬┌─┐┌┬┐  ┌─┐┌─┐┌┐┌┌─┐┌─┐┬  ┌─┐",
                "    │  ├─┤├─┤ │   │  │ ││││└─┐│ ││  ├┤ ",
                "    └─┘┴ ┴┴ ┴ ┴   └─┘└─┘┘└┘└─┘└─┘┴─┘└─┘"
            ]
        elif self.width >= 60:
            ascii_art = [
                "  ┌─┐┬ ┬┌─┐┌┬┐",
                "  │  ├─┤├─┤ │ ",
                "  └─┘┴ ┴┴ ┴ ┴ "
            ]
        else:
            ascii_art = ["Chat Console"]
        
        # Center and colorize ASCII art
        for art_line in ascii_art:
            centered = art_line.center(self.width - 2)
            colored_line = f"{self.theme['muted']}{chars['vertical']} {self.theme['primary']}{centered}{self.theme['muted']} {chars['vertical']}{self.theme['reset']}"
            lines.append(colored_line)
        
        # Add spacing
        empty_line = f"{self.theme['muted']}{chars['vertical']}{' ' * (self.width - 2)}{chars['vertical']}{self.theme['reset']}"
        lines.append(empty_line)
        
        # Add tips
        tips = [
            f"{self.theme['secondary']}💡 Pro Tips:{self.theme['reset']}",
            f"{self.theme['accent']}• Use Shift+Enter for multi-line input{self.theme['reset']}",
            f"{self.theme['accent']}• Press Tab to switch between text and menu modes{self.theme['reset']}",
            f"{self.theme['accent']}• Try 'm' for model browser{self.theme['reset']}"
        ]
        
        for tip in tips:
            # Calculate plain text length for padding
            tip_plain = tip.replace(self.theme.get('secondary', ''), '').replace(self.theme.get('accent', ''), '').replace(self.theme.get('reset', ''), '')
            padding = (self.width - 2 - len(tip_plain)) // 2
            tip_line = f"{self.theme['muted']}{chars['vertical']}{' ' * padding}{tip}{' ' * (self.width - 2 - len(tip_plain) - padding)}{chars['vertical']}{self.theme['reset']}"
            lines.append(tip_line)
        
        return lines

    def draw_messages(self) -> List[str]:
        """Draw all messages in the conversation with enhanced empty state"""
        lines = []
        chars = self.get_border_chars()
        
        if not self.messages:
            # Enhanced empty state with ASCII welcome
            lines.extend(self.draw_ascii_welcome())
        else:
            # Display messages
            for message in self.messages[-10:]:  # Show last 10 messages
                lines.extend(self.format_message(message))
        
        return lines
    
    def draw_input_area(self, current_input: str = "", prompt: str = "Type your message") -> List[str]:
        """Draw the input area with mode indicator"""
        chars = self.get_border_chars()
        lines = []
        
        # Input prompt with mode indicator
        mode_indicator = "📝" if self.input_mode == "text" else "⚡"
        mode_text = "TEXT" if self.input_mode == "text" else "MENU"
        prompt_with_mode = f"{mode_indicator} {prompt} ({mode_text} mode - Tab to switch)"
        prompt_line = chars['vertical'] + f" {prompt_with_mode}: ".ljust(self.width - 2) + chars['vertical']
        lines.append(prompt_line)
        
        # Input field
        if self.input_mode == "text":
            input_content = current_input
            if len(input_content) > self.width - 6:
                input_content = input_content[-(self.width - 9):] + "..."
            input_line = chars['vertical'] + f" > {input_content}".ljust(self.width - 2) + chars['vertical']
        else:
            # Menu mode - show available hotkeys
            menu_help = "n)ew  h)istory  s)ettings  m)odels  q)uit"
            input_line = chars['vertical'] + f" {menu_help}".ljust(self.width - 2) + chars['vertical']
        
        lines.append(input_line)
        
        # Show generating indicator if needed
        if self.generating:
            status_line = chars['vertical'] + " ● Generating response...".ljust(self.width - 2) + chars['vertical']
            lines.append(status_line)
        
        return lines
    
    def draw_screen(self, current_input: str = "", input_prompt: str = "Type your message"):
        """Draw the complete screen"""
        self.clear_screen()
        
        # Calculate layout
        header_lines = self.draw_header()
        footer_lines = self.draw_footer()
        input_lines = self.draw_input_area(current_input, input_prompt)
        
        # Calculate available space for messages
        used_lines = len(header_lines) + len(footer_lines) + len(input_lines)
        available_lines = self.height - used_lines - 2
        
        # Draw header
        for line in header_lines:
            print(line)
        
        # Draw messages
        message_lines = self.draw_messages()
        chars = self.get_border_chars()
        
        # Pad or truncate message area
        if len(message_lines) < available_lines:
            # Pad with empty lines
            empty_line = chars['vertical'] + " " * (self.width - 2) + chars['vertical']
            message_lines.extend([empty_line] * (available_lines - len(message_lines)))
        else:
            # Truncate to fit
            message_lines = message_lines[-available_lines:]
        
        for line in message_lines:
            print(line)
        
        # Draw input area
        for line in input_lines:
            print(line)
        
        # Draw footer
        for line in footer_lines:
            print(line)
        
        # Position cursor
        print("\033[A" * (len(footer_lines) + len(input_lines) - 1), end="")
        print(f"\033[{len(current_input) + 4}C", end="")
        sys.stdout.flush()
    
    def get_input(self, prompt: str = "Type your message") -> str:
        """Enhanced input with multi-line support, history navigation, and hotkey support"""
        # Check if we're in multi-line mode
        if self.multi_line_input:
            current_input = "\n".join(self.multi_line_input)
        else:
            current_input = ""
        
        while True:
            # Update prompt based on multi-line state
            if self.multi_line_input:
                display_prompt = f"Multi-line input (Ctrl+D to send, Esc to cancel)"
            else:
                display_prompt = prompt
                
            self.draw_screen(current_input, display_prompt)
            
            # Get character input with escape sequence handling
            char = self._get_char_with_escape_sequences()
            
            # Handle escape sequences for arrow keys
            if char.startswith('\x1b['):
                if char == '\x1b[A':  # Up arrow - history navigation
                    if self.input_history and self.history_index > 0:
                        self.history_index -= 1
                        current_input = self.input_history[self.history_index]
                        self.multi_line_input = current_input.split('\n') if '\n' in current_input else []
                elif char == '\x1b[B':  # Down arrow - history navigation
                    if self.history_index < len(self.input_history) - 1:
                        self.history_index += 1
                        current_input = self.input_history[self.history_index]
                        self.multi_line_input = current_input.split('\n') if '\n' in current_input else []
                    elif self.history_index == len(self.input_history) - 1:
                        self.history_index = len(self.input_history)
                        current_input = ""
                        self.multi_line_input = []
                continue
            
            # Handle special keys
            if char == '\t':
                # Tab - switch between text and menu mode
                self.input_mode = "menu" if self.input_mode == "text" else "text"
                continue
            elif char == '\r' or char == '\n':
                # Enter - either new line (Shift+Enter) or submit
                if self.input_mode == "text":
                    if self.multi_line_input:
                        # In multi-line mode, add new line
                        self.multi_line_input.append("")
                        current_input = "\n".join(self.multi_line_input)
                    else:
                        # Check for Shift+Enter to start multi-line
                        # For simplicity, just Enter submits, Shift+Enter would need platform-specific detection
                        if current_input.strip():
                            # Add to history
                            if current_input not in self.input_history:
                                self.input_history.append(current_input)
                            self.history_index = len(self.input_history)
                            return current_input.strip()
                        else:
                            self.input_mode = "menu"
                    continue
                else:
                    # In menu mode, Enter does nothing
                    continue
            elif char == '\x04':  # Ctrl+D - send multi-line input
                if self.multi_line_input and any(line.strip() for line in self.multi_line_input):
                    final_input = "\n".join(self.multi_line_input).strip()
                    if final_input not in self.input_history:
                        self.input_history.append(final_input)
                    self.history_index = len(self.input_history)
                    self.multi_line_input = []
                    return final_input
            elif char == '\x1b':  # Escape - cancel multi-line or switch to text mode
                if self.multi_line_input:
                    self.multi_line_input = []
                    current_input = ""
                else:
                    self.input_mode = "text"
                continue
            elif char == '\x03':
                # Ctrl+C
                if self.generating:
                    self.generating = False
                    return ""
                else:
                    raise KeyboardInterrupt
            
            # Mode-specific handling
            if self.input_mode == "text":
                # Text input mode
                if char == '\x7f' or char == '\x08':
                    # Backspace
                    if self.multi_line_input:
                        if self.multi_line_input[-1]:
                            self.multi_line_input[-1] = self.multi_line_input[-1][:-1]
                        elif len(self.multi_line_input) > 1:
                            self.multi_line_input.pop()
                        current_input = "\n".join(self.multi_line_input)
                    else:
                        current_input = current_input[:-1]
                elif char == '\x0a':  # Shift+Enter equivalent (start multi-line)
                    if not self.multi_line_input:
                        self.multi_line_input = [current_input, ""]
                        current_input = "\n".join(self.multi_line_input)
                elif ord(char) >= 32:
                    # Printable character
                    if self.multi_line_input:
                        self.multi_line_input[-1] += char
                        current_input = "\n".join(self.multi_line_input)
                    else:
                        current_input += char
            else:
                # Menu mode - handle hotkeys
                if char.lower() == 'q':
                    return "##QUIT##"
                elif char.lower() == 'n':
                    return "##NEW##"
                elif char.lower() == 'h':
                    return "##HISTORY##"
                elif char.lower() == 's':
                    return "##SETTINGS##"
                elif char.lower() == 'm':
                    return "##MODELS##"
                elif char == '\x1b':  # Escape - back to text mode
                    self.input_mode = "text"
                    continue
    
    def _get_char_with_escape_sequences(self) -> str:
        """Get character input with support for escape sequences (arrow keys)"""
        if os.name == 'nt':
            import msvcrt
            char = msvcrt.getch()
            if char == b'\xe0':  # Special key prefix on Windows
                char = msvcrt.getch()
                if char == b'H':  # Up arrow
                    return '\x1b[A'
                elif char == b'P':  # Down arrow
                    return '\x1b[B'
            return char.decode('utf-8', errors='ignore')
        else:
            import termios, tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                char = sys.stdin.read(1)
                if char == '\x1b':  # Escape sequence
                    char += sys.stdin.read(2)  # Read [A, [B, etc.
                return char
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def _get_dynamic_loading_phrase(self) -> str:
        """Get current loading phrase with cycling inspired by gemini-code-assist usePhraseCycler"""
        elapsed = time.time() - self.start_time
        # Change phrase every 2 seconds
        phrase_index = int(elapsed // 2) % len(self.loading_phrases)
        return self.loading_phrases[phrase_index]
    
    def _update_streaming_display(self, content: str):
        """Update display during streaming without clearing screen"""
        if not self.generating:
            return
            
        # Show dynamic loading indicator with cycling phrases
        elapsed = int(time.time() - self.start_time)
        phrase = self._get_dynamic_loading_phrase()
        
        # Simple cursor positioning update instead of full screen redraw
        print(f"\r{self.theme['accent']}● {phrase}... {self.theme['muted']}({elapsed}s){self.theme['reset']}", end="", flush=True)
        
        # Periodically redraw full screen (every 5 seconds or significant content changes)
        if elapsed % 5 == 0 or len(content) > self.loading_phase_index + 100:
            self.loading_phase_index = len(content)
            # Update the assistant message and redraw
            self.draw_screen("", f"{phrase} ({elapsed}s)")
    
    async def create_new_conversation(self):
        """Create a new conversation"""
        title = "New Conversation"
        conversation_id = self.db.create_conversation(title, self.selected_model, self.selected_style)
        conversation_data = self.db.get_conversation(conversation_id)
        self.current_conversation = Conversation.from_dict(conversation_data)
        self.messages = []
        
    async def add_message(self, role: str, content: str):
        """Add a message to the current conversation"""
        message = Message(role=role, content=content)
        self.messages.append(message)
        
        if self.current_conversation:
            self.db.add_message(self.current_conversation.id, role, content)
    
    async def _generate_title_background(self, first_message: str):
        """Generate conversation title in background after first user message"""
        if not CONFIG.get("generate_dynamic_titles", True):
            return
            
        try:
            # Get client for title generation
            with self._suppress_output():
                client = await BaseModelClient.get_client_for_model(self.selected_model)
            
            # Generate title
            new_title = await generate_conversation_title(first_message, self.selected_model, client)
            
            # Update conversation title in database and UI
            if self.current_conversation and new_title and new_title != "New Conversation":
                self.db.update_conversation_title(self.current_conversation.id, new_title)
                self.current_conversation.title = new_title
                
        except Exception:
            # Silently fail - title generation is not critical
            pass
    
    async def generate_response(self, user_message: str):
        """Generate AI response with enhanced streaming display"""
        self.generating = True
        self.start_time = time.time()  # Reset timer for this generation
        
        try:
            # Add user message
            await self.add_message("user", user_message)
            
            # Generate title for first user message if this is a new conversation
            if (self.current_conversation and 
                self.current_conversation.title == "New Conversation" and 
                len([msg for msg in self.messages if msg.role == "user"]) == 1):
                # Generate title in background (non-blocking)
                import asyncio
                asyncio.create_task(self._generate_title_background(user_message))
            
            # Prepare messages for API
            api_messages = []
            for msg in self.messages:
                api_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Get client with appropriate output suppression
            model_info = CONFIG["available_models"].get(self.selected_model, {})
            is_ollama = (model_info.get("provider") == "ollama" or 
                        "ollama" in self.selected_model.lower() or 
                        self.selected_model in ["gemma:2b", "gemma:7b", "llama3:8b", "mistral:7b"])
            
            if is_ollama:
                with self._suppress_output():
                    client = await BaseModelClient.get_client_for_model(self.selected_model)
            else:
                client = await BaseModelClient.get_client_for_model(self.selected_model)
            
            # Add assistant message
            assistant_message = Message(role="assistant", content="")
            self.messages.append(assistant_message)
            
            # Stream response
            full_response = ""
            
            def update_callback(content: str):
                nonlocal full_response
                full_response = content
                assistant_message.content = content
                # Update screen with streaming content instead of clearing
                self._update_streaming_display(content)
            
            # Apply style to messages
            styled_messages = apply_style_prefix(api_messages, self.selected_style)
            
            # Generate streaming response with output suppression
            with self._suppress_output():
                async for chunk in console_streaming_response(
                    styled_messages, self.selected_model, self.selected_style, client, update_callback
                ):
                    if not self.generating:
                        break
                    if chunk:
                        full_response += chunk
            
            # Update final message content
            assistant_message.content = full_response
            
            # Save final response
            if self.current_conversation and full_response:
                self.db.add_message(self.current_conversation.id, "assistant", full_response)
                
        except Exception as e:
            # Handle errors
            error_msg = f"Error: {str(e)}"
            if self.messages and self.messages[-1].role == "assistant":
                self.messages[-1].content = error_msg
            else:
                await self.add_message("assistant", error_msg)
        finally:
            self.generating = False
    
    def show_history(self):
        """Show conversation history"""
        conversations = self.db.get_all_conversations(limit=20)
        if not conversations:
            input("No conversations found. Press Enter to continue...")
            return
        
        self.clear_screen()
        print("=" * self.width)
        print("CONVERSATION HISTORY".center(self.width))
        print("=" * self.width)
        
        for i, conv in enumerate(conversations):
            print(f"{i+1:2d}. {conv['title'][:60]} ({conv['model']})")
        
        print("\nEnter conversation number to load (or press Enter to cancel):")
        
        try:
            choice = input("> ").strip()
            if choice and choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(conversations):
                    # Load conversation
                    conv_data = self.db.get_conversation(conversations[idx]['id'])
                    self.current_conversation = Conversation.from_dict(conv_data)
                    self.messages = [Message(**msg) for msg in self.current_conversation.messages]
        except (ValueError, KeyboardInterrupt):
            pass
    
    async def show_settings(self):
        """Show enhanced settings menu with style selection and persistence"""
        while True:
            self.clear_screen()
            print("=" * self.width)
            print("SETTINGS".center(self.width))
            print("=" * self.width)
            
            print(f"Current Model: {CONFIG['available_models'].get(self.selected_model, {}).get('display_name', self.selected_model)}")
            print(f"Current Style: {CONFIG['user_styles'].get(self.selected_style, {}).get('name', self.selected_style)}")
            print()
            print("What would you like to change?")
            print("1. Model")
            print("2. Response Style")
            print("3. Advanced Settings")
            print("4. Save Settings")
            print("0. Back to Chat")
            
            try:
                choice = input("\n> ").strip()
                
                if choice == "1":
                    # Model selection
                    await self._select_model()
                elif choice == "2":
                    # Style selection
                    self._select_style()
                elif choice == "3":
                    # Advanced settings
                    await self._show_advanced_settings()
                elif choice == "4":
                    # Save settings
                    self._save_settings()
                elif choice == "0" or choice == "":
                    break
                    
            except (ValueError, KeyboardInterrupt):
                break
    
    async def _select_model(self):
        """Enhanced model selection with all providers"""
        self.clear_screen()
        print("=" * self.width)
        print("MODEL SELECTION".center(self.width))
        print("=" * self.width)
        
        # Group models by provider
        providers = {}
        for model_id, model_info in CONFIG["available_models"].items():
            provider = model_info["provider"]
            if provider not in providers:
                providers[provider] = []
            providers[provider].append((model_id, model_info))
        
        # Add dynamically detected Ollama models
        try:
            with self._suppress_output():
                from .api.ollama import OllamaClient
                client = await OllamaClient.create()
                local_models = await client.get_available_models()
                
                if local_models:
                    if "ollama" not in providers:
                        providers["ollama"] = []
                    
                    for model in local_models:
                        model_id = model.get("id", "unknown")
                        # Only add if not already in config
                        if model_id not in CONFIG["available_models"]:
                            providers["ollama"].append((model_id, {
                                "provider": "ollama",
                                "display_name": model_id,
                                "max_tokens": 4096
                            }))
        except Exception:
            pass  # Ollama not available
        
        # Display models by provider
        model_list = []
        print("Available Models by Provider:\n")
        
        for provider, models in providers.items():
            if models:  # Only show providers with available models
                print(f"=== {provider.upper()} ===")
                for model_id, model_info in models:
                    marker = "►" if model_id == self.selected_model else " "
                    display_name = model_info.get("display_name", model_id)
                    model_list.append(model_id)
                    print(f"{marker} {len(model_list):2d}. {display_name}")
                print()
        
        if not model_list:
            print("No models available. Please check your API keys or Ollama installation.")
            input("Press Enter to continue...")
            return
        
        print("Enter model number to select (or press Enter to cancel):")
        
        try:
            choice = input("> ").strip()
            if choice and choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(model_list):
                    old_model = self.selected_model
                    self.selected_model = model_list[idx]
                    print(f"Model changed from {old_model} to {self.selected_model}")
                    input("Press Enter to continue...")
        except (ValueError, KeyboardInterrupt):
            pass
    
    def _select_style(self):
        """Style selection submenu"""
        self.clear_screen()
        print("=" * self.width)
        print("RESPONSE STYLE SELECTION".center(self.width))
        print("=" * self.width)
        
        styles = list(CONFIG["user_styles"].keys())
        for i, style in enumerate(styles):
            marker = "►" if style == self.selected_style else " "
            name = CONFIG["user_styles"][style]["name"]
            description = CONFIG["user_styles"][style]["description"]
            print(f"{marker} {i+1:2d}. {name}")
            print(f"     {description}")
            print()
        
        print("Enter style number to select (or press Enter to cancel):")
        
        try:
            choice = input("> ").strip()
            if choice and choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(styles):
                    old_style = self.selected_style
                    self.selected_style = styles[idx]
                    print(f"Style changed from {old_style} to {self.selected_style}")
                    input("Press Enter to continue...")
        except (ValueError, KeyboardInterrupt):
            pass
    
    def _save_settings(self):
        """Save current settings to config file"""
        try:
            CONFIG["default_model"] = self.selected_model
            CONFIG["default_style"] = self.selected_style
            save_config(CONFIG)
            print("Settings saved successfully!")
        except Exception as e:
            print(f"Error saving settings: {e}")
        input("Press Enter to continue...")
    
    async def _show_advanced_settings(self):
        """Show advanced settings configuration panel"""
        while True:
            self.clear_screen()
            print("=" * self.width)
            print("ADVANCED SETTINGS".center(self.width))
            print("=" * self.width)
            
            # Display current advanced settings
            print("Current Advanced Settings:")
            print(f"  Code Highlighting: {'On' if CONFIG.get('highlight_code', True) else 'Off'}")
            print(f"  Dynamic Titles: {'On' if CONFIG.get('generate_dynamic_titles', True) else 'Off'}")
            print(f"  Model Preloading: {'On' if CONFIG.get('preload_models', True) else 'Off'}")
            print(f"  Ollama URL: {CONFIG.get('ollama_base_url', 'http://localhost:11434')}")
            print(f"  Inactive Timeout: {CONFIG.get('ollama_inactive_timeout', 30)} minutes")
            print()
            
            print("What would you like to configure?")
            print("1. Provider Settings")
            print("2. UI Settings")
            print("3. Performance Settings")
            print("4. Ollama Settings")
            print("0. Back to Settings")
            
            try:
                choice = input("\n> ").strip()
                
                if choice == "1":
                    await self._configure_provider_settings()
                elif choice == "2":
                    await self._configure_ui_settings()
                elif choice == "3":
                    await self._configure_performance_settings()
                elif choice == "4":
                    await self._configure_ollama_settings()
                elif choice == "0" or choice == "":
                    break
                    
            except (ValueError, KeyboardInterrupt):
                break
    
    async def _configure_provider_settings(self):
        """Configure provider-specific settings"""
        self.clear_screen()
        print("=" * self.width)
        print("PROVIDER SETTINGS".center(self.width))
        print("=" * self.width)
        
        print("Current Provider Settings:")
        print(f"  OpenAI API Key: {'Set' if CONFIG.get('openai_api_key') else 'Not Set'}")
        print(f"  Anthropic API Key: {'Set' if CONFIG.get('anthropic_api_key') else 'Not Set'}")
        print(f"  Ollama Base URL: {CONFIG.get('ollama_base_url', 'http://localhost:11434')}")
        print()
        
        print("Options:")
        print("1. Set OpenAI API Key")
        print("2. Set Anthropic API Key")
        print("3. Set Ollama Base URL")
        print("4. Clear API Keys")
        print("0. Back")
        
        choice = input("\n> ").strip()
        
        if choice == "1":
            key = input("Enter OpenAI API Key (or press Enter to skip): ").strip()
            if key:
                CONFIG["openai_api_key"] = key
                print("OpenAI API Key updated!")
                
        elif choice == "2":
            key = input("Enter Anthropic API Key (or press Enter to skip): ").strip()
            if key:
                CONFIG["anthropic_api_key"] = key
                print("Anthropic API Key updated!")
                
        elif choice == "3":
            url = input(f"Enter Ollama Base URL (current: {CONFIG.get('ollama_base_url', 'http://localhost:11434')}): ").strip()
            if url:
                CONFIG["ollama_base_url"] = url
                print("Ollama Base URL updated!")
                
        elif choice == "4":
            confirm = input("Clear all API keys? (y/N): ").strip().lower()
            if confirm == 'y':
                CONFIG.pop("openai_api_key", None)
                CONFIG.pop("anthropic_api_key", None)
                print("API keys cleared!")
        
        if choice in ["1", "2", "3", "4"]:
            input("\nPress Enter to continue...")
    
    async def _configure_ui_settings(self):
        """Configure UI and display settings"""
        self.clear_screen()
        print("=" * self.width)
        print("UI SETTINGS".center(self.width))
        print("=" * self.width)
        
        print("Current UI Settings:")
        print(f"  Code Highlighting: {'On' if CONFIG.get('highlight_code', True) else 'Off'}")
        print(f"  Emoji Indicators: {'On' if CONFIG.get('use_emoji_indicators', True) else 'Off'}")
        print(f"  Word Wrapping: {'On' if CONFIG.get('word_wrap', True) else 'Off'}")
        print()
        
        print("Options:")
        print("1. Toggle Code Highlighting")
        print("2. Toggle Emoji Indicators")
        print("3. Toggle Word Wrapping")
        print("0. Back")
        
        choice = input("\n> ").strip()
        
        if choice == "1":
            current = CONFIG.get('highlight_code', True)
            CONFIG['highlight_code'] = not current
            print(f"Code highlighting {'enabled' if not current else 'disabled'}!")
            
        elif choice == "2":
            current = CONFIG.get('use_emoji_indicators', True)
            CONFIG['use_emoji_indicators'] = not current
            print(f"Emoji indicators {'enabled' if not current else 'disabled'}!")
            
        elif choice == "3":
            current = CONFIG.get('word_wrap', True)
            CONFIG['word_wrap'] = not current
            print(f"Word wrapping {'enabled' if not current else 'disabled'}!")
        
        if choice in ["1", "2", "3"]:
            input("\nPress Enter to continue...")
    
    async def _configure_performance_settings(self):
        """Configure performance and optimization settings"""
        self.clear_screen()
        print("=" * self.width)
        print("PERFORMANCE SETTINGS".center(self.width))
        print("=" * self.width)
        
        print("Current Performance Settings:")
        print(f"  Dynamic Title Generation: {'On' if CONFIG.get('generate_dynamic_titles', True) else 'Off'}")
        print(f"  Model Preloading: {'On' if CONFIG.get('preload_models', True) else 'Off'}")
        print(f"  History Limit: {CONFIG.get('history_limit', 100)} conversations")
        print(f"  Message Limit: {CONFIG.get('message_limit', 50)} per conversation")
        print()
        
        print("Options:")
        print("1. Toggle Dynamic Title Generation")
        print("2. Toggle Model Preloading")
        print("3. Set History Limit")
        print("4. Set Message Limit")
        print("0. Back")
        
        choice = input("\n> ").strip()
        
        if choice == "1":
            current = CONFIG.get('generate_dynamic_titles', True)
            CONFIG['generate_dynamic_titles'] = not current
            print(f"Dynamic title generation {'enabled' if not current else 'disabled'}!")
            
        elif choice == "2":
            current = CONFIG.get('preload_models', True)
            CONFIG['preload_models'] = not current
            print(f"Model preloading {'enabled' if not current else 'disabled'}!")
            
        elif choice == "3":
            try:
                limit = int(input(f"Enter history limit (current: {CONFIG.get('history_limit', 100)}): "))
                if limit > 0:
                    CONFIG['history_limit'] = limit
                    print(f"History limit set to {limit}!")
            except ValueError:
                print("Invalid number!")
                
        elif choice == "4":
            try:
                limit = int(input(f"Enter message limit (current: {CONFIG.get('message_limit', 50)}): "))
                if limit > 0:
                    CONFIG['message_limit'] = limit
                    print(f"Message limit set to {limit}!")
            except ValueError:
                print("Invalid number!")
        
        if choice in ["1", "2", "3", "4"]:
            input("\nPress Enter to continue...")
    
    async def _configure_ollama_settings(self):
        """Configure Ollama-specific settings"""
        self.clear_screen()
        print("=" * self.width)
        print("OLLAMA SETTINGS".center(self.width))
        print("=" * self.width)
        
        print("Current Ollama Settings:")
        print(f"  Base URL: {CONFIG.get('ollama_base_url', 'http://localhost:11434')}")
        print(f"  Inactive Timeout: {CONFIG.get('ollama_inactive_timeout', 30)} minutes")
        print(f"  Auto Start: {'On' if CONFIG.get('ollama_auto_start', True) else 'Off'}")
        print(f"  Model Cleanup: {'On' if CONFIG.get('ollama_cleanup_models', True) else 'Off'}")
        print()
        
        print("Options:")
        print("1. Set Base URL")
        print("2. Set Inactive Timeout")
        print("3. Toggle Auto Start")
        print("4. Toggle Model Cleanup")
        print("5. Test Connection")
        print("0. Back")
        
        choice = input("\n> ").strip()
        
        if choice == "1":
            url = input(f"Enter Ollama Base URL (current: {CONFIG.get('ollama_base_url', 'http://localhost:11434')}): ").strip()
            if url:
                CONFIG['ollama_base_url'] = url
                print("Ollama Base URL updated!")
                
        elif choice == "2":
            try:
                timeout = int(input(f"Enter inactive timeout in minutes (current: {CONFIG.get('ollama_inactive_timeout', 30)}): "))
                if timeout > 0:
                    CONFIG['ollama_inactive_timeout'] = timeout
                    print(f"Inactive timeout set to {timeout} minutes!")
            except ValueError:
                print("Invalid number!")
                
        elif choice == "3":
            current = CONFIG.get('ollama_auto_start', True)
            CONFIG['ollama_auto_start'] = not current
            print(f"Ollama auto start {'enabled' if not current else 'disabled'}!")
            
        elif choice == "4":
            current = CONFIG.get('ollama_cleanup_models', True)
            CONFIG['ollama_cleanup_models'] = not current
            print(f"Model cleanup {'enabled' if not current else 'disabled'}!")
            
        elif choice == "5":
            print("Testing Ollama connection...")
            try:
                from .api.ollama import OllamaClient
                client = await OllamaClient.create()
                models = await client.get_available_models()
                print(f"✓ Connection successful! Found {len(models)} local models.")
            except Exception as e:
                print(f"✗ Connection failed: {str(e)}")
        
        if choice in ["1", "2", "3", "4", "5"]:
            input("\nPress Enter to continue...")
    
    async def _detect_ollama_models(self):
        """Detect and add locally available Ollama models"""
        self.clear_screen()
        print("=" * self.width)
        print("OLLAMA MODEL DETECTION".center(self.width))
        print("=" * self.width)
        
        print("Checking for local Ollama models...")
        
        try:
            with self._suppress_output():
                from .api.ollama import OllamaClient
                client = await OllamaClient.create()
                local_models = await client.get_available_models()
            
            if not local_models:
                print("No local Ollama models found.")
                print("Use the model browser ('m' key) to download models.")
            else:
                print(f"Found {len(local_models)} local Ollama models:")
                print()
                
                new_models = 0
                for model in local_models:
                    model_id = model.get("id", "unknown")
                    print(f"  • {model_id}")
                    
                    # Add to config if not already present
                    if model_id not in CONFIG["available_models"]:
                        CONFIG["available_models"][model_id] = {
                            "provider": "ollama",
                            "display_name": model_id,
                            "max_tokens": 4096
                        }
                        new_models += 1
                
                if new_models > 0:
                    save_config(CONFIG)
                    print(f"\nAdded {new_models} new models to configuration.")
                else:
                    print("\nAll models already in configuration.")
                    
        except Exception as e:
            print(f"Error detecting Ollama models: {str(e)}")
            print("Make sure Ollama is running and accessible.")
        
        input("\nPress Enter to continue...")
    
    async def show_model_browser(self):
        """Show Ollama model browser for managing local and available models"""
        while True:
            self.clear_screen()
            print("=" * self.width)
            print("OLLAMA MODEL BROWSER".center(self.width))
            print("=" * self.width)
            
            print("What would you like to do?")
            print("1. View Local Models")
            print("2. Browse Available Models")
            print("3. Search Models")
            print("4. Switch Current Model")
            print("0. Back to Chat")
            
            try:
                choice = input("\n> ").strip()
                
                if choice == "1":
                    await self._list_local_models()
                elif choice == "2":
                    await self._list_available_models()
                elif choice == "3":
                    await self._search_models()
                elif choice == "4":
                    await self._switch_model()
                elif choice == "0" or choice == "":
                    break
                    
            except (ValueError, KeyboardInterrupt):
                break
    
    async def _list_local_models(self):
        """List locally installed Ollama models"""
        self.clear_screen()
        print("=" * self.width)
        print("LOCAL OLLAMA MODELS".center(self.width))
        print("=" * self.width)
        
        try:
            # Get Ollama client with output suppression
            with self._suppress_output():
                from .api.ollama import OllamaClient
                client = await OllamaClient.create()
                
                # Get local models
                local_models = await client.get_available_models()
            
            if not local_models:
                print("No local models found.")
                print("Use option 2 to browse and download models from the registry.")
            else:
                print(f"Found {len(local_models)} local models:\n")
                
                for i, model in enumerate(local_models):
                    model_id = model.get("id", "unknown")
                    marker = "►" if model_id == self.selected_model else " "
                    print(f"{marker} {i+1:2d}. {model_id}")
                
                print("\nOptions:")
                print("d) Delete a model")
                print("i) Show model details")
                print("s) Switch to a model")
                print("Enter) Back to model browser")
                
                sub_choice = input("\n> ").strip().lower()
                
                if sub_choice == "d":
                    await self._delete_model_menu(local_models)
                elif sub_choice == "i":
                    await self._show_model_details_menu(local_models)
                elif sub_choice == "s":
                    await self._switch_model_menu(local_models)
                    
        except Exception as e:
            print(f"Error connecting to Ollama: {str(e)}")
            print("Make sure Ollama is running and accessible.")
            
        input("\nPress Enter to continue...")
    
    async def _list_available_models(self):
        """List available models for download from Ollama registry"""
        self.clear_screen()
        print("=" * self.width)
        print("AVAILABLE OLLAMA MODELS".center(self.width))
        print("=" * self.width)
        
        try:
            # Get Ollama client with output suppression
            with self._suppress_output():
                from .api.ollama import OllamaClient
                client = await OllamaClient.create()
            
            print("Loading available models... (this may take a moment)")
            with self._suppress_output():
                available_models = await client.list_available_models_from_registry("")
            
            if not available_models:
                print("No models found in registry.")
            else:
                # Group by model family for better organization
                families = {}
                for model in available_models:
                    family = model.get("model_family", "Other")
                    if family not in families:
                        families[family] = []
                    families[family].append(model)
                
                # Display by family
                model_index = 1
                model_map = {}
                
                for family, models in sorted(families.items()):
                    print(f"\n{family} Models:")
                    print("-" * 40)
                    
                    for model in models[:5]:  # Show first 5 per family
                        name = model.get("name", "unknown")
                        description = model.get("description", "")
                        size = model.get("parameter_size", "Unknown size")
                        
                        print(f"{model_index:2d}. {name} ({size})")
                        if description:
                            print(f"    {description[:60]}...")
                        
                        model_map[str(model_index)] = model
                        model_index += 1
                    
                    if len(models) > 5:
                        print(f"    ... and {len(models) - 5} more {family} models")
                
                print(f"\nShowing top models by family (total: {len(available_models)})")
                print("\nOptions:")
                print("Enter model number to download")
                print("s) Search for specific models")
                print("Enter) Back to model browser")
                
                choice = input("\n> ").strip()
                
                if choice in model_map:
                    await self._download_model(model_map[choice])
                elif choice.lower() == "s":
                    await self._search_models()
                    
        except Exception as e:
            print(f"Error fetching available models: {str(e)}")
            
        input("\nPress Enter to continue...")
    
    async def _search_models(self):
        """Search for models by name or description"""
        self.clear_screen()
        print("=" * self.width)
        print("SEARCH OLLAMA MODELS".center(self.width))
        print("=" * self.width)
        
        query = input("Enter search term (name, family, or description): ").strip()
        
        if not query:
            return
            
        try:
            # Get Ollama client with output suppression
            with self._suppress_output():
                from .api.ollama import OllamaClient
                client = await OllamaClient.create()
            
            print(f"\nSearching for '{query}'...")
            with self._suppress_output():
                all_models = await client.list_available_models_from_registry("")
            
            # Filter models
            matching_models = []
            query_lower = query.lower()
            
            for model in all_models:
                if (query_lower in model.get("name", "").lower() or
                    query_lower in model.get("description", "").lower() or
                    query_lower in model.get("model_family", "").lower()):
                    matching_models.append(model)
            
            if not matching_models:
                print(f"No models found matching '{query}'")
            else:
                print(f"\nFound {len(matching_models)} models matching '{query}':\n")
                
                model_map = {}
                for i, model in enumerate(matching_models[:20]):  # Show first 20 matches
                    name = model.get("name", "unknown")
                    description = model.get("description", "")
                    size = model.get("parameter_size", "Unknown size")
                    family = model.get("model_family", "Unknown")
                    
                    print(f"{i+1:2d}. {name} ({family}, {size})")
                    if description:
                        print(f"    {description[:70]}...")
                    print()
                    
                    model_map[str(i+1)] = model
                
                if len(matching_models) > 20:
                    print(f"... and {len(matching_models) - 20} more matches")
                
                print("\nEnter model number to download (or press Enter to continue):")
                choice = input("> ").strip()
                
                if choice in model_map:
                    await self._download_model(model_map[choice])
                    
        except Exception as e:
            print(f"Error searching models: {str(e)}")
            
        input("\nPress Enter to continue...")
    
    async def _download_model(self, model_info):
        """Download a model with progress indication"""
        model_name = model_info.get("name", "unknown")
        size_info = model_info.get("parameter_size", "Unknown size")
        
        print(f"\nDownloading {model_name} ({size_info})...")
        print("This may take several minutes depending on model size and connection.")
        print("Press Ctrl+C to cancel.\n")
        
        confirm = input(f"Download {model_name}? (y/N): ").strip().lower()
        if confirm != 'y':
            return
            
        try:
            # Get Ollama client with output suppression
            with self._suppress_output():
                from .api.ollama import OllamaClient
                client = await OllamaClient.create()
            
            # Track download progress
            last_status = ""
            
            async for progress in client.pull_model(model_name):
                status = progress.get("status", "")
                
                if status != last_status:
                    print(f"Status: {status}")
                    last_status = status
                
                # Show progress if available
                if "total" in progress and "completed" in progress:
                    total = progress["total"]
                    completed = progress["completed"]
                    percent = (completed / total) * 100 if total > 0 else 0
                    print(f"Progress: {percent:.1f}% ({completed:,}/{total:,} bytes)")
                
                # Check if download is complete
                if status == "success" or "success" in status.lower():
                    print(f"\n✓ {model_name} downloaded successfully!")
                    break
                    
        except KeyboardInterrupt:
            print("\nDownload cancelled by user.")
        except Exception as e:
            print(f"\nError downloading model: {str(e)}")
    
    async def _delete_model_menu(self, local_models):
        """Show model deletion menu"""
        print("\nSelect model to delete:")
        for i, model in enumerate(local_models):
            print(f"{i+1:2d}. {model.get('id', 'unknown')}")
            
        choice = input("\nEnter model number (or press Enter to cancel): ").strip()
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(local_models):
                model_id = local_models[idx].get("id", "unknown")
                
                print(f"\nWARNING: This will permanently delete {model_id}")
                confirm = input("Type 'DELETE' to confirm: ").strip()
                
                if confirm == "DELETE":
                    try:
                        with self._suppress_output():
                            from .api.ollama import OllamaClient
                            client = await OllamaClient.create()
                            await client.delete_model(model_id)
                        print(f"✓ {model_id} deleted successfully!")
                    except Exception as e:
                        print(f"Error deleting model: {str(e)}")
                else:
                    print("Deletion cancelled.")
    
    async def _show_model_details_menu(self, local_models):
        """Show detailed information about a model"""
        print("\nSelect model for details:")
        for i, model in enumerate(local_models):
            print(f"{i+1:2d}. {model.get('id', 'unknown')}")
            
        choice = input("\nEnter model number (or press Enter to cancel): ").strip()
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(local_models):
                model_id = local_models[idx].get("id", "unknown")
                await self._show_model_details(model_id)
    
    async def _show_model_details(self, model_id):
        """Show detailed information about a specific model"""
        try:
            from .api.ollama import OllamaClient
            client = await OllamaClient.create()
            details = await client.get_model_details(model_id)
            
            self.clear_screen()
            print("=" * self.width)
            print(f"MODEL DETAILS: {model_id}".center(self.width))
            print("=" * self.width)
            
            if "error" in details:
                print(f"Error getting details: {details['error']}")
            else:
                print(f"Name: {model_id}")
                
                if details.get("size"):
                    size_gb = details["size"] / (1024**3)
                    print(f"Size: {size_gb:.1f} GB")
                
                if details.get("modified_at"):
                    print(f"Modified: {details['modified_at']}")
                
                if details.get("parameters"):
                    print(f"\nParameters: {details['parameters']}")
                
                if details.get("modelfile"):
                    print(f"\nModelfile (first 500 chars):")
                    print("-" * 40)
                    print(details["modelfile"][:500])
                    if len(details["modelfile"]) > 500:
                        print("...")
                
        except Exception as e:
            print(f"Error getting model details: {str(e)}")
            
        input("\nPress Enter to continue...")
    
    async def _switch_model_menu(self, local_models):
        """Switch to a different local model"""
        print("\nSelect model to switch to:")
        for i, model in enumerate(local_models):
            model_id = model.get("id", "unknown")
            marker = "►" if model_id == self.selected_model else " "
            print(f"{marker} {i+1:2d}. {model_id}")
            
        choice = input("\nEnter model number (or press Enter to cancel): ").strip()
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(local_models):
                old_model = self.selected_model
                self.selected_model = local_models[idx].get("id", "unknown")
                print(f"\n✓ Switched from {old_model} to {self.selected_model}")
    
    async def _switch_model(self):
        """Switch current model (combines local and available models)"""
        try:
            from .api.ollama import OllamaClient
            client = await OllamaClient.create()
            local_models = await client.get_available_models()
            await self._switch_model_menu(local_models)
        except Exception as e:
            print(f"Error getting local models: {str(e)}")
            
        input("\nPress Enter to continue...")
    
    async def run(self):
        """Main application loop"""
        # Create initial conversation
        await self.create_new_conversation()
        
        # Welcome message
        self.draw_screen("", "Type your message (or 'q' to quit)")
        
        while self.running:
            try:
                user_input = self.get_input("Type your message")
                
                if not user_input:
                    continue
                
                # Handle special command tokens from enhanced input
                if user_input == "##QUIT##":
                    self.running = False
                    break
                elif user_input == "##NEW##":
                    await self.create_new_conversation()
                    continue
                elif user_input == "##HISTORY##":
                    self.show_history()
                    continue
                elif user_input == "##SETTINGS##":
                    await self.show_settings()
                    continue
                elif user_input == "##MODELS##":
                    await self.show_model_browser()
                    continue
                
                # Handle legacy single-letter commands for backward compatibility
                if user_input.lower() == 'q':
                    self.running = False
                    break
                elif user_input.lower() == 'n':
                    await self.create_new_conversation()
                    continue
                elif user_input.lower() == 'h':
                    self.show_history()
                    continue
                elif user_input.lower() == 's':
                    await self.show_settings()
                    continue
                elif user_input.lower() == 'm':
                    await self.show_model_browser()
                    continue
                
                # Generate response
                await self.generate_response(user_input)
                
            except KeyboardInterrupt:
                if self.generating:
                    self.generating = False
                    print("\nGeneration cancelled.")
                    time.sleep(1)
                else:
                    self.running = False
                    break
            except Exception as e:
                print(f"\nError: {e}")
                input("Press Enter to continue...")

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(_signum, _frame):
        print("\n\nShutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main entry point for console version"""
    parser = argparse.ArgumentParser(description="Chat Console - Pure Terminal Version")
    parser.add_argument("--model", help="Initial model to use")
    parser.add_argument("--style", help="Response style")
    parser.add_argument("message", nargs="?", help="Initial message to send")
    
    args = parser.parse_args()
    
    # Setup signal handling
    setup_signal_handlers()
    
    # Create console UI
    console = ConsoleUI()
    
    if args.model:
        console.selected_model = resolve_model_id(args.model)
    if args.style:
        console.selected_style = args.style
    
    # Run the application
    await console.run()
    
    print("\nGoodbye!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)