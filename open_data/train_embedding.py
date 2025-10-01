# pip install tf-keras
from torch import cuda
import random
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path


class FairytalePuzzleGenerator:
    def __init__(self, data_path='../data/pickle/processed_sentences.pkl',
                 model_name='jhgan/ko-sroberta-multitask',
                 device=None):
        """
        동화 기반 퍼즐 게임 생성기

        Args:
            data_path: 전처리된 문장 데이터 경로
            model_name: 사용할 임베딩 모델
        """
        # 디바이스 설정
        self.device = 'cuda' if cuda.is_available() else 'cpu'
        print(f"사용 디바이스: {self.device}")

        # 데이터 로드
        with open(data_path, 'rb') as f:
            data = pickle.load(f)
            self.train_sentences = data['train']
            self.thresholds = data.get('thresholds', {})

        # 임베딩 모델 로드
        print("임베딩 모델 로드 중...")
        self.model = SentenceTransformer(model_name, device=self.device)
        print("✓ 모델 로드 완료!")

        # 나이별로 문장 그룹화
        self._group_by_age()

    def _group_by_age(self):
        """나이별로 문장 그룹화"""
        self.sentences_by_age = {}
        for sent in self.train_sentences:
            age = sent.get('age')
            if age:
                if age not in self.sentences_by_age:
                    self.sentences_by_age[age] = []
                self.sentences_by_age[age].append(sent)

        print(f"\n나이별 문장 수:")
        for age in sorted(self.sentences_by_age.keys()):
            print(f"  {age}세: {len(self.sentences_by_age[age])}개")

    def _split_into_sentences(self, text):
        """텍스트를 단일 문장으로 분리"""
        import re

        # 1. 명확한 문장 종결 패턴으로 분리
        # 마침표/느낌표/물음표 + 공백 + 대문자 or 따옴표
        sentences = re.split(r'(?<=[.!?"])\s+(?=[A-Z가-힣"\'])', text)

        # 2. 각 문장 정제
        clean_sentences = []
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue

            # 따옴표로 시작하지 않고 끝에 마침표가 없으면 추가
            if sent and sent[-1] not in '.!?"':
                sent += '.'

            clean_sentences.append(sent)

        return clean_sentences

    def generate_puzzle(self, age=None, difficulty='medium'):
        """
        퍼즐 생성

        Args:
            age: 대상 나이 (None이면 랜덤)
            difficulty: 난이도 ('easy', 'medium', 'hard')

        Returns:
            puzzle 딕셔너리
        """
        # 나이 선택
        if age is None:
            age = random.choice(list(self.sentences_by_age.keys()))

        if age not in self.sentences_by_age:
            raise ValueError(f"{age}세 데이터가 없습니다.")

            # 나이와 난이도별 단어 수 범위 조정
        if age <= 6:
            word_ranges = {
                'easy': (2, 4),
                'medium': (4, 6),
                'hard': (6, 8)
            }
        elif age <= 10:
            word_ranges = {
                'easy': (5, 8),
                'medium': (8, 12),
                'hard': (12, 15)
            }
        else:  # 11세 이상
            word_ranges = {
                'easy': (8, 12),
                'medium': (12, 15),
                'hard': (15, 20)
            }

        min_words, max_words = word_ranges.get(difficulty, (10, 20))

        # 여러 시도
        for _ in range(100):
            sentence_data = random.choice(self.sentences_by_age[age])
            full_text = sentence_data['text']

            # 문장 분리
            sentences = self._split_into_sentences(full_text)

            # 조건에 맞는 단일 문장 찾기
            for sent in sentences:
                words = sent.split()
                word_count = len(words)

                if min_words <= word_count <= max_words:
                    pieces = [
                        {'id': i, 'word': word, 'position': i}
                        for i, word in enumerate(words)
                    ]

                    shuffled_pieces = pieces.copy()
                    random.shuffle(shuffled_pieces)

                    return {
                        'puzzle_id': hash(sent),
                        'age': age,
                        'difficulty': difficulty,
                        'original_sentence': sent,
                        'pieces': shuffled_pieces,
                        'word_count': word_count,
                        'title': sentence_data.get('title', ''),
                        'metadata': {
                            'type': sentence_data.get('type', ''),
                            'form': sentence_data.get('form', ''),
                            'difficulty_range': sentence_data.get('difficulty', '')
                        }
                    }

        # 못 찾은 경우: type이 'summary'인 것 중에서 찾기 (요약문은 더 짧음)
        summary_sentences = [s for s in self.sentences_by_age[age] if s.get('type') == 'summary']
        if summary_sentences:
            sentence_data = random.choice(summary_sentences)
            sent = sentence_data['text'].strip()
            if not sent[-1] in '.!?"':
                sent += '.'

            words = sent.split()
            pieces = [
                {'id': i, 'word': word, 'position': i}
                for i, word in enumerate(words)
            ]

            shuffled_pieces = pieces.copy()
            random.shuffle(shuffled_pieces)

            return {
                'puzzle_id': hash(sent),
                'age': age,
                'difficulty': difficulty,
                'original_sentence': sent,
                'pieces': shuffled_pieces,
                'word_count': len(words),
                'title': sentence_data.get('title', ''),
                'metadata': sentence_data.get('metadata', {})
            }
        return None

    def verify_answer(self, original_sentence, user_answer, threshold=0.85):
        """
        사용자 답안 검증

        Args:
            original_sentence: 원본 문장
            user_answer: 사용자가 조립한 문장
            threshold: 정답 판정 임계값

        Returns:
            결과 딕셔너리
        """
        # 완전 일치 확인
        is_exact_match = original_sentence.strip() == user_answer.strip()

        # 임베딩 계산
        original_emb = self.model.encode(original_sentence)
        user_emb = self.model.encode(user_answer)

        # 코사인 유사도
        similarity = cosine_similarity([original_emb], [user_emb])[0][0]

        # 정답 판정
        is_correct = is_exact_match or similarity >= threshold

        return {
            'passed': is_correct,
            'similarity': float(similarity),
            'exact_match': is_exact_match,
            'original': original_sentence,
            'user_answer': user_answer,
            'threshold': threshold
        }

    def get_hint(self, original_sentence, user_answer):
        """
        힌트 제공 (첫 단어 또는 마지막 단어)

        Args:
            original_sentence: 원본 문장
            user_answer: 현재 사용자 답안

        Returns:
            힌트 딕셔너리
        """
        original_words = original_sentence.split()
        user_words = user_answer.split() if user_answer else []

        # 첫 단어가 맞는지 확인
        first_correct = (len(user_words) > 0 and
                         user_words[0] == original_words[0])

        # 마지막 단어가 맞는지 확인
        last_correct = (len(user_words) > 0 and
                        len(user_words) == len(original_words) and
                        user_words[-1] == original_words[-1])

        hints = []

        if not first_correct:
            hints.append({
                'type': 'first_word',
                'message': f"첫 단어는 '{original_words[0]}'입니다."
            })

        if not last_correct and len(original_words) > 1:
            hints.append({
                'type': 'last_word',
                'message': f"마지막 단어는 '{original_words[-1]}'입니다."
            })

        # 단어 수 힌트
        if len(user_words) != len(original_words):
            hints.append({
                'type': 'word_count',
                'message': f"총 {len(original_words)}개의 단어가 필요합니다."
            })

        return {
            'hints': hints,
            'first_correct': first_correct,
            'last_correct': last_correct
        }


# 테스트 코드
if __name__ == "__main__":
    # 퍼즐 생성기 초기화
    generator = FairytalePuzzleGenerator()

    # 퍼즐 생성 테스트
    print("\n" + "=" * 50)
    print("퍼즐 생성 테스트")
    print("=" * 50)

    for age in [4, 7, 10, 13]:
        try:
            puzzle = generator.generate_puzzle(age=age, difficulty='medium')
            print(f"\n[{age}세 퍼즐]")
            print(f"제목: {puzzle['title']}")
            print(f"원본: {puzzle['original_sentence']}")
            print(f"단어 수: {puzzle['word_count']}개")
            print(f"섞인 조각: {' / '.join([p['word'] for p in puzzle['pieces']])}")

            # 정답 검증 테스트
            print("\n[검증 테스트]")

            # 1. 정답
            result = generator.verify_answer(
                puzzle['original_sentence'],
                puzzle['original_sentence']
            )
            print(f"  정답: passed={result['passed']}, similarity={result['similarity']:.3f}")

            # 2. 순서만 바뀐 경우
            shuffled = ' '.join([p['word'] for p in puzzle['pieces']])
            result = generator.verify_answer(
                puzzle['original_sentence'],
                shuffled
            )
            print(f"  섞인 답: passed={result['passed']}, similarity={result['similarity']:.3f}")

            # 3. 힌트 테스트
            hints = generator.get_hint(puzzle['original_sentence'], shuffled)
            print(f"  힌트: {len(hints['hints'])}개")
            for hint in hints['hints']:
                print(f"    - {hint['message']}")

        except Exception as e:
            print(f"\n[{age}세 퍼즐] 생성 실패: {e}")