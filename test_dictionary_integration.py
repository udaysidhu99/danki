#!/usr/bin/env python3
"""
Test the dictionary integration in danki_app.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test imports
print("Testing imports...")
from danki_app import load_offline_dictionary, lookup_word_in_dictionary, convert_dict_to_anki_format, GERMAN_DICT

print("\n" + "="*60)
print("Dictionary Integration Test")
print("="*60)

# Test 1: Load dictionary
print("\n1. Loading dictionary...")
success = load_offline_dictionary()
if success:
    print(f"   ✅ Dictionary loaded: {len(GERMAN_DICT)} words")
else:
    print("   ❌ Dictionary failed to load")
    sys.exit(1)

# Test 2: Lookup existing word
print("\n2. Testing word lookup (existing word)...")
test_words = ["ich", "sein", "haben", "gehen", "gut"]
for word in test_words:
    result = lookup_word_in_dictionary(word)
    if result:
        print(f"   ✅ '{word}' found: {result.get('translation', 'N/A')}")
    else:
        print(f"   ⚠️  '{word}' not found")

# Test 3: Lookup non-existing word
print("\n3. Testing word lookup (non-existing word)...")
result = lookup_word_in_dictionary("xyzabc123")
if result is None:
    print("   ✅ Correctly returned None for non-existing word")
else:
    print("   ❌ Should have returned None")

# Test 4: Case sensitivity
print("\n4. Testing case sensitivity...")
# Test lowercase
result_lower = lookup_word_in_dictionary("essen")
# Test capitalized (if it exists)
result_upper = lookup_word_in_dictionary("Essen")

if result_lower:
    print(f"   'essen' found: {result_lower.get('translation', 'N/A')}")
if result_upper:
    print(f"   'Essen' found: {result_upper.get('translation', 'N/A')}")
if result_lower or result_upper:
    print("   ✅ Case handling working")

# Test 5: Convert to Anki format
print("\n5. Testing Anki format conversion...")
test_entry = lookup_word_in_dictionary("ich")
if test_entry:
    anki_format = convert_dict_to_anki_format(test_entry, "ich")
    print(f"   ✅ Converted to Anki format:")
    print(f"      base_d: {anki_format.get('base_d')}")
    print(f"      base_e: {anki_format.get('base_e')}")
    print(f"      s1: {anki_format.get('s1', 'N/A')[:50]}...")
    print(f"      s1e: {anki_format.get('s1e', 'N/A')[:50]}...")

# Test 6: Sample words
print("\n6. Sample dictionary entries:")
sample_count = 5
for i, (word, data) in enumerate(list(GERMAN_DICT.items())[:sample_count]):
    print(f"\n   {i+1}. Word: {word}")
    print(f"      Normalized: {data.get('word', 'N/A')}")
    print(f"      Translation: {data.get('translation', 'N/A')}")
    print(f"      Part of speech: {data.get('part_of_speech', 'N/A')}")

print("\n" + "="*60)
print("Test Complete!")
print("="*60)
