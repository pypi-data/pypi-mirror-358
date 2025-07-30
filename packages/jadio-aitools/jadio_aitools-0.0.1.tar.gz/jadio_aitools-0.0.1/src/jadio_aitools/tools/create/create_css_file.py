#!/usr/bin/env python3

import argparse
import sys
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Create a new CSS file with a starter style."
    )
    parser.add_argument("--output", required=True, help="Output .css file path")
    parser.add_argument("--name", default="MainStyle", help="Name of the stylesheet")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    
    try:
        args = parser.parse_args()
    except SystemExit:
        print("❌ Error [1]: Invalid or missing arguments", file=sys.stderr)
        sys.exit(1)

    content = f"""/* {args.name} stylesheet */
body {{
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
}}
"""

    try:
        out_path = Path(args.output)
        out_path.write_text(content, encoding="utf-8")
        
        if args.json:
            result = {
                "status": "success",
                "path": str(out_path),
                "name": args.name
            }
            print(json.dumps(result))
        else:
            print(f"✅ Created CSS file at {out_path}")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Error [2]: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
