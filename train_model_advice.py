import torch
from torch.utils.data import DataLoader
from torch.optim import AdamW
from transformers import BertTokenizer, BertForMaskedLM
from transformers import get_scheduler
from tqdm import tqdm
from app.advice_dataset import AdviceDataset

# 🔹 데이터셋 준비
tokenizer = BertTokenizer.from_pretrained("klue/bert-base")
dataset = AdviceDataset("data/advice.txt", tokenizer, max_len=64)
loader = DataLoader(dataset, batch_size=8, shuffle=True)

# 🔹 모델 준비 (BERT MLM)
model = BertForMaskedLM.from_pretrained("klue/bert-base")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# 🔹 Optimizer & Scheduler
optimizer = AdamW(model.parameters(), lr=5e-5)
num_training_steps = len(loader) * 3  # 3 epoch 예시
lr_scheduler = get_scheduler(
    "linear",
    optimizer=optimizer,
    num_warmup_steps=0,
    num_training_steps=num_training_steps,
)

# 🔹 학습 루프
epochs = 3
model.train()

for epoch in range(epochs):
    loop = tqdm(loader, desc=f"Epoch {epoch+1}")
    for batch in loop:
        batch = {k: v.to(device) for k, v in batch.items()}

        outputs = model(
            input_ids=batch["input_ids"],
            attention_mask=batch["attention_mask"],
            labels=batch["labels"]
        )
        loss = outputs.loss

        loss.backward()
        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()

        loop.set_postfix(loss=loss.item())

# 🔹 모델 저장
model.save_pretrained("model_weights")
tokenizer.save_pretrained("model_weights")
print("✅ 모델 저장 완료: model_weights/")
