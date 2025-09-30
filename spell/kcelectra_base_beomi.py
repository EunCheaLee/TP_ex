# 이 코드는 맞춤법 교정이 아니라 문장 분류 코드다.
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline

# 1. 모델과 토크나이저 로드
model_name = "beomi/KcELECTRA-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# 2. 텍스트 분류 pipeline 생성
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

# 3. 예시 문장
text = "이 문장은 맞춤법이 틀릴수 있습니다."

# 4. 문장 분류
result = classifier(text)
print(result)
