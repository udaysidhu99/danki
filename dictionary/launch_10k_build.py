#!/usr/bin/env python3
"""
Launch 8 parallel workers to build a 10,000-word German-English dictionary using OpenAI.
Automatically extracts API keys from apikeys.txt.rtf file.
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
    print("German-English Dictionary Builder - 10,000 Words (OpenAI)")
    print("=" * 70)
    print()
    
    # Extract API keys from file
    apikeys_file = "../apikeys.txt.rtf"
    api_keys = extract_openai_keys(apikeys_file)
    
    if not api_keys:
        print("❌ No OpenAI API keys found in apikeys.txt.rtf")
        print("Please add OpenAI API keys to the file (format: sk-proj-...)")
        return
    
    print(f"✓ Found {len(api_keys)} OpenAI API keys")
    print()
    print("Configuration:")
    print(f"  - Total words: 10,000")
    print(f"  - Workers: {len(api_keys)}")
    print(f"  - Words per worker: ~{10000 // len(api_keys)}")
    print(f"  - Capitalization variants: Yes (adds extra entries)")
    print(f"  - Resume capability: Yes (auto-resumes if interrupted)")
    print()
    print("Estimated time: 1-2 hours (OpenAI is faster than Gemini)")
    print()
    print("Monitor progress with:")
    print("  tail -f german_english_dict_10k_worker_*.log")
    print()
    
    # Confirm before starting
    response = input("Start building dictionary? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    print()
    print(f"Starting {len(api_keys)} workers...")
    print()
    
    # Launch workers
    processes = []
    for i, api_key in enumerate(api_keys, 1):
        cmd = [sys.executable, "build_10k_dictionary.py", str(i), api_key]
        # Capture stderr to error log file
        error_log = open(f"german_english_dict_10k_worker_{i}_errors.log", 'w')
        proc = subprocess.Popen(cmd, stderr=error_log)
        processes.append((proc, error_log))
        print(f"✓ Worker {i} launched (PID: {proc.pid})")
    
    print()
    print("All workers running in background!")
    print("They will continue even if you close this terminal.")
    print()
    print("Useful commands:")
    print("  Check status:  ps aux | grep build_10k_dictionary")
    print("  Monitor logs:  tail -f german_english_dict_10k_worker_*.log")
    print("  Stop all:      pkill -f build_10k_dictionary")
    print()
    print("Each worker saves checkpoints every 50 words.")
    print("If interrupted, just run this script again - workers will resume!")
    print()

if __name__ == "__main__":
    main()
