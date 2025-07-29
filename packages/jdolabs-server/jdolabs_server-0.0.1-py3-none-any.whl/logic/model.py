import json
from pathlib import Path

CONFIG_PATH = Path("JdoLabsData/aiserver_config.json")
DATA_PATH = Path("JdoLabsData")

def assign_model(model_path: str, port: int, types: list):
    # Extract model name from file
    model_file = Path(model_path).name
    model_name = model_file.rsplit(".", 1)[0]  # removes .gguf, .safetensors, etc
    profile_filename = f"{model_name}profile.json"
    profile_path = DATA_PATH / profile_filename

    # Create model profile JSON
    profile = {
        "profile": model_name,
        "name": "",
        "types": types,
        "tools": [],
        "assignedport": port,
        "logic": [],
        "source_dir": str(Path(model_path).resolve())
    }

    DATA_PATH.mkdir(exist_ok=True)
    with profile_path.open("w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
    print(f"✅ Model profile created: {profile_filename}")

    # Update aiserver_config.json
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {}

    assigned = config.get("assignedports", [])
    if port not in assigned:
        assigned.append(port)
        config["assignedports"] = assigned

    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print(f"📦 Port {port} assigned and saved to aiserver_config.json")
