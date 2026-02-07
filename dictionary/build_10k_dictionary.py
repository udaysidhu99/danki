#!/usr/bin/env python3
"""
Build a 10,000-word German-English dictionary using OpenAI API with resume capability.
Handles capitalization variants and can restart from where it left off.
"""

import json
import time
import requests
import sys
import os
from pathlib import Path

# Configuration
RATE_LIMIT_DELAY = 2  # seconds between requests per worker (OpenAI has higher limits)
CHECKPOINT_INTERVAL = 50  # save progress every N words

def load_word_list(filepath, start_idx=0, count=None):
    """Load words from frequency list."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    words = []
    for line in lines[start_idx:]:
        parts = line.strip().split()
        if parts:
            word = parts[0]
            words.append(word)
            if count and len(words) >= count:
                break
    
    return words

def query_openai(word, api_key):
    """Query OpenAI API for word translation and details."""
    endpoint = "https://api.openai.com/v1/chat/completions"
    
    prompt = (
        f"You are a German language expert. Analyze the word: '{word}'\n\n"
        "FIRST: Determine if this is a valid German word or just a name/foreign word/nonsense.\n"
        "- If it's a proper name (person, place, brand): Return {\"skip\": true, \"reason\": \"proper name\"}\n"
        "- If it's an English/foreign word not used in German: Return {\"skip\": true, \"reason\": \"foreign word\"}\n"
        "- If it's nonsense/gibberish: Return {\"skip\": true, \"reason\": \"not a word\"}\n"
        "- If it's a valid German word: Continue with analysis below.\n\n"
        "SECOND: If the word is a CONJUGATED VERB (like 'sagte', 'macht', 'ging'), convert to INFINITIVE form (sagen, machen, gehen).\n"
        "- Process the infinitive form, not the conjugated form\n"
        "- The 'word' field in the response should be the infinitive\n"
        "- Examples: 'sagte' → process 'sagen', 'macht' → process 'machen', 'geht' → process 'gehen'\n\n"
        "For VALID German words (using infinitive if verb), analyze if they have different meanings when capitalized vs lowercase.\n\n"
        "IMPORTANT: If the word has different meanings based on capitalization, return BOTH entries.\n"
        "For example:\n"
        "- 'essen' (lowercase verb) AND 'Essen' (capitalized noun 'das Essen' = food)\n"
        "- 'lesen' (lowercase verb) AND 'Lesen' (capitalized noun 'das Lesen' = reading)\n\n"
        "Return a JSON object:\n"
        "- If skip: {\"skip\": true, \"reason\": \"...\"}\n"
        "- If valid: {\"skip\": false, \"variants\": [...]}\n\n"
        "Each variant in the array has:\n"
        "1. word: The German word (with correct capitalization)\n"
        "2. translation: English translation(s)\n"
        "3. gender: For nouns only: 'masculine', 'feminine', 'neuter', or null\n"
        "4. verb_forms: For verbs only, object with present_ich, present_du, present_er, past_ich, past_du, past_er, perfect. Use null if not a verb.\n"
        "5. example1: A natural German sentence using the word\n"
        "6. example1_translation: English translation of example1\n"
        "7. example2: Second example (can be empty string)\n"
        "8. example2_translation: English translation of example2 (can be empty string)\n"
        "9. example3: Third example (can be empty string)\n"
        "10. example3_translation: English translation of example3 (can be empty string)\n\n"
        "Example for proper name 'John': {\"skip\": true, \"reason\": \"proper name\"}\n"
        "Example for valid word 'essen':\n"
        "{\n"
        '  "skip": false,\n'
        '  "variants": [\n'
        "    {\n"
        '      "word": "essen",\n'
        '      "translation": "to eat",\n'
        '      "gender": null,\n'
        '      "verb_forms": {"present_ich": "esse", "present_du": "isst", "present_er": "isst", "past_ich": "aß", "past_du": "aßt", "past_er": "aß", "perfect": "hat gegessen"},\n'
        '      "example1": "Ich esse gern Pizza.",\n'
        '      "example1_translation": "I like to eat pizza."\n'
        "    },\n"
        "    {\n"
        '      "word": "Essen",\n'
        '      "translation": "food, meal",\n'
        '      "gender": "neuter",\n'
        '      "verb_forms": null,\n'
        '      "example1": "Das Essen ist lecker.",\n'
        '      "example1_translation": "The food is delicious."\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Return only valid JSON, no other text."
    )
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a German language expert. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=body, timeout=30)
        result = response.json()
        
        if "choices" not in result:
            # Log the error for debugging
            if "error" in result:
                print(f"API Error: {result['error']}", file=sys.stderr)
            return None
        
        content = result["choices"][0]["message"]["content"]
        data = json.loads(content)
        
        # Check if LLM says to skip this word
        if data.get("skip", False):
            return {"skip": True, "reason": data.get("reason", "unknown")}
        
        # Return the variants array (could be 1 or 2 entries)
        return {"skip": False, "variants": data.get("variants", [])}
        
    except Exception as e:
        print(f"Exception in query_openai for word '{word}': {e}", file=sys.stderr)
        return None

def load_checkpoint(worker_id):
    """Load progress checkpoint if exists."""
    checkpoint_file = f"checkpoint_worker_{worker_id}.json"
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed": [], "dictionary": {}}

def save_checkpoint(worker_id, processed, dictionary):
    """Save progress checkpoint."""
    checkpoint_file = f"checkpoint_worker_{worker_id}.json"
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump({
            "processed": processed,
            "dictionary": dictionary
        }, f, ensure_ascii=False)

def build_worker_chunk(worker_id, words, api_key, output_file):
    """Build dictionary for a chunk of words with resume capability."""
    log_file = f"german_english_dict_10k_worker_{worker_id}.log"
    
    # Load checkpoint
    checkpoint = load_checkpoint(worker_id)
    processed_words = set(checkpoint["processed"])
    dictionary = checkpoint["dictionary"]
    
    resume_count = len(processed_words)
    
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write("=" * 60 + "\n")
        log.write(f"German-English Dictionary Builder - Worker {worker_id}\n")
        log.write("=" * 60 + "\n")
        log.write(f"Total words: {len(words)}\n")
        log.write(f"Output: {output_file}\n")
        log.write(f"Rate limit: {RATE_LIMIT_DELAY}s between requests\n")
        if resume_count > 0:
            log.write(f"RESUMING: {resume_count} words already processed\n")
        log.write("\n")
    
    print(f"Worker {worker_id} starting: {len(words)} words -> {output_file}")
    if resume_count > 0:
        print(f"  Resuming from word {resume_count}")
    
    processed = 0
    start_time = time.time()
    
    for idx, word in enumerate(words, 1):
        # Skip if already processed
        if word in processed_words:
            continue
        
        # Process word - may return multiple variants or skip instruction
        result = query_openai(word, api_key)
        
        if not result:
            # API error - do NOT mark as processed, will retry later
            status = "✗ (API error)"
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(f"[{idx}/{len(words)}] Processing: {word}... {status}\n")
        elif result.get("skip", False):
            # LLM says skip this word (name, foreign word, etc.)
            reason = result.get("reason", "unknown")
            status = f"⊘ (skipped: {reason})"
            processed_words.add(word)  # Mark as processed so we don't retry skipped words
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(f"[{idx}/{len(words)}] Processing: {word}... {status}\n")
        else:
            # Valid German word(s)
            variants = result.get("variants", [])
            if len(variants) > 0:
                # Add all variants to dictionary
                for variant in variants:
                    variant_word = variant.get("word", word)
                    dictionary[variant_word] = variant
                    processed_words.add(variant_word)
                
                status = f"✓ ({len(variants)} variant{'s' if len(variants) > 1 else ''})"
                
                # Log all variants
                with open(log_file, 'a', encoding='utf-8') as log:
                    log.write(f"[{idx}/{len(words)}] Processing: {word}... {status}\n")
                    for variant in variants:
                        variant_word = variant.get("word", word)
                        if variant_word != word:
                            log.write(f"    └─ Added variant: {variant_word}\n")
            else:
                status = "✗ (no variants)"
                with open(log_file, 'a', encoding='utf-8') as log:
                    log.write(f"[{idx}/{len(words)}] Processing: {word}... {status}\n")
        
        processed_words.add(word)  # Mark original word as processed
        processed += 1
        
        # Log progress every 10 words
        if idx % 10 == 0:
            with open(log_file, 'a', encoding='utf-8') as log:
                elapsed = time.time() - start_time
                rate = processed / (elapsed / 60) if elapsed > 0 else 0
                remaining = len(words) - len(processed_words)
                eta = (remaining / rate) if rate > 0 else 0
                log.write(f"  Progress: {len(processed_words)}/{len(words)} ({100*len(processed_words)/len(words):.1f}%) | "
                         f"Rate: {rate:.1f} words/min | ETA: {eta:.1f} min\n")
        
        # Save checkpoint periodically
        if processed % CHECKPOINT_INTERVAL == 0:
            save_checkpoint(worker_id, list(processed_words), dictionary)
        
        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)
    
    # Final save
    output_data = {"dictionary": dictionary}
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    # Remove checkpoint
    checkpoint_file = f"checkpoint_worker_{worker_id}.json"
    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)
    
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f"\n{'=' * 60}\n")
        log.write(f"Worker {worker_id} completed: {len(dictionary)} words processed\n")
        log.write(f"Output saved to: {output_file}\n")
        log.write(f"{'=' * 60}\n")
    
    print(f"Worker {worker_id} completed: {len(dictionary)} words")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build_10k_dictionary.py <worker_id> <api_key>")
        sys.exit(1)
    
    worker_id = int(sys.argv[1])
    api_key = sys.argv[2]
    
    # Load all 10k words
    word_list_path = "de_50k.txt"
    all_words = load_word_list(word_list_path, start_idx=0, count=10000)
    
    # Divide among workers (8 workers for 8 API keys)
    num_workers = 8
    words_per_worker = len(all_words) // num_workers
    start_idx = (worker_id - 1) * words_per_worker
    end_idx = start_idx + words_per_worker if worker_id < num_workers else len(all_words)
    
    words = all_words[start_idx:end_idx]
    output_file = f"german_english_dict_10k_part_{worker_id}.json"
    
    build_worker_chunk(worker_id, words, api_key, output_file)
