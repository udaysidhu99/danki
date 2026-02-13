# Windows Build Guide - Danki v1.2

Complete step-by-step instructions for building Danki on Windows for release preparation.

## Prerequisites Setup

### 1. Python Installation
- Install **Python 3.8-3.13** (3.14 also supported)
- Download from [python.org](https://python.org/downloads/)
- ✅ **Important**: Check "Add Python to PATH" during installation

### 2. VSCode Setup
- Open VSCode with the Danki repository
- Open integrated terminal: `Ctrl+`` or **Terminal → New Terminal**
- Ensure you're in the project root directory

### 3. Verify Installation
```bash
python --version
pip --version
```

## Dependency Installation

### Option A: Direct Installation
```bash
# Core build dependencies
pip install pyinstaller pyinstaller-hooks-contrib

# Application dependencies
pip install PyQt5 requests edge-tts asyncio pathlib
```

### Option B: Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv danki-build
danki-build\Scripts\activate

# Install dependencies
pip install pyinstaller pyinstaller-hooks-contrib
pip install PyQt5 requests edge-tts asyncio pathlib
```

## Pre-Build Verification

### 1. Test Application Locally
```bash
python danki_app.py
```

**Verify these features work:**
- ✅ WordMaster: Enter a German word and process it
- ✅ PhraseMaster: Translate a sentence
- ✅ Preferences: Settings load/save correctly
- ✅ TTS Audio: German pronunciation works
- ✅ API Connection: Gemini API responds (if configured)

### 2. Check File Dependencies
```bash
# Verify these files exist:
dir icon.ico          # Windows icon file
dir danki_app.spec     # Windows build spec
dir danki_app.py       # Main application
```

## Build Process

### 1. Clean Previous Builds
```bash
# Remove old build artifacts
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
```

### 2. Build Executable
```bash
# Use Windows-specific spec file
pyinstaller danki_app.spec
```

**Expected output:**
- Build files in `build/` directory  
- Final executable: `dist/danki_app.exe`
- Build should complete without errors

### 3. Build Verification
```bash
# Check executable was created
dir dist\danki_app.exe

# Check file size (should be ~50-100MB)
```

## Post-Build Testing

### 1. Icon Verification ✨
**This is crucial - the main fix for v1.2:**

1. Navigate to `dist/` folder in Windows Explorer
2. **Check file icon** - should show custom Danki icon, NOT Python logo
3. **If still showing Python icon:**
   - Copy `danki_app.exe` to Desktop
   - Restart Windows Explorer: `Ctrl+Shift+Esc` → Processes → Windows Explorer → Restart
   - Check icon again

### 2. Functionality Testing
```bash
# Run the executable
cd dist
danki_app.exe
```

**Test checklist:**
- ✅ Application launches without errors
- ✅ GUI appears with correct layout
- ✅ WordMaster processes German words
- ✅ PhraseMaster translates sentences  
- ✅ TTS audio generation works
- ✅ Preferences can be opened/modified
- ✅ All buttons and inputs respond

### 3. Clean System Testing
- Copy `danki_app.exe` to a machine **without Python installed**
- Verify it runs independently

## Release Preparation

### 1. Version Verification
Check that version matches v1.2.0:
```bash
# Check update.json
type update.json | findstr version
```

### 2. Final Package
```bash
# Create release folder
mkdir danki-v1.2-windows
copy dist\danki_app.exe danki-v1.2-windows\
copy README.md danki-v1.2-windows\ 
copy "Danki Template Deck.apkg" danki-v1.2-windows\
```

### 3. Distribution Testing
- Test executable in different Windows versions if available
- Verify custom icon displays correctly across different systems
- Test with Windows Defender / antivirus software

## Troubleshooting

### Common Issues

**❌ Icon still shows Python logo:**
```bash
# Solution 1: Clear Windows icon cache
ie4uinit.exe -show

# Solution 2: Copy exe to new location
copy danki_app.exe danki_fixed.exe
```

**❌ "Module not found" errors:**
```bash
# Add missing modules to spec file
# Edit danki_app.spec, add to hiddenimports:
hiddenimports=['missing_module_name'],
```

**❌ Build fails with Qt errors:**
```bash
# Reinstall PyQt5
pip uninstall PyQt5
pip install PyQt5
```

**❌ Edge-TTS not working:**
- Ensure internet connection during build and runtime
- Edge-TTS requires online connectivity

### Build Optimization
```bash
# For smaller executable (optional)
pyinstaller danki_app.spec --exclude-module matplotlib --exclude-module scipy
```

## Verification Checklist

Before releasing:
- [ ] Executable icon displays correctly (custom Danki icon)
- [ ] Application launches on clean Windows system
- [ ] WordMaster processes German vocabulary
- [ ] PhraseMaster translates phrases
- [ ] TTS audio generation functions
- [ ] Preferences save/load properly
- [ ] No Python installation required to run
- [ ] File size reasonable (~50-100MB)
- [ ] Version number correct (v1.2.0)

---

## Quick Reference Commands

```bash
# Full build sequence
rmdir /s /q build dist 2>nul
pyinstaller danki_app.spec
dist\danki_app.exe

# Test built executable
cd dist && danki_app.exe

# Check icon in Explorer
explorer dist
```

---
**Note**: The key fix in v1.2 is the corrected icon syntax in `danki_app.spec` - changing from `icon=['icon.ico']` to `icon='icon.ico'` which should resolve the Windows icon display issue.