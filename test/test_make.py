# 빈칸 문제 생성 학습 (KoT5)
from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained('KoT5-small')
model = T5ForConditionalGeneration.from_pretrained('KoT5-small')

# 예시 입력: 빈칸 문제 학습용
input_text = "나는 오늘 [MASK]에서 놀았다."
target_text = "학교"
inputs = tokenizer(input_text, return_tensors="pt")
labels = tokenizer(target_text, return_tensors="pt").input_ids
outputs = model(input_ids=inputs.input_ids, labels=labels)
loss = outputs.loss
loss.backward()
