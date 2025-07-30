"""
Socket.IO Terminal Server
Provides real-time terminal access via Socket.IO
"""

import os
import sys
import asyncio
import json
import uuid
import time
import socket
import platform
from typing import Dict, Optional, List
from pathlib import Path

import socketio
import psutil
from aiohttp import web, WSMsgType
from colorama import Fore, Style

# Import platform-specific terminal modules
if platform.system() == 'Windows':
    try:
        import winpty
    except ImportError:
        winpty = None
else:
    try:
        import pexpect
    except ImportError:
        pexpect = None

from .security import SecurityManager
from .terminal import TerminalManager


class SocketIOTerminalServer:
    """Socket.IO server for real-time terminal communication"""
    
    def __init__(self, api_key: str, port: int = None, workdir: str = None, debug: bool = False):
        self.api_key = api_key
        self.port = port or self._find_free_port()
        self.workdir = workdir or os.getcwd()
        self.debug = debug
        
        # Initialize components
        self.security = SecurityManager()
        self.terminal_manager = TerminalManager(workdir=self.workdir)
        
        # Socket.IO setup
        self.sio = socketio.AsyncServer(
            cors_allowed_origins="*",
            logger=debug,
            engineio_logger=debug
        )
        self.app = web.Application()
        self.sio.attach(self.app)
        
        # Connection tracking
        self.active_connections = {}
        self.connection_token = self._generate_connection_token()
        
        # Setup event handlers
        self._setup_socketio_events()
        self._setup_http_routes()
        
        print(f"{Fore.BLUE}🔧 Socket.IO Terminal Server initialized")
        print(f"{Fore.BLUE}   Port: {self.port}")
        print(f"{Fore.BLUE}   Working Directory: {self.workdir}")
        print(f"{Fore.BLUE}   Connection Token: {self.connection_token}")
    
    def _find_free_port(self, start_port: int = 8000) -> int:
        """Find an available port starting from start_port"""
        for port in range(start_port, start_port + 1000):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        raise RuntimeError("No free ports available")
    
    def _generate_connection_token(self) -> str:
        """Generate unique connection token"""
        user_id = self.api_key.split('_')[1] if '_' in self.api_key else 'user'
        hostname = platform.node().lower()[:8]
        return f"TBC-{user_id}-port{self.port}-{hostname}"
    
    def _setup_socketio_events(self):
        """Setup Socket.IO event handlers"""
        
        @self.sio.event
        async def connect(sid, environ):
            """Handle client connection"""
            client_ip = environ.get('REMOTE_ADDR', 'unknown')
            print(f"{Fore.GREEN}🔗 Client connected: {sid} from {client_ip}")
            
            # Send welcome message
            await self.sio.emit('welcome', {
                'message': 'Connected to NoLink Terminal Bridge',
                'server_version': '1.0.0',
                'token': self.connection_token,
                'working_directory': self.workdir,
                'timestamp': int(time.time())
            }, room=sid)
        
        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection"""
            print(f"{Fore.YELLOW}🔌 Client disconnected: {sid}")
            
            # Clean up terminal session if exists
            if sid in self.active_connections:
                terminal_session = self.active_connections[sid]
                await self.terminal_manager.close_session(terminal_session['session_id'])
                del self.active_connections[sid]
        
        @self.sio.event
        async def authenticate(sid, data):
            """Authenticate client with token"""
            try:
                token = data.get('token')
                
                if token != self.connection_token:
                    await self.sio.emit('error', {
                        'message': 'Invalid connection token',
                        'code': 'INVALID_TOKEN'
                    }, room=sid)
                    await self.sio.disconnect(sid)
                    return
                
                # Create terminal session
                session_id = str(uuid.uuid4())
                terminal_session = await self.terminal_manager.create_session(session_id, self.workdir)
                
                self.active_connections[sid] = {
                    'session_id': session_id,
                    'authenticated': True,
                    'created_at': time.time(),
                    'terminal_session': terminal_session
                }
                
                await self.sio.emit('authenticated', {
                    'session_id': session_id,
                    'working_directory': self.workdir,
                    'message': 'Authentication successful'
                }, room=sid)
                
                print(f"{Fore.GREEN}✅ Client authenticated: {sid}")
                
            except Exception as e:
                await self.sio.emit('error', {
                    'message': f'Authentication failed: {str(e)}',
                    'code': 'AUTH_FAILED'
                }, room=sid)
        
        @self.sio.event
        async def execute_command(sid, data):
            """Execute terminal command"""
            try:
                if sid not in self.active_connections:
                    await self.sio.emit('error', {
                        'message': 'Not authenticated',
                        'code': 'NOT_AUTHENTICATED'
                    }, room=sid)
                    return
                
                command = data.get('command', '').strip()
                options = data.get('options', {})
                request_id = data.get('request_id', str(uuid.uuid4()))
                
                if not command:
                    await self.sio.emit('command_result', {
                        'request_id': request_id,
                        'success': False,
                        'error': 'Command cannot be empty'
                    }, room=sid)
                    return
                
                # Security validation
                if not self.security.is_command_allowed(command):
                    await self.sio.emit('command_result', {
                        'request_id': request_id,
                        'success': False,
                        'error': f'Command blocked for security: {command}',
                        'code': 'COMMAND_BLOCKED'
                    }, room=sid)
                    return
                
                session = self.active_connections[sid]
                session_id = session['session_id']
                
                print(f"{Fore.BLUE}💻 Executing command: {command}")
                
                # Execute command
                result = await self.terminal_manager.execute_command(
                    session_id, command, options
                )
                
                await self.sio.emit('command_result', {
                    'request_id': request_id,
                    'success': result['success'],
                    'output': result['output'],
                    'exit_code': result.get('exit_code', 0),
                    'execution_time': result.get('execution_time', 0),
                    'working_directory': result.get('working_directory', self.workdir),
                    'timestamp': int(time.time())
                }, room=sid)
                
            except Exception as e:
                await self.sio.emit('command_result', {
                    'request_id': data.get('request_id', ''),
                    'success': False,
                    'error': f'Execution failed: {str(e)}',
                    'code': 'EXECUTION_FAILED'
                }, room=sid)
                
                if self.debug:
                    import traceback
                    traceback.print_exc()
        
        @self.sio.event
        async def change_directory(sid, data):
            """Change working directory"""
            try:
                if sid not in self.active_connections:
                    await self.sio.emit('error', {
                        'message': 'Not authenticated',
                        'code': 'NOT_AUTHENTICATED'
                    }, room=sid)
                    return
                
                path = data.get('path', '').strip()
                if not path:
                    await self.sio.emit('error', {
                        'message': 'Path cannot be empty'
                    }, room=sid)
                    return
                
                # Security validation - ensure path is within working directory
                if not self.security.is_path_allowed(path, self.workdir):
                    await self.sio.emit('error', {
                        'message': f'Path access denied: {path}',
                        'code': 'PATH_DENIED'
                    }, room=sid)
                    return
                
                session = self.active_connections[sid]
                session_id = session['session_id']
                
                result = await self.terminal_manager.change_directory(session_id, path)
                
                await self.sio.emit('directory_changed', {
                    'success': result['success'],
                    'path': result['path'],
                    'message': result.get('message', '')
                }, room=sid)
                
            except Exception as e:
                await self.sio.emit('error', {
                    'message': f'Directory change failed: {str(e)}',
                    'code': 'CD_FAILED'
                }, room=sid)
        
        @self.sio.event
        async def read_file(sid, data):
            """Read file content"""
            try:
                if sid not in self.active_connections:
                    await self.sio.emit('error', {
                        'message': 'Not authenticated',
                        'code': 'NOT_AUTHENTICATED'
                    }, room=sid)
                    return
                
                file_path = data.get('path', '').strip()
                if not file_path:
                    await self.sio.emit('error', {
                        'message': 'File path cannot be empty'
                    }, room=sid)
                    return
                
                # Security validation
                if not self.security.is_path_allowed(file_path, self.workdir):
                    await self.sio.emit('error', {
                        'message': f'File access denied: {file_path}',
                        'code': 'FILE_ACCESS_DENIED'
                    }, room=sid)
                    return
                
                # Read file content
                try:
                    full_path = Path(self.workdir) / file_path
                    content = full_path.read_text(encoding='utf-8', errors='replace')
                    
                    await self.sio.emit('file_content', {
                        'path': file_path,
                        'content': content,
                        'size': len(content)
                    }, room=sid)
                    
                except FileNotFoundError:
                    await self.sio.emit('error', {
                        'message': f'File not found: {file_path}',
                        'code': 'FILE_NOT_FOUND'
                    }, room=sid)
                except PermissionError:
                    await self.sio.emit('error', {
                        'message': f'Permission denied: {file_path}',
                        'code': 'PERMISSION_DENIED'
                    }, room=sid)
                
            except Exception as e:
                await self.sio.emit('error', {
                    'message': f'File read failed: {str(e)}',
                    'code': 'FILE_READ_FAILED'
                }, room=sid)
        
        @self.sio.event
        async def list_directory(sid, data):
            """List directory contents"""
            try:
                if sid not in self.active_connections:
                    await self.sio.emit('error', {
                        'message': 'Not authenticated',
                        'code': 'NOT_AUTHENTICATED'
                    }, room=sid)
                    return
                
                dir_path = data.get('path', '.').strip()
                
                # Security validation
                if not self.security.is_path_allowed(dir_path, self.workdir):
                    await self.sio.emit('error', {
                        'message': f'Directory access denied: {dir_path}',
                        'code': 'DIR_ACCESS_DENIED'
                    }, room=sid)
                    return
                
                session = self.active_connections[sid]
                session_id = session['session_id']
                
                # Use ls command for consistent output
                result = await self.terminal_manager.execute_command(
                    session_id, f'ls -la "{dir_path}"', {}
                )
                
                await self.sio.emit('directory_listing', {
                    'path': dir_path,
                    'success': result['success'],
                    'content': result['output']
                }, room=sid)
                
            except Exception as e:
                await self.sio.emit('error', {
                    'message': f'Directory listing failed: {str(e)}',
                    'code': 'DIR_LIST_FAILED'
                }, room=sid)
        
        @self.sio.event
        async def get_system_info(sid, data):
            """Get system information"""
            try:
                if sid not in self.active_connections:
                    await self.sio.emit('error', {
                        'message': 'Not authenticated',
                        'code': 'NOT_AUTHENTICATED'
                    }, room=sid)
                    return
                
                # Gather system information
                system_info = {
                    'platform': platform.system(),
                    'platform_version': platform.version(),
                    'architecture': platform.architecture()[0],
                    'processor': platform.processor(),
                    'hostname': platform.node(),
                    'python_version': platform.python_version(),
                    'working_directory': self.workdir,
                    'cpu_count': psutil.cpu_count(),
                    'memory_total': psutil.virtual_memory().total,
                    'memory_available': psutil.virtual_memory().available,
                    'disk_usage': psutil.disk_usage('.').total,
                    'timestamp': int(time.time())
                }
                
                await self.sio.emit('system_info', system_info, room=sid)
                
            except Exception as e:
                await self.sio.emit('error', {
                    'message': f'System info failed: {str(e)}',
                    'code': 'SYSTEM_INFO_FAILED'
                }, room=sid)
    
    def _setup_http_routes(self):
        """Setup HTTP routes for health checks and info"""
        
        async def health_check(request):
            """Health check endpoint"""
            return web.json_response({
                'status': 'running',
                'version': '1.0.0',
                'connection_token': self.connection_token,
                'active_connections': len(self.active_connections),
                'working_directory': self.workdir,
                'timestamp': int(time.time())
            })
        
        async def server_info(request):
            """Server information endpoint"""
            return web.json_response({
                'server': 'NoLink Terminal Bridge',
                'version': '1.0.0',
                'socketio_version': socketio.__version__,
                'connection_token': self.connection_token,
                'working_directory': self.workdir,
                'platform': platform.system(),
                'python_version': platform.python_version(),
                'active_connections': len(self.active_connections),
                'uptime': int(time.time() - getattr(self, '_start_time', time.time())),
                'security_enabled': True
            })
        
        # Add routes
        self.app.router.add_get('/health', health_check)
        self.app.router.add_get('/info', server_info)
        self.app.router.add_get('/', server_info)
    
    async def start(self) -> Dict:
        """Start the Socket.IO server"""
        try:
            self._start_time = time.time()
            
            # Start the web server
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, 'localhost', self.port)
            await site.start()
            
            print(f"{Fore.GREEN}✅ Socket.IO Terminal Server started on port {self.port}")
            
            return {
                'port': self.port,
                'token': self.connection_token,
                'workdir': self.workdir,
                'url': f'ws://localhost:{self.port}',
                'health_url': f'http://localhost:{self.port}/health'
            }
            
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to start server: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
            return None
    
    async def stop(self):
        """Stop the Socket.IO server"""
        try:
            print(f"{Fore.YELLOW}🛑 Stopping Socket.IO Terminal Server...")
            
            # Close all terminal sessions
            for connection in self.active_connections.values():
                await self.terminal_manager.close_session(connection['session_id'])
            
            self.active_connections.clear()
            
            # Clean up terminal manager
            await self.terminal_manager.cleanup()
            
            print(f"{Fore.GREEN}✅ Server stopped successfully")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error stopping server: {e}")
