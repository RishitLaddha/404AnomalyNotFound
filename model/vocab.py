# model/vocab.py

import json
from collections import Counter
from model.config import DATA_PATH, VOCAB_PATH, PAD_TOKEN, UNK_TOKEN



def build_vocab():
    counter = Counter()

    with open(DATA_PATH) as f:
        for line in f:
            obj = json.loads(line)
            counter.update(obj["tokens"])

    vocab = {
        PAD_TOKEN: 0,
        UNK_TOKEN: 1
    }

    for token in sorted(counter):
        vocab[token] = len(vocab)

    with open(VOCAB_PATH, "w") as f:
        json.dump(vocab, f, indent=2)

    print(f"[+] Vocab size: {len(vocab)}")
    print(f"[+] Saved to {VOCAB_PATH}")

if __name__ == "__main__":
    build_vocab()
