import requests
import json
import re

# ===== CONFIG =====
API_KEY = "AIzaSyDbSs1PM7jYzIuO4WroY_cMBGWlwYspO1Q"
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
ANKI_ENDPOINT = "http://localhost:8765"
DECK_NAME = "New test deck"
NOTE_TYPE = "German Auto "  # ← has a trailing space

# ===== GEMINI INTEGRATION =====
def query_gemini(word):
    prompt = f"""
You are a helpful German language assistant. For the word: **{word}**, provide the following details:

1. English meaning
2. Article (if noun)
3. Plural form (if noun)
4. Conjugation for verbs: just one representative form each from **Präsens**, **Präteritum**, and **Perfekt** (e.g., "macht ab, machte ab, hat abgemacht")
5. One natural example sentence

Reply in JSON format like this (inside a ```json code block):
{{
  "base_d": "",
  "base_e": "",
  "artikel_d": "",
  "plural_d": "",
  "full_d": "",
  "s1e": ""
}}
"""

    headers = {
        'Content-Type': 'application/json'
    }

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_ENDPOINT, headers=headers, json=body)
        result = response.json()
        content = result["candidates"][0]["content"]["parts"][0]["text"]

        # Extract JSON from markdown code block
        match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
        if not match:
            raise ValueError("❌ JSON code block not found in Gemini response.")
        parsed = json.loads(match.group(1))

        # Ensure full_d is a string
        if isinstance(parsed.get("full_d"), dict):
            forms = parsed["full_d"]
            parsed["full_d"] = ", ".join([
                forms.get("Präsens", ""),
                forms.get("Präteritum", ""),
                forms.get("Perfekt", "")
            ])

        return parsed

    except Exception as e:
        print("❌ Error querying Gemini:", e)
        return None

# ===== ANKI INTEGRATION =====
def add_to_anki(parsed_word: dict):
    if not parsed_word:
        print("⚠️ No data to add to Anki.")
        return

    # Ensure all values are strings (AnkiConnect requirement)
    fields = {
        "base_d": str(parsed_word.get("base_d", "") or ""),
        "base_e": str(parsed_word.get("base_e", "") or ""),
        "artikel_d": str(parsed_word.get("artikel_d", "") or ""),
        "plural_d": str(parsed_word.get("plural_d", "") or ""),
        "full_d": str(parsed_word.get("full_d", "") or ""),
        "audio_text_d": str(parsed_word.get("full_d", "") or ""),
        "e": str(parsed_word.get("s1e", "") or "")
    }

    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": DECK_NAME,
                "modelName": NOTE_TYPE,
                "fields": fields,
                "options": {
                    "allowDuplicate": False
                },
                "tags": ["auto-added"]
            }
        }
    }

    try:
        response = requests.post(ANKI_ENDPOINT, json=payload)
        result = response.json()
        if result.get("error") is None:
            print(f"✅ Note for '{fields['base_d']}' added to Anki successfully.")
        else:
            print(f"❌ Anki Error: {result['error']}")
    except Exception as e:
        print("❌ Error communicating with AnkiConnect:", e)
# ===== MAIN WORKFLOW =====
if __name__ == "__main__":
    word = input("🔤 Enter a German word: ").strip()
    print("\n📡 Querying Gemini...")
    data = query_gemini(word)

    if data:
        print("\n📝 Parsed Result:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("\n📬 Sending to Anki...")
        add_to_anki(data)
    else:
        print("❌ Failed to retrieve or parse Gemini output.")