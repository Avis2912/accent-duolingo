from transformers import Wav2Vec2ForCTC, Wav2Vec2FeatureExtractor
import torch
import librosa
import json
from huggingface_hub import hf_hub_download

# Load model and components
print("Loading model and processor...")
model_name = "facebook/wav2vec2-lv-60-espeak-cv-ft"

feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
model = Wav2Vec2ForCTC.from_pretrained(model_name)

# Download and load vocab manually
vocab_path = hf_hub_download(repo_id=model_name, filename="vocab.json")
with open(vocab_path, 'r') as f:
    vocab = json.load(f)

# Create id2token mapping
id2token = {v: k for k, v in vocab.items()}

print("Model loaded successfully!")

# Load audio at 16kHz (required by wav2vec2)
print("Loading audio...")
audio, sr = librosa.load("omer2.wav", sr=16000)
print(f"Audio duration: {len(audio)/sr:.2f} seconds")

# Process audio
input_values = feature_extractor(audio, sampling_rate=16000, return_tensors="pt").input_values

# Retrieve logits
print("Running inference...")
with torch.no_grad():
    logits = model(input_values).logits

# Take argmax and decode
predicted_ids = torch.argmax(logits, dim=-1)[0].tolist()

# Decode manually - collapse repeated tokens and remove blanks
prev_id = None
phonemes = []
for idx in predicted_ids:
    if idx != prev_id and idx != 0:  # 0 is typically the blank token
        token = id2token.get(idx, '?')
        if token not in ['<pad>', '<s>', '</s>', '<unk>']:
            phonemes.append(token)
    prev_id = idx

transcription = ' '.join(phonemes)

print("\n✅ Phoneme transcription:")
print(transcription)
print("\n📝 Original text: 'Hello world, this is a test'")
