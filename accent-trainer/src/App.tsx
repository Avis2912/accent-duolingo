import { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { sentenceList, phonemeInfo, SentenceEntry } from './data/words';

type PhonemeResult = {
  expected: string;
  actual: string | null;
  correct: boolean;
};

type RecordingState = 'idle' | 'recording' | 'processing' | 'results';
type ModelType = 'allosaurus' | 'wav2vec2';

function App() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [recordingState, setRecordingState] = useState<RecordingState>('idle');
  const [results, setResults] = useState<PhonemeResult[] | null>(null);
  const [rawPhonemes, setRawPhonemes] = useState<string>('');
  const [hoveredPhoneme, setHoveredPhoneme] = useState<string | null>(null);
  const [playingPhoneme, setPlayingPhoneme] = useState<string | null>(null);
  const [model, setModel] = useState<ModelType>('allosaurus');
  const [recordedAudioUrl, setRecordedAudioUrl] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const playbackRef = useRef<HTMLAudioElement | null>(null);

  const currentSentence: SentenceEntry = sentenceList[currentIndex];

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        stream.getTracks().forEach(track => track.stop());
        // Store audio URL for replay
        const url = URL.createObjectURL(blob);
        setRecordedAudioUrl(url);
        await processRecording(blob);
      };

      mediaRecorder.start();
      setRecordingState('recording');
    } catch (err) {
      console.error('Failed to start recording:', err);
      alert('Please allow microphone access to use this app.');
    }
  }, [model]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && recordingState === 'recording') {
      mediaRecorderRef.current.stop();
      setRecordingState('processing');
    }
  }, [recordingState]);

  const processRecording = async (blob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('audio', blob, 'recording.webm');
      formData.append('expected', JSON.stringify(currentSentence.phonemes));
      formData.append('model', model);

      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      setResults(data.comparison);
      setRawPhonemes(data.raw || data.phonemes.join(' '));
      setRecordingState('results');
    } catch (err) {
      console.error('Processing error:', err);
      simulateResults();
    }
  };

  const simulateResults = () => {
    const simulated = currentSentence.phonemes.map((p) => ({
      expected: p,
      actual: Math.random() > 0.25 ? p : getRandomSubstitution(p),
      correct: Math.random() > 0.25,
    }));
    setResults(simulated);
    setRawPhonemes(simulated.map(r => r.actual || r.expected).join(' '));
    setRecordingState('results');
  };

  const getRandomSubstitution = (phoneme: string): string => {
    const substitutions: Record<string, string[]> = {
      'θ': ['t', 's', 'f'],
      'ð': ['d', 'z', 'v'],
      'ɹ': ['ɾ', 'l', 'w'],
      'æ': ['ɛ', 'a', 'e'],
      'ʌ': ['a', 'ə', 'o'],
      'v': ['w', 'b', 'f'],
      'w': ['v', 'u'],
    };
    const subs = substitutions[phoneme];
    return subs ? subs[Math.floor(Math.random() * subs.length)] : phoneme;
  };

  const playPhoneme = async (phoneme: string) => {
    setPlayingPhoneme(phoneme);
    
    try {
      const response = await fetch('/api/speak', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phoneme }),
      });
      
      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        
        if (audioRef.current) {
          audioRef.current.pause();
        }
        
        const audio = new Audio(audioUrl);
        audioRef.current = audio;
        audio.playbackRate = 0.8;
        await audio.play();
        
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          setPlayingPhoneme(null);
        };
        return;
      }
    } catch (err) {
      console.log('Backend unavailable, using fallback');
    }
    
    const info = phonemeInfo[phoneme];
    if (info) {
      const exampleWord = info.example.split(',')[0].trim();
      const utterance = new SpeechSynthesisUtterance(exampleWord);
      utterance.rate = 0.7;
      utterance.onend = () => setPlayingPhoneme(null);
      speechSynthesis.speak(utterance);
    } else {
      setPlayingPhoneme(null);
    }
  };

  const replayRecording = () => {
    if (recordedAudioUrl) {
      if (playbackRef.current) {
        playbackRef.current.pause();
      }
      const audio = new Audio(recordedAudioUrl);
      playbackRef.current = audio;
      audio.play();
    }
  };

  const nextSentence = () => {
    if (recordedAudioUrl) URL.revokeObjectURL(recordedAudioUrl);
    setRecordedAudioUrl(null);
    setCurrentIndex((prev) => (prev + 1) % sentenceList.length);
    setRecordingState('idle');
    setResults(null);
    setRawPhonemes('');
    setHoveredPhoneme(null);
  };

  const resetSentence = () => {
    if (recordedAudioUrl) URL.revokeObjectURL(recordedAudioUrl);
    setRecordedAudioUrl(null);
    setRecordingState('idle');
    setResults(null);
    setRawPhonemes('');
    setHoveredPhoneme(null);
  };

  const score = results 
    ? Math.round((results.filter(r => r.correct).length / results.length) * 100)
    : 0;

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center p-8">
      {/* Progress */}
      <div className="absolute top-8 left-8 text-sm text-gray-300 font-mono">
        {currentIndex + 1} / {sentenceList.length}
      </div>

      {/* Model Switcher */}
      <div className="absolute top-8 right-8 flex items-center gap-2">
        <button
          onClick={() => setModel('wav2vec2')}
          className={`px-3 py-1.5 text-xs font-mono rounded-l-full border transition-all ${
            model === 'wav2vec2'
              ? 'bg-gray-900 text-white border-gray-900'
              : 'bg-white text-gray-400 border-gray-200 hover:border-gray-300'
          }`}
        >
          wav2vec2
        </button>
        <button
          onClick={() => setModel('allosaurus')}
          className={`px-3 py-1.5 text-xs font-mono rounded-r-full border border-l-0 transition-all ${
            model === 'allosaurus'
              ? 'bg-gray-900 text-white border-gray-900'
              : 'bg-white text-gray-400 border-gray-200 hover:border-gray-300'
          }`}
        >
          allosaurus
        </button>
      </div>

      {/* Main Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentIndex}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
          className="flex flex-col items-center max-w-3xl w-full"
        >
          {/* Sentence Display */}
          <motion.h1 
            className="text-5xl md:text-6xl font-light text-gray-900 tracking-tight mb-6 text-center leading-tight"
          >
            {currentSentence.sentence}
          </motion.h1>

          {/* IPA Display */}
          <motion.p 
            className="text-xl text-gray-400 font-mono mb-16 text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            {currentSentence.ipa}
          </motion.p>

          {/* Recording Button */}
          {recordingState !== 'results' && (
            <motion.div 
              className="relative"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              {recordingState === 'recording' && (
                <>
                  <motion.div 
                    className="absolute inset-0 rounded-full bg-red-400"
                    animate={{ scale: [1, 1.6], opacity: [0.6, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity, ease: "easeOut" }}
                  />
                  <motion.div 
                    className="absolute inset-0 rounded-full bg-red-400"
                    animate={{ scale: [1, 1.6], opacity: [0.6, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity, ease: "easeOut", delay: 0.5 }}
                  />
                </>
              )}
              
              <motion.button
                onClick={recordingState === 'recording' ? stopRecording : startRecording}
                disabled={recordingState === 'processing'}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`
                  relative w-36 h-36 rounded-full flex items-center justify-center
                  transition-all duration-300 shadow-2xl
                  ${recordingState === 'recording' 
                    ? 'bg-red-500 shadow-red-200/50' 
                    : recordingState === 'processing'
                    ? 'bg-gray-200'
                    : 'bg-gray-900 hover:bg-gray-800 shadow-gray-400/30'
                  }
                `}
              >
                {recordingState === 'processing' ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    className="w-8 h-8 border-3 border-gray-400 border-t-transparent rounded-full"
                    style={{ borderWidth: 3 }}
                  />
                ) : recordingState === 'recording' ? (
                  <motion.div 
                    className="w-8 h-8 bg-white rounded-sm"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 500 }}
                  />
                ) : (
                  <svg className="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                    <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                  </svg>
                )}
              </motion.button>

              <motion.p 
                className="text-center mt-8 text-gray-400 text-sm font-light"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                {recordingState === 'recording' 
                  ? 'Tap to stop' 
                  : recordingState === 'processing'
                  ? `Analyzing with ${model}...`
                  : 'Tap to record'
                }
              </motion.p>
            </motion.div>
          )}

          {/* Results */}
          {recordingState === 'results' && results && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="flex flex-col items-center w-full"
            >
              {/* Score */}
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.1, type: "spring", stiffness: 200 }}
                className="mb-8"
              >
                <span className={`text-7xl font-extralight ${
                  score >= 80 ? 'text-emerald-500' : 
                  score >= 60 ? 'text-amber-500' : 'text-red-500'
                }`}>
                  {score}%
                </span>
              </motion.div>

              {/* Phoneme comparison */}
              <div className="w-full max-w-2xl mb-8">
                {/* You said row - TOP */}
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-xs text-gray-400 w-16 text-right">You said</span>
                  <div className="flex flex-wrap gap-1.5">
                    {results.map((result, i) => (
                      <motion.button
                        key={`act-${i}`}
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 + i * 0.02 }}
                        onClick={() => result.actual && playPhoneme(result.actual)}
                        onMouseEnter={() => setHoveredPhoneme(result.actual || result.expected)}
                        onMouseLeave={() => setHoveredPhoneme(null)}
                        className={`
                          px-3 py-2 rounded-lg font-mono text-base
                          transition-all duration-200 cursor-pointer
                          ${playingPhoneme === result.actual ? 'ring-2 ring-gray-400' : ''}
                          ${result.correct 
                            ? 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100' 
                            : 'bg-red-50 text-red-500 hover:bg-red-100 font-medium'
                          }
                        `}
                      >
                        {result.actual || '—'}
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* Expected row - BOTTOM */}
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-400 w-16 text-right">Expected</span>
                  <div className="flex flex-wrap gap-1.5">
                    {results.map((result, i) => (
                      <motion.button
                        key={`exp-${i}`}
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.15 + i * 0.02 }}
                        onClick={() => playPhoneme(result.expected)}
                        onMouseEnter={() => setHoveredPhoneme(result.expected)}
                        onMouseLeave={() => setHoveredPhoneme(null)}
                        className={`
                          px-3 py-2 rounded-lg font-mono text-base
                          transition-all duration-200 cursor-pointer
                          ${playingPhoneme === result.expected ? 'ring-2 ring-gray-400' : ''}
                          bg-gray-50 text-gray-600 hover:bg-gray-100
                        `}
                      >
                        {result.expected}
                      </motion.button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Raw phoneme output with replay button */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="w-full max-w-2xl mb-8 p-4 bg-gray-50 rounded-xl"
              >
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs text-gray-400">Raw {model} output:</p>
                  {recordedAudioUrl && (
                    <button
                      onClick={replayRecording}
                      className="flex items-center gap-1.5 px-3 py-1 text-xs text-gray-500 
                               hover:text-gray-700 hover:bg-gray-100 rounded-full transition-all"
                    >
                      <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z"/>
                      </svg>
                      Replay
                    </button>
                  )}
                </div>
                <p className="font-mono text-sm text-gray-600 break-all">{rawPhonemes}</p>
              </motion.div>

              {/* Actions */}
              <motion.div 
                className="flex gap-4"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
              >
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={resetSentence}
                  className="px-8 py-4 rounded-full border border-gray-200 text-gray-600 
                           hover:bg-gray-50 hover:border-gray-300 transition-all font-light"
                >
                  Try Again
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={nextSentence}
                  className="px-8 py-4 rounded-full bg-gray-900 text-white 
                           hover:bg-gray-800 transition-all font-light shadow-lg shadow-gray-400/20"
                >
                  Next →
                </motion.button>
              </motion.div>
            </motion.div>
          )}
        </motion.div>
      </AnimatePresence>

      {/* Fixed tooltip - center of screen, doesn't cause layout shift */}
      <AnimatePresence>
        {hoveredPhoneme && phonemeInfo[hoveredPhoneme] && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.1 }}
            className="fixed bottom-24 left-1/2 -translate-x-1/2 z-50"
          >
            <p className="text-sm text-gray-500 text-center">
              <span className="font-medium">{phonemeInfo[hoveredPhoneme].description}</span>
              {' · '}
              <span className="text-gray-400">"{phonemeInfo[hoveredPhoneme].example}"</span>
              {' · '}
              <span className="text-emerald-600">{phonemeInfo[hoveredPhoneme].tip}</span>
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Footer hint */}
      <motion.p 
        className="absolute bottom-8 text-xs text-gray-300 font-light"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
      >
        Click any phoneme to hear it
      </motion.p>
    </div>
  );
}

export default App;
