# Danki – German Vocabulary to Anki with Gemini

Danki is a lightweight macOS app that helps you automate German vocabulary acquisition by generating high-quality word data using Google Gemini and sending it straight into your Anki deck — complete with articles, conjugations, and natural example sentences.

---

## Features

- Supports single and multi-word input (comma or newline-separated)
- Uses Gemini API to fetch structured German word information
- Adds words directly to Anki using AnkiConnect
- Includes sentence examples and verb conjugations
- Duplicate check to prevent re-adding existing notes
- Includes pre-made Anki `.apkg` deck with the correct note type and fields

---

## Installation

### 1. Clone the Repo
```bash
git clone https://github.com/your-username/danki.git
cd danki
```

### 2. Install Dependencies
Make sure you have Python 3, `PyQt5`, and `requests` installed:
```bash
pip install PyQt5 requests
```

---

## Gemini API Key

The app requires a Gemini API key. You can get it here:  
https://aistudio.google.com/app/apikey

The key will be saved locally in a file called `gemini_config.json`.

---

## Setting Up Anki

### 1. Install [Anki](https://apps.ankiweb.net/)
Make sure Anki is running before launching Danki.

### 2. Install [AnkiConnect](https://ankiweb.net/shared/info/2055492159)
This is required for the app to send notes to Anki.

### 3. Import the Template Deck
Before using the app, **import the provided `.apkg` file** to set up the correct note type.

Import `template/Danki_Deck_Template.apkg` into Anki:
- Open Anki
- Go to **File > Import**
- Select the `.apkg` file
- Done!

This step ensures the custom note type **"German Auto"** with required fields exists.

---

## Usage

Launch the app:
```bash
python danki_app.py
```

1. Select the Anki deck
2. Enter German words (comma or newline separated)
3. Press **"Add Words to Deck"**
4. Watch the progress bar and log for results
5. Notes appear in Anki — ready to learn!

---

## Note Structure

Each note contains:
- `base_d`: The original German word
- `base_e`: English translation(s)
- `artikel_d`: Definite article (if a noun)
- `plural_d`: Plural form (for nouns)
- `full_d`: Article + noun or conjugated forms
- `audio_text_d`: Same as `full_d` (for TTS purposes)
- `s1`: A natural sentence in German

---


---

## Credits

Created with care by [Your Name]. Inspired by the joy of language learning.
