import json
import re
from typing import Dict, List, Tuple
from collections import defaultdict
import pandas as pd


class SentenceExtractor:
    def __init__(self):
        self.sentences_by_word = defaultdict(list)  # 단어별 문장 저장

    def fix_spacing_errors(self, text: str) -> str:
        """띄어쓰기 오류 수정"""
        # 단일 글자 + 공백 + 단일 글자 패턴 수정
        # "드 디어" → "드디어"
        text = re.sub(r'(\S)\s(\S)(?=\s|$|[,.!?])', r'\1\2', text)

        # 중복 공백 제거
        text = re.sub(r'\s+', ' ', text)

        # 쉼표/마침표 앞 공백 제거
        text = re.sub(r'\s+([,.!?])', r'\1', text)

        return text.strip()

    def clean_sentence(self, sentence: str) -> str:
        """문장 정제"""
        # 띄어쓰기 오류 수정
        sentence = self.fix_spacing_errors(sentence)

        # 특수문자 제거 (문장부호는 유지)
        sentence = re.sub(r'[^\w\s\.\!\?\,]', '', sentence)

        # 숫자, 쉼표 등 제거
        sentence = re.sub(r'[0-9，]', '', sentence)

        return sentence.strip()

    def split_sentences(self, text: str) -> List[str]:
        """문장 분리"""
        # 띄어쓰기 오류 먼저 수정
        text = self.fix_spacing_errors(text)

        # 마침표, 물음표, 느낌표 기준으로 분리
        sentences = re.split(r'[\.!?]+', text)

        # 정제 및 필터링
        cleaned = []
        for sent in sentences:
            sent = self.clean_sentence(sent)
            # 10글자 이상, 100글자 이하인 문장만
            if 10 <= len(sent) <= 100:
                cleaned.append(sent)

        return cleaned

    def extract_sentences_with_word(self, text: str, target_word: str) -> List[str]:
        """특정 단어가 포함된 문장 추출"""
        sentences = self.split_sentences(text)

        matching = []
        for sent in sentences:
            if target_word in sent:
                matching.append(sent)

        return matching

    def build_sentence_database(self, fairytales: Dict[str, str], vocabulary_df: pd.DataFrame):
        """모든 동화에서 각 단어가 포함된 문장 추출"""
        print("\n" + "=" * 60)
        print("📝 동화 원문에서 문장 추출 중...")
        print("=" * 60)

        # 모든 어휘 단어에 대해
        total_words = len(vocabulary_df)

        for idx, row in vocabulary_df.iterrows():
            word = row['word']

            if (idx + 1) % 100 == 0:
                print(f"  진행: {idx + 1}/{total_words} ({(idx + 1) / total_words * 100:.1f}%)")

            # 모든 동화에서 해당 단어가 포함된 문장 찾기
            for title, content in fairytales.items():
                sentences = self.extract_sentences_with_word(content, word)
                self.sentences_by_word[word].extend(sentences)

        # 통계
        words_with_sentences = sum(1 for sentences in self.sentences_by_word.values() if sentences)
        total_sentences = sum(len(sentences) for sentences in self.sentences_by_word.values())

        print(f"\n✅ 문장 추출 완료!")
        print(f"  📊 문장이 있는 단어: {words_with_sentences}/{total_words}개")
        print(f"  📝 총 추출된 문장: {total_sentences:,}개")
        print(f"  📈 평균 문장/단어: {total_sentences / words_with_sentences:.1f}개\n")

        return self.sentences_by_word

    def create_blank_from_sentence(self, sentence: str, target_word: str) -> Tuple[str, int]:
        """문장에서 목표 단어를 빈칸으로 만들기"""
        # 단어의 위치 찾기
        if target_word not in sentence:
            return None, -1

        # 단어를 ___로 교체
        blank_sentence = sentence.replace(target_word, "___", 1)

        # 빈칸 위치 계산 (단어 인덱스)
        words = sentence.split()
        blank_position = -1
        for i, word in enumerate(words):
            if target_word in word:
                blank_position = i
                break

        return blank_sentence, blank_position

    def save_to_json(self, filepath: str):
        """JSON 파일로 저장"""
        data = {word: sentences for word, sentences in self.sentences_by_word.items()}

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ 문장 데이터베이스 저장: {filepath}\n")


# 실행 예시
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔧 동화 문장 추출 및 띄어쓰기 수정")
    print("=" * 60)

    # 1. JSON 로드
    with open('../data/json/cleaned_pdf.json', 'r', encoding='utf-8') as f:
        fairytales = json.load(f)

    print(f"\n✓ 동화책 {len(fairytales)}권 로드")

    # 2. 띄어쓰기 오류 수정
    extractor = SentenceExtractor()

    print("\n" + "=" * 60)
    print("🔧 띄어쓰기 오류 수정 중...")
    print("=" * 60)

    fixed_fairytales = {}
    for title, content in fairytales.items():
        fixed_content = extractor.fix_spacing_errors(content)
        fixed_fairytales[title] = fixed_content

        # 변경 사항 출력 (샘플)
        if "드 디어" in content or "참 말" in content:
            print(f"\n📖 {title}")
            print(f"  원본: {content[:100]}...")
            print(f"  수정: {fixed_content[:100]}...")

    # 3. 수정된 JSON 저장
    with open('../data/json/fixed_fairytales.json', 'w', encoding='utf-8') as f:
        json.dump(fixed_fairytales, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 띄어쓰기 수정 완료: fixed_fairytales.json\n")

    # 4. 어휘 데이터 로드 (이전에 생성한 것)
    try:
        vocab_df = pd.read_csv('../learning/vocabulary_data.csv')
        print(f"✓ 어휘 데이터 로드: {len(vocab_df)}개 단어\n")

        # 5. 문장 추출
        sentences_db = extractor.build_sentence_database(fixed_fairytales, vocab_df)

        # 6. 저장
        extractor.save_to_json('sentences_database.json')

        # 7. 샘플 확인
        print("=" * 60)
        print("📋 샘플 확인")
        print("=" * 60)

        sample_words = list(sentences_db.keys())[:5]
        for word in sample_words:
            sentences = sentences_db[word]
            if sentences:
                print(f"\n단어: '{word}'")
                print(f"  추출된 문장 수: {len(sentences)}개")
                print(f"  예시: {sentences[0]}")

                # 빈칸 만들기 테스트
                blank, pos = extractor.create_blank_from_sentence(sentences[0], word)
                if blank:
                    print(f"  빈칸 문장: {blank}")

    except FileNotFoundError:
        print("⚠️  vocabulary_data.csv 파일이 없습니다.")
        print("먼저 learn_pipeline.py를 실행해주세요.\n")