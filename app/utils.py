# 토큰화, Word2Vec, 뜻 조회 등 유틸 함수
import xml.etree.ElementTree as ET
import pandas as pd
from urllib.parse import unquote
from fastapi import HTTPException
from konlpy.tag import Okt
from sklearn.preprocessing import LabelEncoder
from gensim.models import Word2Vec
import torch
import logging
import requests
from .dataset import WordDataset
from .config import DATA_PATH, EMBED_DIM, BATCH_SIZE

# 1. 데이터 불러오기
df = pd.read_excel(DATA_PATH)
df = df.dropna().drop_duplicates()
# df.columns = df.columns.str.strip()  # 앞뒤 공백 제거
# Index(['순위', '단어', '품사', '풀이', '등급'], dtype='object')

# 2. 레이블 인코딩 ('등급' 컬럼 사용)
le = LabelEncoder()
df["label"] = le.fit_transform(df["등급"])

# 3. 토큰화 ('단어' 컬럼 사용, Okt)
okt = Okt()
df["tokens"] = df["단어"].apply(lambda w: okt.morphs(w))

# 4. Word2Vec 임베딩 학습
sentences = df["tokens"].tolist()
w2v = Word2Vec(sentences, vector_size=EMBED_DIM, window=3, min_count=1, sg=1)

# 5. 데이터셋
train_ds = WordDataset(df["tokens"].tolist(), df["label"].tolist(), w2v)

# 6. 유틸 함수

def normalize_word(word: str):
    tokens = okt.morphs(word)
    for t in tokens:
        if t in w2v.wv:
            return t
    return None

def most_similar(token, topn=5):
    if token is None:
        return []
    sims = w2v.wv.most_similar(token, topn=topn)
    # JSON 직렬화용 변환: 튜플 -> dict, float32 -> float
    return [{"word": w, "score": float(s)} for w, s in sims]


def get_definition(word: str) -> str:
    logging.basicConfig(level=logging.INFO)
    # unquote 제거 - 이미 main.py에서 디코딩되어 전달됨
    # word = unquote(word)  # 이 줄 제거 또는 주석 처리

    API_URL = "https://stdict.korean.go.kr/api/search.do"
    API_KEY = "21FC20CC381F1909B6699EDFAC4A090A"
    params = {
        "key": API_KEY,
        "q": word,  # 원본 단어 사용
        "req_type": "json",

    }

    try:
        response = requests.get(API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        logging.info(f"{word} API 호출 성공: {response.url}")
        logging.debug(f"{word} API raw data: {data}")
    except requests.RequestException as e:
        logging.error(f"{word} API 요청 실패: {e}")
        return "뜻을 찾을 수 없음(API 요청 실패)"
    except ValueError:
        logging.error(f"{word} API 응답 JSON 파싱 실패")
        return "뜻을 찾을 수 없음(JSON 파싱 실패)"

    # channel / items 안전하게 접근
    channel = data.get("channel", {})
    items = channel.get("item", [])

    # items가 dict이면 리스트로 변환
    if isinstance(items, dict):
        items = [items]

    if not items:
        logging.warning(f"{word} API 응답에 item 없음")
        return "뜻을 찾을 수 없음(항목 없음)"

    first_item = items[0]
    sense = first_item.get("sense")
    definition = None

    # sense가 리스트이면, 첫 번째 dict에서 definition 가져오기
    if isinstance(sense, list):
        for s in sense:
            if isinstance(s, dict) and "definition" in s:
                definition = s["definition"]
                break
    elif isinstance(sense, dict):
        definition = sense.get("definition")

    if not definition:
        logging.warning(f"{word} 정의 없음")
        return "뜻을 찾을 수 없음(정의 없음)"

    # CDATA 제거
    if definition.startswith("<![CDATA[") and definition.endswith("]]>"):
        definition = definition[9:-3].strip()

    return definition