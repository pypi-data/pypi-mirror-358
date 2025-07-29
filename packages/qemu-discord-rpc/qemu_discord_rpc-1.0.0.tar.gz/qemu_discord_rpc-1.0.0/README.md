# QEMU Discord RPC

A Python script that displays your running QEMU virtual machines as Discord Rich Presence status.

## Features

- 🖥️ Automatically detects running QEMU virtual machines
- 🎮 Shows VM status on your Discord profile
- ⏱️ Displays how long the VM has been running
- 🔄 Real-time updates every 15 seconds
- 💾 Saves Discord application settings locally
- 🚀 Lightweight and easy to use

## Prerequisites

- Python 3.6 or higher
- Discord application
- QEMU virtual machines
- Linux/Unix system (uses `ps aux` command)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/qubixq/qemu-discord-rpc.git
cd qemu-discord-rpc
```

2. Install required dependencies:
```bash
pip install pypresence
```

## Setup

### 1. Create a Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name (e.g., "QEMU VM Status")
3. Copy the **Application ID** (Client ID) from the General Information page
4. You can also upload a custom icon for your application

### 2. Configure the Script

1. Run the script for the first time:
```bash
python qemu_discord_rpc.py
```

2. When prompted, enter your Discord Application Client ID
3. The script will save this ID to `config.json` for future use

## Usage

Simply run the script while your QEMU virtual machines are running:

```bash
python qemu_discord_rpc.py
```

The script will:
- Detect running QEMU VMs by looking for `guest=` parameter in process list
- Update your Discord status to show the VM name and runtime
- Continue monitoring until you stop it with `Ctrl+C`

### Example Discord Status
```
🖥️ Playing QEMU VM
Windows-11 VM is running
Started 25 minutes ago
```

## Configuration

The script creates a `config.json` file to store your Discord Application Client ID:

```json
{
    "client_id": "your_discord_application_id_here"
}
```

You can manually edit this file if needed, or delete it to reconfigure.

## How It Works

1. **VM Detection**: Uses `ps aux` to find QEMU processes
2. **Name Extraction**: Parses the `guest=` parameter from QEMU command line
3. **Discord RPC**: Uses pypresence library to communicate with Discord
4. **Status Updates**: Updates every 15 seconds, clears when no VMs are running

## Requirements

- `pypresence` - Discord Rich Presence library for Python

Install with:
```bash
pip install pypresence
```

## Troubleshooting

### Script doesn't detect VMs
- Ensure your QEMU command includes the `guest=` parameter
- Check that QEMU processes are visible with `ps aux | grep qemu`

### Discord status not showing
- Make sure Discord is running and you're logged in
- Verify your Discord Application Client ID is correct
- Check that your Discord privacy settings allow Rich Presence

### Multiple VMs
- Currently shows only the first detected VM
- Feel free to modify the script for multiple VM support

## Contributing

Contributions are welcome! Please feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [pypresence](https://github.com/qwertyquerty/pypresence) - Discord RPC library
- QEMU community for the amazing virtualization platform

---

**Note**: This script is designed for Linux/Unix systems.
