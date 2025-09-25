import torch
from torch.utils.data import Dataset

class AdviceDataset(Dataset):
    def __init__(self, file_path, tokenizer, max_len=64):
        with open(file_path, "r", encoding="utf-8") as f:
            self.texts = [line.strip() for line in f if line.strip()]
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        enc = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt"
        )
        return {
            "input_ids": enc["input_ids"].squeeze(),
            "attention_mask": enc["attention_mask"].squeeze(),
            "labels": enc["input_ids"].squeeze()
        }
