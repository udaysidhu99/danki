# Danki - TODO List

## High Priority

### 1. Configurable Article TTS
**Status:** Planned  
**Priority:** High  
**Branch:** TBD

**Description:**
Currently, the TTS audio includes the article with the word (e.g., "der Mann" instead of just "Mann"). Add a user preference to make this configurable.

**Implementation Details:**
- Add checkbox in Preferences tab: "Include article in TTS pronunciation"
- Default: ON (current behavior)
- When OFF: TTS should only pronounce the base word without article
- Modify `generate_tts_audio()` function in `danki_app.py`:
  - Check preference setting before generating audio
  - If article should be excluded, strip `artikel_d` from TTS input
  - Example: "der Mann" → "Mann" for TTS, but full "der Mann" still displayed in card
- Save preference to `~/.danki/gemini_config.json`
- Affects both new cards and regenerated audio

**Files to Modify:**
- `danki_app.py`:
  - Add checkbox to preferences UI
  - Update `load_config()` / `save_config()` for new setting
  - Modify `generate_tts_audio()` to conditionally include/exclude article
  - Update `process_words()` to pass preference to TTS function

**Testing:**
- Test with article included (default)
- Test with article excluded
- Verify preference persists across app restarts
- Test with various noun genders (der/die/das)

---

## Medium Priority

### 2. Complete Offline Dictionary Integration
**Status:** In Progress  
**Priority:** High  
**Branch:** `offline-dictionary`

**Description:**
Integrate the offline German-English dictionary into the main application to reduce API calls and improve performance.

**Current Progress:**
- ✅ Dictionary infrastructure created (`dictionary/` folder)
- ✅ Word list downloaded (50,000 German words from OpenSubtitles)
- ✅ Parser script completed (`parse_wordlist.py`)
- ✅ Dictionary builder completed (`build_dictionary.py`)
- ✅ Parallel builder created for faster processing (`build_dictionary_parallel.py`)
- ✅ Merge script for combining parallel results (`merge_dictionaries.py`)
- 🔄 Dictionary building in progress (5,000 words)

**Remaining Tasks:**
1. **Complete dictionary build** (currently running with 4 parallel workers)
2. **Post-build deduplication:**
   - Create `deduplicate_dictionary.py`
   - Remove duplicate base forms where `input_form` differs but `word` is the same
   - Merge conjugated forms that normalized to the same base
   - Expected reduction: 5,000 → ~3,500-4,000 unique base forms

3. **Add capitalized noun variants:**
   - Create script to identify common nouns from the 5,000 words
   - Generate capitalized versions (e.g., add "Essen" if "essen" exists)
   - Build supplementary dictionary for ~500-1,000 capitalized nouns
   - Handle case-sensitive lookups (Essen = food vs essen = to eat)

4. **Integrate into danki_app.py:**
   - Add `get_resource_path()` function for PyInstaller compatibility
   - Load dictionary at startup: `GERMAN_DICT = load_dictionary()`
   - Implement `lookup_word(word)` function:
     - Try exact match first (case-sensitive)
     - Try lowercase match as fallback
     - Return None if not found (triggers API fallback)
   - Modify `process_words()` to check dictionary before calling `query_gemini()`
   - Add preference: "Always use AI (skip dictionary)" checkbox
   - Keep German→English only in dictionary; other languages use API

5. **Update PyInstaller bundling:**
   - Modify `Danki.spec`:
     ```python
     datas=[
         ('dictionary/german_english_dict.json', 'dictionary'),
         ('icon.icns', '.'),
         # existing resources
     ]
     ```
   - Test bundled .app includes dictionary
   - Verify dictionary loads correctly from bundle

6. **End-to-end testing:**
   - Test common word lookup (should use dictionary)
   - Test rare word lookup (should fall back to API)
   - Test capitalization handling (Essen vs essen)
   - Test conjugated form lookup (läuft should find laufen)
   - Test Spanish/Hindi/French translations (should use API, not dictionary)
   - Verify "Always use AI" preference bypasses dictionary

**Files to Create:**
- `dictionary/deduplicate_dictionary.py`
- `dictionary/build_capitalized_nouns.py` (optional)

**Files to Modify:**
- `danki_app.py` (dictionary integration)
- `Danki.spec` (PyInstaller bundling)
- `CLAUDE.md` (update progress)

**Performance Metrics:**
- Dictionary lookup: O(1) hash table, <1ms
- File size: ~2-3 MB JSON (bundled in .app)
- Coverage: 80-90% of daily German usage
- API call reduction: 90%+ for common vocabulary

---

### 3. Replace edge-tts with Platform-Specific TTS
**Status:** Planned  
**Priority:** Medium  
**Branch:** TBD

**Description:**
Replace the current `edge-tts` implementation with native platform-specific TTS to reduce dependencies and app size.

**Implementation Details:**
- **macOS:** Use `say` command (built-in)
  - Voices: "Anna" (de-DE), "Petra" (de-DE)
  - Example: `say -v Anna "Guten Tag" -o output.aiff`
  - Convert AIFF to MP3 if needed for Anki compatibility

- **Windows:** Use Windows SAPI or `pyttsx3`
  - Install German voice pack if not present
  - Fallback to `pyttsx3` library

**Benefits:**
- Smaller app bundle (remove async dependencies)
- No internet required for TTS
- Native OS integration
- Faster audio generation

**Files to Modify:**
- `danki_app.py`:
  - Replace `generate_tts_audio()` function
  - Add platform detection: `platform.system()`
  - Implement macOS version with `subprocess.run(['say', ...])`
  - Implement Windows version with SAPI/pyttsx3
  - Remove `edge-tts` and `asyncio` imports

**Testing:**
- Test on macOS with different voices
- Test on Windows with SAPI
- Verify audio format compatibility with Anki
- Compare audio quality with edge-tts

---

## Low Priority

### 4. Vocabulary Statistics Dashboard
**Status:** Idea  
**Priority:** Low

**Description:**
Add a statistics tab showing vocabulary learning metrics.

**Potential Features:**
- Total words added to Anki
- Words added per day/week/month
- Most frequent parts of speech added
- API vs dictionary lookup ratio
- Coverage percentage (how many lookups hit dictionary)
- Graph of vocabulary growth over time

**Implementation:**
- Store metrics in `~/.danki/stats.json`
- Add new tab to GUI with charts (using matplotlib or similar)
- Track each word addition with timestamp
- Calculate and display statistics on demand

---

### 5. Batch Import from Text Files
**Status:** Idea  
**Priority:** Low

**Description:**
Allow users to import vocabulary lists from text files or CSV.

**Features:**
- File picker dialog
- Support formats: TXT (one word per line), CSV (word, context)
- Batch processing with progress bar
- Option to preview words before import
- Duplicate detection across entire batch

---

### 6. Custom Example Sentences
**Status:** Idea  
**Priority:** Low

**Description:**
Allow users to provide their own example sentences instead of AI-generated ones.

**Features:**
- Text field for custom sentence input
- Option: "Use custom sentence" checkbox
- Still generate translation with AI
- Store custom sentences with metadata flag
- Preference: "Always request custom sentences" mode

---

## Completed

### ✅ Offline Dictionary - Infrastructure Setup
**Completed:** January 31, 2026

- Created `dictionary/` folder structure
- Downloaded German frequency word list (50,000 words)
- Built parser for extracting valid German words
- Created dictionary builder with OpenAI API integration
- Implemented full verb conjugations (16 forms)
- Added 3 example sentences per word
- Implemented LLM-based normalization for conjugated forms
- Created parallel builder for 4x speed improvement
- Built merge script for combining parallel results

---

## Notes

### Contribution Guidelines
When adding to this TODO:
1. Use clear, descriptive titles
2. Include status: Planned / In Progress / Blocked / Completed
3. Set priority: High / Medium / Low
4. Provide detailed implementation notes
5. List all files that need modification
6. Include testing criteria
7. Move completed items to "Completed" section with date

### Priority Definitions
- **High:** Core functionality, user-requested, performance improvements
- **Medium:** Nice-to-have features, optimizations, refactoring
- **Low:** Future ideas, experimental features, convenience improvements

### Status Definitions
- **Planned:** Approved for implementation, not started
- **In Progress:** Actively being worked on
- **Blocked:** Waiting on dependencies or decisions
- **Completed:** Finished and merged
