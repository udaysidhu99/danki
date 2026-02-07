#!/usr/bin/env python3
"""
Merge 8 worker checkpoint files into a single German-English dictionary.
"""

import json

print("Merging 8 worker dictionaries...")

merged = {}
stats = {
    "total_entries": 0,
    "per_worker": []
}

for i in range(1, 9):
    part_file = f"german_english_dict_10k_part_{i}.json"
    
    with open(part_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        worker_dict = data["dictionary"]
        
    count = len(worker_dict)
    stats["per_worker"].append(count)
    
    # Merge into main dictionary (later workers override earlier ones if duplicate)
    merged.update(worker_dict)
    
    print(f"  Worker {i}: {count} entries")

stats["total_entries"] = len(merged)

# Save merged dictionary
output_file = "german_english_dict_10k.json"
output_data = {"dictionary": merged}

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Merged dictionary saved: {output_file}")
print(f"   Total unique entries: {stats['total_entries']}")
print(f"   Average per worker: {sum(stats['per_worker']) / 8:.0f}")
