"""
Enhanced NoLink Connector with Auto-Start Detection
Monitors for website launches and auto-starts terminal server
"""

import asyncio
import os
import sys
import json
import time
import subprocess
import socket
import psutil
import signal
from pathlib import Path
from colorama import Fore, Style
import aiohttp
from .detector import APIKeyDetector
from .security import SecurityManager


class AutoStartNoLinkConnector:
    """Enhanced connector with auto-start detection for website launches"""
    
    def __init__(self, target_port=3456, workdir=None, debug=False):
        self.target_port = target_port
        self.workdir = workdir or os.getcwd()
        self.debug = debug
        self.detector = APIKeyDetector()
        self.security = SecurityManager()
        self.api_key_info = None
        self.terminal_process = None
        self.monitoring = False
        self.connection_token = None
        
    async def start_monitoring(self):
        """Start monitoring for website launches"""
        print(f"{Fore.CYAN}🔍 NoLink Connector - Auto-Start Mode Activated")
        print(f"{Fore.BLUE}   Monitoring for website launches on port {self.target_port}")
        print(f"{Fore.BLUE}   Will auto-start terminal server when needed")
        print(f"{Fore.YELLOW}💡 Keep this running in background - minimize this window")
        print(f"{Fore.GRAY}Press Ctrl+C to stop monitoring{Style.RESET_ALL}\n")
        
        # Detect API key once
        self.api_key_info = await self.detector.detect_api_key(self.workdir)
        if not self.api_key_info:
            print(f"{Fore.RED}❌ No API key found in current directory")
            print(f"{Fore.YELLOW}💡 Make sure you're in a folder with embedded API key")
            return False
        
        print(f"{Fore.GREEN}✅ API key detected: {self.api_key_info['key'][:20]}...")
        print(f"{Fore.BLUE}🎯 Monitoring for website connection requests...\n")
        
        self.monitoring = True
        
        # Generate connection token for database storage
        self.connection_token = self.generate_connection_token()
        print(f"{Fore.CYAN}🔑 Connection Token: {Fore.YELLOW}{self.connection_token}")
        print(f"{Fore.BLUE}💾 Store this token in your database for website integration")
        print(f"{Fore.GRAY}────────────────────────────────────────────────────{Style.RESET_ALL}\n")
        
        # Start monitoring loop
        consecutive_checks = 0
        while self.monitoring:
            try:
                # Check if website is trying to connect
                website_detected = await self.detect_website_launch()
                
                if website_detected:
                    consecutive_checks += 1
                    if consecutive_checks >= 2:  # Confirm detection
                        if not self.is_terminal_running():
                            print(f"{Fore.YELLOW}🚀 Website launch detected! Auto-starting terminal server...")
                            await self.start_terminal_server()
                        consecutive_checks = 0
                else:
                    consecutive_checks = 0
                
                # Check if terminal server is still needed
                if self.is_terminal_running():
                    if not await self.is_website_active():
                        # Wait a bit before stopping (website might reconnect)
                        await asyncio.sleep(10)
                        if not await self.is_website_active():
                            print(f"{Fore.YELLOW}📴 Website disconnected. Stopping terminal server...")
                            await self.stop_terminal_server()
                
                # Wait before next check
                await asyncio.sleep(3)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                if self.debug:
                    print(f"{Fore.RED}⚠️ Monitoring error: {e}")
                await asyncio.sleep(5)
        
        # Cleanup on exit
        await self.stop_terminal_server()
        print(f"{Fore.GREEN}✅ NoLink Connector monitoring stopped{Style.RESET_ALL}")
        return True
    
    async def detect_website_launch(self):
        """Detect if website is trying to connect to terminal"""
        try:
            # Method 1: Check if something is trying to connect to port
            if self.is_port_being_accessed(self.target_port):
                if self.debug:
                    print(f"{Fore.BLUE}🔍 Port access detected on {self.target_port}")
                return True
            
            # Method 2: Try to connect to see if something is listening
            if await self.check_for_connection_attempts():
                if self.debug:
                    print(f"{Fore.BLUE}🔍 Connection attempt detected")
                return True
                
            return False
            
        except Exception as e:
            if self.debug:
                print(f"{Fore.RED}Detection error: {e}")
            return False
    
    def is_port_being_accessed(self, port):
        """Check if something is trying to access the port"""
        try:
            # Check network connections for attempts to connect to our port
            connections = psutil.net_connections(kind='inet')
            for conn in connections:
                if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == port:
                    if conn.status in ['SYN_RECV', 'ESTABLISHED', 'LISTEN']:
                        return True
                        
            # Also check if anything is trying to bind to the port
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('localhost', port))
                sock.close()
                return False  # Port is free
            except OSError:
                return True  # Port is in use or being accessed
                
        except Exception as e:
            if self.debug:
                print(f"{Fore.YELLOW}Port check error: {e}")
            return False
    
    async def check_for_connection_attempts(self):
        """Check for connection attempts to the port"""
        try:
            # Try a quick health check to see if something responds
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1)) as session:
                try:
                    async with session.get(f'http://localhost:{self.target_port}/health') as response:
                        # If we get any response, server is already running
                        return False
                except aiohttp.ClientConnectorError:
                    # Connection refused - might indicate website trying to connect
                    # but server not running yet
                    return True
                except asyncio.TimeoutError:
                    return True
                except Exception:
                    return False
        except Exception:
            return False
    
    def is_terminal_running(self):
        """Check if terminal server is already running"""
        try:
            if self.terminal_process and self.terminal_process.poll() is None:
                return True
            
            # Check if something is listening on the target port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', self.target_port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    async def start_terminal_server(self):
        """Start the terminal server"""
        try:
            current_dir = self.workdir
            
            # Look for existing server files in order of preference
            start_commands = [
                # Node.js based server
                ('npm start', 'package.json'),
                ('node build/index.js', 'build/index.js'),
                ('node src/index.js', 'src/index.js'),
                ('node index.js', 'index.js'),
                
                # Python based server
                ('python -m http.server 3456', None),
                ('python3 -m http.server 3456', None),
                
                # Basic HTTP server fallback
                ('python -c \"import http.server; import socketserver; socketserver.TCPServer((\\\"\\\", 3456), http.server.SimpleHTTPRequestHandler).serve_forever()\"', None)
            ]
            
            for command, check_file in start_commands:
                if check_file and not os.path.exists(os.path.join(current_dir, check_file)):
                    continue
                    
                if await self.try_start_command(command, current_dir):
                    break
            
            # Wait for server to start
            await asyncio.sleep(3)
            
            if self.is_terminal_running():
                print(f"{Fore.GREEN}✅ Terminal server started successfully on port {self.target_port}")
                print(f"{Fore.CYAN}🔗 Server URL: http://localhost:{self.target_port}")
                print(f"{Fore.GREEN}✅ Ready for website connection!")
                return True
            else:
                print(f"{Fore.RED}❌ Failed to start terminal server")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error starting terminal server: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
            return False
    
    async def try_start_command(self, command, working_dir):
        """Try to start server with given command"""
        try:
            print(f"{Fore.BLUE}🔧 Starting terminal server with: {command}")
            
            # Start the process
            self.terminal_process = subprocess.Popen(
                command,
                shell=True,
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            # Give it a moment to start
            await asyncio.sleep(2)
            
            # Check if it's still running
            if self.terminal_process.poll() is None:
                return True
            else:
                return False
            
        except Exception as e:
            if self.debug:
                print(f"{Fore.YELLOW}⚠️ Command failed: {command} - {e}")
            return False
    
    def generate_connection_token(self):
        """Generate connection token for the user"""
        if not self.api_key_info:
            return f"TBC-unknown-port{self.target_port}-desktop"
        
        user_id = self.api_key_info['key'].split('_')[1] if '_' in self.api_key_info['key'] else 'user'
        hostname = socket.gethostname().lower()[:8]
        return f"TBC-{user_id}-port{self.target_port}-{hostname}"
    
    async def is_website_active(self):
        """Check if website is still active/connected"""
        try:
            # Check for active connections to the port
            connections = psutil.net_connections(kind='inet')
            active_connections = 0
            
            for conn in connections:
                if (hasattr(conn, 'laddr') and conn.laddr and 
                    conn.laddr.port == self.target_port and 
                    conn.status == 'ESTABLISHED'):
                    active_connections += 1
            
            # Consider website active if there are connections
            return active_connections > 0
            
        except Exception:
            return False
    
    async def stop_terminal_server(self):
        """Stop the terminal server"""
        try:
            if self.terminal_process:
                # Terminate gracefully first
                if os.name != 'nt':
                    # Unix-like systems
                    os.killpg(os.getpgid(self.terminal_process.pid), signal.SIGTERM)
                else:
                    # Windows
                    self.terminal_process.terminate()
                
                # Wait a bit for graceful shutdown
                try:
                    self.terminal_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    if os.name != 'nt':
                        os.killpg(os.getpgid(self.terminal_process.pid), signal.SIGKILL)
                    else:
                        self.terminal_process.kill()
                
                self.terminal_process = None
                print(f"{Fore.YELLOW}🛑 Terminal server stopped")
                
        except Exception as e:
            if self.debug:
                print(f"{Fore.YELLOW}Stop error: {e}")
            pass
