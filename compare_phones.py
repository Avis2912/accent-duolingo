from allosaurus.app import read_recognizer

print("Loading Allosaurus model...")
model = read_recognizer()

print("\n" + "="*70)
print("NATIVE ENGLISH REFERENCE (macOS Samantha voice)")
print("="*70)
native_phones = model.recognize("reference_native.wav")
print(native_phones)

print("\n" + "="*70)
print("SPEAKER RECORDING (omer1.wav)")
print("="*70)
speaker_phones = model.recognize("omer1.wav")
print(speaker_phones)

print("\n" + "="*70)
print("SIDE-BY-SIDE COMPARISON")
print("="*70)

# Split into lists for easier comparison
native_list = native_phones.split()
speaker_list = speaker_phones.split()

print(f"\nNative phones:  {len(native_list)} phones")
print(f"Speaker phones: {len(speaker_list)} phones")

# Show first 50 phones side by side
print("\n{:<20} {:<20}".format("NATIVE", "SPEAKER"))
print("-" * 40)
max_len = max(len(native_list), len(speaker_list))
for i in range(min(60, max_len)):
    n = native_list[i] if i < len(native_list) else "-"
    s = speaker_list[i] if i < len(speaker_list) else "-"
    match = "✅" if n == s else "❌"
    print(f"{n:<20} {s:<20} {match}")

