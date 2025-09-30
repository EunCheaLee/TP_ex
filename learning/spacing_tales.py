import json

# 입력 파일과 출력 파일 경로
INPUT_FILE = '../data/txt/sentences_spaced_pykospacing.txt'
OUTPUT_FILE = '../data/json/learning_data.json'

learning_data = []

# 파일 읽기
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        # 띄어쓰기 기준으로 분리
        words = line.split()
        # 학습 데이터 형식으로 저장
        learning_data.append({
            "original_sentence": line,
            "words": words
        })

# JSON으로 저장
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(learning_data, f, ensure_ascii=False, indent=2)

print(f"학습 데이터 저장 완료: {OUTPUT_FILE}")
