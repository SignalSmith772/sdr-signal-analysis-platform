"""
ml/training/train_classifier.py
Alternative training entry-point using the ml/ folder directly.
Saves model to ml/models/modulation_classifier.pkl.

Usage:
    cd sdr-signal-analysis-platform
    python ml/training/train_classifier.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
from backend.scripts.train_model import train

if __name__ == '__main__':
    accuracy = train()
    print(f'\n🎯 Final accuracy: {accuracy * 100:.2f}%')
