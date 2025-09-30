import json
import re

def clean_title():
    # 1. 합쳐진 json('../data/json/fixed_fairytales.json')을 불러오기.
    tales = '../data/json/fixed_fairytales.json'
    with open(tales, 'r', encoding='utf-8') as f:
        tales = json.load(f)

    # 2. 제목의 숫자 제거
    new_tales = {}
    for key, value in tales.items():
        # (1) 숫자. 제거
        new_key = re.sub(r'^\d+\.', '', key).strip()
        # (2) 괄호와 그 안 내용 제거
        new_key = re.sub(r'\(.*?\)', '', new_key).strip()
        new_tales[new_key] = value

    # 3. 결과 확인
    print(list(new_tales.keys())[:20], flush=True)  # 앞 20개 제목 확인

    # 4. 필요하다면 다시 저장
    with open('../data/json/fixed_fairytales.json', 'w', encoding='utf-8') as f:
        json.dump(new_tales, f, ensure_ascii=False, indent=4)

def extraction_tales_txt():
    # 1. 합쳐진 json('../data/json/fixed_fairytales.json')을 불러오기.
    tales = '../data/json/fixed_fairytales.json'
    with open(tales, 'r', encoding='utf-8') as f:
        tales = json.load(f)

    # 2. 동화 내용만 추출하기
    all_texts = []
    all_texts = []
    for value in tales.values():
        # (1) 따옴표(“...”) 블록을 우선 분리
        parts = re.split(r'(“[^”]*”)', value)

        sentences = []
        for part in parts:
            part = part.strip()
            if not part:
                continue

            if part.startswith("“") and part.endswith("”"):
                # 따옴표로 감싸진 건 그대로 한 줄
                sentences.append(part)
            else:
                # 나머지는 문장부호(.?) 뒤에서 줄바꿈
                subs = re.split(r'(?<=[.?])\s*', part)
                subs = [s.strip() for s in subs if s.strip()]
                sentences.extend(subs)

        all_texts.extend(sentences)

    # 3. 문장마다 한 줄씩 엔터 쳐지는 방식으로 txt로 저장하기
    with open('../data/txt/tales_sentences.txt', 'w', encoding='utf-8') as f:
        for sentence in all_texts:
            f.write(sentence + '\n')

    print("저장 완료! 문장 수:", len(all_texts))

if __name__ == '__main__':
    tales_path = '../data/txt/tales_sentences.txt'
    with open(tales_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 1. 모든 줄을 하나로 붙임 → 기존 줄바꿈 제거
    text = ' '.join(line.strip() for line in lines)

    # 2. 사진링크 ▶ … ) 및 괄호(...) 패턴 삭제
    # 먼저 사진링크 패턴 제거
    # text = re.sub(r'사진링크\s*▶.*?\)', '', text, flags=re.DOTALL)
    # 그 다음 일반 괄호 패턴 제거
    text = re.sub(r'\([^)]*?\)', '', text, flags=re.DOTALL)

    # 3. 따옴표 대사(“…”) 기준으로 분리
    parts = re.split(r'(“[^”]*”)', text)

    sentences = []
    for part in parts:
        part = part.strip()
        if not part:
            continue

        if part.startswith("“") and part.endswith("”"):
            # 대사는 그대로 한 줄
            sentences.append(part)
        else:
            # 나머지는 문장부호(.?) 기준으로 줄바꿈
            subs = re.split(r'(?<=[.?])\s+', part)
            subs = [s.strip() for s in subs if s.strip()]
            sentences.extend(subs)

    # 4. txt로 저장
    output_path = '../data/txt/tales_sentences_fixed.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        for s in sentences:
            f.write(s + '\n')

    print("수정 완료! 문장 수:", len(sentences))