#!/usr/bin/env python3
"""
NoLink Connector - Main Entry Point
Auto-detecting Socket.IO Terminal Bridge for web platforms
"""

import os
import sys
import asyncio
import signal
import json
import click
from pathlib import Path
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)

from .detector import APIKeyDetector
from .server import SocketIOTerminalServer
from .security import SecurityManager


class NoLinkConnector:
    def __init__(self, port=None, workdir=None, debug=False):
        self.server = None
        self.detector = APIKeyDetector()
        self.security = SecurityManager()
        self.port = port
        self.workdir = workdir or os.getcwd()
        self.debug = debug
        self.running = False
        
    async def start(self):
        """Main entry point - auto-detect and start server"""
        try:
            print(f"{Fore.CYAN}🔍 NoLink Connector - Scanning for API key...{Style.RESET_ALL}")
            
            # Auto-detect API key from current folder
            api_key_info = await self.detector.detect_api_key(self.workdir)
            
            if not api_key_info:
                print(f"{Fore.RED}❌ No valid API key found in current directory")
                print(f"{Fore.YELLOW}💡 Make sure you're in a folder with embedded API key")
                print(f"{Fore.YELLOW}💡 Typically looks like: config/api-key.txt or .nolink-key")
                return False
                
            print(f"{Fore.GREEN}✅ API key detected: {api_key_info['key'][:20]}...{Style.RESET_ALL}")
            
            # Security validation
            if not self.security.validate_working_directory(self.workdir):
                print(f"{Fore.RED}❌ Security validation failed for directory: {self.workdir}")
                return False
                
            # Start Socket.IO server
            self.server = SocketIOTerminalServer(
                api_key=api_key_info['key'],
                port=self.port,
                workdir=self.workdir,
                debug=self.debug
            )
            
            server_info = await self.server.start()
            
            if server_info:
                self.running = True
                self._print_connection_info(server_info)
                
                # Setup signal handlers for graceful shutdown
                signal.signal(signal.SIGINT, self._signal_handler)
                signal.signal(signal.SIGTERM, self._signal_handler)
                
                # Keep running
                await self._keep_alive()
                
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to start NoLink Connector: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
            return False
    
    def _print_connection_info(self, server_info):
        """Print connection information in a nice format"""
        print(f"\n{Back.GREEN}{Fore.BLACK} 🎉 NoLink Connector Started! {Style.RESET_ALL}")
        print(f"{Fore.CYAN}═════════════════════════════════════════{Style.RESET_ALL}")
        print(f"{Fore.WHITE}📡 Socket.IO Server: {Fore.YELLOW}ws://localhost:{server_info['port']}")
        print(f"{Fore.WHITE}🔑 Connection Token: {Fore.GREEN}{server_info['token']}")
        print(f"{Fore.WHITE}📁 Working Directory: {Fore.BLUE}{server_info['workdir']}")
        print(f"{Fore.WHITE}🛡️  Security Level: {Fore.MAGENTA}Folder-scoped")
        print(f"{Fore.CYAN}═════════════════════════════════════════{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Ready for web interface connection!")
        print(f"{Fore.YELLOW}💡 Copy the connection token above and paste it in your web platform")
        print(f"{Fore.GRAY}Press Ctrl+C to stop the server{Style.RESET_ALL}\n")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n{Fore.YELLOW}🛑 Received shutdown signal...")
        self.running = False
        if self.server:
            asyncio.create_task(self.server.stop())
    
    async def _keep_alive(self):
        """Keep the server running until shutdown signal"""
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}🛑 Shutting down...")
        finally:
            if self.server:
                await self.server.stop()
            print(f"{Fore.GREEN}✅ NoLink Connector stopped gracefully{Style.RESET_ALL}")


@click.command()
@click.option('--port', '-p', type=int, default=None, 
              help='Custom port for Socket.IO server (default: auto-detect)')
@click.option('--workdir', '-w', type=click.Path(exists=True), default=None,
              help='Working directory (default: current directory)')
@click.option('--debug', '-d', is_flag=True, default=False,
              help='Enable debug logging')
@click.option('--version', '-v', is_flag=True, default=False,
              help='Show version information')
def main(port, workdir, debug, version):
    """
    NoLink Connector - Auto-detecting Socket.IO Terminal Bridge
    
    Automatically detects API keys in current folder and creates secure 
    real-time terminal connections for web interfaces.
    """
    if version:
        from . import __version__
        print(f"NoLink Connector v{__version__}")
        return
    
    # Set environment variables for debugging
    if debug:
        os.environ['NOLINK_DEBUG'] = 'true'
    
    # Override with environment variables if available
    port = port or os.getenv('NOLINK_PORT')
    workdir = workdir or os.getenv('NOLINK_WORK_DIR', os.getcwd())
    
    if port:
        port = int(port)
    
    print(f"{Fore.MAGENTA}╔══════════════════════════════════════════╗")
    print(f"{Fore.MAGENTA}║           NoLink Connector v1.0.0        ║")
    print(f"{Fore.MAGENTA}║    Socket.IO Terminal Bridge for Web     ║")
    print(f"{Fore.MAGENTA}╚══════════════════════════════════════════╝{Style.RESET_ALL}\n")
    
    # Create and start connector
    connector = NoLinkConnector(
        port=port,
        workdir=workdir,
        debug=debug
    )
    
    try:
        # Run the async main function
        success = asyncio.run(connector.start())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}💥 Unexpected error: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
