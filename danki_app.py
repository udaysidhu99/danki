from PyQt5.QtCore import Qt, QTimer
is_processing = False
is_processing_phrase = False
import requests
import json
import re
import os
import tempfile
import base64
import asyncio
from edge_tts import Communicate
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout,
    QComboBox, QHBoxLayout, QMessageBox, QInputDialog, QProgressBar, QLineEdit, QCheckBox, QToolButton
)
from PyQt5.QtCore import QSize
import sys
from pathlib import Path

# --- Shortcut-aware QTextEdit ---
class ShortcutAwareTextEdit(QTextEdit):
    def __init__(self, callback=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback

    def keyPressEvent(self, event):
        if ((event.modifiers() & Qt.ShiftModifier) and
                event.key() in (Qt.Key_Return, Qt.Key_Enter)):
            if self.callback and callable(self.callback) and self.toPlainText().strip():
                self.setDisabled(True)  # Prevent further input
                def safe_callback():
                    if self.callback and callable(self.callback):
                        self.callback()
                    QTimer.singleShot(1500, lambda: self.setDisabled(False))
                QTimer.singleShot(0, safe_callback)
                return
        super().keyPressEvent(event)

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

CONFIG_PATH = Path(os.path.expanduser("~/.danki/gemini_config.json"))

def save_api_key(api_key, allow_duplicates=True, include_notes=True):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump({
            "api_key": api_key,
            "allow_duplicates": allow_duplicates,
            "include_notes": include_notes
        }, f)

def load_api_key():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            config = json.load(f)
            return (
                config.get("api_key"),
                config.get("allow_duplicates", True),
                config.get("include_notes", True)
            )
    return None, True, True

def is_connected():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except:
        return False

# === CONFIG ===
NOTE_TYPE = "German Auto"  
ANKI_ENDPOINT = "http://localhost:8765"

# === GEMINI QUERY ===
def query_gemini(word):
    global API_KEY
    GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    prompt = (
        f"You are a helpful German language assistant. For the word: **{word}**, provide the following structured information.\n"
        "If the word is not a valid German word, return this JSON exactly:\n"
        "{\"error\": \"Not a valid German word\"}\n\n"
        "1. **base_d**: The original German word\n"
        "2. **base_e**: The English translation(s)\n"
        "3. **artikel_d**: The definite article if the word is a noun (e.g., \"der\", \"die\", \"das\"). Leave empty if not a noun.\n"
        "4. **plural_d**: The plural form (for nouns). Leave empty if not a noun.\n"
        "5. **praesens**: Present tense (3rd person singular), e.g., \"läuft\"\n"
        "6. **praeteritum**: Simple past tense (3rd person singular), e.g., \"lief\"\n"
        "7. **perfekt**: Present perfect form, e.g., \"ist gelaufen\"\n"
        "8. **full_d**: A combined string of the above three conjugation forms, e.g., \"läuft, lief, ist gelaufen\"\n"
        "9. **s1**: A natural German sentence using the word, with its English translation in parentheses.\n"
        "10. **s2** (optional): A second sentence only if the word has a different context.\n"
        "11. **s3** (optional): A third sentence to demonstrate nuance or complexity, if useful.\n\n"
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
        "  \"s1\": \"Ich laufe jeden Morgen im Park. (I run every morning in the park.)\",\n"
        "  \"s2\": \"Er läuft zur Arbeit, weil er den Bus verpasst hat. (He runs to work because he missed the bus.)\",\n"
        "  \"s3\": \"Der Hund läuft im Garten herum. (The dog is running around in the garden.)\"\n"
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
        print(f"[DEBUG] Raw s1: {s1_raw}")
        if "(" in s1_raw and ")" in s1_raw:
            parsed["s1"] = s1_raw.split("(")[0].strip()
            parsed["s1e"] = s1_raw.split("(")[1].rstrip(")").strip()
        else:
            parsed["s1e"] = ""
        
        # Clean up s2
        s2_raw = parsed.get("s2", "")
        if "(" in s2_raw and ")" in s2_raw:
            parsed["s2"] = s2_raw.split("(")[0].strip()
            parsed["s2e"] = s2_raw.split("(")[1].rstrip(")").strip()
        else:
            parsed["s2e"] = ""
        
        # Clean up s3
        s3_raw = parsed.get("s3", "")
        if "(" in s3_raw and ")" in s3_raw:
            parsed["s3"] = s3_raw.split("(")[0].strip()
            parsed["s3e"] = s3_raw.split("(")[1].rstrip(")").strip()
        else:
            parsed["s3e"] = ""

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
def add_to_anki(parsed_word, deck_name, allow_duplicates):
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

    audio_fields = []
    artikel = parsed_word.get("artikel_d", "").strip()
    base_d = parsed_word.get("base_d", "").strip()
    if artikel:
        base_for_audio = f"{artikel} {base_d}"
    else:
        base_for_audio = base_d
    base_audio = generate_tts_audio(base_for_audio.replace(" ", ""), os.urandom(8).hex())
    s1 = parsed_word.get("s1", "").strip()
    s2 = parsed_word.get("s2", "").strip()
    s3 = parsed_word.get("s3", "").strip()
    print(base_d)
    if base_audio:
        audio_fields.append({
            "url": None,
            "filename": base_audio["filename"],
            "data": base_audio["data"],
            "fields": ["base_a"]
        })

    if s1:
        s1_audio = generate_tts_audio(s1, os.urandom(8).hex())
        if s1_audio:
            audio_fields.append({
                "url": None,
                "filename": s1_audio["filename"],
                "data": s1_audio["data"],
                "fields": ["s1a"]
            })

    if s2:
        s2_audio = generate_tts_audio(s2, os.urandom(8).hex())
        if s2_audio:
            audio_fields.append({
                "url": None,
                "filename": s2_audio["filename"],
                "data": s2_audio["data"],
                "fields": ["s2a"]
            })

    if s3:
        s3_audio = generate_tts_audio(s3, os.urandom(8).hex())
        if s3_audio:
            audio_fields.append({
                "url": None,
                "filename": s3_audio["filename"],
                "data": s3_audio["data"],
                "fields": ["s3a"]
            })

    fields = {
        "base_d": str(parsed_word.get("base_d", "") or ""),
        "base_e": str(parsed_word.get("base_e", "") or ""),
        "artikel_d": str(parsed_word.get("artikel_d", "") or ""),
        "plural_d": str(parsed_word.get("plural_d", "") or ""),
        "full_d": parsed_word.get("full_d") if parsed_word.get("full_d") is not None else "",
        "audio_text_d": parsed_word.get("full_d") if parsed_word.get("full_d") is not None else "",
        "s1": str(parsed_word.get("s1", "") or ""),
        "s1e": str(parsed_word.get("s1e", "") or ""),
        "s2": str(parsed_word.get("s2", "") or ""),
        "s2e": str(parsed_word.get("s2e", "") or ""),
        "s3": str(parsed_word.get("s3", "") or ""),
        "s3e": str(parsed_word.get("s3e", "") or "")
    }

    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deck_name,
                "modelName": NOTE_TYPE,
                "fields": fields,
                "options": {"allowDuplicate": allow_duplicates},
                "tags": ["auto-added"],
                "audio": audio_fields
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

def generate_tts_audio(text, filename_hint):
    try:
        filename = os.path.join(tempfile.gettempdir(), f"sapi5js-{filename_hint}.mp3")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        communicate = Communicate(text, "de-DE-KatjaNeural")
        loop.run_until_complete(communicate.save(filename))
        with open(filename, "rb") as f:
            audio_data = base64.b64encode(f.read()).decode("utf-8")
        os.remove(filename)
        return {
            "filename": filename,
            "data": audio_data
        }
    except Exception as e:
        print(f"[ERROR] TTS generation failed for '{filename_hint}': {e}")
        return None

# === FETCH DECKS FROM ANKI ===
def get_anki_decks():
    payload = {"action": "deckNames", "version": 6}
    try:
        response = requests.post(ANKI_ENDPOINT, json=payload, timeout=5)
        decks = response.json().get("result", [])
        return decks
    except Exception:
        QMessageBox.warning(None, "Anki not responding", "Anki is not running or AnkiConnect is not enabled.")
        return []

def find_note_count(query):
    payload = {
        "action": "findNotes",
        "version": 6,
        "params": {"query": query}
    }
    try:
        response = requests.post(ANKI_ENDPOINT, json=payload)
        notes = response.json().get("result", [])
        return len(notes)
    except Exception:
        return 0

def get_wordmaster_decks():
    decks = get_anki_decks()
    wordmaster_decks = []
    for deck in decks:
        # Exclude default deck
        if deck.strip().lower() == "default":
            continue
        # Check if deck is empty
        note_count = find_note_count(f'deck:"{deck}"')
        if note_count == 0:
            wordmaster_decks.append(deck)
        else:
            german_note_count = find_note_count(f'deck:"{deck}" note:"{NOTE_TYPE}"')
            if german_note_count > 0:
                wordmaster_decks.append(deck)
    return wordmaster_decks

def get_phrasemaster_decks():
    payload = {"action": "deckNames", "version": 6}
    try:
        response = requests.post(ANKI_ENDPOINT, json=payload, timeout=5)
        decks = response.json().get("result", [])
    except Exception:
        QMessageBox.warning(None, "Anki not responding", "Anki is not running or AnkiConnect is not enabled.")
        return []

    valid_decks = []
    for deck in decks:
        # Exclude default deck
        if deck.strip().lower() == "default":
            continue
        note_count = find_note_count(f'deck:"{deck}"')
        if note_count == 0:
            valid_decks.append(deck)
        else:
            phrase_note_count = find_note_count(f'deck:"{deck}" note:"Phrase Auto"')
            if phrase_note_count > 0:
                valid_decks.append(deck)
    return valid_decks
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
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowIcon(QtGui.QIcon(resource_path("icon.ico")))

    # Menu bar with Preferences
    menu_bar = QtWidgets.QMenuBar()
    preferences_menu = menu_bar.addMenu("Preferences")

    def open_preferences():
        QMessageBox.information(window, "Preferences", "Preferences dialog would open here.")

    pref_action = QtWidgets.QAction("Open Preferences", window)
    pref_action.triggered.connect(open_preferences)
    preferences_menu.addAction(pref_action)

    layout = QVBoxLayout()

    tabs = QtWidgets.QTabWidget()

    # WordMaster tab
    wordmaster_tab = QWidget()
    main_layout = QVBoxLayout()

    global API_KEY
    API_KEY, allow_duplicates, include_notes = load_api_key()
    if not API_KEY:
        API_KEY, ok = QInputDialog.getText(window, "Gemini API Key", "Enter your Gemini API Key:")
        if not ok or not API_KEY:
            QMessageBox.critical(window, "Missing API Key", "API key is required to use the app.")
            return
        save_api_key(API_KEY, allow_duplicates)

    # Deck Dropdown
    deck_layout = QHBoxLayout()
    deck_label = QLabel("Select Anki Deck:")
    deck_combo = QComboBox()
    deck_list = get_wordmaster_decks()
    deck_combo.addItems(deck_list)
    if deck_list:
        deck_combo.setCurrentIndex(0)
    else:
        deck_combo.setCurrentIndex(-1)
    deck_layout.addWidget(deck_label)
    deck_layout.addWidget(deck_combo)

    refresh_btn = QPushButton("Refresh")
    def refresh_decks():
        deck_combo.clear()
        updated = get_wordmaster_decks()
        deck_combo.addItems(updated)
        if updated:
            deck_combo.setCurrentIndex(0)
        else:
            deck_combo.setCurrentIndex(-1)
    refresh_btn.clicked.connect(refresh_decks)
    deck_layout.addWidget(refresh_btn)

    main_layout.addLayout(deck_layout)

    # Input box
    input_label = QLabel("Enter German words (comma or newline separated):")
    disclaimer = QLabel("Gemini free tier may reject large requests. Add fewer words if it fails.")
    disclaimer.setStyleSheet("color: grey; font-size: 10px;")
    main_layout.addWidget(input_label)
    main_layout.addWidget(disclaimer)
    input_box = ShortcutAwareTextEdit()
    input_box.setFixedHeight(300)
    input_box.setTabChangesFocus(True)
    main_layout.addWidget(input_box)

    # Output log
    output_box = QTextEdit()
    output_box.setReadOnly(True)
    output_box.setTabChangesFocus(True)
    output_box.setFixedHeight(150)
    main_layout.addWidget(output_box)

    # Clear button
    def clear_text_boxes():
        input_box.clear()
        output_box.clear()

    # Progress bar
    progress_bar = QProgressBar()
    progress_bar.setValue(0)
    main_layout.addWidget(progress_bar)

    # Process button
    def process_words():
        global is_processing
        if is_processing:
            return
        is_processing = True
        add_btn.setEnabled(False)
        QApplication.processEvents()
        try:
            if not is_connected():
                QMessageBox.critical(window, "No Internet", "An internet connection is required to use Gemini.")
                return

            words_raw = input_box.toPlainText()
            selected_deck = deck_combo.currentText()
            words = re.split(r"[,\n]", words_raw)
            words = [w.strip() for w in words if w.strip()]
            valid_word_pattern = re.compile(r"^[a-zA-ZäöüÄÖÜß\s\-]+$")

            output_box.clear()
            progress_bar.setMaximum(len(words))
            progress_bar.setValue(0)

            for word in words:
                if not valid_word_pattern.match(word):
                    output_box.append(f"'{word}' contains invalid characters. Skipping.\n")
                    progress_bar.setValue(progress_bar.value() + 1)
                    continue

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

                success, msg = add_to_anki(gemini_data, selected_deck, allow_duplicates)
                status = "Success" if success else "Failed"
                meaning_display = f" → {gemini_data.get('base_e', '')}" if success else ""
                output_box.append(f"{status} {msg}{meaning_display}\n")
                progress_bar.setValue(progress_bar.value() + 1)

            output_box.append("Done!")
        finally:
            is_processing = False
            add_btn.setEnabled(True)

    button_layout = QHBoxLayout()
    
    clear_btn = QPushButton("Clear")
    clear_btn.clicked.connect(clear_text_boxes)
    button_layout.addWidget(clear_btn)
    
    def update_clear_button_state():
        clear_btn.setEnabled(bool(input_box.toPlainText().strip() or output_box.toPlainText().strip()))

    add_btn = QPushButton("Add Words to Deck")
    add_btn.setToolTip(f"Shortcut: {'Shift+Return' if sys.platform == 'darwin' else 'Shift+Enter'}")
    # Add logic to enable/disable the "Add Words to Deck" button
    def update_add_button_state():
        add_btn.setEnabled(bool(input_box.toPlainText().strip()))
    input_box.textChanged.connect(update_add_button_state)
    update_add_button_state()

    input_box.textChanged.connect(update_clear_button_state)
    output_box.textChanged.connect(update_clear_button_state)
    update_clear_button_state()
    
    add_btn.clicked.connect(process_words)
    input_box.callback = process_words
    button_layout.addWidget(add_btn)

    # Add keyboard shortcut for Add Words to Deck using QAction
    from PyQt5.QtGui import QKeySequence
    shortcut_action = QtWidgets.QAction(window)
    keyseq = QKeySequence("Meta+Return" if sys.platform == "darwin" else "Ctrl+Return")
    shortcut_action.setShortcut(keyseq)
    shortcut_action.triggered.connect(process_words)
    window.addAction(shortcut_action)
    
    main_layout.addLayout(button_layout)

    wordmaster_tab.setLayout(main_layout)

    # Preferences tab (currently empty)
    preferences_tab = QWidget()
    preferences_main_layout = QVBoxLayout()

    api_label = QLabel("Gemini API Key:")

    api_input_layout = QHBoxLayout()
    api_input = QLineEdit()
    api_input.setPlaceholderText(API_KEY[:5] + "..." if API_KEY else "")
    save_btn = QPushButton("Save API Key")

    allow_dupes_checkbox = QCheckBox("Allow Duplicate Notes")
    allow_dupes_checkbox.setChecked(allow_duplicates)
    allow_dupes_checkbox.stateChanged.connect(lambda _: save_api_key(API_KEY, allow_dupes_checkbox.isChecked(), include_notes_checkbox.isChecked()))

    def save_preferences():
        new_key = api_input.text().strip()
        if not new_key:
            QMessageBox.warning(window, "Missing API Key", "The Gemini API Key cannot be blank.")
            return
        new_allow_dupes = allow_dupes_checkbox.isChecked()
        save_api_key(new_key, new_allow_dupes)
        QMessageBox.information(window, "Saved", "Preferences updated successfully.")
        api_input.clear()
        api_input.setPlaceholderText(new_key[:5] + "...")

    save_btn.clicked.connect(save_preferences)

    api_input_layout.addWidget(api_label)
    api_input_layout.addWidget(api_input)
    api_input_layout.addWidget(save_btn)
    preferences_main_layout.addLayout(api_input_layout)
    preferences_main_layout.addWidget(allow_dupes_checkbox)
    disclaimer = QLabel("Note: Duplicate detection is handled by Anki.\nIt checks across all decks using the same note type.")
    disclaimer.setWordWrap(True)
    disclaimer.setStyleSheet("color: gray; font-size: 10px;")
    preferences_main_layout.addWidget(disclaimer)
    include_notes_checkbox = QCheckBox("Include grammar/usage notes in PhraseMaster")
    include_notes_checkbox.setChecked(include_notes)
    preferences_main_layout.addWidget(include_notes_checkbox)
    include_notes_checkbox.stateChanged.connect(lambda _: save_api_key(API_KEY, allow_dupes_checkbox.isChecked(), include_notes_checkbox.isChecked()))

    preferences_main_layout.addStretch()

    preferences_tab.setLayout(preferences_main_layout)

    tabs.addTab(wordmaster_tab, "WordMaster")
    # PhraseMaster tab
    phrasemaster_tab = QWidget()
    phrasemaster_layout = QVBoxLayout()
    
    # Deck Dropdown
    phrase_deck_layout = QHBoxLayout()
    phrase_deck_label = QLabel("Select Anki Deck:")
    phrase_deck_combo = QComboBox()
    phrase_deck_list = get_phrasemaster_decks()
    phrase_deck_combo.addItems(phrase_deck_list)
    if phrase_deck_list:
        phrase_deck_combo.setCurrentIndex(0)
    else:
        phrase_deck_combo.setCurrentIndex(-1)
    phrase_deck_layout.addWidget(phrase_deck_label)
    phrase_deck_layout.addWidget(phrase_deck_combo)
    
    phrase_refresh_btn = QPushButton("Refresh")
    def refresh_phrase_decks():
        phrase_deck_combo.clear()
        updated = get_phrasemaster_decks()
        phrase_deck_combo.addItems(updated)
        if updated:
            phrase_deck_combo.setCurrentIndex(0)
        else:
            phrase_deck_combo.setCurrentIndex(-1)
    phrase_refresh_btn.clicked.connect(refresh_phrase_decks)
    phrase_deck_layout.addWidget(phrase_refresh_btn)
    
    phrasemaster_layout.addLayout(phrase_deck_layout)
    
    # Input box
    phrase_input_label = QLabel("Enter sentences (English or German), one per line:")
    phrasemaster_layout.addWidget(phrase_input_label)
    phrase_format_disclaimer = QLabel("Separate multiple sentences with newlines. Commas are allowed within sentences.")
    phrase_format_disclaimer.setStyleSheet("color: grey; font-size: 10px;")
    phrasemaster_layout.addWidget(phrase_format_disclaimer)
    phrase_disclaimer = QLabel("Gemini free tier may reject requests with large number of sentences.")
    phrase_disclaimer.setStyleSheet("color: grey; font-size: 10px;")
    phrasemaster_layout.addWidget(phrase_disclaimer)
    phrase_input_box = ShortcutAwareTextEdit()
    phrase_input_box.setFixedHeight(250)
    phrase_input_box.setTabChangesFocus(True)
    phrasemaster_layout.addWidget(phrase_input_box)
    
    # Context input box (optional) with help
    context_row = QHBoxLayout()
    
    context_label = QLabel("Context (optional):")
    context_label.setStyleSheet("font-size: 11px; color: grey;")
    context_row.addWidget(context_label)
    
    context_help_btn = QToolButton()
    style = QApplication.style()
    context_help_btn.setIcon(style.standardIcon(QtWidgets.QStyle.SP_MessageBoxInformation))
    context_help_btn.setIconSize(QSize(24, 24))
    context_help_btn.setToolTip("What is 'Context'?")
    context_help_btn.setFocusPolicy(Qt.NoFocus)
    context_help_btn.setStyleSheet("""
        QToolButton {
            border: none;
            background: transparent;
            padding: 0px;
        }
    """)
    context_help_btn.setIconSize(QSize(24, 24))
    def show_context_help():
        QMessageBox.information(None, "What is 'Context'?",
            "You can optionally add context to your sentence (e.g., informal chat, business email, on a date, asking directions from a stranger).\n"
            "This helps the model provide more accurate translations.")
    context_help_btn.clicked.connect(show_context_help)
    context_row.addWidget(context_help_btn)
    context_row.addStretch()
    
    phrasemaster_layout.addLayout(context_row)
    
    context_input_box = QTextEdit()
    context_input_box.setFixedHeight(50)
    context_input_box.setTabChangesFocus(True)
    phrasemaster_layout.addWidget(context_input_box)

    def update_context_box_state():
        text = phrase_input_box.toPlainText()
        has_multiple_sentences = "\n" in text.strip()
        context_input_box.setDisabled(has_multiple_sentences)
        context_label.setText("Context (optional):" if not has_multiple_sentences else "Context (disabled for multiple sentences)")

    phrase_input_box.textChanged.connect(update_context_box_state)
    update_context_box_state()
    
    # Output log
    phrase_output_box = QTextEdit()
    phrase_output_box.setReadOnly(True)
    phrase_output_box.setFixedHeight(100)
    phrasemaster_layout.addWidget(phrase_output_box)
    
    # Progress bar
    phrase_progress_bar = QProgressBar()
    phrase_progress_bar.setValue(0)
    phrasemaster_layout.addWidget(phrase_progress_bar)
    
    # Clear button
    def clear_phrase_boxes():
        phrase_input_box.clear()
        phrase_output_box.clear()
        context_input_box.clear()
    
    # Process button (placeholder for now)
    def process_phrase():
        global is_processing_phrase
        if is_processing_phrase:
            return
        is_processing_phrase = True
        phrase_add_btn.setEnabled(False)
        QApplication.processEvents()
        try:
            if not is_connected():
                QMessageBox.critical(None, "No Internet", "An internet connection is required to use Gemini.")
                return

            sentences_raw = phrase_input_box.toPlainText()
            context_text = context_input_box.toPlainText().strip()
            selected_deck = phrase_deck_combo.currentText()
            sentences = [s.strip() for s in sentences_raw.split("\n") if s.strip()]
            phrase_output_box.clear()
            phrase_progress_bar.setMaximum(len(sentences))
            phrase_progress_bar.setValue(0)

            for sentence in sentences:
                prompt = (
                    "INSTRUCTIONS: Return ONLY a JSON code block with the following fields.\n"
                    "- german: corrected or original German sentence\n"
                    "- english: English translation of the sentence\n"
                    "- note: (optional) a short grammar or usage note\n"
                    "- error: (optional) only include if input is invalid\n\n"
                    f"Context: {context_text if context_text else 'General'}\n"
                    f"Sentence: {sentence}\n\n"
                    "Respond ONLY with a JSON code block like:\n"
                    "```json\n"
                    "{\n"
                    "  \"german\": \"Ich gehe jeden Tag zur Arbeit.\",\n"
                    "  \"english\": \"I go to work every day.\",\n"
                    "  \"note\": \"'zur' is a contraction of 'zu der'.\"\n"
                    "}\n"
                    "```"
                )

                GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
                headers = {'Content-Type': 'application/json'}
                body = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }

                try:
                    response = requests.post(GEMINI_ENDPOINT, headers=headers, json=body)
                    result = response.json()
                    if "candidates" not in result:
                        phrase_output_box.append(f"Gemini error: {result.get('error', 'No candidates returned')}\n")
                        phrase_progress_bar.setValue(phrase_progress_bar.value() + 1)
                        continue

                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"[DEBUG] Gemini raw content:\n{content}")
                    match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
                    if not match:
                        phrase_output_box.append("❌ JSON block not found in Gemini response.\n")
                        phrase_progress_bar.setValue(phrase_progress_bar.value() + 1)
                        continue

                    try:
                        parsed = json.loads(match.group(1))
                        print(f"[DEBUG] Parsed JSON keys: {list(parsed.keys())}")
                    except json.JSONDecodeError as e:
                        phrase_output_box.append(f"❌ JSON decoding error: {str(e)}\n")
                        phrase_progress_bar.setValue(phrase_progress_bar.value() + 1)
                        continue

                    if "error" in parsed:
                        phrase_output_box.append(f"⚠️ Gemini error: {parsed['error']}\n")
                        phrase_progress_bar.setValue(phrase_progress_bar.value() + 1)
                        continue

                    required_keys = ["german", "english"]
                    if not all(parsed.get(k, "").strip() for k in required_keys):
                        phrase_output_box.append(f"❌ Incomplete Gemini response. Missing 'german' or 'english'. Parsed keys: {list(parsed.keys())}\n")
                        phrase_progress_bar.setValue(phrase_progress_bar.value() + 1)
                        continue

                    phrase_output_box.append(f"ENG: {parsed['english']}\nDEU: {parsed['german']}\n")
                    german_text = parsed.get("german", "").strip()
                    english_text = parsed.get("english", "").strip()
                    fields = {
                        "Phrase(German)": german_text,
                        "Translation": english_text,
                        "audio_text_d": german_text
                    }
                    if include_notes_checkbox.isChecked():
                        fields["note"] = parsed.get("note", "")
                    
                    audio_fields = []
                    base_audio = generate_tts_audio(fields["Phrase(German)"], os.urandom(8).hex())
                    if base_audio:
                        audio_fields.append({
                            "url": None,
                            "filename": base_audio["filename"],
                            "data": base_audio["data"],
                            "fields": ["audio_d"]
                        })
                    
                    payload = {
                        "action": "addNote",
                        "version": 6,
                        "params": {
                            "note": {
                                "deckName": selected_deck,
                                "modelName": "Phrase Auto",
                                "fields": fields,
                                "options": {"allowDuplicate": allow_duplicates},
                                "tags": ["auto-added"],
                                "audio": audio_fields
                            }
                        }
                    }
                    
                    try:
                        res = requests.post(ANKI_ENDPOINT, json=payload)
                        res_json = res.json()
                        if res_json.get("error") is None:
                            phrase_output_box.append("Successfully added to Anki!\n")
                        else:
                            phrase_output_box.append(f"❌ Anki error: {res_json['error']}\n")
                    except Exception as e:
                        phrase_output_box.append(f"❌ Failed to send to Anki: {str(e)}\n")

                except Exception as e:
                    phrase_output_box.append(f"❌ Exception: {str(e)}\n")

                phrase_progress_bar.setValue(phrase_progress_bar.value() + 1)

            phrase_output_box.append("Done.")
        finally:
            is_processing_phrase = False
            phrase_add_btn.setEnabled(True)
    
    phrase_button_layout = QHBoxLayout()
    phrase_clear_btn = QPushButton("Clear")
    phrase_clear_btn.clicked.connect(clear_phrase_boxes)
    def update_phrase_clear_button_state():
        phrase_clear_btn.setEnabled(bool(phrase_input_box.toPlainText().strip() or phrase_output_box.toPlainText().strip()))

    phrase_add_btn = QPushButton("Add Phrase to Deck")
    phrase_add_btn.setToolTip(f"Shortcut: {'Shift+Return' if sys.platform == 'darwin' else 'Shift+Enter'}")
    # Add logic to enable/disable the "Add Phrase to Deck" button
    def update_phrase_add_button_state():
        phrase_add_btn.setEnabled(bool(phrase_input_box.toPlainText().strip()))
    phrase_input_box.textChanged.connect(update_phrase_add_button_state)
    update_phrase_add_button_state()

    phrase_input_box.textChanged.connect(update_phrase_clear_button_state)
    phrase_output_box.textChanged.connect(update_phrase_clear_button_state)
    update_phrase_clear_button_state()
    phrase_button_layout.addWidget(phrase_clear_btn)
    phrase_add_btn.clicked.connect(process_phrase)
    phrase_input_box.callback = process_phrase
    phrase_button_layout.addWidget(phrase_add_btn)
    # Add keyboard shortcut for Add Phrase to Deck using QAction
    phrase_shortcut_action = QtWidgets.QAction(window)
    phrase_keyseq = QKeySequence("Meta+Return" if sys.platform == "darwin" else "Ctrl+Return")
    phrase_shortcut_action.setShortcut(phrase_keyseq)
    phrase_shortcut_action.triggered.connect(process_phrase)
    window.addAction(phrase_shortcut_action)
    phrasemaster_layout.addLayout(phrase_button_layout)
    phrasemaster_tab.setLayout(phrasemaster_layout)
    tabs.addTab(phrasemaster_tab, "PhraseMaster")
    tabs.addTab(preferences_tab, "Preferences")

    layout.addWidget(tabs)

    window.setLayout(layout)
    window.resize(500, 500)
    window.show()
    sys.exit(app.exec_())


# === RUN ===
if __name__ == "__main__":
    run_gui()   