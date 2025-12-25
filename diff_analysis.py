"""
Manual word-by-word phone comparison
Native (macOS Samantha) vs Speaker (omer1.wav)
"""

# Raw outputs from Allosaurus
native = "ɔ ɹ d ɪ ŋ z w ɪ l b̥ i k l o w z d f ɔ ɹ θ æ ŋ k s g ɪ v ɪ ŋ d e j æ n d b̥ l æ k f ɹ ɒ j d i n o w v ɛ m b̥ ɹ̩ t w ɛ n tʰ i s ɛ v ə n θ æ n d t w ɛ n tʰ i e j tʰ t w ɛ n tʰ i t w ɛ n tʰ i f a j v w i w ɪ l b̥ i b̥ æ k ɪ n æ k ʃ ə n ɑ n m ʌ n d i d ɪ s ɛ m b̥ ɾ ɹ̩ f ɹ̩ s t"
speaker = "ɔ ɹ d ɪ ŋ z w ɪ lʲ ɪ k l o w z f ɔ ɾ t æ n z g i v ɪ ŋ lʲ e j æ n d b̥ l ɛ k f a j ɾ ə n o v ɛ m b̥ ə l s t w ɛ n tʰ i s ə v ə n s ə n t w æ n ð ə e j s t w ɛ n tʰ ə tʂʰ uə ɛ n ɳ lʲ i f a j lʲ w ɨ z b̥ iː b ɛ g iː n a k͡p̚ ʂ æ n o n m a n d ə ð ə s ʌ n d ɤ f ə s d ə b̞ e ɪ z o n ə i tʲ ɪ m s"

# Word-by-word segmentation (approximate)
comparisons = [
    ("boardings", "ɔ ɹ d ɪ ŋ z", "ɔ ɹ d ɪ ŋ z"),
    ("will", "w ɪ l", "w ɪ lʲ"),
    ("be", "b̥ i", "ɪ"),  # speaker drops it?
    ("closed", "k l o w z d", "k l o w z"),
    ("for", "f ɔ ɹ", "f ɔ ɾ"),
    ("Thanksgiving", "θ æ ŋ k s g ɪ v ɪ ŋ", "t æ n z g i v ɪ ŋ"),
    ("day", "d e j", "lʲ e j"),
    ("and", "æ n d", "æ n d"),
    ("Black", "b̥ l æ k", "b̥ l ɛ k"),
    ("Friday", "f ɹ ɒ j d i", "f a j ɾ ə"),
    ("November", "n o w v ɛ m b̥ ɹ̩", "n o v ɛ m b̥ ə l s"),
    ("twenty-seventh", "t w ɛ n tʰ i s ɛ v ə n θ", "t w ɛ n tʰ i s ə v ə n s"),
    ("and", "æ n d", "ə n"),
    ("twenty-eighth", "t w ɛ n tʰ i e j tʰ", "t w æ n ð ə e j s"),
    ("twenty", "t w ɛ n tʰ i", "t w ɛ n tʰ ə"),
    ("twenty-five", "t w ɛ n tʰ i f a j v", "tʂʰ uə ɛ n ɳ lʲ i f a j lʲ"),
    ("we", "w i", "w ɨ z"),
    ("will", "w ɪ l", "—"),
    ("be", "b̥ i", "b̥ iː"),
    ("back", "b̥ æ k", "b ɛ g"),
    ("in", "ɪ n", "iː n"),
    ("action", "æ k ʃ ə n", "a k͡p̚ ʂ æ n"),
    ("on", "ɑ n", "o n"),
    ("Monday", "m ʌ n d i", "m a n d ə"),
    ("December", "d ɪ s ɛ m b̥ ɾ ɹ̩", "ð ə s ʌ n d ɤ"),
    ("first", "f ɹ̩ s t", "f ə s d ə"),
]

print("="*80)
print("WORD-BY-WORD PHONE COMPARISON")
print("Native American English vs Hebrew-accented Speaker")
print("="*80)

print(f"\n{'WORD':<15} {'NATIVE':<30} {'SPEAKER':<30} {'ISSUE'}")
print("-"*80)

issues = {
    "θ→t/d": "TH-stopping (Hebrew has no θ/ð)",
    "ɹ→ɾ": "Tap R instead of approximant",
    "l→lʲ": "Palatalized L",
    "v→lʲ": "Unexpected substitution", 
    "vowel": "Vowel quality difference",
    "missing": "Missing sound",
    "extra": "Extra sound inserted",
}

for word, nat, spk in comparisons:
    # Detect issues
    detected = []
    if "θ" in nat and "θ" not in spk:
        detected.append("θ→t/d")
    if "ɹ" in nat and "ɾ" in spk:
        detected.append("ɹ→ɾ")
    if "lʲ" in spk and "lʲ" not in nat:
        detected.append("l→lʲ")
    if nat != spk and not detected:
        detected.append("diff")
    
    issue_str = ", ".join(detected) if detected else "✅"
    marker = "❌" if detected and detected != ["✅"] else "✅"
    
    print(f"{word:<15} {nat:<30} {spk:<30} {issue_str}")

print("\n" + "="*80)
print("KEY ACCENT MARKERS DETECTED")
print("="*80)
print("""
1. TH-STOPPING (θ → t, ð → d)
   - "Thanksgiving" → θ becomes t
   - "twenty-seventh" → θ becomes s  
   - Hebrew has no dental fricatives /θ, ð/
   
2. TAP R (ɹ → ɾ)  
   - "for" → ɹ becomes ɾ
   - "Friday" → ɹ becomes ɾ
   - Hebrew R is typically a tap or trill, not approximant
   
3. PALATALIZED L (l → lʲ)
   - "will" → l becomes lʲ
   - "day" → unexpected lʲ insertion
   - Hebrew L has different tongue position
   
4. VOWEL SHIFTS
   - "Black" → æ becomes ɛ  
   - "back" → æ becomes ɛ
   - "Monday" → ʌ becomes a
   - Hebrew vowel system is simpler (5 vowels vs English 15+)

5. FINAL CONSONANT ISSUES
   - "closed" → missing final d
   - "first" → d instead of t (voicing)
   - Hebrew word-final consonants handled differently
""")


