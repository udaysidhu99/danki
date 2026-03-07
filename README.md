# Danki – German Vocabulary to Anki

Danki is a desktop app (macOS & Windows) that automates German vocabulary acquisition by generating rich word data using **Google Gemini** or **OpenAI** and sending it straight into your Anki deck — complete with articles, conjugations, example sentences, and audio.

---

## Features

### Core
- Supports single and multi-word input (comma or newline-separated)
- **Dual AI provider** — choose Google Gemini or OpenAI (auto-detected from your API key)
- **20,000-word offline dictionary** — instant lookups before hitting the API
- Up to three natural example sentences per word (with translations)
- Adds notes directly to Anki via AnkiConnect
- High-quality offline TTS audio via `edge-tts` (German voices), with macOS `say` fallback

### Card Types
- **German Auto** — base word, translation, article, plural, conjugations, sentences + audio
- **German Auto Advanced** — everything above plus full verb conjugation table (ich/du/er present, past, & perfect)
- **Phrase Auto** (PhraseMaster tab) — add entire German phrases with translation, grammar notes, and audio

### Quality of Life
- Duplicate detection with informative feedback (and a Preferences toggle)
- Smart error handling: invalid input, no internet, API rate limits, Anki not running
- Built-in update checker
- Preferences tab for all settings (provider, TTS, duplicates, dark mode, and more)
- Windows dark mode option

---

## Downloads

Download the latest release from the [**Releases page**](https://github.com/udaysidhu99/danki/releases/latest).

| Platform | File | Notes |
|----------|------|-------|
| **macOS** (Apple Silicon) | `Danki-v2.0.0-beta.1-macos.zip` | Unzip → move to Applications → right-click → Open |
| **Windows** (x64) | `Danki-v2.0.0-beta.1-windows.zip` | Unzip the folder → run `Danki.exe` |
| **Template Deck** | `Danki Template Deck.apkg` | Import into Anki before first use |

---

## macOS Permissions

macOS may block the app because it is not notarized. This is expected.

### To allow it to run:

1. Try launching the app once by double-clicking — macOS will block it.
2. Open **System Settings → Privacy & Security**.
3. Scroll down to the "Security" section.
4. Click **"Allow Anyway"** next to the message about `Danki.app`.
5. Launch the app again and click **Open** when prompted.

You only need to do this once.

---

## Getting an API Key

Danki works with **either** provider — pick whichever you prefer:

| Provider | Free tier | Get a key |
|----------|-----------|-----------|
| **Google Gemini** | Generous free tier | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| **OpenAI** | Pay-as-you-go | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |

On first launch, Danki will ask for your API key and **auto-detect** the provider from the key format. You can switch providers anytime in **Preferences**.

> **Tip:** Submitting many words quickly may hit the free-tier rate limit. Danki handles this gracefully and will tell you when to slow down.

Your key is saved locally at `~/.danki/gemini_config.json` (macOS) or `%USERPROFILE%\.danki\gemini_config.json` (Windows).

---

## Setting Up Anki

### 1. Install [Anki](https://apps.ankiweb.net/)
Make sure Anki is running before launching Danki.

### 2. Install [AnkiConnect](https://ankiweb.net/shared/info/2055492159)
This add-on is required for Danki to communicate with Anki.

### 3. Import the Template Deck
Before using the app, **import the provided `Danki Template Deck.apkg`** to set up the required note types.

- Open Anki → **File → Import**
- Select `Danki Template Deck.apkg`
- Done!

This creates the **German Auto**, **German Auto Advanced**, and **Phrase Auto** note types with all required fields.

---

## Usage

Launch the app by double-clicking `Danki.app` (macOS) or `Danki.exe` (Windows), or from source:

```bash
python danki_app.py
```

### Words Tab
1. Select an Anki deck from the dropdown
2. Enter German words (comma or newline-separated)
3. Press **"Add Words to Deck"**
4. Watch the progress bar and log — notes appear in Anki automatically

### PhraseMaster Tab
1. Select a deck
2. Enter German phrases (one per line)
3. Optionally add context to guide the AI
4. Press **"Add Phrases"** — each phrase gets a translation, grammar note, and audio

### Preferences
- Switch between **Gemini** and **OpenAI**
- Toggle **Advanced cards** (verb conjugation tables)
- Toggle **Edge TTS** for audio
- Toggle **Allow duplicate notes**
- Toggle **Windows dark mode** (Windows only)
- **Always use API** — bypass the offline dictionary for every lookup

---

## Note Types & Fields

### German Auto (basic)
| Field | Description |
|-------|-------------|
| `base_d` | Original German word |
| `base_e` | English translation(s) |
| `artikel_d` | Definite article (nouns only) |
| `plural_d` | Plural form (nouns only) |
| `full_d` | Article + noun, or conjugation summary |
| `audio_text_d` | TTS source text for the base word |
| `base_a` | Base word audio |
| `s1`, `s2`, `s3` | German example sentences |
| `s1e`, `s2e`, `s3e` | English translations of sentences |
| `s1a`, `s2a`, `s3a` | TTS audio for each sentence |

### German Auto Advanced (adds)
| Field | Description |
|-------|-------------|
| `ich_present`, `du_present`, `er_sie_es_present` | Present tense conjugations |
| `ich_past`, `du_past`, `er_sie_es_past` | Past tense conjugations |
| `perfect` | Perfect tense form |

### Phrase Auto
| Field | Description |
|-------|-------------|
| `Phrase(German)` | The German phrase |
| `Translation` | English translation |
| `note` | Grammar/usage note |
| `audio_text_d` | TTS source text |
| `audio_d` | Phrase audio |

---

## Error Handling

- Detects and skips entries with invalid characters or nonsense input
- Alerts if no internet connection is available
- Gracefully handles API timeouts and rate limits (Gemini & OpenAI)
- Warns if Anki or AnkiConnect is not running
- Informative messages when duplicate cards are rejected
