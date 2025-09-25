import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from app.models import SimpleClassifier
from app.utils import train_ds
from app.config import BATCH_SIZE, EPOCHS, LEARNING_RATE, MODEL_PATH, EMBED_DIM

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)

num_classes = len(set(train_ds.labels))  # 클래스 수
model = SimpleClassifier(embed_dim=EMBED_DIM, num_classes=num_classes)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

for epoch in range(EPOCHS):
    for vecs, labels in train_loader:
        preds = model(vecs)
        loss = criterion(preds, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    print(f"epoch {epoch} loss {loss.item():.4f}")

# 모델 저장
torch.save(model.state_dict(), MODEL_PATH)
print(f"모델 저장 완료: {MODEL_PATH}")
