# Hindi Transliteration Library

A Python library for transliterating English text to Hindi using AI4Bharat's model. This library provides a simple interface for converting English words to their Hindi (Devanagari) equivalents.

## Features

- Simple and intuitive API
- Supports both single word and batch transliteration
- Returns multiple transliteration candidates
- CPU-only implementation (no GPU required)
- Interactive command-line interface

## Installation

```bash
pip install hindi-xlit
```

## Usage

### Basic Usage

```python
from hindi_xlit import HindiTransliterator

# Initialize the transliterator
transliterator = HindiTransliterator()

# Transliterate a single word
word = "namaste"
candidates = transliterator.transliterate(word)
print(f"Transliteration candidates for '{word}':")
for i, candidate in enumerate(candidates, 1):
    print(f"{i}. {candidate}")

# Transliterate multiple words
words = ["hello", "world"]
results = transliterator.transliterate_batch(words)
for word, candidates in zip(words, results):
    print(f"\nTransliteration candidates for '{word}':")
    for i, candidate in enumerate(candidates, 1):
        print(f"{i}. {candidate}")
```

### Command Line Interface

After installing the package (e.g., via pip from PyPI), you can use the command line interface:

```bash
hindi-xlit <word> [topk]
```

- `<word>`: The word in Roman script to transliterate (required)
- `[topk]`: (Optional) Number of transliteration candidates to return (default: 3)

**Examples:**

```bash
hindi-xlit namaste
# Output:
# Transliteration candidates for 'namaste':
# 1. नमस्ते
# 2. नमसते
# 3. नामसते

hindi-xlit hello 5
# Output:
# Transliteration candidates for 'hello':
# 1. हेलो
# 2. हैलो
# 3. हेलों
# 4. हिलो
# 5. हीलो
```

If you run the command without arguments, it will show usage instructions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This library uses the transliteration model from [AI4Bharat](https://github.com/AI4Bharat/IndicXlit).

See [CHANGELOG.md](./CHANGELOG.md) for release notes.