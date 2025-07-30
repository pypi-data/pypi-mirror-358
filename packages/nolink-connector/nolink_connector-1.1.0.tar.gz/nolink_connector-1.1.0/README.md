# NoLink Connector - Socket.IO Terminal Bridge

🚀 **Auto-detecting Socket.IO Terminal Bridge for web platforms**

NoLink Connector automatically detects API keys embedded in folders and creates secure real-time terminal connections for web interfaces.

## ✨ Features

- 🔍 **Auto-detection** - Automatically finds API keys in current folder
- 🔗 **Socket.IO Bridge** - Real-time terminal communication
- 🔒 **Secure** - Folder-scoped security with command filtering
- 🌐 **Cross-platform** - Works on Windows, macOS, and Linux
- ⚡ **Fast Setup** - One command installation and connection
- 🎯 **Million User Ready** - Designed for massive scale

## 🚀 Quick Start

### 1. Install the package

```bash
pip install nolink-connector
```

### 2. Navigate to your folder with embedded API key

```bash
cd /path/to/your/downloaded/folder
```

### 3. Start the connector

**Normal Mode:**
```bash
nolink-connector
```

**Auto-Start Mode (Detects Website Launches):**
```bash
nolink-connector --auto-start
```

### 4. Copy the connection token

```bash
🎉 NoLink Connector Started!
📡 Socket.IO Server: ws://localhost:8472
🔑 Connection Token: TBC-user123-port8472-desktop
📁 Working Directory: /Users/username/project
✅ Ready for web interface connection!
```

### 5. Paste token in your web interface

Use the `TBC-user123-port8472-desktop` token in your web platform's terminal connection field.

## 📋 How It Works

```
1. User downloads ZIP with embedded API key from web platform
2. User extracts folder to desktop  
3. User runs: pip install nolink-connector (in folder)
4. Command auto-detects API key from current folder
5. Returns connection token like: TBC-user123-port8472-desktop
6. User pastes token in web interface
7. Real-time terminal access via Socket.IO
```

## 🔧 Advanced Usage

### Environment Variables

```bash
# Custom port (default: auto-assigned)
export NOLINK_PORT=8080

# Custom working directory restriction
export NOLINK_WORK_DIR=/safe/directory

# Debug mode
export NOLINK_DEBUG=true

# Database connection (for web platform integration)
export NOLINK_DB_URL=postgresql://user:pass@host:5432/db
```

### Command Line Options

```bash
# Start with custom port
nolink-connector --port 8080

# Specify working directory
nolink-connector --workdir /custom/path

# Enable debug logging
nolink-connector --debug

# Show version
nolink-connector --version

# Show help
nolink-connector --help
```

## 🛡️ Security Features

- **API Key Authentication** - Unique keys per installation
- **Folder Scope Security** - Can't access files outside current folder
- **Command Filtering** - Dangerous commands blocked by default
- **Timeout Protection** - Auto-kill long-running commands
- **Process Isolation** - Commands run in separate processes

### Default Blocked Commands

```python
BLOCKED_COMMANDS = [
    'sudo', 'su', 'passwd', 'useradd', 'userdel', 
    'systemctl', 'service', 'iptables', 'ufw',
    'fdisk', 'mkfs', 'mount', 'umount'
]
```

## 🔌 Socket.IO Events

### Client → Server

```javascript
// Execute command
socket.emit('execute_command', {
    command: 'ls -la',
    options: { timeout: 30000 }
});

// Change directory
socket.emit('change_directory', {
    path: './subfolder'
});

// Get file content
socket.emit('read_file', {
    path: './readme.txt'
});
```

### Server → Client

```javascript
// Command result
socket.on('command_result', (data) => {
    console.log(data.output);
    console.log(data.exitCode);
    console.log(data.executionTime);
});

// Directory changed
socket.on('directory_changed', (data) => {
    console.log('New directory:', data.path);
});

// Error occurred
socket.on('error', (data) => {
    console.error('Error:', data.message);
});
```

## 📊 PostgreSQL Integration

For web platform developers, NoLink Connector can integrate with PostgreSQL to store connection details:

```sql
-- Example query to get user's connection
SELECT connection_token, socket_port, status 
FROM user_connections 
WHERE api_key = 'wtmcp_1719431106_a1b2c3d4e5f6...'
AND status = 'active';
```

## 🔧 Development

### Local Development

```bash
# Clone repository
git clone https://github.com/Sumedh99/nolink-connector.git
cd nolink-connector

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Run with debug
python -m nolink_connector.main --debug
```

### Building Package

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## 🤝 Integration Examples

### Web Frontend (JavaScript)

```javascript
const socket = io(`ws://localhost:${port}`);

socket.on('connect', () => {
    socket.emit('authenticate', { token: 'TBC-user123-port8472-desktop' });
});

socket.on('authenticated', () => {
    socket.emit('execute_command', { command: 'pwd' });
});

socket.on('command_result', (result) => {
    document.getElementById('terminal').textContent = result.output;
});
```

### Backend API (Python/Flask)

```python
import socketio

def execute_user_command(user_token, command):
    # Get user's connection details from database
    connection = get_user_connection(user_token)
    
    # Connect to user's local Socket.IO server
    sio = socketio.SimpleClient()
    sio.connect(f'http://localhost:{connection.port}')
    
    # Execute command
    sio.emit('execute_command', {'command': command})
    result = sio.receive()
    
    return result
```

## 📋 Requirements

- Python 3.8+
- pip (package installer for Python)
- Internet connection (for initial setup)
- Operating System: Windows 10+, macOS 10.15+, or Linux

## 🚀 Production Ready

NoLink Connector is designed to handle millions of users with:

- **Auto-port detection** - Finds available ports automatically
- **Graceful error handling** - Comprehensive error recovery
- **Resource optimization** - Minimal memory and CPU footprint
- **Logging & monitoring** - Built-in logging for debugging
- **Cross-platform compatibility** - Works everywhere Python runs

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

- GitHub Issues: [Report bugs or request features](https://github.com/Sumedh99/nolink-connector/issues)
- Documentation: [Full documentation](https://github.com/Sumedh99/nolink-connector#readme)
- Email: sumedhpatil99@gmail.com

---

**Made with ❤️ for seamless web-to-terminal integration**
