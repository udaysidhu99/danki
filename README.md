# Danki – German Vocabulary to Anki 

Danki is a lightweight macOS app that helps you automate German vocabulary acquisition by generating high-quality word data using Google Gemini and sending it straight into your Anki deck — complete with articles, conjugations, and natural example sentences.

---

## Features

- Supports single and multi-word input (comma or newline-separated)
- Uses Gemini API to fetch structured German word information
- Automatically includes up to three example sentences (when applicable)
- Adds notes directly to Anki using AnkiConnect
- High-quality offline TTS audio via `edge-tts` (German voices)
- Includes sentence audio for each example sentence
- Skips duplicates already present in Anki
- Smart error handling: invalid characters, missing internet, Gemini rate limits
- Includes pre-made Anki `.apkg` deck with the correct note type and fields

---

## Installation

### Download the App

Download the latest release ZIP from the [Releases page](https://github.com/udaysidhu99/danki/releases/latest).

Unzip it — it includes:
- `Danki.app` (macOS app)
- `Danki_Deck_Template.apkg` (Anki deck template)
---

## Gemini API Key

The app requires a Gemini API key. You can get it here:  
https://aistudio.google.com/app/apikey

> **Note**: Submitting too many words in a short time may exceed the request limit of Gemini's free tier.

The key will be saved locally in a file called `gemini_config.json`.

---

## Setting Up Anki

### 1. Install [Anki](https://apps.ankiweb.net/)
Make sure Anki is running before launching Danki.

### 2. Install [AnkiConnect](https://ankiweb.net/shared/info/2055492159)
This is required for the app to send notes to Anki.

### 3. Import the Template Deck
Before using the app, **import the provided `.apkg` file** to set up the correct note type.

Import `Danki_Deck_Template.apkg` from the ZIP into Anki:
- Open Anki
- Go to **File > Import**
- Select the `.apkg` file
- Done!

This step ensures the custom note type **"German Auto"** with required fields exists.

---

## Usage

Note: If using the macOS app version, double-click `Danki.app` to launch.

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
- `audio_text_d`: Same as `full_d` (used for TTS base word audio)
- `s1`, `s2`, `s3`: Natural German example sentences (1–3 depending on context)
- `s1e`, `s2e`, `s3e`: English translations of the above sentences
- `s1a`, `s2a`, `s3a`: TTS audio for each example sentence

---

## Error Handling

- Detects and skips entries with invalid characters or nonsense input
- Alerts if no internet connection is available
- Gracefully handles Gemini timeouts and rate limits
- Warns if Anki or AnkiConnect is not running
