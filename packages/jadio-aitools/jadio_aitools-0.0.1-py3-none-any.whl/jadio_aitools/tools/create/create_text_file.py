#!/usr/bin/env python3

import argparse
import sys
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Create a simple text (.txt) file with optional content."
    )
    parser.add_argument("--output", required=True, help="Output .txt file path")
    parser.add_argument("--content", default="Hello, World!", help="Content of the text file")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    
    try:
        args = parser.parse_args()
    except SystemExit:
        print("❌ Error [1]: Invalid or missing arguments", file=sys.stderr)
        sys.exit(1)

    content = f"{args.content}\n"

    try:
        out_path = Path(args.output)
        out_path.write_text(content, encoding="utf-8")

        if args.json:
            result = {
                "status": "success",
                "path": str(out_path),
                "content": args.content
            }
            print(json.dumps(result))
        else:
            print(f"✅ Created text file at {out_path}")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Error [2]: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
