import time
import subprocess
import re
import json
import os
from pypresence import Presence

CONFIG_FILE = "config.json"

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
        print(f"Error: {e}")
        return []

def main():
    config = load_config()
    client_id = config.get("client_id")

    if not client_id:
        client_id = ask_for_client_id()
        config["client_id"] = client_id
        save_config(config)
        print(f"Client ID saved to {CONFIG_FILE}.")

    RPC = Presence(client_id)
    RPC.connect()

    start_time = None
    current_vm = None

    try:
        while True:
            running_vms = get_running_vms()
            if running_vms:
                vm_name = running_vms[0]
                if vm_name != current_vm:
                    current_vm = vm_name
                    start_time = time.time()
                RPC.update(
                    details=f"{vm_name} VM is running",
                    start=start_time
                )
                print(f"{vm_name} is running, presence updated.")
            else:
                if current_vm is not None:
                    current_vm = None
                    start_time = None
                RPC.clear()
                print("No running VMs, presence cleared.")
            time.sleep(15)
    except KeyboardInterrupt:
        print("Exiting...")
        RPC.clear()

if __name__ == "__main__":
    main()
