# reading_comprehension_assessment.py (개선)
from konlpy.tag import Okt
import random
import re


class ReadingComprehensionAssessment:
    def __init__(self, train_embedding):
        self.generator = train_embedding
        self.model = train_embedding.model
        self.okt = Okt()  # 형태소 분석기

    def _extract_proper_nouns(self, sentence):
        """~이/~가로 끝나는 고유명사 추출"""
        # "OOO이", "OOO가" 패턴 찾기
        pattern = r'([가-힣]{2,})(?:이|가)'
        matches = re.findall(pattern, sentence)
        return matches

    def _analyze_sentence(self, sentence):
        """개선된 문장 분석 - 우선순위 기반 요소 추출"""
        clean_sentence = sentence.replace('"', '').replace("'", '').replace('!', '').replace('?', '')

        # 1인칭 확인
        first_person_pronouns = ['나', '저', '내가', '제가', '우리']
        has_first_person = any(p in clean_sentence for p in first_person_pronouns)

        # 고유명사 패턴
        korean_names = re.findall(r'([가-힣]{2,})(?:이|가|은|는)', clean_sentence)
        foreign_names = re.findall(r'([가-힣]*[A-Z][a-z가-힣]+[가-힣]*)', sentence)
        proper_nouns = korean_names + foreign_names

        # 형태소 분석
        morphs = self.okt.pos(clean_sentence, norm=True, stem=False)

        nouns = []
        verbs = []
        verb_phrases = []
        persons = []
        objects = []
        all_locations = []

        # 키워드 정의
        person_keywords = ['사람', '아이', '엄마', '아빠', '할머니', '할아버지',
                           '선생님', '친구', '어부', '왕자', '공주', '임금',
                           '소년', '소녀', '남자', '여자', '어린이', '아이들']

        country_keywords = ['고구려', '백제', '신라', '가야', '고려', '조선',
                            '한국', '중국', '일본', '미국', '영국', '프랑스']

        specific_locations = ['집', '학교', '공원', '산', '바다', '강', '숲',
                              '마을', '궁전', '성', '호수', '탑']

        abstract_locations = ['나라', '세상', '곳', '안', '밖', '방', '길', '하늘', '땅']

        # 복합 명사 처리 (학교 체육관 → 체육관 우선)
        compound_locations = []

        # 1인칭 화자
        if has_first_person:
            persons.insert(0, '화자')

        # 고유명사 추가
        persons.extend([name.rstrip('이가은는') for name in proper_nouns if len(name) >= 2])

        # 형태소 처리
        i = 0
        while i < len(morphs):
            word, pos = morphs[i]

            if pos == 'Noun' and len(word) >= 2:
                nouns.append(word)

                # 복합 장소명: 명사 + 명사 (학교 + 체육관)
                if word in specific_locations and i + 1 < len(morphs):
                    next_word, next_pos = morphs[i + 1]
                    if next_pos == 'Noun' and next_word in specific_locations:
                        # 두 번째 명사가 더 구체적
                        compound_locations.append(next_word)
                        i += 2
                        continue

                # 동사구: 명사 + 을/를 + 동사
                if i + 2 < len(morphs):
                    josa, josa_pos = morphs[i + 1]
                    verb, verb_pos = morphs[i + 2]

                    if josa_pos == 'Josa' and josa in ['을', '를'] and verb_pos == 'Verb':
                        verb_clean = verb.rstrip('다')

                        # 추상명사 제외 (여기, 이것 등)
                        abstract_words = ['여기', '거기', '저기', '이것', '그것', '것']
                        if word not in abstract_words:
                            verb_phrase = f"{word}을 {verb_clean}다"
                            verb_phrases.append(verb_phrase)
                            objects.append(word)
                        i += 3
                        continue

                # 목적격 조사
                if i + 1 < len(morphs):
                    next_word, next_pos = morphs[i + 1]
                    if next_pos == 'Josa' and next_word in ['을', '를']:
                        objects.append(word)

                # 사람 키워드
                if word in person_keywords or word.endswith('님'):
                    if word not in persons:
                        persons.append(word)

                # 장소 우선순위
                if word in country_keywords:
                    all_locations.append({'word': word, 'priority': 'high'})
                elif word in specific_locations or word in compound_locations:
                    # 복합명사의 구체적 부분 우선
                    priority = 'high' if word in compound_locations else 'medium'
                    all_locations.append({'word': word, 'priority': priority})
                elif word in abstract_locations:
                    # "바다"를 추상으로 분류 (불바다 같은 비유적 표현 방지)
                    if word == '바다' and '불바다' in sentence:
                        continue  # 스킵
                    all_locations.append({'word': word, 'priority': 'low'})

            elif pos == 'Verb' and len(word) >= 2:
                verbs.append(word)

            i += 1

        # 주어: 1인칭 > 고유명사 > 사람 키워드
        subject = persons[0] if persons else (nouns[0] if nouns else None)

        # 목적어: 동사구 > 목적격 명사
        if verb_phrases:
            obj = verb_phrases[0]
        elif objects:
            obj = objects[0]
        else:
            obj_candidates = [n for n in nouns if n != subject and n not in persons]
            obj = obj_candidates[0] if obj_candidates else None

        # 장소: 우선순위별
        location = None
        for priority in ['high', 'medium', 'low']:
            candidates = [loc['word'] for loc in all_locations if loc['priority'] == priority]
            if candidates:
                location = candidates[0]
                break

        # 동작
        action = verb_phrases[0] if verb_phrases else (verbs[0] if verbs else None)

        return {
            'subject': subject,
            'object': obj,
            'location': location,
            'action': action,
            'verb_phrases': verb_phrases,
            'nouns': nouns,
            'persons': persons,
            'locations': [loc['word'] for loc in all_locations],
            'verbs': verbs,
            'has_first_person': has_first_person,
            'full_sentence': sentence
        }

    def _create_question(self, sentence, sentence_info, question_type):
        """개선된 질문 생성"""
        subject = sentence_info['subject']
        obj = sentence_info['object']
        location = sentence_info['location']
        action = sentence_info['action']
        persons = sentence_info.get('persons', [])
        has_first_person = sentence_info.get('has_first_person', False)
        verb_phrases = sentence_info.get('verb_phrases', [])

        if question_type == 'who':
            if not persons:
                raise ValueError("사람 주체를 찾을 수 없습니다.")

            # 1인칭 화자가 있고 다른 인물도 있는 경우
            if persons[0] == '화자' and len(persons) > 1:
                # 실제 주인공(다른 인물)을 정답으로
                correct_answer = persons[1]
                question = "이 글의 주인공(주요 인물)은 누구인가요?"

            # 순수 1인칭 독백 (화자만 있음)
            elif persons[0] == '화자' and len(persons) == 1:
                # 이런 문장은 who 문제로 부적합 → 에러 발생시켜 스킵
                raise ValueError("1인칭 독백은 who 문제 부적합")

            # 3인칭 서술 (화자 아님)
            else:
                correct_answer = persons[0]
                question = "이 글의 주인공(주요 인물)은 누구인가요?"

        elif question_type == 'what':
            # 동사구가 있으면 우선 사용
            correct_answer = obj or sentence_info['action']
            if not correct_answer:
                raise ValueError("목적어/동작을 찾을 수 없습니다.")

            persons = sentence_info.get('persons', [])
            if subject and subject in persons:
                question = f"{subject}이(가) 무엇을 했나요?"
            else:
                question = "이 글에서 일어난 일은 무엇인가요?"

        elif question_type == 'where':
            correct_answer = location
            if not correct_answer:
                raise ValueError("장소를 찾을 수 없습니다.")
            question = "이 일이 어디에서 일어났나요?"

        elif question_type == 'why':
            correct_answer = action
            if not correct_answer:
                raise ValueError("동작을 찾을 수 없습니다.")
            question = "왜 이런 일이 일어났나요?"

        elif question_type == 'how':
            correct_answer = action
            if not correct_answer:
                raise ValueError("동작을 찾을 수 없습니다.")
            question = "어떻게 이 일이 일어났나요?"

        else:
            correct_answer = subject or obj
            question = "이 글의 내용으로 알맞은 것은?"

        return question, correct_answer

    def generate_comprehension_question(self, age_level, question_type='auto'):
        """문해력 문제 생성 (검증 강화)"""
        sentences = self.generator.sentences_by_age.get(age_level, [])
        if not sentences:
            raise ValueError(f"{age_level}세 데이터가 없습니다.")

        suitable = [s for s in sentences if 10 <= s['word_count'] <= 20]
        if not suitable:
            suitable = sentences

        max_attempts = 50

        for attempt in range(max_attempts):
            sentence_data = random.choice(suitable)
            sentence = sentence_data['text']

            # 부적절한 문장 필터링
            quote_count = sentence.count('"') + sentence.count("'")
            question_mark_count = sentence.count('?')

            # 미래형/추측형 필터링
            future_patterns = ['것이다', '것입니다', '할 것', '될 것', '겠']
            has_future = any(pattern in sentence for pattern in future_patterns)

            # 대화문, 물음표, 미래형 필터링
            if quote_count > 2 or question_mark_count > 1:
                continue

            sentence_info = self._analyze_sentence(sentence)

            # what 질문 조건 강화
            if question_type == 'what':
                has_action = bool(sentence_info.get('verb_phrases') or
                                  sentence_info.get('action'))
                # 미래형이거나 동작이 없거나 대화문이면 스킵
                if not has_action or question_mark_count > 0 or has_future:
                    continue

            # 질문 유형별 필수 조건 체크
            if question_type == 'who' and not sentence_info.get('persons'):
                continue
            if question_type == 'where' and not sentence_info['location']:
                continue

            # auto 모드
            if question_type == 'auto':
                available = []
                if sentence_info.get('persons'):
                    available.append('who')

                # what: 동작 명확 + 대화문X + 미래형X
                if (sentence_info.get('verb_phrases') or sentence_info['action']) and \
                        question_mark_count == 0 and not has_future:
                    available.append('what')

                if sentence_info['location']:
                    available.append('where')

                if not available:
                    continue

                question_type = random.choice(available)

            try:
                question_text, correct_answer = self._create_question(
                    sentence, sentence_info, question_type
                )

                if not correct_answer or len(correct_answer) < 2:
                    continue

                distractors = self._generate_distractors(
                    correct_answer, sentence_info, age_level
                )

                if len(distractors) < 3:
                    continue

                choices = [correct_answer] + distractors[:3]
                random.shuffle(choices)

                return {
                    'type': 'comprehension',
                    'question_type': question_type,
                    'age_level': age_level,
                    'passage': sentence,
                    'question': question_text,
                    'choices': choices,
                    'correct_answer': correct_answer,
                    'correct_index': choices.index(correct_answer),
                    'title': sentence_data.get('title', '')
                }

            except ValueError:
                continue

        raise ValueError(f"{age_level}세, {question_type} 유형의 적절한 문제를 생성할 수 없습니다.")

    def _generate_distractors(self, correct_answer, sentence_info, age_level):
        """개선된 오답 생성"""
        distractors = []

        # 1. 같은 문장의 다른 명사 활용
        all_nouns = sentence_info.get('nouns', [])
        valid_nouns = [n for n in all_nouns if n != correct_answer and len(n) >= 2]
        distractors.extend(valid_nouns[:2])

        # 2. 같은 나이 수준의 다른 문장에서 명사 추출
        same_age_sentences = self.generator.sentences_by_age.get(age_level, [])
        if same_age_sentences and len(distractors) < 3:
            for _ in range(5):  # 5번 시도
                random_sent = random.choice(same_age_sentences)
                info = self._analyze_sentence(random_sent['text'])
                candidates = [n for n in info.get('nouns', [])
                              if n != correct_answer and len(n) >= 2]
                if candidates:
                    distractors.append(random.choice(candidates))
                    if len(distractors) >= 3:
                        break

        # 3. 중복 제거
        distractors = list(dict.fromkeys(distractors))  # 순서 유지하며 중복 제거

        return distractors[:3]

    def verify_answer(self, question_data, user_choice_index):
        """답안 검증"""
        is_correct = (user_choice_index == question_data['correct_index'])

        return {
            'correct': is_correct,
            'age_level': question_data['age_level'],
            'correct_answer': question_data['correct_answer'],
            'user_answer': question_data['choices'][user_choice_index],
            'question_type': question_data['question_type']
        }

    def adaptive_test(self, initial_age=7, num_questions=10):
        """적응형 문해력 평가"""
        current_age = initial_age
        results = []
        correct_count = 0

        print(f"\n{'=' * 60}")
        print(f"문해력 수준 측정 시작 (초기 난이도: {current_age}세)")
        print(f"{'=' * 60}\n")

        for i in range(num_questions):
            try:
                question = self.generate_comprehension_question(current_age, question_type='auto')

                print(f"\n[문제 {i + 1}/{num_questions}] (난이도: {current_age}세)")
                print(f"\n지문: {question['passage']}\n")
                print(f"질문: {question['question']}\n")

                for idx, choice in enumerate(question['choices'], 1):
                    print(f"{idx}) {choice}")

                user_input = int(input("\n답을 선택하세요 (1-4): ")) - 1
                result = self.verify_answer(question, user_input)

                results.append(result)

                if result['correct']:
                    print("✓ 정답입니다!")
                    correct_count += 1
                    if current_age < 13:
                        current_age += 1
                else:
                    print(f"✗ 오답입니다. 정답: {result['correct_answer']}")
                    if current_age > 4:
                        current_age -= 1
            except (ValueError, IndexError):
                print("잘못된 입력입니다.")
                continue
            except Exception as e:
                print(f"문제 생성 실패: {e}")
                continue

        accuracy = correct_count / num_questions * 100

        print(f"\n{'=' * 60}")
        print(f"문해력 평가 결과")
        print(f"{'=' * 60}")
        print(f"정답률: {accuracy:.1f}% ({correct_count}/{num_questions})")
        print(f"추정 문해력 수준: {current_age}세")
        print(f"{'=' * 60}\n")

        return {
            'estimated_level': current_age,
            'accuracy': accuracy,
            'correct_count': correct_count,
            'total_questions': num_questions,
            'results': results
        }

# 테스트 코드
if __name__ == "__main__":
    from train_embedding import FairytalePuzzleGenerator

    print("퍼즐 생성기 초기화 중...")
    puzzle_gen = FairytalePuzzleGenerator()

    print("문해력 평가 시스템 초기화 중...")
    assessment = ReadingComprehensionAssessment(puzzle_gen)

    print("\n" + "=" * 60)
    print("문해력 문제 생성 테스트")
    print("=" * 60)

    for age in [5, 8, 11]:
        print(f"\n{'=' * 60}")
        print(f"{age}세 수준 문제")
        print(f"{'=' * 60}")

        for q_type in ['who', 'what', 'where']:
            try:
                question = assessment.generate_comprehension_question(
                    age_level=age,
                    question_type=q_type
                )

                print(f"\n[{q_type} 유형]")
                print(f"지문: {question['passage']}")
                print(f"질문: {question['question']}")

                for i, choice in enumerate(question['choices'], 1):
                    marker = "✓" if i - 1 == question['correct_index'] else " "
                    print(f"  {marker} {i}) {choice}")

            except Exception as e:
                print(f"\n[{age}세 {q_type}] 생성 실패: {e}")

    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)