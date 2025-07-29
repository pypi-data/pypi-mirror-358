import json
from pathlib import Path

CONFIG_PATH = Path("JdoLabsData/aiserver_config.json")

def get_active_mode():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("❌ aiserver_config.json not found in JdoLabsData.")

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        config = json.load(f)

    mode = config.get("mode", "").strip().lower()
    if mode not in ("chat", "agent", "image"):
        raise ValueError(f"❌ Invalid mode in config: '{mode}'")

    print(f"🔍 Current mode: {mode}")
    return mode
