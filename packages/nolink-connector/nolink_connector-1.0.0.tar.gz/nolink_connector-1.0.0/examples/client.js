"""
Example JavaScript client for connecting to NoLink Connector
"""

class NoLinkClient {
    constructor(serverUrl, connectionToken) {
        this.serverUrl = serverUrl;
        this.connectionToken = connectionToken;
        this.socket = null;
        this.isConnected = false;
        this.isAuthenticated = false;
        this.eventHandlers = {};
        this.requestCallbacks = {};
        this.requestId = 0;
    }

    // Connect to the NoLink terminal server
    async connect() {
        return new Promise((resolve, reject) => {
            try {
                // Use Socket.IO client library
                this.socket = io(this.serverUrl, {
                    transports: ['websocket', 'polling'],
                    timeout: 10000
                });

                this.socket.on('connect', () => {
                    console.log('🔗 Connected to NoLink Terminal Bridge');
                    this.isConnected = true;
                    
                    // Automatically authenticate
                    this.authenticate()
                        .then(() => resolve())
                        .catch(reject);
                });

                this.socket.on('disconnect', () => {
                    console.log('🔌 Disconnected from NoLink Terminal Bridge');
                    this.isConnected = false;
                    this.isAuthenticated = false;
                    this.emit('disconnected');
                });

                this.socket.on('error', (error) => {
                    console.error('❌ Socket error:', error);
                    reject(error);
                });

                this.socket.on('authenticated', (data) => {
                    console.log('✅ Authenticated successfully');
                    this.isAuthenticated = true;
                    this.emit('authenticated', data);
                });

                this.socket.on('command_result', (data) => {
                    const callback = this.requestCallbacks[data.request_id];
                    if (callback) {
                        callback(data);
                        delete this.requestCallbacks[data.request_id];
                    }
                    this.emit('command_result', data);
                });

                this.socket.on('directory_changed', (data) => {
                    this.emit('directory_changed', data);
                });

                this.socket.on('file_content', (data) => {
                    this.emit('file_content', data);
                });

                this.socket.on('directory_listing', (data) => {
                    this.emit('directory_listing', data);
                });

                this.socket.on('system_info', (data) => {
                    this.emit('system_info', data);
                });

                this.socket.on('welcome', (data) => {
                    console.log('👋 Welcome message:', data.message);
                    this.emit('welcome', data);
                });

            } catch (error) {
                reject(error);
            }
        });
    }

    // Authenticate with the server
    async authenticate() {
        return new Promise((resolve, reject) => {
            if (!this.isConnected) {
                reject(new Error('Not connected to server'));
                return;
            }

            const timeout = setTimeout(() => {
                reject(new Error('Authentication timeout'));
            }, 5000);

            const authHandler = (data) => {
                clearTimeout(timeout);
                this.socket.off('authenticated', authHandler);
                this.socket.off('error', errorHandler);
                resolve(data);
            };

            const errorHandler = (error) => {
                clearTimeout(timeout);
                this.socket.off('authenticated', authHandler);
                this.socket.off('error', errorHandler);
                reject(error);
            };

            this.socket.on('authenticated', authHandler);
            this.socket.on('error', errorHandler);

            this.socket.emit('authenticate', {
                token: this.connectionToken
            });
        });
    }

    // Execute a terminal command
    async executeCommand(command, options = {}) {
        return new Promise((resolve, reject) => {
            if (!this.isAuthenticated) {
                reject(new Error('Not authenticated'));
                return;
            }

            const requestId = `req_${++this.requestId}_${Date.now()}`;
            const timeout = options.timeout || 30000;

            const timeoutId = setTimeout(() => {
                delete this.requestCallbacks[requestId];
                reject(new Error(`Command execution timeout after ${timeout}ms`));
            }, timeout);

            this.requestCallbacks[requestId] = (result) => {
                clearTimeout(timeoutId);
                if (result.success) {
                    resolve(result);
                } else {
                    reject(new Error(result.error || 'Command execution failed'));
                }
            };

            this.socket.emit('execute_command', {
                command,
                options,
                request_id: requestId
            });
        });
    }

    // Change directory
    async changeDirectory(path) {
        return new Promise((resolve, reject) => {
            if (!this.isAuthenticated) {
                reject(new Error('Not authenticated'));
                return;
            }

            const handler = (data) => {
                this.socket.off('directory_changed', handler);
                if (data.success) {
                    resolve(data);
                } else {
                    reject(new Error(data.message || 'Directory change failed'));
                }
            };

            this.socket.on('directory_changed', handler);
            this.socket.emit('change_directory', { path });

            // Timeout after 5 seconds
            setTimeout(() => {
                this.socket.off('directory_changed', handler);
                reject(new Error('Directory change timeout'));
            }, 5000);
        });
    }

    // Read file content
    async readFile(filePath) {
        return new Promise((resolve, reject) => {
            if (!this.isAuthenticated) {
                reject(new Error('Not authenticated'));
                return;
            }

            const handler = (data) => {
                this.socket.off('file_content', handler);
                resolve(data);
            };

            const errorHandler = (error) => {
                this.socket.off('error', errorHandler);
                reject(new Error(error.message || 'File read failed'));
            };

            this.socket.on('file_content', handler);
            this.socket.on('error', errorHandler);
            this.socket.emit('read_file', { path: filePath });

            // Timeout after 10 seconds
            setTimeout(() => {
                this.socket.off('file_content', handler);
                this.socket.off('error', errorHandler);
                reject(new Error('File read timeout'));
            }, 10000);
        });
    }

    // List directory contents
    async listDirectory(dirPath = '.') {
        return new Promise((resolve, reject) => {
            if (!this.isAuthenticated) {
                reject(new Error('Not authenticated'));
                return;
            }

            const handler = (data) => {
                this.socket.off('directory_listing', handler);
                if (data.success) {
                    resolve(data);
                } else {
                    reject(new Error('Directory listing failed'));
                }
            };

            this.socket.on('directory_listing', handler);
            this.socket.emit('list_directory', { path: dirPath });

            // Timeout after 10 seconds
            setTimeout(() => {
                this.socket.off('directory_listing', handler);
                reject(new Error('Directory listing timeout'));
            }, 10000);
        });
    }

    // Get system information
    async getSystemInfo() {
        return new Promise((resolve, reject) => {
            if (!this.isAuthenticated) {
                reject(new Error('Not authenticated'));
                return;
            }

            const handler = (data) => {
                this.socket.off('system_info', handler);
                resolve(data);
            };

            this.socket.on('system_info', handler);
            this.socket.emit('get_system_info', {});

            // Timeout after 5 seconds
            setTimeout(() => {
                this.socket.off('system_info', handler);
                reject(new Error('System info timeout'));
            }, 5000);
        });
    }

    // Event handler system
    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }

    off(event, handler) {
        if (this.eventHandlers[event]) {
            const index = this.eventHandlers[event].indexOf(handler);
            if (index > -1) {
                this.eventHandlers[event].splice(index, 1);
            }
        }
    }

    emit(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in event handler for ${event}:`, error);
                }
            });
        }
    }

    // Disconnect from server
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        this.isConnected = false;
        this.isAuthenticated = false;
        this.requestCallbacks = {};
    }

    // Get connection status
    getStatus() {
        return {
            isConnected: this.isConnected,
            isAuthenticated: this.isAuthenticated,
            serverUrl: this.serverUrl,
            connectionToken: this.connectionToken ? this.connectionToken.substring(0, 20) + '...' : null
        };
    }
}

// Example usage
async function exampleUsage() {
    try {
        // Initialize client
        const client = new NoLinkClient('ws://localhost:8472', 'TBC-user123-port8472-desktop');

        // Set up event listeners
        client.on('authenticated', (data) => {
            console.log('Connected to terminal:', data);
        });

        client.on('command_result', (result) => {
            console.log('Command completed:', result);
        });

        client.on('disconnected', () => {
            console.log('Terminal disconnected');
        });

        // Connect
        await client.connect();
        console.log('✅ Connected and authenticated');

        // Execute commands
        const result1 = await client.executeCommand('ls -la');
        console.log('Directory listing:', result1.output);

        const result2 = await client.executeCommand('pwd');
        console.log('Current directory:', result2.output);

        // Change directory
        await client.changeDirectory('./subfolder');
        console.log('Changed to subfolder');

        // Read a file
        const fileContent = await client.readFile('README.md');
        console.log('File content:', fileContent.content);

        // Get system info
        const sysInfo = await client.getSystemInfo();
        console.log('System info:', sysInfo);

    } catch (error) {
        console.error('Error:', error);
    }
}

// Export for use in web applications
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NoLinkClient;
}
