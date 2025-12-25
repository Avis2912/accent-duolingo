"""
Phone Alignment & Scoring using:
1. Needleman-Wunsch sequence alignment (handles insertions/deletions)
2. Panphon phonetic feature distance (scores substitutions by similarity)
"""

import panphon
from panphon.distance import Distance
import numpy as np

dst = Distance()

def phone_distance(p1, p2):
    """Get distance between two phones (0 = identical, 1 = very different)"""
    if p1 == p2:
        return 0.0
    if p1 == '-' or p2 == '-':  # gap
        return 0.5  # gap penalty
    try:
        return dst.feature_edit_distance(p1, p2)
    except:
        return 1.0  # unknown phone

def needleman_wunsch(seq1, seq2, gap_penalty=0.5):
    """Align two phone sequences using Needleman-Wunsch algorithm"""
    n, m = len(seq1), len(seq2)
    
    # Initialize score matrix
    score = np.zeros((n + 1, m + 1))
    for i in range(n + 1):
        score[i][0] = i * gap_penalty
    for j in range(m + 1):
        score[0][j] = j * gap_penalty
    
    # Fill score matrix
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            match = score[i-1][j-1] + phone_distance(seq1[i-1], seq2[j-1])
            delete = score[i-1][j] + gap_penalty
            insert = score[i][j-1] + gap_penalty
            score[i][j] = min(match, delete, insert)
    
    # Traceback to get alignment
    align1, align2 = [], []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and score[i][j] == score[i-1][j-1] + phone_distance(seq1[i-1], seq2[j-1]):
            align1.append(seq1[i-1])
            align2.append(seq2[j-1])
            i -= 1
            j -= 1
        elif i > 0 and score[i][j] == score[i-1][j] + gap_penalty:
            align1.append(seq1[i-1])
            align2.append('-')
            i -= 1
        else:
            align1.append('-')
            align2.append(seq2[j-1])
            j -= 1
    
    return align1[::-1], align2[::-1], score[n][m]

def compare_pronunciations(native_phones, speaker_phones):
    """Compare two phone strings and return detailed analysis"""
    native_list = native_phones.split()
    speaker_list = speaker_phones.split()
    
    # Align sequences
    aligned_native, aligned_speaker, total_distance = needleman_wunsch(native_list, speaker_list)
    
    # Analyze each position
    results = []
    for n, s in zip(aligned_native, aligned_speaker):
        dist = phone_distance(n, s)
        if n == s:
            status = '✅'
        elif dist < 0.2:
            status = '🟡'  # close
        elif n == '-':
            status = '➕'  # insertion
        elif s == '-':
            status = '➖'  # deletion  
        else:
            status = '❌'  # substitution
        results.append((n, s, dist, status))
    
    return results, total_distance, len(native_list)


# === TEST IT ===
if __name__ == "__main__":
    # Your actual data
    native = "b̥ o j s ɹ ɪ k ɔ ɹ d ɹ̩ t ɹ æ n s k ɹ ɪ p ʃ ə n k ʌ m z k ə m p l i tʰ l i f ɹ i"
    speaker = "v o j s ɹ ɪ k ʁ ɔ ɹ tʰ ɹ̩ æ z k ə m n p ʁ i tʰ l i f ɹ i"
    
    results, total_dist, native_len = compare_pronunciations(native, speaker)
    
    print("="*70)
    print("ALIGNED PHONE COMPARISON")
    print("="*70)
    print()
    print(f"{'NATIVE':<8} {'SPEAKER':<8} {'DIST':<8} {'STATUS'}")
    print("-"*35)
    
    for native_p, speaker_p, dist, status in results:
        print(f"{native_p:<8} {speaker_p:<8} {dist:<8.3f} {status}")
    
    print()
    print("="*70)
    print(f"TOTAL DISTANCE: {total_dist:.2f}")
    print(f"AVERAGE ERROR:  {total_dist/native_len:.2f} per phone")
    print(f"ACCURACY SCORE: {max(0, 100 - (total_dist/native_len)*100):.1f}%")
    print("="*70)
    print()
    print("Legend: ✅=correct, 🟡=close, ❌=wrong, ➕=extra, ➖=missing")

