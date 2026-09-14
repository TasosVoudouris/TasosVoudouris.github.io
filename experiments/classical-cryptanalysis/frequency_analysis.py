"""Simple monoalphabetic frequency-analysis helper for teaching."""
from collections import Counter
from string import ascii_uppercase


def frequencies(text: str):
    letters = [c for c in text.upper() if c in ascii_uppercase]
    counts = Counter(letters)
    total = len(letters) or 1
    return [(c, counts[c], counts[c] / total) for c in ascii_uppercase]


def ranked(text: str):
    return sorted(frequencies(text), key=lambda row: (-row[1], row[0]))


if __name__ == "__main__":
    sample = "KHOOR ZRUOG"  # Caesar-shifted HELLO WORLD
    for symbol, count, proportion in ranked(sample)[:10]:
        print(symbol, count, f"{proportion:.3f}")
