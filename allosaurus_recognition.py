from allosaurus.app import read_recognizer

# Load the universal phone recognizer
print("Loading Allosaurus model...")
model = read_recognizer()

# Recognize phones from audio
print("Processing audio...")
audio_file = "omer1.wav"

# Default: outputs IPA phones with timestamps
phones = model.recognize(audio_file)
print("\n✅ Phone transcription (narrow):")
print(phones)

# You can also get phones with timestamps
print("\n📍 Phones with timestamps:")
phones_with_time = model.recognize(audio_file, timestamp=True)
print(phones_with_time[:500] + "..." if len(phones_with_time) > 500 else phones_with_time)

# Compare to the original wav2vec2 output
print("\n" + "="*60)
print("COMPARISON")
print("="*60)
print("\nwav2vec2 (English phonemes):")
print("b oʊ d ɪ ŋ z w ɪ l b iː k l oʊ z d f ɔːɹ t eɪ ŋ s ɡ iː v ɪ ŋ...")
print("\nAllosaurus (universal phones):")
print(phones[:100] + "..." if len(phones) > 100 else phones)


