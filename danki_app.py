import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import requests
import json
import re
import os

def save_api_key(api_key):
    with open("gemini_config.json", "w") as f:
        json.dump({"api_key": api_key}, f)

def load_api_key():
    if os.path.exists("gemini_config.json"):
        with open("gemini_config.json") as f:
            return json.load(f).get("api_key")
    return None

# === CONFIG ===
NOTE_TYPE = "German Auto "  # ← trailing space
ANKI_ENDPOINT = "http://localhost:8765"

# === GEMINI QUERY ===
def query_gemini(word):
    global API_KEY
    GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    prompt = f"""
You are a helpful German language assistant. For the word: **{word}**, provide the following details:

1. English meaning
2. Article (if noun)
3. Plural form (if noun)
4. Conjugation for verbs: just one representative form each from **Präsens**, **Präteritum**, and **Perfekt** (e.g., "macht ab, machte ab, hat abgemacht")
5. One natural example sentence (German + English in parentheses)

Reply in JSON format like this (inside a ```json code block):
{{
  "base_d": "",
  "base_e": "",
  "artikel_d": "",
  "plural_d": "",
  "full_d": "",
  "s1": "Wir gehen ins Kino. (We are going to the cinema.)"
}}
"""

    headers = {'Content-Type': 'application/json'}
    body = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        response = requests.post(GEMINI_ENDPOINT, headers=headers, json=body)
        result = response.json()
        if "candidates" not in result:
            return {"error": f"Gemini error: {result.get('error', 'No candidates returned')}"}
        content = result["candidates"][0]["content"]["parts"][0]["text"]

        match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
        if not match:
            raise ValueError("❌ JSON block not found.")
        parsed = json.loads(match.group(1))

        # Extract s1/s1e
        s1_raw = parsed.get("s1", "")
        if "(" in s1_raw and ")" in s1_raw:
            parsed["s1"] = s1_raw.split("(")[0].strip()
            parsed["s1e"] = s1_raw.split("(")[1].rstrip(")").strip()
        else:
            parsed["s1e"] = ""

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
        return {"error": str(e)}

# === ANKI ADD ===
def add_to_anki(parsed_word, deck_name):
    required_fields = ["base_d", "base_e", "s1", "s1e"]
    if (
        not parsed_word or
        "error" in parsed_word or
        any(not str(parsed_word.get(field, "")).strip() for field in required_fields)
    ):
        return False, "❌ Cannot create note: required fields missing or Gemini failed."

    fields = {
        "base_d": str(parsed_word.get("base_d", "") or ""),
        "base_e": str(parsed_word.get("base_e", "") or ""),
        "artikel_d": str(parsed_word.get("artikel_d", "") or ""),
        "plural_d": str(parsed_word.get("plural_d", "") or ""),
        "full_d": parsed_word.get("full_d") if parsed_word.get("full_d") is not None else "",
        "audio_text_d": parsed_word.get("full_d") if parsed_word.get("full_d") is not None else "",
        "s1": str(parsed_word.get("s1", "") or ""),
        "s1e": str(parsed_word.get("s1e", "") or "")
    }

    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deck_name,
                "modelName": NOTE_TYPE,
                "fields": fields,
                "options": {"allowDuplicate": False},
                "tags": ["auto-added"]
            }
        }
    }

    try:
        response = requests.post(ANKI_ENDPOINT, json=payload)
        result = response.json()
        if result.get("error") is None:
            return True, f"Added: {fields['base_d']}"
        else:
            return False, result["error"]
    except Exception as e:
        return False, str(e)

# === FETCH DECKS FROM ANKI ===
def get_anki_decks():
    payload = {"action": "deckNames", "version": 6}
    try:
        response = requests.post(ANKI_ENDPOINT, json=payload)
        return response.json().get("result", [])
    except Exception:
        return []
# === Check for duplicates ===
def is_duplicate(base_d_value):
    query = f'note:"{NOTE_TYPE.strip()}" base_d:"{base_d_value}"'
    payload = {
        "action": "findNotes",
        "version": 6,
        "params": {
            "query": query
        }
    }

    try:
        response = requests.post(ANKI_ENDPOINT, json=payload)
        result = response.json().get("result", [])
        return len(result) > 0
    except Exception:
        return False

# === GUI ===
def run_gui():
    root = tk.Tk()
    root.title("German ↔ Anki Word Adder")

    global API_KEY
    API_KEY = load_api_key()
    if not API_KEY:
        API_KEY = simpledialog.askstring("Gemini API Key", "Enter your Gemini API Key:")
        if not API_KEY:
            messagebox.showerror("Missing API Key", "API key is required to use the app.")
            root.destroy()
            return
        save_api_key(API_KEY)

    # Deck Dropdown
    deck_frame = tk.Frame(root)
    deck_frame.pack()

    tk.Label(deck_frame, text="Select Anki Deck:").pack(side=tk.LEFT)

    deck_var = tk.StringVar()
    deck_list = get_anki_decks()
    deck_menu = ttk.Combobox(deck_frame, textvariable=deck_var, values=deck_list, state="readonly", width=30)
    deck_menu.pack(side=tk.LEFT, padx=5)
    if deck_list:
        deck_var.set(deck_list[0])

    def refresh_decks():
        updated_decks = get_anki_decks()
        deck_menu['values'] = updated_decks
        if updated_decks:
            deck_var.set(updated_decks[0])

    tk.Button(deck_frame, text="🔄 Refresh", command=refresh_decks).pack(side=tk.LEFT)

    # Word input area
    tk.Label(root, text="Enter German words (comma or newline separated):").pack()
    input_text = scrolledtext.ScrolledText(root, width=50, height=8)
    input_text.pack(pady=5)

    # Output log
    output_box = scrolledtext.ScrolledText(root, width=50, height=10, state='disabled')
    output_box.pack(pady=10)

    # Action
    def process_words():
        words_raw = input_text.get("1.0", tk.END)
        selected_deck = deck_var.get()
        words = re.split(r"[,\n]", words_raw)
        words = [w.strip() for w in words if w.strip()]

        output_box.configure(state='normal')
        output_box.delete("1.0", tk.END)

        for word in words:
            output_box.insert(tk.END, f"🔍 Processing: {word}...\n")
            root.update()
            if is_duplicate(word):
                output_box.insert(tk.END, f"⚠️ Skipped duplicate: {word}\n\n")
                continue
            
            # Retry Gemini once if it fails
            for attempt in range(4):
                gemini_data = query_gemini(word)
                if "error" not in gemini_data:
                    break
                print(f"[DEBUG] Gemini failed (attempt {attempt+1}) for '{word}': {gemini_data['error']}")

            if "error" in gemini_data:
                print(f"[DEBUG] Skipping '{word}' due to repeated Gemini failure.\n")
                print(f"[DEBUG] Gemini final response for '{word}':", gemini_data)
                continue

            success, msg = add_to_anki(gemini_data, selected_deck)

            # [DEBUG] Print Gemini output when add_to_anki fails
            if not success:
                print(f"[DEBUG] Gemini output for failed word '{word}':\n{json.dumps(gemini_data, indent=2, ensure_ascii=False)}")

            status = "✅" if success else "❌"
            output_box.insert(tk.END, f"{status} {msg}\n\n")
            output_box.see(tk.END)

        output_box.insert(tk.END, "🎉 Done!\n")
        output_box.configure(state='disabled')

    tk.Button(root, text="➕ Add Words to Anki", command=process_words).pack(pady=15)

    root.mainloop()

# === RUN ===
if __name__ == "__main__":
    run_gui()