#!/usr/bin/env python3

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(
        description="Create a LICENSE file with optional type, holder, year."
    )
    parser.add_argument("--output", required=True, help="Output LICENSE file path")
    parser.add_argument("--type", default="MIT", help="License type (default: MIT)")
    parser.add_argument("--holder", default="Your Name", help="Copyright holder")
    parser.add_argument("--year", default=str(datetime.now().year), help="Year")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    
    try:
        args = parser.parse_args()
    except SystemExit:
        print("❌ Error [1]: Invalid or missing arguments", file=sys.stderr)
        sys.exit(1)

    content = f"""{args.type} License

Copyright (c) {args.year} {args.holder}

Permission is hereby granted, free of charge, to any person obtaining a copy...
"""

    try:
        out_path = Path(args.output)
        out_path.write_text(content, encoding="utf-8")

        if args.json:
            result = {
                "status": "success",
                "path": str(out_path),
                "type": args.type,
                "holder": args.holder,
                "year": args.year
            }
            print(json.dumps(result))
        else:
            print(f"✅ Created LICENSE file at {out_path}")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Error [2]: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
