# Dataset 클래스 정의
import torch
from torch.utils.data import Dataset

class WordDataset(Dataset):
    def __init__(self, tokens_list, labels, w2v_model):
        self.tokens_list = tokens_list
        self.labels = labels
        self.w2v = w2v_model

    def __len__(self):
        return len(self.tokens_list)

    def __getitem__(self, idx):
        tokens = self.tokens_list[idx]
        vecs = [self.w2v.wv[t] for t in tokens if t in self.w2v.wv]
        if len(vecs) == 0:
            vec = torch.zeros(self.w2v.vector_size)
        else:
            vec = torch.tensor(sum(vecs)/len(vecs), dtype=torch.float32)
        label = torch.tensor(self.labels[idx], dtype=torch.long)
        return vec, label