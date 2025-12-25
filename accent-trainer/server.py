"""
Backend API for accent trainer
Supports both Allosaurus and wav2vec2 models
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import tempfile
import os
import subprocess
import io
import json

app = Flask(__name__)
CORS(app)

# Lazy load models
allosaurus_model = None
wav2vec2_model = None
wav2vec2_processor = None
wav2vec2_vocab = None

def get_allosaurus():
    global allosaurus_model
    if allosaurus_model is None:
        print("Loading Allosaurus model...")
        from allosaurus.app import read_recognizer
        allosaurus_model = read_recognizer()
        print("Allosaurus loaded!")
    return allosaurus_model

def get_wav2vec2():
    global wav2vec2_model, wav2vec2_processor, wav2vec2_vocab
    if wav2vec2_model is None:
        print("Loading wav2vec2 model...")
        from transformers import Wav2Vec2ForCTC, Wav2Vec2FeatureExtractor
        from huggingface_hub import hf_hub_download
        import torch
        
        model_name = "facebook/wav2vec2-lv-60-espeak-cv-ft"
        wav2vec2_processor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
        wav2vec2_model = Wav2Vec2ForCTC.from_pretrained(model_name)
        
        vocab_path = hf_hub_download(repo_id=model_name, filename="vocab.json")
        with open(vocab_path, 'r') as f:
            vocab = json.load(f)
        wav2vec2_vocab = {v: k for k, v in vocab.items()}
        print("wav2vec2 loaded!")
    return wav2vec2_model, wav2vec2_processor, wav2vec2_vocab

# Example words for phoneme playback
PHONEME_EXAMPLES = {
    'θ': 'think', 'ð': 'the', 'ɹ': 'red', 'ɚ': 'butter',
    'æ': 'cat', 'ʌ': 'cup', 'ɑ': 'father', 'ɔ': 'thought',
    'ɛ': 'bed', 'ɪ': 'bit', 'i': 'see', 'u': 'too',
    'ə': 'about', 'ŋ': 'sing', 'ʃ': 'ship', 'tʃ': 'church',
    'a': 'my', 'w': 'we', 'v': 'very', 'n': 'no', 
    'm': 'me', 'l': 'love', 'k': 'cat', 't': 'top', 
    'd': 'dog', 'b': 'boy', 'p': 'pen', 's': 'sun', 
    'z': 'zoo', 'f': 'fish', 'h': 'hat', 'ɡ': 'go', 
    'j': 'yes', 'o': 'go', 'ɜ': 'bird', 'ʊ': 'book',
}

# Similar phones - what counts as "close enough"
SIMILAR_PHONES = {
    'θ': {'θ', 't', 's', 'f'},
    'ð': {'ð', 'd', 'z', 'v'},
    'ɹ': {'ɹ', 'r', 'ɾ', 'l', 'w', 'ʋ'},
    'r': {'ɹ', 'r', 'ɾ', 'l'},
    'æ': {'æ', 'ɛ', 'a', 'e'},
    'ʌ': {'ʌ', 'a', 'ə', 'ɐ'},
    'ɑ': {'ɑ', 'a', 'ɔ', 'o', 'ɒ'},
    'ɔ': {'ɔ', 'o', 'ɑ', 'ɒ'},
    'i': {'i', 'ɪ', 'iː', 'e'},
    'ɪ': {'ɪ', 'i', 'e', 'ɨ'},
    'u': {'u', 'ʊ', 'uː', 'w'},
    'ʊ': {'ʊ', 'u', 'o'},
    'ɛ': {'ɛ', 'e', 'æ'},
    'ə': {'ə', 'ʌ', 'ɨ', 'a', 'ɐ'},
    'ɚ': {'ɚ', 'ə', 'ɹ', 'ɝ', 'ɜ'},
    'ɜ': {'ɜ', 'ɚ', 'ə', 'ɝ', '3'},
    'v': {'v', 'w', 'b', 'f', 'β'},
    'w': {'w', 'v', 'u', 'ʋ'},
    'l': {'l', 'lʲ', 'ɫ', 'ɹ'},
    'n': {'n', 'ŋ', 'm', 'ɲ'},
    'ŋ': {'ŋ', 'n', 'ɡ', 'g'},
    'ʃ': {'ʃ', 's', 'ʂ'},
    'tʃ': {'tʃ', 'tʂ', 't', 'ʃ'},
    'b': {'b', 'b̥', 'p', 'β'},
    'd': {'d', 'd̥', 't', 'ɾ'},
    'ɡ': {'ɡ', 'g', 'k'},
    'g': {'ɡ', 'g', 'k'},
    'k': {'k', 'kʰ', 'ɡ', 'g'},
    't': {'t', 'tʰ', 'd', 'ɾ'},
    'p': {'p', 'pʰ', 'b'},
    'a': {'a', 'ɑ', 'æ', 'ʌ', 'ɐ'},
    'j': {'j', 'i', 'ʝ'},
    'o': {'o', 'ɔ', 'oʊ', 'əʊ', 'ʊ'},
    's': {'s', 'z', 'ʃ'},
    'z': {'z', 's', 'ʒ'},
    'f': {'f', 'v', 'θ'},
    'h': {'h', 'ɦ', 'x'},
    'm': {'m', 'n', 'ɱ'},
}

def normalize_phone(phone: str) -> str:
    """Remove diacritics and normalize phone"""
    # Remove common diacritics
    for diacritic in ['ʲ', 'ʰ', '̥', '̩', 'ː', '̪', '̃', '̚', '͡']:
        phone = phone.replace(diacritic, '')
    return phone

def phones_similar(p1: str, p2: str) -> bool:
    """Check if two phones are similar enough to count as correct"""
    if p1 == p2:
        return True
    
    # Normalize both
    p1_norm = normalize_phone(p1)
    p2_norm = normalize_phone(p2)
    
    if p1_norm == p2_norm:
        return True
    
    # Check similarity sets
    similar_set = SIMILAR_PHONES.get(p1_norm, {p1_norm})
    if p2_norm in similar_set:
        return True
    
    # Check reverse
    similar_set2 = SIMILAR_PHONES.get(p2_norm, {p2_norm})
    if p1_norm in similar_set2:
        return True
    
    return False

def align_sequences(expected: list, actual: list) -> list:
    """
    Align two phone sequences using dynamic programming (edit distance style)
    Returns list of {expected, actual, correct} for each expected phone
    """
    n, m = len(expected), len(actual)
    
    # DP table: dp[i][j] = (cost, backtrack_direction)
    # 0 = match/substitute, 1 = delete (skip actual), 2 = insert (skip expected)
    INF = float('inf')
    
    # Cost matrix
    dp = [[INF] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0
    
    # Initialize first row and column
    for i in range(1, n + 1):
        dp[i][0] = i  # deletions from expected
    for j in range(1, m + 1):
        dp[0][j] = j  # insertions from actual
    
    # Fill DP table
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            # Match or substitute
            is_match = phones_similar(expected[i-1], actual[j-1])
            sub_cost = 0 if is_match else 1
            
            dp[i][j] = min(
                dp[i-1][j-1] + sub_cost,  # match/substitute
                dp[i-1][j] + 1,            # delete from expected (no actual match)
                dp[i][j-1] + 0.5           # skip actual phone (insertion, lower cost)
            )
    
    # Backtrack to get alignment
    results = []
    i, j = n, m
    alignment = []
    
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            is_match = phones_similar(expected[i-1], actual[j-1])
            sub_cost = 0 if is_match else 1
            
            if dp[i][j] == dp[i-1][j-1] + sub_cost:
                # Match or substitute
                alignment.append((expected[i-1], actual[j-1], is_match))
                i -= 1
                j -= 1
            elif dp[i][j] == dp[i-1][j] + 1:
                # Skip expected (no match in actual)
                alignment.append((expected[i-1], None, False))
                i -= 1
            else:
                # Skip actual (extra phone detected)
                j -= 1
        elif i > 0:
            alignment.append((expected[i-1], None, False))
            i -= 1
        else:
            j -= 1
    
    # Reverse alignment
    alignment.reverse()
    
    # Convert to result format
    for exp, act, correct in alignment:
        results.append({
            'expected': exp,
            'actual': act,
            'correct': correct
        })
    
    return results

def recognize_with_allosaurus(wav_path: str) -> str:
    model = get_allosaurus()
    return model.recognize(wav_path)

def recognize_with_wav2vec2(wav_path: str) -> str:
    import torch
    import librosa
    
    model, processor, vocab = get_wav2vec2()
    audio, sr = librosa.load(wav_path, sr=16000)
    input_values = processor(audio, sampling_rate=16000, return_tensors="pt").input_values
    
    with torch.no_grad():
        logits = model(input_values).logits
    
    predicted_ids = torch.argmax(logits, dim=-1)[0].tolist()
    
    prev_id = None
    phonemes = []
    for idx in predicted_ids:
        if idx != prev_id and idx != 0:
            token = vocab.get(idx, '?')
            if token not in ['<pad>', '<s>', '</s>', '<unk>']:
                phonemes.append(token)
        prev_id = idx
    
    return ' '.join(phonemes)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        expected = request.form.get('expected', '[]')
        model_type = request.form.get('model', 'allosaurus')
        
        expected_phones = json.loads(expected)
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
            audio_file.save(f.name)
            webm_path = f.name
        
        # Convert to wav
        wav_path = webm_path.replace('.webm', '.wav')
        subprocess.run([
            'ffmpeg', '-y', '-i', webm_path, 
            '-ar', '16000', '-ac', '1', 
            wav_path
        ], capture_output=True)
        
        # Recognize
        if model_type == 'wav2vec2':
            phones_str = recognize_with_wav2vec2(wav_path)
        else:
            phones_str = recognize_with_allosaurus(wav_path)
        
        actual_phones = phones_str.split()
        
        # Clean up
        os.unlink(webm_path)
        os.unlink(wav_path)
        
        # Use proper alignment
        comparison = align_sequences(expected_phones, actual_phones)
        
        # Debug: print comparison
        print(f"Expected: {expected_phones}")
        print(f"Actual:   {actual_phones}")
        for c in comparison:
            print(f"  {c['expected']} vs {c['actual']} -> {'✓' if c['correct'] else '✗'}")
        
        return jsonify({
            'phonemes': actual_phones,
            'comparison': comparison,
            'raw': phones_str,
            'model': model_type
        })
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/speak', methods=['POST'])
def speak():
    try:
        data = request.json
        phoneme = data.get('phoneme', '')
        example_word = PHONEME_EXAMPLES.get(phoneme, phoneme)
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            wav_path = f.name
        
        subprocess.run([
            'espeak-ng', '-v', 'en-us', '-s', '120', '-p', '50',
            '-w', wav_path, example_word
        ], capture_output=True)
        
        with open(wav_path, 'rb') as f:
            audio_data = f.read()
        
        os.unlink(wav_path)
        
        return send_file(io.BytesIO(audio_data), mimetype='audio/wav')
        
    except Exception as e:
        print(f"Speak error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    get_allosaurus()
    app.run(port=5001, debug=True)
