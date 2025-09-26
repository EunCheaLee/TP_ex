# 단어 임베딩 학습 (KoBERT)
from transformers import BertTokenizer, BertModel
import torch

tokenizer = BertTokenizer.from_pretrained('monologg/kobert')
model = BertModel.from_pretrained('monologg/kobert')

sentences = ["나는 사과를 먹었다.", "오늘 학교에 갔다."]  # Korpora 문장
inputs = tokenizer(sentences, return_tensors="pt", padding=True, truncation=True)
outputs = model(**inputs)
embeddings = outputs.last_hidden_state  # 단어 임베딩
