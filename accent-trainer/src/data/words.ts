// Sentence list with expected American English phonemes
export interface SentenceEntry {
  sentence: string;
  phonemes: string[];  // Expected phonemes (Allosaurus-style)
  ipa: string;         // Display IPA
}

export const sentenceList: SentenceEntry[] = [
  {
    sentence: "The weather is nice.",
    phonemes: ["ð", "ə", "w", "ɛ", "ð", "ə", "ɪ", "z", "n", "a", "j", "s"],
    ipa: "/ðə ˈwɛðər ɪz naɪs/"
  },
  {
    sentence: "I think so.",
    phonemes: ["a", "j", "θ", "ɪ", "ŋ", "k", "s", "o", "w"],
    ipa: "/aɪ θɪŋk soʊ/"
  },
  {
    sentence: "This is my brother.",
    phonemes: ["ð", "ɪ", "s", "ɪ", "z", "m", "a", "j", "b", "ɹ", "ʌ", "ð", "ə"],
    ipa: "/ðɪs ɪz maɪ ˈbrʌðər/"
  },
  {
    sentence: "Where is the water?",
    phonemes: ["w", "ɛ", "ɹ", "ɪ", "z", "ð", "ə", "w", "ɔ", "t", "ə"],
    ipa: "/wɛr ɪz ðə ˈwɔtər/"
  },
  {
    sentence: "Three things matter.",
    phonemes: ["θ", "ɹ", "i", "θ", "ɪ", "ŋ", "z", "m", "æ", "t", "ə"],
    ipa: "/θri θɪŋz ˈmætər/"
  },
  {
    sentence: "Thank you very much.",
    phonemes: ["θ", "æ", "ŋ", "k", "j", "u", "v", "ɛ", "ɹ", "i", "m", "ʌ", "tʃ"],
    ipa: "/θæŋk ju ˈvɛri mʌtʃ/"
  },
  {
    sentence: "What do you think?",
    phonemes: ["w", "ʌ", "t", "d", "u", "j", "u", "θ", "ɪ", "ŋ", "k"],
    ipa: "/wʌt du ju θɪŋk/"
  },
  {
    sentence: "Father and mother.",
    phonemes: ["f", "ɑ", "ð", "ə", "æ", "n", "d", "m", "ʌ", "ð", "ə"],
    ipa: "/ˈfɑðər ænd ˈmʌðər/"
  },
  {
    sentence: "Right or wrong?",
    phonemes: ["ɹ", "a", "j", "t", "ɔ", "ɹ", "ɹ", "ɔ", "ŋ"],
    ipa: "/raɪt ɔr rɔŋ/"
  },
  {
    sentence: "Hello world.",
    phonemes: ["h", "ə", "l", "o", "w", "w", "ɜ", "ɹ", "l", "d"],
    ipa: "/həˈloʊ wɜrld/"
  },
  {
    sentence: "Good morning.",
    phonemes: ["ɡ", "ʊ", "d", "m", "ɔ", "ɹ", "n", "ɪ", "ŋ"],
    ipa: "/ɡʊd ˈmɔrnɪŋ/"
  },
  {
    sentence: "How are you?",
    phonemes: ["h", "a", "w", "ɑ", "ɹ", "j", "u"],
    ipa: "/haʊ ɑr ju/"
  },
];

// Phoneme info for learning
export const phonemeInfo: Record<string, { description: string; example: string; tip: string }> = {
  "θ": {
    description: "Voiceless TH",
    example: "think, three, bath",
    tip: "Put tongue between teeth, blow air without vibrating throat"
  },
  "ð": {
    description: "Voiced TH", 
    example: "the, this, brother",
    tip: "Put tongue between teeth, vibrate your throat"
  },
  "ɹ": {
    description: "American R",
    example: "red, right, car",
    tip: "Curl tongue back, don't touch roof of mouth"
  },
  "ɚ": {
    description: "R-colored schwa",
    example: "water, butter, never",
    tip: "Relaxed 'uh' + R sound combined"
  },
  "æ": {
    description: "Short A",
    example: "cat, man, hand",
    tip: "Open mouth wide, tongue low and front"
  },
  "ʌ": {
    description: "Short U",
    example: "cup, love, mother",
    tip: "Short, relaxed 'uh' in the middle of mouth"
  },
  "ɑ": {
    description: "Open A",
    example: "father, calm, spa",
    tip: "Open mouth wide, tongue low and back"
  },
  "ɔ": {
    description: "Open O",
    example: "thought, caught, all",
    tip: "Round lips slightly, back of tongue raised"
  },
  "ɛ": {
    description: "Short E",
    example: "bed, head, said", 
    tip: "Mouth slightly open, tongue mid-front"
  },
  "ɪ": {
    description: "Short I",
    example: "bit, will, this",
    tip: "Short 'ih' sound, relaxed tongue"
  },
  "i": {
    description: "Long E",
    example: "see, we, easy",
    tip: "Smile position, tongue high and front"
  },
  "u": {
    description: "Long U",
    example: "too, blue, through",
    tip: "Round lips tightly, tongue high and back"
  },
  "ə": {
    description: "Schwa",
    example: "about, the, banana",
    tip: "Most relaxed vowel, mouth barely open"
  },
  "ŋ": {
    description: "NG sound",
    example: "sing, thing, going",
    tip: "Back of tongue touches soft palate"
  },
  "ʃ": {
    description: "SH sound",
    example: "she, fish, action",
    tip: "Lips rounded, air through teeth gap"
  },
  "tʃ": {
    description: "CH sound",
    example: "church, watch, much",
    tip: "Start with T, release into SH"
  },
  "w": {
    description: "W sound",
    example: "we, water, with",
    tip: "Round lips tight, then open to vowel"
  },
  "v": {
    description: "V sound",
    example: "very, love, never",
    tip: "Upper teeth on lower lip, vibrate throat"
  },
  "a": {
    description: "Open A / diphthong start",
    example: "my, high, time",
    tip: "Start of 'ai' diphthong, open mouth"
  },
  "j": {
    description: "Y glide",
    example: "yes, you, beyond",
    tip: "Like 'ee' but quickly glides to next sound"
  },
  "o": {
    description: "O sound",
    example: "go, so, no",
    tip: "Round lips, back vowel"
  },
  "ɜ": {
    description: "UR vowel",
    example: "bird, world, hurt",
    tip: "Like 'er' without the final R sound"
  },
  "ʊ": {
    description: "Short OO",
    example: "book, good, put",
    tip: "Short, relaxed 'oo' sound"
  },
  "ɡ": {
    description: "G sound",
    example: "go, big, dog",
    tip: "Back of tongue touches soft palate, voiced"
  },
};
