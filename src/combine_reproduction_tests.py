import os
import json
import argparse
import sys
from glob import glob
from collections import defaultdict

def load_entries(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError(f"{path}: JSON must be an object or array")

def combine_patches(input_dir, dedup=False):
    if dedup:
        combined = defaultdict(set)
    else:
        combined = defaultdict(list)

    # normal JSON files
    json_paths = sorted(glob(os.path.join(input_dir, "*.json")))
    # exclude reproduction_tests.jsonl if misnamed
    json_paths = [p for p in json_paths if not p.endswith("reproduction_tests.jsonl")]

    if not json_paths and not os.path.isfile(os.path.join(input_dir, "reproduction_tests.jsonl")):
        raise SystemExit(f"No JSON or JSONL files found in: {input_dir}")

    for p in json_paths:
        try:
            for entry in load_entries(p):
                inst = entry.get("instance_id")
                patch = entry.get("model_patch")
                if not inst or not patch:
                    continue
                if dedup:
                    combined[inst].add(patch)
                else:
                    combined[inst].append(patch)
        except Exception as e:
            print(f"Warning: skipping {p}: {e}", file=sys.stderr)

    # extra step: handle reproduction_tests.jsonl if present
    repro_path = os.path.join(input_dir, "reproduction_tests.jsonl")
    if os.path.isfile(repro_path):
        with open(repro_path, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception as e:
                    print(f"Warning: skipping line {lineno} in {repro_path}: {e}", file=sys.stderr)
                    continue
                inst = obj.get("instance_id")
                patch = obj.get("test_patch")  # note: different field
                if not inst or not patch:
                    continue
                if dedup:
                    combined[inst].add(patch)
                else:
                    combined[inst].append(patch)

    if dedup:
        return {k: list(v) for k, v in combined.items()}
    return combined

def main():
    parser = argparse.ArgumentParser(
        description="Combine patches from multiple JSON files into a single JSON grouped by instance_id."
    )
    parser.add_argument("input_dir", help="Directory containing JSON files (and optionally reproduction_tests.jsonl)")
    parser.add_argument("output_file", help="Path to write combined JSON output")
    parser.add_argument(
        "--dedup", action="store_true",
        help="Remove duplicate patches per instance_id"
    )
    args = parser.parse_args()

    combined = combine_patches(args.input_dir, dedup=args.dedup)

    with open(args.output_file, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)

    print(f"Wrote {args.output_file} with {len(combined)} instances.")

if __name__ == "__main__":
    main()
