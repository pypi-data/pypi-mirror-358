"""
Example usage of NoLink Connector for web platform integration
"""

import asyncio
import json
import socketio
from typing import Dict, List, Optional


class NoLinkWebIntegration:
    """Example integration for web platforms"""
    
    def __init__(self, database_url: str = None):
        self.db_url = database_url
        self.active_connections = {}
    
    async def register_user_connection(self, user_id: str, api_key: str, 
                                     connection_token: str, port: int) -> bool:
        """
        Register a new user connection in the database
        Called when user starts nolink-connector and gets a token
        """
        # In real implementation, this would insert into PostgreSQL
        connection_data = {
            'user_id': user_id,
            'api_key': api_key,
            'connection_token': connection_token,
            'socket_port': port,
            'status': 'active',
            'created_at': 'now()',
            'last_heartbeat': 'now()'
        }
        
        print(f"📝 Registered connection for user {user_id}: {connection_token}")
        return True
    
    async def execute_command_for_user(self, connection_token: str, 
                                     command: str) -> Dict:
        """
        Execute a command for a user via their local NoLink connector
        This is called from your web platform's backend
        """
        try:
            # 1. Look up user's connection details from database
            connection = await self.get_connection_by_token(connection_token)
            
            if not connection:
                return {
                    'success': False,
                    'error': 'Invalid connection token'
                }
            
            # 2. Connect to user's local Socket.IO server
            sio = socketio.AsyncSimpleClient()
            
            try:
                await sio.connect(f'http://localhost:{connection["port"]}')
                
                # 3. Authenticate with the token
                await sio.emit('authenticate', {'token': connection_token})
                
                # Wait for authentication response
                auth_response = await sio.receive()
                if auth_response[0] != 'authenticated':
                    return {
                        'success': False,
                        'error': 'Authentication failed'
                    }
                
                # 4. Execute the command
                await sio.emit('execute_command', {
                    'command': command,
                    'request_id': f'web_{int(asyncio.get_event_loop().time())}'
                })
                
                # 5. Wait for command result
                result_event = await sio.receive()
                
                if result_event[0] == 'command_result':
                    result = result_event[1]
                    
                    # 6. Log the command execution
                    await self.log_command_execution(
                        connection['id'], command, result
                    )
                    
                    return {
                        'success': result['success'],
                        'output': result['output'],
                        'exit_code': result.get('exit_code', 0),
                        'execution_time': result.get('execution_time', 0)
                    }
                
                return {
                    'success': False,
                    'error': 'Unexpected response from terminal'
                }
                
            finally:
                await sio.disconnect()
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Connection failed: {str(e)}'
            }
    
    async def get_connection_by_token(self, token: str) -> Optional[Dict]:
        """Get connection details by token from database"""
        # In real implementation, this would query PostgreSQL
        # SELECT * FROM user_connections WHERE connection_token = %s AND status = 'active'
        
        # Mock response for example
        return {
            'id': 1,
            'user_id': 'user123',
            'connection_token': token,
            'port': 8472,
            'status': 'active'
        }
    
    async def log_command_execution(self, connection_id: int, command: str, 
                                  result: Dict):
        """Log command execution to database"""
        # In real implementation, this would insert into command_executions table
        log_data = {
            'connection_id': connection_id,
            'command_text': command,
            'output_preview': result.get('output', '')[:1000],
            'exit_code': result.get('exit_code', 0),
            'execution_time_ms': result.get('execution_time', 0),
            'executed_at': 'now()'
        }
        
        print(f"📊 Logged command execution: {command[:50]}...")
    
    async def get_user_connections(self, user_id: str) -> List[Dict]:
        """Get all active connections for a user"""
        # In real implementation, this would query PostgreSQL
        # SELECT * FROM user_connections WHERE user_id = %s AND status = 'active'
        
        return [
            {
                'connection_token': 'TBC-user123-port8472-desktop',
                'port': 8472,
                'hostname': 'desktop',
                'platform': 'macOS',
                'last_heartbeat': '2024-12-26T10:30:00Z',
                'created_at': '2024-12-26T09:00:00Z'
            }
        ]
    
    async def heartbeat_check(self, connection_token: str) -> bool:
        """Check if a connection is still alive"""
        try:
            connection = await self.get_connection_by_token(connection_token)
            if not connection:
                return False
            
            # Try to connect and ping
            sio = socketio.AsyncSimpleClient()
            
            try:
                await asyncio.wait_for(
                    sio.connect(f'http://localhost:{connection["port"]}'),
                    timeout=5.0
                )
                
                # Update last_heartbeat in database
                await self.update_heartbeat(connection['id'])
                
                return True
                
            except asyncio.TimeoutError:
                return False
            finally:
                try:
                    await sio.disconnect()
                except:
                    pass
                    
        except Exception:
            return False
    
    async def update_heartbeat(self, connection_id: int):
        """Update last heartbeat timestamp"""
        # In real implementation:
        # UPDATE user_connections SET last_heartbeat = now() WHERE id = %s
        print(f"💓 Updated heartbeat for connection {connection_id}")


# Example Flask/FastAPI endpoint integration
class WebPlatformAPI:
    """Example web platform API endpoints"""
    
    def __init__(self):
        self.nolink = NoLinkWebIntegration()
    
    async def register_terminal_connection(self, user_id: str, 
                                         connection_data: Dict) -> Dict:
        """
        POST /api/terminal/register
        Called when user starts nolink-connector and gets a token
        """
        try:
            success = await self.nolink.register_user_connection(
                user_id=user_id,
                api_key=connection_data['api_key'],
                connection_token=connection_data['token'],
                port=connection_data['port']
            )
            
            return {
                'success': success,
                'message': 'Terminal connection registered successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def execute_terminal_command(self, user_id: str, 
                                     connection_token: str, 
                                     command: str) -> Dict:
        """
        POST /api/terminal/execute
        Execute a command on user's local machine
        """
        try:
            result = await self.nolink.execute_command_for_user(
                connection_token, command
            )
            
            return {
                'success': result['success'],
                'output': result.get('output', ''),
                'exit_code': result.get('exit_code', 0),
                'execution_time': result.get('execution_time', 0),
                'error': result.get('error')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_user_terminals(self, user_id: str) -> Dict:
        """
        GET /api/terminal/connections
        Get all active terminal connections for user
        """
        try:
            connections = await self.nolink.get_user_connections(user_id)
            
            return {
                'success': True,
                'connections': connections,
                'count': len(connections)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def check_terminal_status(self, connection_token: str) -> Dict:
        """
        GET /api/terminal/status/{token}
        Check if a terminal connection is still active
        """
        try:
            is_alive = await self.nolink.heartbeat_check(connection_token)
            
            return {
                'success': True,
                'is_alive': is_alive,
                'status': 'active' if is_alive else 'inactive'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Example usage
async def main():
    """Example of how to use the NoLink integration"""
    
    # Initialize the integration
    api = WebPlatformAPI()
    
    # Example 1: Register a new terminal connection
    print("1. Registering terminal connection...")
    register_result = await api.register_terminal_connection(
        user_id='user123',
        connection_data={
            'api_key': 'wtmcp_1719431106_a1b2c3d4e5f6...',
            'token': 'TBC-user123-port8472-desktop',
            'port': 8472
        }
    )
    print(f"   Result: {register_result}")
    
    # Example 2: Execute a command
    print("\n2. Executing command...")
    command_result = await api.execute_terminal_command(
        user_id='user123',
        connection_token='TBC-user123-port8472-desktop',
        command='ls -la'
    )
    print(f"   Result: {command_result}")
    
    # Example 3: Get user's terminals
    print("\n3. Getting user terminals...")
    terminals_result = await api.get_user_terminals('user123')
    print(f"   Result: {terminals_result}")
    
    # Example 4: Check terminal status
    print("\n4. Checking terminal status...")
    status_result = await api.check_terminal_status('TBC-user123-port8472-desktop')
    print(f"   Result: {status_result}")


if __name__ == '__main__':
    asyncio.run(main())
