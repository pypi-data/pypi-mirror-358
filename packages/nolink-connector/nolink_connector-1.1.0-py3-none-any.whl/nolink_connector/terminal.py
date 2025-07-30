"""
Terminal Manager Module
Handles terminal sessions and command execution across platforms
"""

import os
import sys
import asyncio
import uuid
import time
import platform
import subprocess
from typing import Dict, Optional, List, Any
from pathlib import Path
from colorama import Fore, Style

# Platform-specific imports
if platform.system() == 'Windows':
    try:
        import winpty
        HAS_WINPTY = True
    except ImportError:
        HAS_WINPTY = False
else:
    try:
        import pexpect
        HAS_PEXPECT = True
    except ImportError:
        HAS_PEXPECT = False


class TerminalSession:
    """Represents a single terminal session"""
    
    def __init__(self, session_id: str, working_directory: str):
        self.session_id = session_id
        self.working_directory = working_directory
        self.created_at = time.time()
        self.last_activity = time.time()
        self.command_history = []
        self.is_active = True
        
        # Platform-specific terminal process
        self.process = None
        self.shell_type = self._detect_shell()
    
    def _detect_shell(self) -> str:
        """Detect the appropriate shell for the platform"""
        if platform.system() == 'Windows':
            return 'cmd' if not HAS_WINPTY else 'powershell'
        else:
            return os.environ.get('SHELL', '/bin/bash')
    
    async def execute_command(self, command: str, options: Dict = None) -> Dict:
        """Execute a command in this terminal session"""
        options = options or {}
        timeout = options.get('timeout', 30)
        
        start_time = time.time()
        self.last_activity = start_time
        
        try:
            # Add command to history
            self.command_history.append({
                'command': command,
                'timestamp': start_time,
                'status': 'executing'
            })
            
            # Execute command based on platform
            if platform.system() == 'Windows':
                result = await self._execute_windows(command, timeout)
            else:
                result = await self._execute_unix(command, timeout)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Update command history
            self.command_history[-1].update({
                'status': 'completed' if result['success'] else 'failed',
                'execution_time': execution_time,
                'exit_code': result.get('exit_code', 0)
            })
            
            result['execution_time'] = execution_time
            result['working_directory'] = self.working_directory
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            # Update command history
            if self.command_history:
                self.command_history[-1].update({
                    'status': 'error',
                    'execution_time': execution_time,
                    'error': str(e)
                })
            
            return {
                'success': False,
                'output': f'Command execution failed: {str(e)}',
                'exit_code': 1,
                'execution_time': execution_time,
                'working_directory': self.working_directory
            }
    
    async def _execute_windows(self, command: str, timeout: int) -> Dict:
        """Execute command on Windows"""
        try:
            # Use subprocess for Windows command execution
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=self.working_directory,
                shell=True
            )
            
            try:
                stdout, _ = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                
                output = stdout.decode('utf-8', errors='replace') if stdout else ''
                exit_code = process.returncode
                
                # Handle directory change commands
                if command.strip().lower().startswith('cd '):
                    await self._handle_cd_command(command)
                
                return {
                    'success': exit_code == 0,
                    'output': output.strip(),
                    'exit_code': exit_code
                }
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    'success': False,
                    'output': f'Command timed out after {timeout} seconds',
                    'exit_code': 124
                }
                
        except Exception as e:
            return {
                'success': False,
                'output': f'Windows execution error: {str(e)}',
                'exit_code': 1
            }
    
    async def _execute_unix(self, command: str, timeout: int) -> Dict:
        """Execute command on Unix-like systems"""
        try:
            # Use subprocess for Unix command execution
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=self.working_directory,
                shell=True
            )
            
            try:
                stdout, _ = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                
                output = stdout.decode('utf-8', errors='replace') if stdout else ''
                exit_code = process.returncode
                
                # Handle directory change commands
                if command.strip().startswith('cd '):
                    await self._handle_cd_command(command)
                
                return {
                    'success': exit_code == 0,
                    'output': output.strip(),
                    'exit_code': exit_code
                }
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    'success': False,
                    'output': f'Command timed out after {timeout} seconds',
                    'exit_code': 124
                }
                
        except Exception as e:
            return {
                'success': False,
                'output': f'Unix execution error: {str(e)}',
                'exit_code': 1
            }
    
    async def _handle_cd_command(self, command: str):
        """Handle directory change commands"""
        try:
            # Extract the target directory from cd command
            parts = command.strip().split(None, 1)
            if len(parts) > 1:
                target_dir = parts[1].strip().strip('"\'')
                
                # Resolve the target directory
                if not os.path.isabs(target_dir):
                    target_dir = os.path.join(self.working_directory, target_dir)
                
                target_dir = os.path.normpath(target_dir)
                
                # Verify directory exists and update working directory
                if os.path.exists(target_dir) and os.path.isdir(target_dir):
                    self.working_directory = target_dir
            else:
                # cd without arguments goes to home directory
                self.working_directory = os.path.expanduser('~')
                
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Could not change directory: {e}")
    
    async def change_directory(self, path: str) -> Dict:
        """Change the working directory for this session"""
        try:
            # Resolve the target directory
            if not os.path.isabs(path):
                target_dir = os.path.join(self.working_directory, path)
            else:
                target_dir = path
            
            target_dir = os.path.normpath(target_dir)
            
            # Verify directory exists
            if not os.path.exists(target_dir):
                return {
                    'success': False,
                    'path': self.working_directory,
                    'message': f'Directory does not exist: {path}'
                }
            
            if not os.path.isdir(target_dir):
                return {
                    'success': False,
                    'path': self.working_directory,
                    'message': f'Path is not a directory: {path}'
                }
            
            # Update working directory
            self.working_directory = target_dir
            self.last_activity = time.time()
            
            return {
                'success': True,
                'path': self.working_directory,
                'message': f'Changed directory to {self.working_directory}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'path': self.working_directory,
                'message': f'Failed to change directory: {str(e)}'
            }
    
    def get_status(self) -> Dict:
        """Get the current status of this terminal session"""
        return {
            'session_id': self.session_id,
            'working_directory': self.working_directory,
            'shell_type': self.shell_type,
            'created_at': self.created_at,
            'last_activity': self.last_activity,
            'is_active': self.is_active,
            'command_count': len(self.command_history),
            'uptime': int(time.time() - self.created_at)
        }
    
    async def cleanup(self):
        """Clean up the terminal session"""
        self.is_active = False
        if self.process:
            try:
                self.process.terminate()
                await asyncio.sleep(0.1)
                if self.process.poll() is None:
                    self.process.kill()
            except:
                pass


class TerminalManager:
    """Manages multiple terminal sessions"""
    
    def __init__(self, workdir: str = None):
        self.base_workdir = workdir or os.getcwd()
        self.sessions: Dict[str, TerminalSession] = {}
        self.max_sessions = 10
        self.session_timeout = 3600  # 1 hour
    
    async def create_session(self, session_id: str = None, working_directory: str = None) -> TerminalSession:
        """Create a new terminal session"""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        working_directory = working_directory or self.base_workdir
        
        # Clean up expired sessions
        await self._cleanup_expired_sessions()
        
        # Check session limit
        if len(self.sessions) >= self.max_sessions:
            # Remove oldest session
            oldest_id = min(self.sessions.keys(), 
                          key=lambda k: self.sessions[k].last_activity)
            await self.close_session(oldest_id)
        
        # Create new session
        session = TerminalSession(session_id, working_directory)
        self.sessions[session_id] = session
        
        print(f"{Fore.GREEN}✅ Created terminal session: {session_id}")
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[TerminalSession]:
        """Get an existing terminal session"""
        return self.sessions.get(session_id)
    
    async def execute_command(self, session_id: str, command: str, options: Dict = None) -> Dict:
        """Execute a command in the specified session"""
        session = self.sessions.get(session_id)
        
        if not session:
            return {
                'success': False,
                'output': f'Terminal session not found: {session_id}',
                'exit_code': 1
            }
        
        if not session.is_active:
            return {
                'success': False,
                'output': f'Terminal session is not active: {session_id}',
                'exit_code': 1
            }
        
        return await session.execute_command(command, options)
    
    async def change_directory(self, session_id: str, path: str) -> Dict:
        """Change directory for the specified session"""
        session = self.sessions.get(session_id)
        
        if not session:
            return {
                'success': False,
                'path': self.base_workdir,
                'message': f'Terminal session not found: {session_id}'
            }
        
        return await session.change_directory(path)
    
    async def close_session(self, session_id: str) -> bool:
        """Close and clean up a terminal session"""
        session = self.sessions.get(session_id)
        
        if session:
            await session.cleanup()
            del self.sessions[session_id]
            print(f"{Fore.YELLOW}🗑️  Closed terminal session: {session_id}")
            return True
        
        return False
    
    async def list_sessions(self) -> List[Dict]:
        """List all active terminal sessions"""
        await self._cleanup_expired_sessions()
        
        return [session.get_status() for session in self.sessions.values()]
    
    async def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Get status of a specific session"""
        session = self.sessions.get(session_id)
        return session.get_status() if session else None
    
    async def _cleanup_expired_sessions(self):
        """Clean up expired terminal sessions"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if (current_time - session.last_activity) > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self.close_session(session_id)
            print(f"{Fore.YELLOW}⏰ Expired terminal session: {session_id}")
    
    async def cleanup(self):
        """Clean up all terminal sessions"""
        session_ids = list(self.sessions.keys())
        
        for session_id in session_ids:
            await self.close_session(session_id)
        
        print(f"{Fore.GREEN}✅ All terminal sessions cleaned up")
    
    def get_manager_status(self) -> Dict:
        """Get the overall status of the terminal manager"""
        return {
            'active_sessions': len(self.sessions),
            'max_sessions': self.max_sessions,
            'session_timeout': self.session_timeout,
            'base_workdir': self.base_workdir,
            'platform': platform.system(),
            'has_pexpect': HAS_PEXPECT if platform.system() != 'Windows' else None,
            'has_winpty': HAS_WINPTY if platform.system() == 'Windows' else None
        }
