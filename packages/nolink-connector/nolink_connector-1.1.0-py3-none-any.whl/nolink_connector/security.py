"""
Security Manager Module
Handles command filtering, path validation, and security policies
"""

import os
import re
import stat
from pathlib import Path
from typing import List, Set, Optional
from colorama import Fore, Style


class SecurityManager:
    """Security policies and validation for terminal commands"""
    
    def __init__(self):
        # Dangerous commands that should never be allowed
        self.blocked_commands = {
            # System administration
            'sudo', 'su', 'passwd', 'useradd', 'userdel', 'usermod',
            'groupadd', 'groupdel', 'groupmod', 'chown', 'chgrp',
            
            # System services
            'systemctl', 'service', 'systemd', 'init', 'launchctl',
            'sc', 'net', 'runas',
            
            # Network/Firewall
            'iptables', 'ufw', 'firewall-cmd', 'netsh', 'route',
            'ifconfig', 'ip', 'netstat', 'ss',
            
            # Disk operations
            'fdisk', 'parted', 'mkfs', 'mount', 'umount', 'fsck',
            'dd', 'losetup', 'cryptsetup',
            
            # Package management (system-wide)
            'apt', 'apt-get', 'yum', 'dnf', 'pacman', 'zypper',
            'brew', 'port', 'pkg', 'choco',
            
            # System modification
            'crontab', 'at', 'batch', 'schtasks', 'launchd',
            'dmesg', 'modprobe', 'insmod', 'rmmod',
            
            # Process control (dangerous)
            'kill', 'killall', 'pkill', 'pgrep', 'nohup',
            'disown', 'jobs', 'bg', 'fg',
            
            # File operations (dangerous patterns)
            'shred', 'wipe', 'srm'
        }
        
        # Dangerous command patterns
        self.blocked_patterns = [
            r'rm\s+-rf\s*/',  # rm -rf /
            r'dd\s+if=.*of=/dev/',  # Direct disk writing
            r'>\s*/dev/sd[a-z]',  # Writing to disk devices
            r'mkfs\.',  # Creating filesystems
            r'format\s+[a-z]:',  # Windows format command
            r'del\s+/s\s+/q\s+[a-z]:',  # Windows delete
        ]
        
        # Commands that are allowed but need monitoring
        self.monitored_commands = {
            'rm', 'rmdir', 'del', 'rd',  # File deletion
            'mv', 'move', 'rename',      # File moving
            'cp', 'copy', 'xcopy',       # File copying
            'chmod', 'attrib', 'icacls', # Permission changes
            'curl', 'wget', 'powershell', 'bash', 'sh'  # Download/execution
        }
        
        # Safe commands that are always allowed
        self.safe_commands = {
            # File viewing/listing
            'ls', 'dir', 'cat', 'type', 'more', 'less', 'head', 'tail',
            'find', 'locate', 'which', 'where', 'whereis',
            
            # Text processing
            'grep', 'awk', 'sed', 'sort', 'uniq', 'wc', 'cut',
            'tr', 'tee', 'comm', 'diff', 'cmp',
            
            # Directory operations
            'pwd', 'cd', 'mkdir', 'md', 'pushd', 'popd', 'dirs',
            
            # File operations (safe)
            'touch', 'stat', 'file', 'du', 'df', 'tree',
            
            # Archive operations
            'tar', 'zip', 'unzip', 'gzip', 'gunzip', '7z',
            
            # Development tools
            'node', 'npm', 'yarn', 'python', 'python3', 'pip', 'pip3',
            'git', 'svn', 'hg', 'make', 'cmake', 'gcc', 'g++',
            'javac', 'java', 'mvn', 'gradle', 'cargo', 'go',
            
            # Text editors (command line)
            'nano', 'vim', 'vi', 'emacs', 'micro',
            
            # System info (read-only)
            'whoami', 'id', 'groups', 'uptime', 'date', 'cal',
            'uname', 'hostname', 'env', 'printenv', 'set',
            
            # Process viewing (read-only)
            'ps', 'top', 'htop', 'tasklist', 'pstree',
            
            # Utilities
            'echo', 'printf', 'basename', 'dirname', 'realpath',
            'sleep', 'timeout', 'time', 'history', 'clear', 'cls'
        }
        
        # Blocked file extensions for execution
        self.blocked_extensions = {
            '.exe', '.bat', '.cmd', '.com', '.scr', '.msi',
            '.vbs', '.js', '.jar', '.app', '.dmg', '.pkg'
        }
        
        # Maximum command length
        self.max_command_length = 1000
        
        # Maximum output size (1MB)
        self.max_output_size = 1024 * 1024
        
        # Command timeout (30 seconds)
        self.command_timeout = 30
    
    def is_command_allowed(self, command: str) -> bool:
        """
        Check if a command is allowed to execute
        
        Args:
            command: Command string to validate
            
        Returns:
            True if command is allowed, False otherwise
        """
        if not command or len(command.strip()) == 0:
            return False
        
        # Check command length
        if len(command) > self.max_command_length:
            print(f"{Fore.RED}❌ Command too long: {len(command)} characters")
            return False
        
        # Parse the main command (first word)
        main_command = self._extract_main_command(command)
        
        # Check against blocked commands
        if main_command.lower() in self.blocked_commands:
            print(f"{Fore.RED}❌ Blocked command: {main_command}")
            return False
        
        # Check against dangerous patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                print(f"{Fore.RED}❌ Dangerous pattern detected: {pattern}")
                return False
        
        # Check for suspicious file operations
        if not self._validate_file_operations(command):
            return False
        
        # Log monitored commands
        if main_command.lower() in self.monitored_commands:
            print(f"{Fore.YELLOW}⚠️  Monitored command: {main_command}")
        
        return True
    
    def is_path_allowed(self, path: str, base_directory: str) -> bool:
        """
        Check if a file path is allowed for access
        
        Args:
            path: Path to validate
            base_directory: Base working directory
            
        Returns:
            True if path is allowed, False otherwise
        """
        try:
            # Convert to absolute paths for comparison
            base_path = Path(base_directory).resolve()
            target_path = Path(path)
            
            # If path is relative, resolve it relative to base directory
            if not target_path.is_absolute():
                target_path = (base_path / target_path).resolve()
            else:
                target_path = target_path.resolve()
            
            # Check if target path is within base directory
            try:
                target_path.relative_to(base_path)
                return True
            except ValueError:
                # Path is outside base directory
                print(f"{Fore.RED}❌ Path outside working directory: {target_path}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Path validation error: {e}")
            return False
    
    def validate_working_directory(self, directory: str) -> bool:
        """
        Validate that a directory is safe to use as working directory
        
        Args:
            directory: Directory path to validate
            
        Returns:
            True if directory is safe, False otherwise
        """
        try:
            dir_path = Path(directory).resolve()
            
            # Check if directory exists
            if not dir_path.exists():
                print(f"{Fore.RED}❌ Directory does not exist: {directory}")
                return False
            
            if not dir_path.is_dir():
                print(f"{Fore.RED}❌ Path is not a directory: {directory}")
                return False
            
            # Check for dangerous system directories
            dangerous_dirs = {
                '/', '/root', '/etc', '/var', '/sys', '/proc', '/dev',
                '/usr/bin', '/usr/sbin', '/sbin', '/bin',
                'C:\\', 'C:\\Windows', 'C:\\Program Files', 'C:\\System32'
            }
            
            # Convert to string for comparison
            dir_str = str(dir_path)
            
            for dangerous_dir in dangerous_dirs:
                if dir_str.startswith(dangerous_dir) and len(dir_str) <= len(dangerous_dir) + 1:
                    print(f"{Fore.RED}❌ Cannot use system directory: {directory}")
                    return False
            
            # Check directory permissions
            if not os.access(dir_path, os.R_OK | os.W_OK):
                print(f"{Fore.RED}❌ Insufficient permissions for directory: {directory}")
                return False
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Directory validation error: {e}")
            return False
    
    def _extract_main_command(self, command: str) -> str:
        """Extract the main command from a command string"""
        # Handle command substitution and pipes
        command = command.strip()
        
        # Split on pipes and take the first part
        if '|' in command:
            command = command.split('|')[0].strip()
        
        # Split on && and take the first part
        if '&&' in command:
            command = command.split('&&')[0].strip()
        
        # Split on ; and take the first part
        if ';' in command:
            command = command.split(';')[0].strip()
        
        # Get the first word (actual command)
        parts = command.split()
        if not parts:
            return ""
        
        main_cmd = parts[0]
        
        # Handle path prefixes (./command, /path/to/command)
        if '/' in main_cmd or '\\' in main_cmd:
            main_cmd = os.path.basename(main_cmd)
        
        # Remove file extensions
        if '.' in main_cmd:
            main_cmd = main_cmd.split('.')[0]
        
        return main_cmd
    
    def _validate_file_operations(self, command: str) -> bool:
        """Validate file operations in the command"""
        
        # Check for attempts to access blocked file extensions
        for ext in self.blocked_extensions:
            if ext in command.lower():
                # Check if it's actually trying to execute the file
                if re.search(rf'\.{ext[1:]}\s*$', command, re.IGNORECASE):
                    print(f"{Fore.RED}❌ Blocked file extension: {ext}")
                    return False
        
        # Check for dangerous redirection
        dangerous_redirects = [
            r'>\s*/dev/',  # Writing to device files
            r'>\s*/etc/',  # Writing to system config
            r'>\s*/var/',  # Writing to system variables
            r'>\s*/usr/',  # Writing to system files
            r'>\s*[a-z]:\\windows',  # Writing to Windows system
            r'>\s*[a-z]:\\system32',  # Writing to System32
        ]
        
        for pattern in dangerous_redirects:
            if re.search(pattern, command, re.IGNORECASE):
                print(f"{Fore.RED}❌ Dangerous file redirection detected")
                return False
        
        return True
    
    def get_security_summary(self) -> dict:
        """Get a summary of security policies"""
        return {
            'blocked_commands': len(self.blocked_commands),
            'blocked_patterns': len(self.blocked_patterns),
            'monitored_commands': len(self.monitored_commands),
            'safe_commands': len(self.safe_commands),
            'max_command_length': self.max_command_length,
            'max_output_size': self.max_output_size,
            'command_timeout': self.command_timeout,
            'security_level': 'folder-scoped'
        }
