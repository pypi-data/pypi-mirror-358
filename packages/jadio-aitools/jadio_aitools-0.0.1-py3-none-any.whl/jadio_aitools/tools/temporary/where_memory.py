#!/usr/bin/env python3

import argparse
import sys
import json
from pathlib import Path

CONFIG_PATH = Path("jadio_config/temporary_memory_config.json")

def main():
    parser = argparse.ArgumentParser(
        description="Output the path to the temporary memory folder."
    )
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    
    try:
        args = parser.parse_args()
    except SystemExit:
        print("❌ Error [1]: Invalid arguments", file=sys.stderr)
        sys.exit(1)

    if not CONFIG_PATH.exists():
        msg = "❌ Error [1]: Config file not found"
        if args.json:
            print(json.dumps({"error": "Config file not found"}))
        else:
            print(msg, file=sys.stderr)
        sys.exit(1)

    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        path = config.get("path")
        if not path:
            raise ValueError("Missing 'path' in config")

        if args.json:
            print(json.dumps({"path": path}))
        else:
            print(path)

        sys.exit(0)

    except Exception as e:
        msg = f"❌ Error [1]: {e}"
        if args.json:
            print(json.dumps({"error": str(e)}))
        else:
            print(msg, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
