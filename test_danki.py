import pyttsx3

def save_tts(text, filename):
    # Use espeak backend on macOS (default `nsss` does not support save_to_file)
    engine = pyttsx3.init(driverName='espeak')
    engine.save_to_file(text, filename)
    engine.runAndWait()
    print(f"Saved TTS audio to {filename}")

if __name__ == "__main__":
    text = "Hallo, wie geht es dir?"
    filename = "test_output.mp3"
    save_tts(text, filename)