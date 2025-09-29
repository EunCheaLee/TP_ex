import pandas as pd
import json


def analyze_vocabulary():
    """어휘 데이터 분석"""

    # CSV 로드
    vocab_df = pd.read_csv('fairytale_vocabulary.csv')

    # age_group 정수 변환
    if vocab_df['age_group'].dtype == 'object':
        vocab_df['age_group'] = (
            vocab_df['age_group']
            .str.extract(r'(\d+)')  # 숫자만 추출
            .astype(float)
            .astype('Int64')
        )

    print("=" * 60)
    print("📊 어휘 데이터 분석")
    print("=" * 60)

    # 전체 통계
    print(f"\n총 단어 수: {len(vocab_df):,}개")

    # 연령별 분포
    print("\n📈 연령별 단어 분포:")
    age_counts = vocab_df['age_group'].value_counts().sort_index()

    for age, count in age_counts.items():
        percentage = count / len(vocab_df) * 100
        print(f"  {age}세: {count:4d}개 ({percentage:5.1f}%)")

    # 4세 단어 상세 분석
    age_4 = vocab_df[vocab_df['age_group'] == 4]

    print(f"\n{'=' * 60}")
    print(f"🎯 4세 단어 상세 분석 ({len(age_4)}개)")
    print("=" * 60)

    if len(age_4) == 0:
        print("\n❌ 4세 단어가 하나도 없습니다!")
        print("vocabulary_data.csv의 age_group 컬럼을 확인하세요.")
        return

    # 4세 단어 샘플
    print("\n📝 4세 단어 샘플 (처음 30개):")
    sample_words = age_4['word'].head(30).tolist()

    for i in range(0, len(sample_words), 5):
        print("  " + ", ".join(sample_words[i:i + 5]))

    # 품사별 분포
    if 'pos' in age_4.columns:
        print(f"\n📚 4세 단어 품사 분포:")
        pos_counts = age_4['pos'].value_counts()
        for pos, count in pos_counts.items():
            print(f"  {pos}: {count}개")

    # 빈도수 통계
    if 'frequency' in age_4.columns:
        print(f"\n📊 4세 단어 빈도수 통계:")
        print(f"  평균: {age_4['frequency'].mean():.1f}")
        print(f"  최소: {age_4['frequency'].min()}")
        print(f"  최대: {age_4['frequency'].max()}")

    # 난이도 통계
    if 'difficulty_score' in age_4.columns:
        print(f"\n⭐ 4세 단어 난이도 점수:")
        print(f"  평균: {age_4['difficulty_score'].mean():.2f}")
        print(f"  최소: {age_4['difficulty_score'].min():.2f}")
        print(f"  최대: {age_4['difficulty_score'].max():.2f}")


def check_fairytale_coverage():
    """동화에 4세 단어가 얼마나 포함되어 있는지 확인"""

    vocab_df = pd.read_csv('vocabulary_data_reclassified.csv')
    age_4_words = set(vocab_df[vocab_df['age_group'] == 4]['word'].tolist())

    if len(age_4_words) == 0:
        print("\n❌ 4세 단어가 없어서 커버리지를 확인할 수 없습니다.")
        return

    # 동화 파일 로드
    fairytale_files = [
        '../data/json/cleaned_hwp.json',
        '../data/json/fixed_fairytales.json',
        '../data/json/grim_bro.json'
        '../data/json/aesop_fables.json'
    ]

    for filepath in fairytale_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 그림 형제 형식 처리
            if 'fairy_tales' in data:
                contents = [story['content'] for story in data['fairy_tales']]
            else:
                contents = list(data.values())

            all_text = ' '.join(contents)

            # 4세 단어 중 동화에 등장하는 단어 찾기
            found_words = []
            for word in age_4_words:
                if word in all_text:
                    found_words.append(word)

            print(f"\n{'=' * 60}")
            print(f"📖 {filepath}")
            print("=" * 60)
            print(
                f"4세 단어 중 발견된 단어: {len(found_words)}/{len(age_4_words)}개 ({len(found_words) / len(age_4_words) * 100:.1f}%)")

            if found_words:
                print(f"\n발견된 4세 단어 샘플 (처음 20개):")
                for i in range(0, min(20, len(found_words)), 5):
                    print("  " + ", ".join(found_words[i:i + 5]))

            # 발견되지 않은 단어
            not_found = age_4_words - set(found_words)
            if not_found:
                print(f"\n❌ 발견되지 않은 4세 단어 샘플 (처음 20개):")
                not_found_list = list(not_found)[:20]
                for i in range(0, len(not_found_list), 5):
                    print("  " + ", ".join(not_found_list[i:i + 5]))

            break

        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"❌ {filepath} 로드 실패: {e}")


if __name__ == "__main__":
    print("\n")

    # 1. 어휘 데이터 분석
    analyze_vocabulary()

    # 2. 동화 커버리지 확인
    print("\n")
    check_fairytale_coverage()

    print("\n" + "=" * 60)
    print("✅ 분석 완료")
    print("=" * 60)