#!/usr/bin/env python3

import argparse
import sys
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Create a new HTML file with an optional title."
    )
    parser.add_argument("--output", required=True, help="Output HTML file path")
    parser.add_argument("--title", default="New Page", help="HTML <title> content")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    
    try:
        args = parser.parse_args()
    except SystemExit:
        print("❌ Error [1]: Invalid or missing arguments", file=sys.stderr)
        sys.exit(1)

    html_content = f"""<!DOCTYPE html>
<html>
  <head>
    <title>{args.title}</title>
  </head>
  <body>
  </body>
</html>"""

    try:
        out_path = Path(args.output)
        out_path.write_text(html_content, encoding="utf-8")
        
        if args.json:
            result = {
                "status": "success",
                "path": str(out_path),
                "title": args.title
            }
            print(json.dumps(result))
        else:
            print(f"✅ Created HTML file at {out_path}")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Error [2]: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
