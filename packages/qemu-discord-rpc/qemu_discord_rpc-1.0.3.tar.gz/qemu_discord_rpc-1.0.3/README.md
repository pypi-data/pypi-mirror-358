# QEMU Discord RPC

A Python script that displays your running QEMU virtual machines as Discord Rich Presence status.

## Features

- 🖥️ Automatically detects running QEMU virtual machines
- 🎮 Shows VM status on your Discord profile with runtime
- ⏱️ Displays how long the VM has been running
- 🔄 Real-time updates (configurable interval)
- 💾 Saves Discord application settings locally
- ⚙️ Easy configuration management with built-in editor
- 🚀 Lightweight and easy to use
- 📦 Multiple installation options

## Prerequisites

- Python 3.6 or higher
- Discord application
- QEMU virtual machines
- Linux/Unix system (uses `ps aux` command)
- nano text editor (for config editing)

## Installation

### Option 1: Using pipx (Recommended)

pipx installs packages in isolated environments and makes them available globally:

```bash
# Install pipx if you don't have it
pip install pipx

# Install QEMU Discord RPC
pipx install qemu-discord-rpc

# Run anywhere
qemu-discord-rpc
```

### Option 2: Using pip

```bash
pip install qemu-discord-rpc
```

### Option 3: From Source

```bash
git clone https://github.com/qubixq/qemu-discord-rpc.git
cd qemu-discord-rpc
pip install .
```

### Option 4: Development Installation

```bash
git clone https://github.com/qubixq/qemu-discord-rpc.git
cd qemu-discord-rpc
pip install -e .
```

## Quick Start

1. **Create a Discord Application**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and name it (e.g., "QEMU VM Status")
   - Copy the **Application ID** (Client ID)

2. **Run the application**
   ```bash
   qemu-discord-rpc
   ```

3. **First-time setup**
   - Enter your Discord Application Client ID when prompted
   - The script will save your settings automatically

That's it! Your QEMU VMs will now appear in your Discord status.

## Usage

### Basic Commands

```bash
# Start the Discord RPC service
qemu-discord-rpc

# Edit configuration file
qemu-discord-rpc --config

# Show help
qemu-discord-rpc --help

# Show version
qemu-discord-rpc --version
```

### Discord Status Example
```
🖥️ Playing QEMU VM
Windows-11 VM is running
Virtualization with QEMU VM
Started 25 minutes ago
```

## Configuration

### Automatic Configuration
On first run, the script will create a `config.json` file with your settings.

### Manual Configuration
Use the built-in config editor:
```bash
qemu-discord-rpc --config
```

This opens the configuration file in nano editor where you can modify:

```json
{
    "client_id": "your_discord_application_id",
    "update_interval": 15,
    "app_name": "QEMU VM"
}
```

**Configuration Options:**
- `client_id`: Your Discord Application Client ID
- `update_interval`: How often to check for VMs (seconds, default: 15)
- `app_name`: Application name shown in Discord status

### Manual Config Editing
You can also edit `config.json` directly in any text editor.

## Advanced Setup

### Creating a Custom Discord Application Icon

1. Go to your Discord Application in the Developer Portal
2. Navigate to "Rich Presence" → "Art Assets"
3. Upload an icon named `qemu-logo` (this matches the script)
4. Your VM status will now show your custom icon!

### VM Detection Requirements

Your QEMU command must include the `guest=` parameter for detection:
```bash
qemu-system-x86_64 -name guest=MyVM,debug-threads=on ...
```

## Troubleshooting

### Common Issues

**VMs not detected:**
- Ensure QEMU processes include `guest=` parameter
- Test detection: `ps aux | grep qemu`
- Check that QEMU is actually running

**Discord status not showing:**
- Verify Discord is running and you're logged in
- Check Discord privacy settings allow Rich Presence
- Confirm Client ID is correct (use `--config` to update)

**Config editor not working:**
- Install nano: `sudo apt install nano` (Ubuntu/Debian)
- Or edit `config.json` manually in any text editor

### Installation Issues

**Command not found after pip install:**
```bash
# Try reinstalling with --user flag
pip install --user qemu-discord-rpc

# Or use pipx (recommended)
pipx install qemu-discord-rpc
```

**Permission issues:**
```bash
# Use pipx to avoid permission issues
pipx install qemu-discord-rpc

# Or install with --user flag
pip install --user qemu-discord-rpc
```

## Development

### Running from Source
```bash
git clone https://github.com/qubixq/qemu-discord-rpc.git
cd qemu-discord-rpc
python -m qemu_discord_rpc
```

### Building
```bash
pip install build
python -m build
```

## Contributing

Contributions are welcome! Please feel free to:
- 🐛 Report bugs
- 💡 Suggest new features  
- 🔧 Submit pull requests
- 📚 Improve documentation

### Development Setup
```bash
git clone https://github.com/qubixq/qemu-discord-rpc.git
cd qemu-discord-rpc
pip install -e .[dev]
```

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [pypresence](https://github.com/qwertyquerty/pypresence) - Discord RPC library
- QEMU community for the amazing virtualization platform
- All contributors and users of this project

## Changelog

### v1.0.3
- ✨ Added configuration management with `--config` option
- ✨ Added command-line help and startup information
- ✨ Improved error handling and user feedback
- ✨ Added configurable update interval
- 📚 Updated installation options (pipx support)

### v1.0.2
- 🐛 Bug fixes and stability improvements
- 📚 Documentation updates

### v1.0.1
- 🚀 Initial release

---

**Note**: This script is designed for Linux/Unix systems and requires Discord to be running for Rich Presence to work.

For support, please open an issue on [GitHub](https://github.com/qubixq/qemu-discord-rpc/issues).
