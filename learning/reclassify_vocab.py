import pandas as pd
import json
import re
from collections import Counter


def extract_words_from_fairytales(filepath):
    """동화에서 모든 단어 추출"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    contents = []

    # 그림 형제 형식
    if 'fairy_tales' in data:
        contents = [story['content'] for story in data['fairy_tales']]

    # 이솝 우화 형식
    elif 'fables' in data:
        contents = [fable['title'] + " " + fable['content'] for fable in data['fables']]

    # 일반 key-value 형식
    else:
        # 숫자 등 비문자 데이터 제외
        contents = [str(v) for v in data.values() if isinstance(v, (str, list, dict))]

    all_text = ' '.join(contents)

    # 한글 단어만 추출 (2글자 이상)
    words = re.findall(r'[가-힣]{2,}', all_text)

    return words


def classify_by_frequency():
    """동화 빈도 기반으로 4-10세 어휘 분류"""

    print("=" * 60)
    print("동화 기반 어휘 추출 및 분류")
    print("=" * 60)

    # 1. 동화에서 단어 추출
    print("\n동화 파일에서 단어 추출 중...")

    fairytale_files = [
        '../data/json/cleaned_hwp.json',
        '../data/json/cleaned_pdf.json',
        '../data/json/grim_bro.json',
        '../data/json/aesop_fables.json',
    ]

    all_words = []

    for filepath in fairytale_files:
        try:
            words = extract_words_from_fairytales(filepath)
            all_words.extend(words)
            print(f"  ✓ {filepath}: {len(words):,}개 단어")
        except FileNotFoundError:
            print(f"  ⚠ {filepath}: 파일 없음")
        except Exception as e:
            print(f"  ❌ {filepath}: {e}")

    if not all_words:
        print("\n❌ 동화 파일을 로드하지 못했습니다.")
        return

    # 2. 빈도수 계산
    word_freq = Counter(all_words)
    print(f"\n총 추출 단어: {len(all_words):,}개")
    print(f"고유 단어: {len(word_freq):,}개")

    # 3. 빈도 기반 연령 분류
    print("\n" + "=" * 60)
    print("빈도 기반 연령 분류")
    print("=" * 60)

    vocab_list = []

    for word, freq in word_freq.items():
        # 빈도가 너무 낮은 단어는 제외 (5회 미만)
        if freq < 5:
            continue

        # 연령 분류 (기준 대폭 완화)
        if freq >= 400:  # 4세: 400회 이상
            age = 4
        elif freq >= 200:  # 5세: 200-399회
            age = 5
        elif freq >= 100:  # 6세: 100-199회
            age = 6
        elif freq >= 50:  # 7세: 50-99회
            age = 7
        elif freq >= 25:  # 8세: 25-49회
            age = 8
        elif freq >= 12:  # 9세: 12-24회
            age = 9
        else:  # 10세: 5-11회
            age = 10

        vocab_list.append({
            'word': word,
            'frequency': freq,
            'age_group': age,
            'length': len(word)
        })

    # DataFrame 생성
    vocab_df = pd.DataFrame(vocab_list)

    # 4. 통계
    print("\n연령별 단어 분포:")
    age_counts = vocab_df['age_group'].value_counts().sort_index()

    for age, count in age_counts.items():
        percentage = count / len(vocab_df) * 100
        print(f"  {age}세: {count:5d}개 ({percentage:5.1f}%)")

    # 5. 각 연령별 상위 단어 샘플
    print("\n" + "=" * 60)
    print("연령별 단어 샘플 (빈도 높은 순)")
    print("=" * 60)

    for age in range(4, 11):
        age_words = vocab_df[vocab_df['age_group'] == age].nlargest(15, 'frequency')

        if len(age_words) > 0:
            print(f"\n{age}세 단어 ({len(vocab_df[vocab_df['age_group'] == age])}개):")
            for idx, row in age_words.iterrows():
                print(f"  {row['word']:10s} (빈도: {row['frequency']:4d})")

    # 6. 저장
    output_file = 'fairytale_vocabulary.csv'

    # 빈도 순으로 정렬
    vocab_df = vocab_df.sort_values('frequency', ascending=False)

    vocab_df.to_csv(output_file, index=False, encoding='utf-8')

    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)
    print(f"\n동화에서 추출된 어휘: {len(vocab_df):,}개 (빈도 5회 이상)")
    print(f"제외된 저빈도 단어: {len(word_freq) - len(vocab_df):,}개")

    # 추가 통계
    print("\n추가 통계:")
    print(f"  평균 빈도: {vocab_df['frequency'].mean():.1f}")
    print(f"  중앙값 빈도: {vocab_df['frequency'].median():.1f}")
    print(f"  최고 빈도: {vocab_df['frequency'].max()} ({vocab_df.iloc[0]['word']})")

    print("\n다음 단계:")
    print("1. fairytale_vocabulary.csv 확인")
    print("2. 기존 vocabulary_data.csv 백업")
    print("3. fairytale_vocabulary.csv를 vocabulary_data.csv로 교체")
    print("4. 학습 파이프라인 재실행")


if __name__ == "__main__":
    classify_by_frequency()