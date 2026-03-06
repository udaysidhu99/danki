#!/usr/bin/env python3
"""
Merge the original 10K dictionary + next 10K worker parts into a single 20K dictionary.
Also creates a standalone next_10k merged file for reference.
"""

import json
import os
import sys

def main():
    print("=" * 60)
    print("Merging dictionaries into 20K combined dictionary")
    print("=" * 60)
    print()

    # Step 1: Load the original 10K dictionary
    original_file = "german_english_dict_10k.json"
    if not os.path.exists(original_file):
        print(f"❌ Original dictionary not found: {original_file}")
        sys.exit(1)

    with open(original_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
        original_dict = original_data["dictionary"]

    print(f"✓ Original 10K dictionary: {len(original_dict)} entries")

    # Step 2: Find and merge all next_10k worker part files
    next_10k_merged = {}
    worker_id = 1
    found_parts = 0

    while True:
        part_file = f"german_english_dict_next_10k_part_{worker_id}.json"
        if not os.path.exists(part_file):
            break

        with open(part_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            worker_dict = data["dictionary"]

        count = len(worker_dict)
        next_10k_merged.update(worker_dict)
        print(f"  Worker {worker_id}: {count} entries")
        found_parts += 1
        worker_id += 1

    if found_parts == 0:
        print(f"❌ No next_10k worker part files found (german_english_dict_next_10k_part_*.json)")
        print(f"   Run launch_next_10k_build.py first and wait for workers to complete.")
        sys.exit(1)

    print(f"✓ Next 10K merged from {found_parts} workers: {len(next_10k_merged)} entries")
    print()

    # Step 3: Save standalone next_10k merged file
    next_10k_file = "german_english_dict_next_10k.json"
    with open(next_10k_file, 'w', encoding='utf-8') as f:
        json.dump({"dictionary": next_10k_merged}, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved standalone next 10K: {next_10k_file} ({len(next_10k_merged)} entries)")

    # Step 4: Combine original 10K + next 10K into 20K
    combined = {}
    combined.update(original_dict)

    # Count new vs overlapping
    new_words = 0
    overlap_words = 0
    for word, entry in next_10k_merged.items():
        if word in combined:
            overlap_words += 1
        else:
            new_words += 1
        combined[word] = entry  # next 10K overrides on overlap (fresher data)

    # Step 5: Save the combined 20K dictionary
    output_file = "german_english_dict_20k.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"dictionary": combined}, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 60)
    print(f"✅ Combined dictionary saved: {output_file}")
    print(f"   Original 10K entries:  {len(original_dict)}")
    print(f"   Next 10K entries:      {len(next_10k_merged)}")
    print(f"   Overlapping words:     {overlap_words}")
    print(f"   New words added:       {new_words}")
    print(f"   Total unique entries:  {len(combined)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
