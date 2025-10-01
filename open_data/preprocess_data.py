# preprocess_data.py
import re
import json
import pandas as pd
from pathlib import Path
from collections import Counter


class DataPreprocessor:
    def __init__(self, base_path):
        self.base_path = Path(base_path)

    def parse_age_from_folder(self, folder_name):
        """폴더명에서 나이 범위 추출"""
        match = re.match(r'(\d+)_(\d+)', folder_name)
        if match:
            min_age = int(match.group(1))
            max_age = int(match.group(2))
            return {
                'min': min_age,
                'max': max_age,
                'range': list(range(min_age, max_age + 1)),
                'label': folder_name
            }
        return None

    def calculate_age_thresholds(self, sentences):
        """실제 데이터 분포를 기반으로 나이별 임계값 계산 (조정된 버전)"""
        age_thresholds = {}

        for age_label in ['4_7', '8_10', '11_13']:
            group_sentences = [s for s in sentences if s.get('difficulty') == age_label]
            if not group_sentences:
                continue

            word_counts = sorted([s['word_count'] for s in group_sentences])
            age_info = self.parse_age_from_folder(age_label)

            if age_info:
                num_ages = len(age_info['range'])

                # 더 균등한 분배를 위한 백분위수 조정
                if age_label == '4_7':
                    # 4세: 0-20%, 5세: 20-50%, 6세: 50-75%, 7세: 75-100%
                    percentiles = [20, 50, 75]
                elif age_label == '8_10':
                    # 8세: 0-35%, 9세: 35-70%, 10세: 70-100%
                    percentiles = [35, 70]
                elif age_label == '11_13':
                    # 11세: 0-40%, 12세: 40-80%, 13세: 80-100%
                    percentiles = [40, 80]
                else:
                    # 기본값: 균등 분배
                    percentiles = [i * (100 / num_ages) for i in range(1, num_ages)]

                thresholds = [word_counts[int(len(word_counts) * p / 100)] for p in percentiles]
                age_thresholds[age_label] = thresholds

        return age_thresholds

    def assign_specific_age_dynamic(self, age_info, word_count, thresholds):
        """동적 임계값 기반으로 나이 할당"""
        if not age_info or not thresholds:
            return None

        age_label = age_info['label']
        age_range = age_info['range']

        if age_label not in thresholds:
            return age_range[len(age_range) // 2]

        thresh = thresholds[age_label]

        for i, t in enumerate(thresh):
            if word_count < t:
                return age_range[i]

        return age_range[-1]

    def load_training_data(self):
        """Training 폴더의 라벨링데이터 로드"""
        train_label_path = self.base_path / "training"
        sentences = []

        # 1차: 나이 할당 없이 로드
        for json_file in train_label_path.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    difficulty_folder = json_file.parent.name

                    if 'paragraphInfo' in data:
                        for paragraph in data['paragraphInfo']:
                            if 'srcText' in paragraph:
                                sentences.append({
                                    'text': paragraph['srcText'],
                                    'type': 'original',
                                    'difficulty': difficulty_folder,
                                    'title': data.get('title', ''),
                                    'word_count': paragraph.get('srcWordEA', 0),
                                    'source_file': json_file.name
                                })

                            if 'plotSummaryInfo' in paragraph and paragraph['plotSummaryInfo']:
                                plot_summary = paragraph['plotSummaryInfo']
                                if 'plotSummaryText' in plot_summary:
                                    sentences.append({
                                        'text': plot_summary['plotSummaryText'],
                                        'type': 'summary',
                                        'form': plot_summary.get('form', ''),
                                        'difficulty': difficulty_folder,
                                        'title': data.get('title', ''),
                                        'word_count': plot_summary.get('textWordEA', 0),
                                        'source_file': json_file.name
                                    })

                print(f"✓ 로드 완료: {json_file.name}")
            except Exception as e:
                print(f"✗ 로드 실패: {json_file.name} - {e}")

        print(f"\n총 {len(sentences)}개 문장 로드 완료!")

        # 2차: 임계값 계산 및 나이 할당
        print("\n임계값 계산 중...")
        thresholds = self.calculate_age_thresholds(sentences)

        print("\n[계산된 임계값]")
        for age_label, thresh in sorted(thresholds.items()):
            age_info = self.parse_age_from_folder(age_label)
            print(f"  {age_label}:")
            for i, t in enumerate(thresh):
                print(f"    ~{t}단어 → {age_info['range'][i]}세")
            print(f"    {t}단어~ → {age_info['range'][-1]}세")

        for sent in sentences:
            age_info = self.parse_age_from_folder(sent['difficulty'])
            sent['age'] = self.assign_specific_age_dynamic(age_info, sent['word_count'], thresholds)

        return sentences

    def load_validation_data_with_thresholds(self, train_thresholds):
        """Validation 데이터 로드 (Training 임계값 사용)"""
        val_label_path = self.base_path / "validation"
        sentences = []

        for json_file in val_label_path.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    difficulty_folder = json_file.parent.name

                    if 'paragraphInfo' in data:
                        for paragraph in data['paragraphInfo']:
                            if 'srcText' in paragraph:
                                sentences.append({
                                    'text': paragraph['srcText'],
                                    'type': 'original',
                                    'difficulty': difficulty_folder,
                                    'title': data.get('title', ''),
                                    'word_count': paragraph.get('srcWordEA', 0),
                                    'source_file': json_file.name
                                })

                            if 'plotSummaryInfo' in paragraph and paragraph['plotSummaryInfo']:
                                plot_summary = paragraph['plotSummaryInfo']
                                if 'plotSummaryText' in plot_summary:
                                    sentences.append({
                                        'text': plot_summary['plotSummaryText'],
                                        'type': 'summary',
                                        'form': plot_summary.get('form', ''),
                                        'difficulty': difficulty_folder,
                                        'title': data.get('title', ''),
                                        'word_count': plot_summary.get('textWordEA', 0),
                                        'source_file': json_file.name
                                    })

                print(f"✓ 로드 완료: {json_file.name}")
            except Exception as e:
                print(f"✗ 로드 실패: {json_file.name} - {e}")

        print(f"\n총 {len(sentences)}개 검증 문장 로드 완료!")

        # Training 임계값 사용!
        for sent in sentences:
            age_info = self.parse_age_from_folder(sent['difficulty'])
            sent['age'] = self.assign_specific_age_dynamic(age_info, sent['word_count'], train_thresholds)

        return sentences

    def clean_sentences(self, sentences, min_words=3, max_words=50):
        """문장 정제 (단어 수 기반)"""
        # 자주 나오는 오타 매핑
        typo_dict = {
            '빗주라': '빗자루',
        }

        cleaned = []
        for item in sentences:
            sent = item['text']
            word_count = item.get('word_count', 0)

            if min_words <= word_count <= max_words:
                # 오타 수정
                for wrong, correct in typo_dict.items():
                    sent = sent.replace(wrong, correct)

                sent = sent.strip()
                if sent:
                    cleaned_item = item.copy()
                    cleaned_item['text'] = sent
                    cleaned.append(cleaned_item)
        return cleaned

    def get_statistics(self, sentences):
        """데이터 통계 출력"""
        print("\n=== 데이터 통계 ===")

        difficulty_counts = Counter([s['difficulty'] for s in sentences])
        print("\n[난이도 범위별 문장 수]")
        for diff, count in sorted(difficulty_counts.items()):
            print(f"  {diff}: {count}개")

        age_counts = Counter([s.get('age') for s in sentences if s.get('age') is not None])
        print("\n[세부 나이별 문장 수]")
        for age, count in sorted(age_counts.items()):
            print(f"  {age}세: {count}개")

        type_counts = Counter([s['type'] for s in sentences])
        print("\n[타입별 문장 수]")
        for t, count in type_counts.items():
            print(f"  {t}: {count}개")

        summary_sentences = [s for s in sentences if s['type'] == 'summary']
        if summary_sentences:
            form_counts = Counter([s.get('form', 'unknown') for s in summary_sentences])
            print("\n[요약 형태별]")
            for form, count in form_counts.items():
                print(f"  {form}: {count}개")

        print("\n[나이별 평균 단어 수]")
        for age in sorted(set(s['age'] for s in sentences if s.get('age'))):
            age_data = [s for s in sentences if s['age'] == age]
            avg_words = sum(s['word_count'] for s in age_data) / len(age_data)
            print(f"  {age}세: {avg_words:.1f}개")


if __name__ == "__main__":
    preprocessor = DataPreprocessor("../data/open_data")

    print("=" * 50)
    print("Training 데이터 로드 중...")
    print("=" * 50)
    train_sentences = preprocessor.load_training_data()

    print("\n" + "=" * 50)
    print("Validation 데이터 로드 중...")
    print("=" * 50)
    # Training에서 이미 계산된 임계값을 저장
    # 먼저 clean 전 데이터로 임계값 계산
    train_thresholds = preprocessor.calculate_age_thresholds(train_sentences)

    # Validation 로드 시 Training 임계값 전달
    val_sentences = preprocessor.load_validation_data_with_thresholds(train_thresholds)

    # clean은 나이 할당 후에
    train_clean = preprocessor.clean_sentences(train_sentences, min_words=3, max_words=50)
    val_clean = preprocessor.clean_sentences(val_sentences, min_words=3, max_words=50)

    print("\n" + "=" * 50)
    print("Training 데이터 통계")
    print("=" * 50)
    preprocessor.get_statistics(train_clean)

    print("\n" + "=" * 50)
    print("Validation 데이터 통계")
    print("=" * 50)
    preprocessor.get_statistics(val_clean)

    import pickle

    output_file = '../data/pickle/processed_sentences.pkl'
    with open(output_file, 'wb') as f:
        pickle.dump({
            'train': train_clean,
            'validation': val_clean,
            'thresholds': train_thresholds  # 임계값도 저장
        }, f)
    print(f"\n✓ {output_file} 저장 완료!")

    print("\n" + "=" * 50)
    print("샘플 데이터 (각 나이별 1개씩)")
    print("=" * 50)
    ages_shown = set()
    for sent in train_clean:
        if sent.get('age') and sent['age'] not in ages_shown:
            ages_shown.add(sent['age'])
            print(f"\n[{sent['age']}세] 난이도: {sent['difficulty']}, 단어수: {sent['word_count']}개")
            print(f"  제목: {sent['title']}")
            print(f"  텍스트: {sent['text'][:60]}...")
            if len(ages_shown) >= 10:
                break