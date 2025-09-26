# main.py (라우트 디버깅 버전)
from urllib.parse import unquote, quote
from fastapi import FastAPI, Query
from fastapi.encoders import jsonable_encoder
from app.utils import most_similar, normalize_word, train_ds, get_definition
from app.models import SimpleClassifier
from app.config import MODEL_PATH, EMBED_DIM
import torch
import os

app = FastAPI()

# 모델 로드
num_classes = len(set(train_ds.labels))
model = SimpleClassifier(embed_dim=EMBED_DIM, num_classes=num_classes)

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"{MODEL_PATH}가 존재하지 않습니다. 먼저 train_model.py로 학습하세요.")

model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
model.eval()

@app.get("/")
def read_root():
    print("Root endpoint called")
    return {"message": "FastAPI 서버 준비 완료!"}


# 라우트 등록 확인용 - 간단한 테스트 엔드포인트
@app.get("korpora_test")
def test_endpoint():
    return {"message": "테스트 엔드포인트 동작!"}

@app.get("/similar/{word}")
def similar_word(word: str, topn: int = 5):
    decoded_word = unquote(word)
    definition = get_definition(decoded_word)

    token = normalize_word(decoded_word)
    if token is None:
        similar = []
        token_used = "학습 데이터 없음"
    else:
        similar = most_similar(token, topn)
        token_used = token

    response = {
        "word": decoded_word,
        "token_used": token_used,
        "definition": definition,
        "similar_words": similar
    }

    return jsonable_encoder(response)