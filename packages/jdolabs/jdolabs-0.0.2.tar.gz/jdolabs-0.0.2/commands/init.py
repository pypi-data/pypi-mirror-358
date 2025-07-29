import os
import json

def run(args):
    os.makedirs(".jdolabs_modules", exist_ok=True)
    os.makedirs("JdoLabsData", exist_ok=True)

    config_path = ".jdolabs_modules/jdolabs_config.json"
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            json.dump({"tools": {}}, f, indent=2)

    print("✅ jdolabs initialized with .jdolabs_modules/ and JdoLabsData/")