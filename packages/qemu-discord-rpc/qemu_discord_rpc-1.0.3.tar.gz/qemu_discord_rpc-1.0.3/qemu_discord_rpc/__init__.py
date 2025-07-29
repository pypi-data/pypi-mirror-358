import time
import subprocess
import re
import json
import os
import sys
import argparse
from pypresence import Presence

CONFIG_FILE = "config.json"
VERSION = "1.0.3"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def ask_for_client_id():
    client_id = input("Enter your Discord Application Client ID: ").strip()
    return client_id

def open_config_editor():
    """Open config file in nano editor"""
    if not os.path.exists(CONFIG_FILE):
        print("Config file doesn't exist. Creating a default one...")
        default_config = {
            "client_id": "",
            "update_interval": 15,
            "app_name": "QEMU VM"
        }
        save_config(default_config)

    try:
        subprocess.run(["nano", CONFIG_FILE])
        print("Config file updated successfully!")
    except FileNotFoundError:
        print("Error: nano editor not found. Please install nano or edit the config.json file manually.")
        print(f"Config file location: {os.path.abspath(CONFIG_FILE)}")
    except Exception as e:
        print(f"Error opening config editor: {e}")

def show_help():
    """Show available commands and usage info"""
    print(f"""
QEMU Discord RPC v{VERSION}

Available commands:
  qemu-discord-rpc          - Start the Discord RPC service
  qemu-discord-rpc --config - Open config editor (nano)
  qemu-discord-rpc --help   - Show this help message
  qemu-discord-rpc --version - Show version information

Configuration:
  Config file: {CONFIG_FILE}

Tips:
  - Make sure your QEMU VMs use the 'guest=' parameter
  - Discord must be running for Rich Presence to work
  - Press Ctrl+C to stop the service

For more information, visit: https://github.com/qubixq/qemu-discord-rpc
""")

def get_running_vms():
    try:
        output = subprocess.check_output(["ps", "aux"], text=True)
        vms = []
        for line in output.splitlines():
            if "qemu" in line:
                match = re.search(r"guest=([^\s,]+)", line)
                if match:
                    vm_name = match.group(1)
                    if vm_name not in vms:
                        vms.append(vm_name)
        return vms
    except Exception as e:
        print(f"Error detecting VMs: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description='QEMU Discord RPC - Display running VMs in Discord')
    parser.add_argument('--config', action='store_true', help='Open config editor')
    parser.add_argument('--version', action='version', version=f'QEMU Discord RPC v{VERSION}')

    args = parser.parse_args()

    if args.config:
        open_config_editor()
        return

    # Show startup info
    print(f"QEMU Discord RPC v{VERSION}")
    print("━" * 40)
    print("Starting Discord Rich Presence service...")
    print("\nAvailable commands:")
    print("  --config  : Edit configuration")
    print("  --help    : Show help")
    print("  Ctrl+C    : Stop service")
    print("━" * 40)

    config = load_config()
    client_id = config.get("client_id")
    update_interval = config.get("update_interval", 15)
    app_name = config.get("app_name", "QEMU VM")

    if not client_id:
        print("\nFirst time setup required!")
        print("You need to create a Discord Application first.")
        print("Visit: https://discord.com/developers/applications")
        print("")
        client_id = ask_for_client_id()
        config["client_id"] = client_id
        config["update_interval"] = update_interval
        config["app_name"] = app_name
        save_config(config)
        print(f"Configuration saved to {CONFIG_FILE}")
        print("Tip: Use 'qemu-discord-rpc --config' to edit settings later")

    try:
        RPC = Presence(client_id)
        RPC.connect()
        print("Connected to Discord successfully!")
    except Exception as e:
        print(f"Failed to connect to Discord: {e}")
        print("Make sure Discord is running and your Client ID is correct.")
        print("Use 'qemu-discord-rpc --config' to update your settings.")
        return

    start_time = None
    current_vm = None

    try:
        print(f"\nMonitoring QEMU VMs (checking every {update_interval}s)...")
        while True:
            running_vms = get_running_vms()
            if running_vms:
                vm_name = running_vms[0]
                if vm_name != current_vm:
                    current_vm = vm_name
                    start_time = time.time()
                    print(f"New VM detected: {vm_name}")

                RPC.update(
                    details=f"{vm_name} VM is running",
                    state=f"Virtualization with {app_name}",
                    start=start_time,
                    large_image="qemu-logo",
                    large_text="QEMU Virtual Machine"
                )
                print(f"Status updated: {vm_name} VM running")
            else:
                if current_vm is not None:
                    current_vm = None
                    start_time = None
                    print("No VMs running, clearing Discord status")
                RPC.clear()

            time.sleep(update_interval)
    except KeyboardInterrupt:
        print("\nStopping QEMU Discord RPC...")
        RPC.clear()
        print("Discord status cleared. Goodbye!")
    except Exception as e:
        print(f"Unexpected error: {e}")
        RPC.clear()

if __name__ == "__main__":
    main()
