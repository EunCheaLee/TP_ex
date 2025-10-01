# vocabulary_assessment.py
import random
from collections import defaultdict


class VocabularyAssessment:
    def __init__(self, train_embedding):
        """
        어휘력 수준 측정 시스템

        Args:
            puzzle_generator: FairytalePuzzleGenerator 인스턴스
        """
        self.generator = train_embedding
        self.model = train_embedding.model

        # 어휘 난이도별 단어 데이터베이스 (동화 데이터에서 추출)
        self.vocab_db = self._build_vocabulary_database()

    def _build_vocabulary_database(self):
        """나이별 어휘 데이터베이스 구축"""
        vocab_by_age = defaultdict(set)

        for age, sentences in self.generator.sentences_by_age.items():
            for sent_data in sentences:
                words = sent_data['text'].split()
                # 조사 제외, 2글자 이상 단어만
                exclude_particles = ['은', '는', '이', '가', '을', '를', '에', '와', '과', '의', '도', '만', '에서', '으로']
                meaningful_words = [
                    w for w in words
                    if len(w) >= 2 and not any(w.endswith(p) for p in exclude_particles)
                ]
                vocab_by_age[age].update(meaningful_words)

        return {age: list(words) for age, words in vocab_by_age.items()}

    def generate_assessment_question(self, target_age, question_type='definition'):
        """
        평가 문제 생성

        Args:
            target_age: 목표 나이 (4~13)
            question_type: 'definition' (단어 뜻), 'context' (문맥), 'synonym' (유사어)

        Returns:
            문제 딕셔너리
        """
        if question_type == 'definition':
            return self._generate_definition_question(target_age)
        elif question_type == 'context':
            return self._generate_context_question(target_age)
        elif question_type == 'synonym':
            return self._generate_synonym_question(target_age)
        return None

    def _generate_context_question(self, target_age):
        """문맥 속 단어 의미 파악 문제"""
        # 해당 나이 수준의 문장 선택
        sentences = self.generator.sentences_by_age.get(target_age, [])
        if not sentences:
            raise ValueError(f"{target_age}세 데이터가 없습니다.")

        # 적절한 길이의 문장 찾기 (5~15단어)
        suitable = [s for s in sentences if 5 <= s['word_count'] <= 15]
        if not suitable:
            suitable = sentences

        sentence_data = random.choice(suitable)
        sentence = sentence_data['text']
        words = sentence.split()

        # 의미 있는 단어 선택 (명사, 동사, 형용사)
        exclude = ['은', '는', '이', '가', '을', '를', '에', '와', '과', '의', '도', '만']
        candidates = [w for w in words if len(w) >= 2 and not any(w.endswith(e) for e in exclude)]

        if not candidates:
            return self._generate_context_question(target_age)  # 재시도

        # 빈칸 문장 생성(랜덤 위치 마스킹)
        target_word = random.choice(candidates)
        blank_sentence = sentence.replace(target_word, '_______', 1)

        # 오답 선지: 다른 나이 수준의 단어 사용
        distractors = []

        # 쉬운 단어 (더 어린 나이)
        if target_age > 4:
            easier_words = self.vocab_db.get(target_age - 2, [])
            if easier_words:
                distractors.append(random.choice(easier_words))

        # 어려운 단어 (더 높은 나이)
        if target_age < 13:
            harder_words = self.vocab_db.get(target_age + 2, [])
            if harder_words:
                distractors.append(random.choice(harder_words))

        # 같은 수준 단어
        same_level = [w for w in self.vocab_db.get(target_age, []) if w != target_word]
        if same_level:
            distractors.append(random.choice(same_level))

        # 선지 개수 맞추기
        while len(distractors) < 3:
            all_words = [w for words in self.vocab_db.values() for w in words if w != target_word]
            if all_words:
                distractors.append(random.choice(all_words))

        # 정답 포함 섞기(객관식 구성)
        choices = [target_word] + distractors[:3]
        random.shuffle(choices)

        return {
            'type': 'context',
            'age_level': target_age,
            'question': f'다음 문장의 빈칸에 들어갈 알맞은 단어를 고르세요.\n\n{blank_sentence}',
            'original_sentence': sentence,
            'choices': choices,
            'correct_answer': target_word,
            'correct_index': choices.index(target_word),
            'title': sentence_data.get('title', '')
        }

    def _generate_definition_question(self, target_age):
        """단어 뜻 맞추기 문제 (간단 버전)"""
        # 문맥 문제와 유사하지만 단어만 제시
        question = self._generate_context_question(target_age)

        # 문장 전체 대신 단어만 제시
        question['question'] = f'"{question["correct_answer"]}"의 의미로 가장 적절한 것은?'
        question['type'] = 'definition'

        return question

    def _generate_synonym_question(self, target_age):
        """유사어 찾기 문제"""
        # 기본적으로 문맥 문제와 동일하지만, 지문을 "비슷한 말"로 변경
        question = self._generate_context_question(target_age)
        question['question'] = f'다음 문장에서 "{question["correct_answer"]}"와 비슷한 의미의 단어는?'
        question['type'] = 'synonym'

        return question

    def verify_answer(self, question_data, user_choice_index):
        """답안 검증"""
        is_correct = (user_choice_index == question_data['correct_index'])

        return {
            'correct': is_correct,
            'age_level': question_data['age_level'],
            'correct_answer': question_data['correct_answer'],
            'user_answer': question_data['choices'][user_choice_index]
        }

    def adaptive_test(self, initial_age=7, num_questions=10):
        """
        적응형 어휘력 평가

        Args:
            initial_age: 시작 난이도
            num_questions: 문제 수

        Returns:
            평가 결과 및 추정 어휘력 수준
        """
        current_age = initial_age
        results = []
        correct_count = 0

        print(f"\n{'=' * 60}")
        print(f"어휘력 수준 측정 시작 (초기 난이도: {current_age}세)")
        print(f"{'=' * 60}\n")

        for i in range(num_questions):
            # 문제 생성
            question = self._generate_context_question(current_age)

            print(f"\n[문제 {i + 1}/{num_questions}] (난이도: {current_age}세)")
            print(f"{question['question']}\n")

            for idx, choice in enumerate(question['choices'], 1):
                print(f"{idx}) {choice}")

            # 사용자 입력 (실제 서비스에서는 API로 받음)
            try:
                user_input = int(input("\n답을 선택하세요 (1-4): ")) - 1
                result = self.verify_answer(question, user_input)

                results.append(result)

                if result['correct']:
                    print("✓ 정답입니다!")
                    correct_count += 1
                    # 난이도 상승
                    if current_age < 13:
                        current_age += 1
                else:
                    print(f"✗ 오답입니다. 정답: {result['correct_answer']}")
                    # 난이도 하락
                    if current_age > 4:
                        current_age -= 1

            except (ValueError, IndexError):
                print("잘못된 입력입니다. 다음 문제로 넘어갑니다.")
                continue

        # 최종 추정 어휘력
        estimated_level = current_age
        accuracy = correct_count / num_questions * 100

        print(f"\n{'=' * 60}")
        print(f"어휘력 평가 결과")
        print(f"{'=' * 60}")
        print(f"정답률: {accuracy:.1f}% ({correct_count}/{num_questions})")
        print(f"추정 어휘력 수준: {estimated_level}세")
        print(f"{'=' * 60}\n")

        return {
            'estimated_level': estimated_level,
            'accuracy': accuracy,
            'correct_count': correct_count,
            'total_questions': num_questions,
            'results': results
        }


# 테스트 코드
if __name__ == "__main__":
    from train_embedding import FairytalePuzzleGenerator

    # 초기화
    puzzle_gen = FairytalePuzzleGenerator()
    assessment = VocabularyAssessment(puzzle_gen)

    # 개별 문제 생성 테스트
    print("\n" + "=" * 60)
    print("문제 생성 테스트")
    print("=" * 60)

    for age in [5, 8, 11]:
        question = assessment.generate_assessment_question(age, question_type='context')
        print(f"\n[{age}세 수준 문제]")
        print(question['question'])
        for i, choice in enumerate(question['choices'], 1):
            marker = "✓" if i - 1 == question['correct_index'] else " "
            print(f"  {marker} {i}) {choice}")

    # 적응형 평가 실행 (대화형)
    # assessment.adaptive_test(initial_age=7, num_questions=5)