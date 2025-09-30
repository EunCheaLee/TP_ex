import json
from konlpy.tag import Okt
import re

# 데이터 파일
DATA_FILE = '../data/txt/sentences_spaced_pykospacing.txt'
OUTPUT_FILE = '../data/json/learning_tales_data.json'

# Konlpy Okt 초기화
okt = Okt()

# 불용어
stopwords = ['은', '는', '이', '가', '을', '를', '에', '의', '도', '와', '과']

# 난이도 판단 함수
def assign_difficulty(word):
    """
    단순 발음 기준 난이도 + 한자어 가산
    """
    base_difficulty = 4  # 최소 4세

    # 받침 적고 발음 쉬운 단어는 낮은 난이도
    if len(word) <= 2:
        base_difficulty = 4
    elif len(word) == 3:
        base_difficulty = 5
    elif len(word) == 4:
        base_difficulty = 6
    elif len(word) == 5:
        base_difficulty = 7
    elif len(word) == 6:
        base_difficulty = 8
    elif len(word) == 7:
        base_difficulty = 9
    else:
        base_difficulty = 10
    # 난이도가 문제다.
    return base_difficulty

# 고유명사 탐지 함수
def detect_proper_nouns(text):
    words_pos = okt.pos(text, stem=True)
    proper_nouns = []
    normal_words = []

    for i, (word, pos) in enumerate(words_pos):
        if word in stopwords:
            continue
        # 명사이면서 뒤에 조사(Josa)가 붙은 경우 고유명사 후보
        if pos == 'Noun' and i + 1 < len(words_pos) and words_pos[i + 1][1] == 'Josa':
            proper_nouns.append(word)
        else:
            normal_words.append(word)

    return normal_words, proper_nouns

# 학습 데이터 만들기
learning_data = []

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        normal_words, proper_nouns = detect_proper_nouns(line)
        for word in normal_words:
            learning_data.append({
                "word": word,
                "difficulty": assign_difficulty(word),
                "is_proper": False
            })
        for word in proper_nouns:
            learning_data.append({
                "word": word,
                "difficulty": assign_difficulty(word),
                "is_proper": True
            })

# JSON으로 저장
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(learning_data, f, ensure_ascii=False, indent=2)

print(f"총 단어 수: {len(learning_data)}")
print(f"JSON 파일로 저장 완료: {OUTPUT_FILE}")
