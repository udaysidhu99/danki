import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import requests
import json
import re
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout,
    QComboBox, QHBoxLayout, QMessageBox, QInputDialog, QProgressBar
)
import sys

def save_api_key(api_key):
    with open("gemini_config.json", "w") as f:
        json.dump({"api_key": api_key}, f)

def load_api_key():
    if os.path.exists("gemini_config.json"):
        with open("gemini_config.json") as f:
            return json.load(f).get("api_key")
    return None

# === CONFIG ===
NOTE_TYPE = "German Auto"  # ← trailing space
ANKI_ENDPOINT = "http://localhost:8765"

# === GEMINI QUERY ===
def query_gemini(word):
    global API_KEY
    GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    prompt = (
        f"You are a helpful German language assistant. For the word: **{word}**, provide the following structured information:\n\n"
        "1. **base_d**: The original German word\n"
        "2. **base_e**: The English translation(s)\n"
        "3. **artikel_d**: The definite article if the word is a noun (e.g., \"der\", \"die\", \"das\"). Leave empty if not a noun.\n"
        "4. **plural_d**: The plural form (for nouns). Leave empty if not a noun.\n"
        "5. **praesens**: Present tense (3rd person singular), e.g., \"läuft\"\n"
        "6. **praeteritum**: Simple past tense (3rd person singular), e.g., \"lief\"\n"
        "7. **perfekt**: Present perfect form, e.g., \"ist gelaufen\"\n"
        "8. **full_d**: A combined string of the above three conjugation forms, e.g., \"läuft, lief, ist gelaufen\"\n"
        "9. **s1**: A natural German sentence using the word, with its English translation in parentheses\n\n"
        "Example:\n"
        "```json\n"
        "{\n"
        "  \"base_d\": \"laufen\",\n"
        "  \"base_e\": \"to run\",\n"
        "  \"artikel_d\": \"\",\n"
        "  \"plural_d\": \"\",\n"
        "  \"praesens\": \"läuft\",\n"
        "  \"praeteritum\": \"lief\",\n"
        "  \"perfekt\": \"ist gelaufen\",\n"
        "  \"full_d\": \"läuft, lief, ist gelaufen\",\n"
        "  \"s1\": \"Ich laufe jeden Morgen im Park. (I run every morning in the park.)\"\n"
        "}\n"
        "```"
    )

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
        elif parsed.get("artikel_d") and parsed.get("base_d"):
            base_d_clean = parsed["base_d"].strip()
            artikel_d = parsed["artikel_d"].strip()
            # Avoid duplicate article if base_d already contains it
            if base_d_clean.lower().startswith(artikel_d.lower() + " "):
                parsed["full_d"] = base_d_clean
            else:
                parsed["full_d"] = f"{artikel_d} {base_d_clean}"

        return parsed

    except Exception as e:
        return {"error": str(e)}

# === ANKI ADD ===
def add_to_anki(parsed_word, deck_name):
    required_fields = ["base_d", "base_e", "s1"]
    if (
        not parsed_word or
        "error" in parsed_word or
        any(not str(parsed_word.get(field, "")).strip() for field in required_fields)
    ):
        print(f"[DEBUG] Incomplete Gemini response for word. Full content:\n{json.dumps(parsed_word, indent=2, ensure_ascii=False)}")
        return False, "Cannot create note: required fields missing or Gemini failed."

    # === Fallback for full_d ===
    if not parsed_word.get("full_d"):
        praesens = parsed_word.get("praesens", "").strip()
        praeteritum = parsed_word.get("praeteritum", "").strip()
        perfekt = parsed_word.get("perfekt", "").strip()

        if praesens or praeteritum or perfekt:
            parsed_word["full_d"] = ", ".join(filter(None, [praesens, praeteritum, perfekt]))
        elif parsed_word.get("artikel_d") and parsed_word.get("base_d"):
            parsed_word["full_d"] = f"{parsed_word['artikel_d'].strip()} {parsed_word['base_d'].strip()}"
        else:
            parsed_word["full_d"] = parsed_word.get("base_d", "")

    fields = {
        "base_d": str(parsed_word.get("base_d", "") or ""),
        "base_e": str(parsed_word.get("base_e", "") or ""),
        "artikel_d": str(parsed_word.get("artikel_d", "") or ""),
        "plural_d": str(parsed_word.get("plural_d", "") or ""),
        "full_d": parsed_word.get("full_d") if parsed_word.get("full_d") is not None else "",
        "audio_text_d": parsed_word.get("full_d") if parsed_word.get("full_d") is not None else "",
        "s1": str(parsed_word.get("s1", "") or "")
    }

    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deck_name,
                "modelName": NOTE_TYPE,
                "fields": fields,
                "options": {"allowDuplicate": True},
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
def is_duplicate(base_d_value, base_a_value):
    query = f'note:"{NOTE_TYPE.strip()}" base_d:"{base_d_value}" base_a:"{base_a_value}"'
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
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Danki")

    global API_KEY
    API_KEY = load_api_key()
    if not API_KEY:
        API_KEY, ok = QInputDialog.getText(window, "Gemini API Key", "Enter your Gemini API Key:")
        if not ok or not API_KEY:
            QMessageBox.critical(window, "Missing API Key", "API key is required to use the app.")
            return
        save_api_key(API_KEY)

    layout = QVBoxLayout()

    # Deck Dropdown
    deck_layout = QHBoxLayout()
    deck_label = QLabel("Select Anki Deck:")
    deck_combo = QComboBox()
    deck_list = get_anki_decks()
    deck_combo.addItems(deck_list)
    deck_layout.addWidget(deck_label)
    deck_layout.addWidget(deck_combo)

    refresh_btn = QPushButton("Refresh")
    def refresh_decks():
        deck_combo.clear()
        updated = get_anki_decks()
        deck_combo.addItems(updated)
    refresh_btn.clicked.connect(refresh_decks)
    deck_layout.addWidget(refresh_btn)

    layout.addLayout(deck_layout)

    # Input box
    layout.addWidget(QLabel("Enter German words (comma or newline separated):"))
    input_box = QTextEdit()
    input_box.setFixedHeight(200)
    layout.addWidget(input_box)

    # Output log
    output_box = QTextEdit()
    output_box.setReadOnly(True)
    output_box.setFixedHeight(100)
    layout.addWidget(output_box)

    # Progress bar
    progress_bar = QProgressBar()
    progress_bar.setValue(0)
    layout.addWidget(progress_bar)

    # Process button
    def process_words():
        words_raw = input_box.toPlainText()
        selected_deck = deck_combo.currentText()
        words = re.split(r"[,\n]", words_raw)
        words = [w.strip() for w in words if w.strip()]

        output_box.clear()
        progress_bar.setMaximum(len(words))
        progress_bar.setValue(0)

        for word in words:
            output_box.append(f"Processing: {word}...")
            QApplication.processEvents()

            for attempt in range(4):
                gemini_data = query_gemini(word)
                if "error" not in gemini_data:
                    print(f"[DEBUG] Gemini raw data for '{word}':\n{json.dumps(gemini_data, indent=2, ensure_ascii=False)}")
                    break

            if "error" in gemini_data:
                output_box.append(f"Gemini failed for: {word}\n")
                progress_bar.setValue(progress_bar.value() + 1)
                continue

            if is_duplicate(gemini_data.get("base_d", ""), gemini_data.get("base_a", "")):
                output_box.append(f"Skipped duplicate: {gemini_data.get('base_d', '')}\n")
                progress_bar.setValue(progress_bar.value() + 1)
                continue

            success, msg = add_to_anki(gemini_data, selected_deck)
            status = "Success" if success else "Failed"
            output_box.append(f"{status} {msg}\n")
            progress_bar.setValue(progress_bar.value() + 1)

        output_box.append("Done!")

    add_btn = QPushButton("Add Words to Deck")
    add_btn.clicked.connect(process_words)
    layout.addWidget(add_btn)

    window.setLayout(layout)
    window.resize(500, 500)
    window.show()
    sys.exit(app.exec_())

# === RUN ===
if __name__ == "__main__":
    run_gui()