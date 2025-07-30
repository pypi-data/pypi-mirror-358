#!/usr/bin/env python3

import argparse
import sys
import json
from pathlib import Path

QUEUE_PATH = Path("jadio_config/promptqueue.json")
STATE_PATH = Path("jadio_config/promptqueue_state.json")


def load_json(path):
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Outputs the next prompt from the prompt queue."
    )
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    # Load prompt queue
    queue_data = load_json(QUEUE_PATH)
    if not queue_data or "queue" not in queue_data or not isinstance(queue_data["queue"], list):
        err = "❌ Error [1]: No valid promptqueue.json found"
        if args.json:
            print(json.dumps({"error": "No valid promptqueue.json found"}))
        else:
            print(err, file=sys.stderr)
        sys.exit(1)

    queue = queue_data["queue"]

    # Load state
    state_data = load_json(STATE_PATH)
    if not state_data or "index" not in state_data:
        # If missing or invalid, assume fresh start
        state_data = {"index": 0}

    index = state_data["index"]

    # Check if finished
    if index >= len(queue):
        msg = "✅ Prompt queue completed"
        if args.json:
            print(json.dumps({"status": "done"}))
        else:
            print(msg)
        sys.exit(0)

    # Get next prompt
    next_prompt = queue[index]

    # Increment state
    state_data["index"] = index + 1
    save_json(STATE_PATH, state_data)

    # Output next prompt
    if args.json:
        print(json.dumps({"prompt": next_prompt}))
    else:
        print(f"Next prompt:\n{next_prompt}")

    sys.exit(0)


if __name__ == "__main__":
    main()
