import os
import time
import json
from pathlib import Path

# Path to the persistent config file
CONFIG_PATH = Path("JdoLabsData/aiserver_config.json")

# Load the server config from JSON
def get_config():
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Write this process's PID to disk
def write_pid():
    data_path = Path("JdoLabsData")
    data_path.mkdir(exist_ok=True)
    pid_path = data_path / "aiserver.pid"
    pid_path.write_text(str(os.getpid()))
    print(f"🆔 PID written to {pid_path}")

# Main loop: simulate persistent background process
def run_core():
    cfg = get_config()

    port = cfg.get("port", 47800)
    autostart = cfg.get("autostart", False)
    leave_on = cfg.get("leave_on", True)

    print(f"🚀 AI Server initialized on port {port}")
    print(f"🧠 Autostart: {autostart} | Leave-on: {leave_on}")

    write_pid()

    print("🟢 Server running in passive mode. Awaiting model instructions...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("❌ Shutdown requested.")
        pid_file = Path("JdoLabsData/aiserver.pid")
        pid_file.unlink(missing_ok=True)
