# Danki — Windows Build Guide (v2.0.0-beta.1)

> Complete build instructions for Windows. Written for both human developers and AI coding assistants (Copilot, Claude, etc.).

---

## Quick Build (Copy-Paste)

```powershell
git clone https://github.com/udaysidhu99/danki.git
cd danki
pip install PyQt5 requests edge-tts pyinstaller
pyinstaller danki_app_onedir.spec --clean --noconfirm
# Output: dist\Danki\Danki.exe
```

---

## Prerequisites

### 1. Python 3.10+
- Download: https://www.python.org/downloads/
- ✅ **Check "Add Python to PATH"** during installation
- Verify: `python --version`

### 2. Git
- Download: https://git-scm.com/download/win
- Keep defaults during install
- Verify: `git --version`

### 3. VS Code (optional)
- Download: https://code.visualstudio.com/
- Install Python extension

---

## Build Steps

### 1. Clone the repository
```powershell
git clone https://github.com/udaysidhu99/danki.git
cd danki
```

### 2. Install Python dependencies
```powershell
pip install PyQt5 requests edge-tts pyinstaller
```

### 3. Verify the app runs from source
```powershell
python danki_app.py
```
The GUI should launch with the first-run API key dialog. Close after confirming.

### 4. Check required files exist
```powershell
dir icon.ico
dir danki_app_onedir.spec
dir danki_app.py
dir dictionary\german_english_dict_20k.json
dir "Danki Template Deck.apkg"
dir githubstar_banner.png
```

### 5. Build the executable
```powershell
pyinstaller danki_app_onedir.spec --clean --noconfirm
```

Output: `dist\Danki\Danki.exe` (recommended, stable taskbar icon)

### 6. Test the executable
```powershell
dist\Danki\Danki.exe
```

---

## Spec Files

| File | Platform | Output | Type |
|------|----------|--------|------|
| `Danki.spec` | macOS | `dist/Danki.app` | Folder bundle |
| `danki_app.spec` | Windows | `dist/Danki.exe` | Single file |
| `danki_app_onedir.spec` | Windows | `dist/Danki/Danki.exe` | Folder bundle (recommended) |

### What's bundled in the Windows exe
- `dictionary/german_english_dict_20k.json` — 15,973 word offline dictionary
- `Danki Template Deck.apkg` — Anki template deck for first-time users
- `githubstar_banner.png` — GitHub star banner image
- `icon.ico` — Windows application icon

---

## Post-Build Testing

### Test Checklist
- [ ] App launches without errors
- [ ] First-launch popup appears (if no API key saved) with provider dropdown
- [ ] WordMaster: enter a German word → processes correctly
- [ ] PhraseMaster: enter a sentence → translates
- [ ] Preferences: API provider dropdown (Gemini/OpenAI), all settings save/load
- [ ] Duplicate words show feedback message with Preferences hint
- [ ] TTS audio plays (requires internet for edge-tts)
- [ ] Update checker: Help → Check for Updates shows "Up to Date"
- [ ] Custom Danki icon displays on exe (not Python logo)

### Clean System Test
Copy the `dist\Danki\` folder to a machine without Python installed — it should run standalone.

---

## Release Packaging

```powershell
mkdir danki-v2.0.0-beta.1-windows
robocopy dist\Danki danki-v2.0.0-beta.1-windows\Danki /E
copy README.md danki-v2.0.0-beta.1-windows\
copy "Danki Template Deck.apkg" danki-v2.0.0-beta.1-windows\
```

---

## Troubleshooting

### `pip` not found
Python wasn't added to PATH. Reinstall and check "Add Python to PATH".

### `ModuleNotFoundError`
```powershell
pip install PyQt5 requests edge-tts pyinstaller
```

### PyInstaller can't find `icon.ico`
Run from the repo root (`cd danki`), not a subfolder.

### Dictionary not found at runtime
Verify `dictionary/german_english_dict_20k.json` exists before building. The spec bundles it automatically.

### Icon shows Python logo instead of Danki
```powershell
# Clear Windows icon cache
ie4uinit.exe -show
# Or copy exe to a new location to force icon refresh
```

### Antivirus flags the exe
Common with PyInstaller single-file builds. The exe is safe — it's Python packed into a binary. Whitelist it in your AV.

### Edge-TTS not working
Requires internet connectivity. There is no native TTS fallback on Windows (unlike macOS which falls back to `say`).

---

## Architecture Notes (for AI Assistants)

| Component | Details |
|-----------|---------|
| **Version** | `v2.0.0-beta.1` |
| **AI Providers** | Gemini (`gemini-2.5-flash-lite`) + OpenAI (`gpt-4o-mini`) |
| **Provider selection** | Auto-detected from key format, or manual in Preferences |
| **Config path** | `%USERPROFILE%\.danki\gemini_config.json` |
| **TTS** | `edge-tts` (async, requires internet) |
| **Anki integration** | AnkiConnect addon at `http://localhost:8765` |
| **Dictionary** | 15,973 entries, offline lookup with AI fallback |
| **Update checker** | Fetches `update.json` from `main` branch on GitHub |

### Key rules
- **Never commit API keys** — `.gitignore` covers `apikeys*`
- Windows spec is `danki_app_onedir.spec`, macOS spec is `Danki.spec`
- Always use `--clean --noconfirm` flags with PyInstaller
- Test the exe, not just `python danki_app.py` — bundling can surface missing imports