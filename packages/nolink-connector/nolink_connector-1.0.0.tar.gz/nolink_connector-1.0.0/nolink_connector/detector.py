"""
API Key Auto-Detection Module
Automatically finds and validates API keys in the current folder
"""

import os
import re
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, List
from colorama import Fore, Style


class APIKeyDetector:
    """Auto-detect API keys embedded in folder structure"""
    
    def __init__(self):
        self.api_key_patterns = [
            # Web Terminal MCP pattern
            r'wtmcp_\d+_[a-f0-9]+',
            # General API key patterns
            r'[a-zA-Z0-9]{32,}',
            r'sk-[a-zA-Z0-9]{32,}',
            r'key_[a-zA-Z0-9]+',
            r'token_[a-zA-Z0-9]+',
        ]
        
        self.search_files = [
            'config/api-key.txt',
            'config/server-config.json',
            '.nolink-key',
            '.api-key',
            '.env',
            'credentials.json',
            'config.json',
            'settings.json',
            'api-credentials.txt'
        ]
        
        self.search_folders = [
            'config',
            'credentials',
            'auth',
            '.config',
            'settings'
        ]
    
    async def detect_api_key(self, directory: str = None) -> Optional[Dict]:
        """
        Auto-detect API key in the specified directory
        
        Args:
            directory: Directory to search (default: current directory)
            
        Returns:
            Dict with API key info or None if not found
        """
        directory = directory or os.getcwd()
        search_path = Path(directory)
        
        print(f"{Fore.BLUE}🔍 Searching for API keys in: {search_path}")
        
        # Method 1: Search specific known files
        api_key_info = await self._search_known_files(search_path)
        if api_key_info:
            return api_key_info
        
        # Method 2: Search configuration folders
        api_key_info = await self._search_config_folders(search_path)
        if api_key_info:
            return api_key_info
        
        # Method 3: Deep search in all text files (fallback)
        api_key_info = await self._deep_search_files(search_path)
        if api_key_info:
            return api_key_info
        
        return None
    
    async def _search_known_files(self, search_path: Path) -> Optional[Dict]:
        """Search in known file locations"""
        for file_path in self.search_files:
            full_path = search_path / file_path
            
            if full_path.exists() and full_path.is_file():
                print(f"{Fore.YELLOW}📄 Checking: {file_path}")
                
                api_key_info = await self._extract_from_file(full_path)
                if api_key_info:
                    return api_key_info
        
        return None
    
    async def _search_config_folders(self, search_path: Path) -> Optional[Dict]:
        """Search in configuration folders"""
        for folder in self.search_folders:
            folder_path = search_path / folder
            
            if folder_path.exists() and folder_path.is_dir():
                print(f"{Fore.YELLOW}📁 Searching folder: {folder}")
                
                for file_path in folder_path.iterdir():
                    if file_path.is_file() and self._is_text_file(file_path):
                        api_key_info = await self._extract_from_file(file_path)
                        if api_key_info:
                            return api_key_info
        
        return None
    
    async def _deep_search_files(self, search_path: Path) -> Optional[Dict]:
        """Deep search in all text files (last resort)"""
        print(f"{Fore.YELLOW}🔎 Performing deep search...")
        
        # Search up to 2 levels deep to avoid scanning entire system
        for file_path in search_path.rglob('*'):
            if (file_path.is_file() and 
                self._is_text_file(file_path) and 
                len(file_path.parts) - len(search_path.parts) <= 2):
                
                api_key_info = await self._extract_from_file(file_path)
                if api_key_info:
                    return api_key_info
        
        return None
    
    async def _extract_from_file(self, file_path: Path) -> Optional[Dict]:
        """Extract API key from a specific file"""
        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Try different extraction methods based on file type
            if file_path.suffix.lower() == '.json':
                api_key_info = self._extract_from_json(content, file_path)
            else:
                api_key_info = self._extract_from_text(content, file_path)
            
            if api_key_info:
                print(f"{Fore.GREEN}✅ Found API key in: {file_path.relative_to(Path.cwd())}")
                return api_key_info
                
        except Exception as e:
            # Silently skip files that can't be read
            pass
        
        return None
    
    def _extract_from_json(self, content: str, file_path: Path) -> Optional[Dict]:
        """Extract API key from JSON content"""
        try:
            data = json.loads(content)
            
            # Search for API key in common JSON keys
            api_key_keys = [
                'apiKey', 'api_key', 'API_KEY',
                'token', 'TOKEN', 'authToken',
                'key', 'KEY', 'secretKey',
                'credential', 'credentials'
            ]
            
            def search_nested(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key in api_key_keys and isinstance(value, str):
                            if self._validate_api_key(value):
                                return {
                                    'key': value,
                                    'source': str(file_path),
                                    'type': 'json',
                                    'field': f"{path}.{key}" if path else key
                                }
                        
                        if isinstance(value, (dict, list)):
                            result = search_nested(value, f"{path}.{key}" if path else key)
                            if result:
                                return result
                                
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        if isinstance(item, (dict, list)):
                            result = search_nested(item, f"{path}[{i}]")
                            if result:
                                return result
                
                return None
            
            return search_nested(data)
            
        except json.JSONDecodeError:
            return None
    
    def _extract_from_text(self, content: str, file_path: Path) -> Optional[Dict]:
        """Extract API key from plain text content"""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if line.startswith('#') or line.startswith('//') or not line:
                continue
            
            # Check for key-value patterns
            for pattern in ['=', ':', ' ']:
                if pattern in line:
                    parts = line.split(pattern, 1)
                    if len(parts) == 2:
                        key, value = parts
                        key = key.strip().strip('"\'')
                        value = value.strip().strip('"\'')
                        
                        if self._validate_api_key(value):
                            return {
                                'key': value,
                                'source': str(file_path),
                                'type': 'text',
                                'line': line_num,
                                'field': key
                            }
            
            # Check for standalone API key (whole line)
            if self._validate_api_key(line):
                return {
                    'key': line,
                    'source': str(file_path),
                    'type': 'text',
                    'line': line_num,
                    'field': 'standalone'
                }
        
        return None
    
    def _validate_api_key(self, potential_key: str) -> bool:
        """Validate if a string looks like a valid API key"""
        if not potential_key or len(potential_key) < 16:
            return False
        
        # Check against known patterns
        for pattern in self.api_key_patterns:
            if re.match(pattern, potential_key):
                return True
        
        # Additional validation for generic keys
        if (len(potential_key) >= 32 and 
            re.match(r'^[a-zA-Z0-9_-]+$', potential_key) and
            not potential_key.isdigit()):
            return True
        
        return False
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is likely a text file"""
        text_extensions = {
            '.txt', '.json', '.yaml', '.yml', '.ini', '.cfg', '.conf',
            '.env', '.key', '.token', '.cred', '.credentials', '.config',
            '.properties', '.toml', '.xml'
        }
        
        # Check by extension
        if file_path.suffix.lower() in text_extensions:
            return True
        
        # Check by name pattern
        text_patterns = [
            'api-key', 'apikey', 'token', 'credential', 'auth',
            'config', 'setting', 'env'
        ]
        
        filename = file_path.name.lower()
        for pattern in text_patterns:
            if pattern in filename:
                return True
        
        # Check if file is small and likely text
        try:
            if file_path.stat().st_size < 10 * 1024:  # Less than 10KB
                return True
        except:
            pass
        
        return False
