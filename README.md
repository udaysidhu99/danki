# Danki – German Vocabulary to Anki

Danki is a lightweight app that helps automate your German learning by generating high-quality vocabulary and sentence data using Google Gemini, then sending it straight into your Anki deck — complete with grammar, context, and native-sounding audio.

Supports both macOS and Windows.

---

## Features

- WordMaster: Add single or multi-word vocabulary with translations, grammar, and example sentences
- PhraseMaster: Add full German or English sentences, with optional grammar notes and context-awareness
- Context mode: Get better translations by specifying the situation (e.g., formal email, conversation, travel)
- High-quality offline TTS audio via `edge-tts` (German voices)
- Audio for both vocabulary and full phrases
- Duplicate detection via AnkiConnect
- Smart error handling: invalid characters, no internet, Gemini rate limits
- Comes with pre-built Anki `.apkg` template decks

---

## New in v1.1.0

- **PhraseMaster tab**: Input full sentences (German or English), with Gemini-assisted correction and translation
- Add context (e.g. "business", "casual", "giving directions") to improve translation accuracy
- Automatically adds sentence audio to Anki
- Optional usage/grammar notes
- Preferences panel: Save your Gemini API key, toggle duplicates, and include/exclude notes
- First **Windows release**

---

## macOS Permissions

macOS may block the app from opening because it is not notarized. This is expected.

### To allow it to run:

1. Try launching the app once by double-clicking. macOS will block it.
2. Open **System Settings → Privacy & Security**
3. Scroll to the Security section and click **“Allow Anyway”**
4. Open the app again, then click **Open** when prompted

---

## Installation

### Download the App

Download the latest release ZIP from the [Releases page](https://github.com/udaysidhu99/danki/releases/latest).

Unzip it — it includes:
- `Danki.app` (macOS) or `Danki.exe` (Windows)
- `PhraseMasterTemplate.apkg`
- `WordMasterTemplate.apkg`

---

## Gemini API Key

The app requires a Gemini API key. You can get it here:  
https://aistudio.google.com/app/apikey

> **Note**: Submitting too many words or sentences in a short time may exceed Gemini's free-tier rate limits.

The key is saved locally in a file called `gemini_config.json`.

---

## Setting Up Anki

1. **Install [Anki](https://apps.ankiweb.net/)**  
2. **Install [AnkiConnect](https://ankiweb.net/shared/info/2055492159)**  
3. **Import the Template Decks**  
   - Open Anki → File → Import
   - Import both:
     - `PhraseMasterTemplate.apkg`
     - `WordMasterTemplate.apkg`

This creates the necessary note types:  
- `"German Auto"` (WordMaster)  
- `"Phrase Auto"` (PhraseMaster)

---

## Usage

1. Select the desired Anki deck
2. Enter words (WordMaster) or sentences (PhraseMaster)
3. Optionally provide context (for PhraseMaster)
4. Click **"Add"**
5. Your notes will appear in Anki — with translations, grammar, and audio

---

## Note Structure

### WordMaster Notes
- `base_d`: German word
- `base_e`: English meaning
- `artikel_d`, `plural_d`: Article & plural (for nouns)
- `full_d`: Conjugation string or full noun form
- `audio_text_d`: TTS base word
- `s1`, `s2`, `s3`: German example sentences
- `s1e`, `s2e`, `s3e`: English translations
- `s1a`, `s2a`, `s3a`: Audio for each sentence

### PhraseMaster Notes
- `Phrase(German)`: Final/corrected German sentence
- `Translation`: English meaning
- `note`: (optional) grammar or usage explanation
- `audio_d`: TTS for full phrase

---

## Error Handling

- Skips invalid entries and nonsense input
- Alerts if internet is disconnected
- Handles Gemini timeouts and free-tier limits
- Warns if Anki or AnkiConnect is not running
- Disables context box automatically for multiple sentences

---
