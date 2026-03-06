#!/usr/bin/env python3
"""
Launch parallel workers to build the NEXT 10,000-word German-English dictionary (words 10,001-20,000).
Automatically extracts API keys from apikeys.txt.rtf file.
Number of workers = number of API keys found.
"""

import subprocess
import sys
import re
import os

def extract_openai_keys(filepath):
    """Extract OpenAI API keys from RTF file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract sk-proj- keys (OpenAI project keys)
        keys = re.findall(r'sk-proj-[A-Za-z0-9_-]+', content)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keys = []
        for key in keys:
            if key not in seen:
                seen.add(key)
                unique_keys.append(key)
        
        return unique_keys
    except Exception as e:
        print(f"Error reading API keys file: {e}")
        return []

def main():
    print("=" * 70)
    print("German-English Dictionary Builder - NEXT 10,000 Words (OpenAI)")
    print("Words 10,001 - 20,000 from de_50k.txt")
    print("=" * 70)
    print()
    
    # Extract API keys from file
    apikeys_file = "../apikeys.txt.rtf"
    api_keys = extract_openai_keys(apikeys_file)
    
    if not api_keys:
        print("❌ No OpenAI API keys found in apikeys.txt.rtf")
        print("Please add OpenAI API keys to the file (format: sk-proj-...)")
        return
    
    num_workers = len(api_keys)
    
    print(f"✓ Found {num_workers} OpenAI API keys")
    print()
    print("Configuration:")
    print(f"  - Word range: 10,001 - 20,000 from de_50k.txt")
    print(f"  - Total words: 10,000")
    print(f"  - Workers: {num_workers}")
    print(f"  - Words per worker: ~{10000 // num_workers}")
    print(f"  - Capitalization variants: Yes (adds extra entries)")
    print(f"  - Resume capability: Yes (auto-resumes if interrupted)")
    print()
    print("Estimated time: 1-2 hours (OpenAI is faster than Gemini)")
    print()
    print("Monitor progress with:")
    print("  tail -f german_english_dict_next_10k_worker_*.log")
    print("  python3 monitor_next_10k_progress.py")
    print()
    
    # Confirm before starting
    response = input("Start building dictionary? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    print()
    print(f"Starting {num_workers} workers...")
    print()
    
    # Launch workers - pass NUM_WORKERS so each worker knows the total
    env = os.environ.copy()
    env["NUM_WORKERS"] = str(num_workers)
    
    processes = []
    for i, api_key in enumerate(api_keys, 1):
        cmd = [sys.executable, "build_next_10k_dictionary.py", str(i), api_key]
        error_log = open(f"german_english_dict_next_10k_worker_{i}_errors.log", 'w')
        proc = subprocess.Popen(cmd, stderr=error_log, env=env)
        processes.append((proc, error_log))
        print(f"✓ Worker {i} launched (PID: {proc.pid})")
    
    print()
    print("All workers running in background!")
    print("They will continue even if you close this terminal.")
    print()
    print("Useful commands:")
    print(f"  Check status:  ps aux | grep build_next_10k_dictionary")
    print(f"  Monitor logs:  tail -f german_english_dict_next_10k_worker_*.log")
    print(f"  Stop all:      pkill -f build_next_10k_dictionary")
    print()
    print(f"Each worker saves checkpoints every 50 words.")
    print(f"If interrupted, just run this script again - workers will resume!")
    print()
    print(f"When all workers finish, run:")
    print(f"  python3 merge_to_20k.py")
    print()

if __name__ == "__main__":
    main()
