# model/dataset.py

import json
import torch
from torch.utils.data import Dataset
from model.config import (
    DATA_PATH,
    VOCAB_PATH,
    MAX_SEQ_LEN,
    PAD_TOKEN,
    UNK_TOKEN
)



class RequestDataset(Dataset):
    def __init__(self):
        with open(VOCAB_PATH) as f:
            self.vocab = json.load(f)

        self.pad_id = self.vocab[PAD_TOKEN]
        self.unk_id = self.vocab[UNK_TOKEN]

        self.samples = []

        with open(DATA_PATH) as f:
            for line in f:
                tokens = json.loads(line)["tokens"]
                ids = [self.vocab.get(t, self.unk_id) for t in tokens]
                self.samples.append(self._pad(ids))

    def _pad(self, seq):
        if len(seq) > MAX_SEQ_LEN:
            return seq[:MAX_SEQ_LEN]
        return seq + [self.pad_id] * (MAX_SEQ_LEN - len(seq))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        x = torch.tensor(self.samples[idx], dtype=torch.long)
        return x, x   # autoencoder: input == target
