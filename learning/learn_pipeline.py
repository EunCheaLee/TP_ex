import json
import re
from typing import Dict, List
from collections import defaultdict
import pandas as pd
import os


class SentenceExtractor:
    def __init__(self):
        self.sentences_by_word = defaultdict(list)

        # soynlp 로드
        try:
            from soynlp.normalizer import repeat_normalize
            self.repeat_normalize = repeat_normalize
            print("✓ soynlp 로드 완료")
        except ImportError:
            self.repeat_normalize = None
            print("⚠ soynlp 로드 실패 (기본 로직 사용)")

        # 한국어 조사/어미 목록
        self.particles = [
            '이', '가', '을', '를', '은', '는', '에', '의', '와', '과', '도', '만',
            '부터', '까지', '로', '으로', '에게', '한테', '께', '더러', '라고',
            '고', '며', '면', '자', '니', '냐', '나', '지', '요', '습니다', 'ㅂ니다'
        ]

    def normalize_text(self, text: str) -> str:
        """soynlp를 사용한 텍스트 정규화"""
        if self.repeat_normalize:
            text = self.repeat_normalize(text, num_repeats=2)
        return text

    def fix_spacing_comprehensive(self, text: str) -> str:
        """강화된 띄어쓰기 수정"""
        text = self.normalize_text(text)

        def merge_single_chars(text):
            result = []
            parts = text.split()
            i = 0
            while i < len(parts):
                if i + 2 < len(parts) and all(len(parts[j]) == 1 for j in range(i, i + 3)):
                    merged = parts[i]
                    j = i + 1
                    while j < len(parts) and len(parts[j]) == 1:
                        merged += parts[j]
                        j += 1
                    result.append(merged)
                    i = j
                else:
                    result.append(parts[i])
                    i += 1
            return ' '.join(result)

        text = merge_single_chars(text)

        for particle in self.particles:
            text = re.sub(f'([가-힣])\s+({particle})(?=\s|$|[,.!?])', r'\1\2', text)

        text = re.sub(r'([가-힣]+)\s+(의)\s+([가-힣]+)', r'\1\2 \3', text)
        text = re.sub(r'([가-힣]{1,3})\s+(습니다|ㅂ니다|었습니다|였습니다|겠습니다)', r'\1\2', text)
        text = re.sub(r'([가-힣]{1,3})\s+(합니다|했습니다|하다|하는|한)', r'\1\2', text)
        text = re.sub(r'\s+([,.!?])', r'\1', text)
        text = re.sub(r'([,.!?])(?=[가-힣])', r'\1 ', text)
        text = re.sub(r'(\d+)\s+(개|명|마리|권|번|살|년|월|일)', r'\1\2', text)
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def clean_sentence(self, sentence: str) -> str:
        """문장 정제"""
        sentence = re.sub(r'[^\w\s\.\!\?\,]', '', sentence)
        sentence = re.sub(r'[0-9，。、]', '', sentence)
        sentence = re.sub(r'\s+', ' ', sentence)
        return sentence.strip()

    def is_valid_sentence(self, sentence: str) -> bool:
        """유효한 문장인지 검사"""
        if not (10 <= len(sentence) <= 100):
            return False

        korean_chars = len(re.findall(r'[가-힣]', sentence))
        if korean_chars < len(sentence) * 0.5:
            return False

        if re.search(r'([가-힣])\1{3,}', sentence):
            return False

        words = sentence.split()
        if words and len(words) > 3 and all(len(w) <= 2 for w in words):
            return False

        return True

    def split_sentences(self, text: str) -> List[str]:
        """문장 분리"""
        sentences = re.split(r'[\.!?]+', text)

        cleaned = []
        for sent in sentences:
            sent = self.clean_sentence(sent)
            if self.is_valid_sentence(sent):
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

        total_words = len(vocabulary_df)
        found_count = 0

        for idx, row in vocabulary_df.iterrows():
            word = row['word']

            if (idx + 1) % 100 == 0:
                print(f"  진행: {idx + 1}/{total_words} ({(idx + 1) / total_words * 100:.1f}%)")

            for title, content in fairytales.items():
                sentences = self.extract_sentences_with_word(content, word)
                if sentences:
                    self.sentences_by_word[word].extend(sentences)
                    found_count += 1

        for word in self.sentences_by_word:
            unique_sents = list(set(self.sentences_by_word[word]))
            unique_sents.sort(key=len)
            self.sentences_by_word[word] = unique_sents[:10]

        words_with_sentences = sum(1 for sents in self.sentences_by_word.values() if sents)
        total_sentences = sum(len(sents) for sents in self.sentences_by_word.values())

        print(f"\n✅ 문장 추출 완료!")
        print(f"  📊 문장이 있는 단어: {words_with_sentences}/{total_words}개 ({words_with_sentences / total_words * 100:.1f}%)")
        print(f"  📝 총 추출된 문장: {total_sentences:,}개")
        if words_with_sentences > 0:
            print(f"  📈 평균 문장/단어: {total_sentences / words_with_sentences:.1f}개\n")

        return self.sentences_by_word

    def save_to_json(self, filepath: str):
        """JSON 파일로 저장"""
        data = {word: sents for word, sents in self.sentences_by_word.items() if sents}

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ 문장 데이터베이스 저장: {filepath}")
        print(f"   단어 수: {len(data):,}개\n")


def load_fairytales(filepath: str, source: str) -> Dict[str, str]:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    fairytales = {}

    if source == "grimm":
        stories = data.get("fairy_tales", [])
        for s in stories:
            key = f"{s.get('number','')}. {s.get('title','')}"
            fairytales[key] = s.get("content","")

    elif source == "aesops":
        stories = data.get("fables", [])
        for s in stories:
            key = f"{s.get('id','')}. {s.get('title','')}" if s.get("id") else s.get("title","")
            fairytales[key] = s.get("content","")

    return fairytales

# 실행
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔧 동화 학습 파이프라인 (그림 형제 포함)")
    print("=" * 60)

    # JSON 파일 경로
    json_files = {
        'hwp': '../data/json/cleaned_hwp.json',
        'pdf': '../data/json/cleaned_pdf.json',
        'grimm': '../data/json/grim_bro.json',  # 그림 형제 동화
        'aesops': '../data/json/aesop_fables.json',
    }

    # 1. JSON 로드
    fairytales = {}
    print("\n📂 동화 파일 로드 중...")

    # HWP, PDF (기존 형식)
    for key in ['hwp', 'pdf']:
        filepath = json_files[key]
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                fairytales.update(data)
            print(f"  ✓ {key.upper()}: {len(data)}권")
        except FileNotFoundError:
            print(f"  ⚠ {key.upper()}: 파일 없음 ({filepath})")
        except Exception as e:
            print(f"  ❌ {key.upper()}: {e}")

    # 그림 형제 동화 (새로운 형식)
    grimm_file = json_files['grimm']
    try:
        grimm_tales = load_fairytales(json_files['grimm'], "grimm")
        fairytales.update(grimm_tales)
        print(f"  ✓ 그림 형제: {len(grimm_tales)}권")
    except FileNotFoundError:
        print(f"  ⚠ 그림 형제: 파일 없음 ({grimm_file})")
    except Exception as e:
        print(f"  ❌ 그림 형제: {e}")

    if not fairytales:
        print("\n❌ 로드된 동화가 없습니다!")
        print("파일 경로를 확인하세요.\n")
        exit(1)

    # 이솝 우화 동화 (새로운 형식)
    aesops_file = json_files['aesops']
    try:
        aesops_tales = load_fairytales(json_files['aesops'], "aesops")
        fairytales.update(aesops_tales)
        print(f"  ✓ 이솝 우화: {len(aesops_tales)}권")
    except FileNotFoundError:
        print(f"  ⚠ 이솝 우화: 파일 없음 ({aesops_file})")
    except Exception as e:
        print(f"  ❌ 이솝 우화: {e}")

    if not fairytales:
        print("\n❌ 로드된 동화가 없습니다!")
        print("파일 경로를 확인하세요.\n")
        exit(1)

    print(f"\n✅ 총 {len(fairytales)}권 로드\n")

    # 2. 띄어쓰기 교정
    extractor = SentenceExtractor()

    print("=" * 60)
    print("🔧 띄어쓰기 교정 중 (soynlp)...")
    print("=" * 60)

    fixed_fairytales = {}
    for idx, (title, content) in enumerate(fairytales.items(), 1):
        display_title = title[:50] + "..." if len(title) > 50 else title
        print(f"  [{idx}/{len(fairytales)}] {display_title}")

        fixed_content = extractor.fix_spacing_comprehensive(content)
        fixed_fairytales[title] = fixed_content

    # 3. 저장
    output_file = '../data/json/fixed_fairytales.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fixed_fairytales, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 띄어쓰기 교정 완료: {output_file}\n")

    # 4. 어휘 데이터 로드
    vocab_file = 'vocabulary_data_reclassified.csv'

    if not os.path.exists(vocab_file):
        print(f"❌ {vocab_file} 파일이 없습니다.")
        print("먼저 어휘 데이터를 생성하세요.\n")
        exit(1)

    vocab_df = pd.read_csv(vocab_file)
    print(f"✓ 어휘 데이터: {len(vocab_df):,}개 단어\n")

    # 5. 문장 추출
    sentences_db = extractor.build_sentence_database(fixed_fairytales, vocab_df)

    # 6. 저장
    extractor.save_to_json('sentences_database.json')

    # 7. 샘플
    print("=" * 60)
    print("📋 샘플 확인")
    print("=" * 60)

    shown = 0
    for word, sentences in sentences_db.items():
        if sentences and shown < 5:
            print(f"\n💬 '{word}' ({len(sentences)}개 문장)")
            for i, sent in enumerate(sentences[:2], 1):
                print(f"   {i}. {sent}")
            shown += 1

    print("\n" + "=" * 60)
    print("✅ 완료!")
    print("=" * 60)
    print("\n📦 생성 파일:")
    print(f"  ✓ {output_file}")
    print(f"  ✓ sentences_database.json")
    print(f"\n📊 최종 통계:")
    print(f"  전체 동화: {len(fairytales)}권")
    print(f"  추출 문장: {sum(len(s) for s in sentences_db.values()):,}개")
    print(f"  학습 단어: {len([w for w, s in sentences_db.items() if s])}개")
    print("\n🚀 FastAPI 서버를 재시작하세요!\n")