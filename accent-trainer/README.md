# Accent Trainer

A minimal pronunciation training app that uses Allosaurus for phone recognition.

## Setup

### 1. Install Frontend Dependencies

```bash
cd accent-trainer
npm install
```

### 2. Install Backend Dependencies

```bash
pip install flask flask-cors allosaurus
```

Also make sure you have `ffmpeg` installed:
```bash
brew install ffmpeg
```

### 3. Run the App

**Terminal 1 - Backend:**
```bash
python server.py
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

Open http://localhost:5173

## How It Works

1. A word is displayed
2. Click the record button and say the word
3. Your pronunciation is analyzed by Allosaurus
4. Phonemes are shown in green (correct) or red (needs work)
5. Click any phoneme to hear how it should sound

## Tech Stack

- **Frontend:** React + TypeScript + Vite + Tailwind + Framer Motion
- **Backend:** Flask + Allosaurus
- **Phone Recognition:** Allosaurus universal phone recognizer


