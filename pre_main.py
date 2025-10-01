from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from gensim.models import Word2Vec
import pandas as pd
import random
import os
import json
from datetime import datetime

# ================== 설정 ==================
WORD2VEC_MODEL_PATH = "learning/word2vec_model.bin"
VOCABULARY_CSV_PATH = "learning/fairytale_vocabulary.csv"
SENTENCES_DB_PATH = "learning/sentences_database.json"

# ================== 메모리 저장소 ==================
vocabulary_data: Dict[int, Dict] = {}
quiz_history: List[Dict] = []
word_id_counter = 0
sentences_database: Dict[str, List[str]] = {}  # 단어별 실제 문장


# ================== Pydantic 스키마 ==================
class WordInfo(BaseModel):
    id: int
    word: str
    pos: str
    age_group: int
    difficulty_score: float
    frequency: int


class QuizRequest(BaseModel):
    age_group: int = Field(..., ge=4, le=10, description="연령 (4-10세)")
    num_questions: int = Field(5, ge=1, le=20, description="문제 수")
    user_id: Optional[str] = Field("anonymous", description="사용자 ID")


class QuizQuestion(BaseModel):
    question_id: int
    sentence: str
    blank_position: int
    options: List[str]
    correct_answer: str
    word_info: WordInfo


class QuizResponse(BaseModel):
    questions: List[QuizQuestion]


class AnswerSubmit(BaseModel):
    user_id: Optional[str] = "anonymous"
    question_id: int
    user_answer: str
    correct_answer: str
    word: str
    sentence: str
    age_group: int


class AnswerResult(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: Optional[str] = None


class StatsResponse(BaseModel):
    total_questions: int
    correct_count: int
    accuracy: float
    by_age_group: dict


# ================== FastAPI 앱 ==================
app = FastAPI(
    title="어휘력 학습 API",
    description="4-10세 아동 어휘력 학습을 위한 API (실제 동화 문장 사용)",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Word2Vec 모델 (전역)
w2v_model = None


# ================== 헬퍼 함수 ==================
def load_vocabulary_data():
    """CSV에서 어휘 데이터 로드"""
    global vocabulary_data, word_id_counter

    if not os.path.exists(VOCABULARY_CSV_PATH):
        print(f"⚠ {VOCABULARY_CSV_PATH} 파일이 없습니다.")
        return

    df = pd.read_csv(VOCABULARY_CSV_PATH)

    for idx, row in df.iterrows():
        word_id = idx + 1
        vocabulary_data[word_id] = {
            'id': word_id,
            'word': row['word'],
            'pos': row['pos'] if 'pos' in row else 'Noun',
            'length': int(row['length']),
            'frequency': int(row['frequency']),
            'has_hanja': bool(row['has_hanja']) if 'has_hanja' in row else False,
            'has_foreign': bool(row['has_foreign']) if 'has_foreign' in row else False,
            'pos_complexity': int(row['pos_complexity']) if 'pos_complexity' in row else 1,
            'age_group': int(row['age_group']),
            'difficulty_score': float(row['difficulty_score']) if 'difficulty_score' in row else 1.0,
            'pca_1': float(row['pca_1']) if 'pca_1' in row else 0.0,
            'pca_2': float(row['pca_2']) if 'pca_2' in row else 0.0
        }

    word_id_counter = len(vocabulary_data)
    print(f"✓ {len(vocabulary_data)}개 단어 로드 완료")


def load_word2vec_model():
    """Word2Vec 모델 로드"""
    global w2v_model

    if not os.path.exists(WORD2VEC_MODEL_PATH):
        print(f"⚠ {WORD2VEC_MODEL_PATH} 파일이 없습니다.")
        return

    try:
        w2v_model = Word2Vec.load(WORD2VEC_MODEL_PATH)
        print(f"✓ Word2Vec 모델 로드 완료: {len(w2v_model.wv)} 단어")
    except Exception as e:
        print(f"❌ Word2Vec 모델 로드 실패: {e}")


def load_sentences_database():
    """문장 데이터베이스 로드"""
    global sentences_database

    if not os.path.exists(SENTENCES_DB_PATH):
        print(f"⚠ {SENTENCES_DB_PATH} 파일이 없습니다.")
        print("  템플릿 문장을 사용합니다.")
        return

    try:
        with open(SENTENCES_DB_PATH, 'r', encoding='utf-8') as f:
            sentences_database = json.load(f)
        total_sentences = sum(len(sents) for sents in sentences_database.values())
        print(f"✓ 문장 데이터베이스 로드 완료: {len(sentences_database)}개 단어, {total_sentences}개 문장")
    except Exception as e:
        print(f"❌ 문장 데이터베이스 로드 실패: {e}")


def get_similar_words(word: str, top_n: int = 10) -> List[str]:
    """유사 단어 찾기 (오답 선택지용)"""
    if w2v_model and word in w2v_model.wv:
        similar = w2v_model.wv.most_similar(word, topn=top_n)
        return [w for w, _ in similar]
    return []


def generate_sentence_with_blank(word: str, pos: str, age_group: int) -> str:
    """빈칸 문장 생성 (실제 동화 문장 우선, 없으면 템플릿)"""

    # 1순위: 실제 동화에서 추출한 문장 사용
    if word in sentences_database and sentences_database[word]:
        real_sentences = sentences_database[word]
        # 적절한 길이의 문장 선택 (10-80자)
        suitable = [s for s in real_sentences if 10 <= len(s) <= 80 and word in s]
        if suitable:
            selected = random.choice(suitable)
            # 단어를 빈칸으로 교체
            return selected.replace(word, "___", 1)

    # 2순위: 템플릿 사용
    noun_templates = {
        4: [
            f"나는 ___을(를) 좋아해요.",
            f"엄마가 ___을(를) 주셨어요.",
            f"우리 집에 ___이(가) 있어요.",
            f"동생이 ___을(를) 가지고 놀아요.",
        ],
        5: [
            f"오늘 ___을(를) 보았어요.",
            f"___이(가) 정말 예뻐요.",
            f"공원에서 ___을(를) 발견했어요.",
            f"나는 ___을(를) 배우고 싶어요.",
        ],
        6: [
            f"선생님이 ___에 대해 가르쳐 주셨어요.",
            f"___은(는) 매우 중요해요.",
            f"우리는 ___을(를) 함께 만들었어요.",
            f"책에서 ___에 대해 읽었어요.",
        ],
        7: [
            f"나는 ___에 대해 궁금해요.",
            f"___을(를) 통해 많은 것을 알았어요.",
            f"___이(가) 매우 신기해요.",
            f"___의 특징은 무엇일까요?",
        ],
        8: [
            f"___은(는) 우리 생활에 필요해요.",
            f"___을(를) 연구하는 것은 흥미로워요.",
            f"___의 원리를 이해하게 되었어요.",
            f"___에는 여러 종류가 있어요.",
        ],
        9: [
            f"___은(는) 우리 생활에서 중요한 역할을 해요.",
            f"___에 관한 흥미로운 사실을 발견했어요.",
            f"___의 영향력은 매우 커요.",
            f"미래에는 ___이(가) 더 중요해질 거예요.",
        ],
        10: [
            f"___의 원리를 설명할 수 있나요?",
            f"___에 대한 다양한 관점이 존재해요.",
            f"___을(를) 분석하면 많은 것을 알 수 있어요.",
            f"___은(는) 복잡하지만 매력적이에요.",
        ]
    }

    verb_adj_templates = {
        4: [
            f"토끼가 ___.",
            f"나는 매일 ___.",
            f"동생이 ___.",
        ],
        5: [
            f"친구와 함께 ___.",
            f"오늘 아침에 ___.",
            f"공원에서 ___.",
        ],
        6: [
            f"우리는 함께 ___.",
            f"선생님께서 ___ 하셨어요.",
            f"나는 열심히 ___.",
        ],
        7: [
            f"그 순간 무언가가 ___.",
            f"모두가 함께 ___.",
            f"시간이 지나면서 ___.",
        ],
        8: [
            f"사람들은 종종 ___.",
            f"자연스럽게 ___.",
            f"점점 더 ___.",
        ],
        9: [
            f"우리는 언제나 ___.",
            f"상황에 따라 ___.",
            f"결국 모든 것이 ___.",
        ],
        10: [
            f"복잡한 과정을 거쳐 ___.",
            f"다양한 요인으로 인해 ___.",
            f"결과적으로 ___.",
        ]
    }

    if pos == 'Noun':
        templates = noun_templates
    else:
        templates = verb_adj_templates

    age_templates = templates.get(age_group, templates[7])
    return random.choice(age_templates)


def get_words_by_age(age_group: int, limit: int = 100) -> List[Dict]:
    """연령별 단어 가져오기"""
    words = [w for w in vocabulary_data.values() if w['age_group'] == age_group]
    words = sorted(words, key=lambda x: x['frequency'], reverse=True)
    return words[:limit]


# ================== API 엔드포인트 ==================

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 데이터 로드"""
    print("\n" + "=" * 60)
    print("🚀 어휘력 학습 API 서버 시작")
    print("=" * 60)
    load_vocabulary_data()
    load_word2vec_model()
    load_sentences_database()
    print("=" * 60 + "\n")


@app.get("/")
async def root():
    return {
        "message": "어휘력 학습 API (실제 동화 문장 사용)",
        "version": "1.0.0",
        "total_words": len(vocabulary_data),
        "model_loaded": w2v_model is not None,
        "sentences_loaded": len(sentences_database) > 0,
        "endpoints": {
            "quiz": "/api/quiz (POST)",
            "submit": "/api/submit (POST)",
            "stats": "/api/stats/{user_id} (GET)",
            "words": "/api/words (GET)",
            "age_stats": "/api/age-stats (GET)"
        }
    }


@app.get("/api/words", response_model=List[WordInfo])
async def get_words(
        age_group: Optional[int] = None,
        limit: int = 100
):
    """단어 목록 조회"""
    if age_group:
        words = get_words_by_age(age_group, limit)
    else:
        words = list(vocabulary_data.values())[:limit]

    return [
        WordInfo(
            id=w['id'],
            word=w['word'],
            pos=w['pos'],
            age_group=w['age_group'],
            difficulty_score=w['difficulty_score'],
            frequency=w['frequency']
        )
        for w in words
    ]


@app.get("/api/age-stats")
async def get_age_statistics():
    """연령별 단어 통계"""
    stats = {}
    for age in range(4, 11):
        age_words = [w for w in vocabulary_data.values() if w['age_group'] == age]
        stats[age] = {
            "total_words": len(age_words),
            "avg_length": round(sum(w['length'] for w in age_words) / len(age_words), 2) if age_words else 0,
            "avg_difficulty": round(sum(w['difficulty_score'] for w in age_words) / len(age_words),
                                    3) if age_words else 0
        }

    return {"age_statistics": stats, "total_vocabulary": len(vocabulary_data)}


@app.post("/api/quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    """실제 동화 문장 기반 퀴즈 + 의미 있는 오답 최적화"""

    words = get_words_by_age(request.age_group, limit=100)

    if len(words) < request.num_questions:
        raise HTTPException(
            status_code=404,
            detail=f"{request.age_group}세 단어가 부족합니다. (필요: {request.num_questions}, 보유: {len(words)})"
        )

    selected_words = random.sample(words, request.num_questions)
    questions = []

    for idx, word_data in enumerate(selected_words):
        word = word_data['word']
        pos = word_data['pos']

        # ------------------ 문장 생성 ------------------
        sentence = generate_sentence_with_blank(word, pos, request.age_group)

        # ------------------ 오답 후보 ------------------
        wrong_options = []

        # 1) Word2Vec 유사 단어
        similar_words = get_similar_words(word, top_n=20)
        similar_same_pos = [w for w in similar_words if any(v['word'] == w and v['pos'] == pos for v in words)]
        wrong_options.extend(similar_same_pos)

        # 2) 같은 연령대 & 같은 POS 단어
        same_pos_candidates = [w['word'] for w in words if w['pos'] == pos and w['word'] != word]
        wrong_options.extend(same_pos_candidates)

        # 3) 전체 vocabulary에서 같은 POS 단어
        all_same_pos = [w['word'] for w in vocabulary_data.values() if w['pos'] == pos and w['word'] != word]
        wrong_options.extend(all_same_pos)

        # ------------------ 중복 제거 & 정답 제외 ------------------
        wrong_options = list(set(wrong_options))
        wrong_options = [w for w in wrong_options if w != word]

        # ------------------ 최소 3개 오답 확보 ------------------
        if len(wrong_options) < 3:
            extra_candidates = [w['word'] for w in vocabulary_data.values() if w['word'] != word]
            wrong_options.extend(extra_candidates)
            wrong_options = list(set(wrong_options))
        wrong_options = random.sample(wrong_options, min(3, len(wrong_options)))

        # ------------------ 최종 옵션 구성 ------------------
        options = [word] + wrong_options
        random.shuffle(options)

        question = QuizQuestion(
            question_id=idx + 1,
            sentence=sentence,
            blank_position=0,
            options=options,
            correct_answer=word,
            word_info=WordInfo(
                id=word_data['id'],
                word=word_data['word'],
                pos=pos,
                age_group=word_data['age_group'],
                difficulty_score=word_data.get('difficulty_score', 1),
                frequency=word_data['frequency']
            )
        )
        questions.append(question)

    return QuizResponse(questions=questions)

@app.post("/api/submit", response_model=AnswerResult)
async def submit_answer(answer: AnswerSubmit):
    """답안 제출 및 채점"""

    is_correct = answer.user_answer == answer.correct_answer

    quiz_history.append({
        'user_id': answer.user_id or "anonymous",
        'word': answer.word,
        'sentence': answer.sentence,
        'correct_answer': answer.correct_answer,
        'user_answer': answer.user_answer,
        'is_correct': is_correct,
        'age_group': answer.age_group,
        'created_at': datetime.now().isoformat()
    })

    explanation = None
    if not is_correct:
        explanation = f"정답은 '{answer.correct_answer}'입니다. 다시 한번 생각해보세요!"
    else:
        explanation = "정확합니다! 잘했어요! 🎉"

    return AnswerResult(
        is_correct=is_correct,
        correct_answer=answer.correct_answer,
        explanation=explanation
    )


@app.get("/api/stats/{user_id}", response_model=StatsResponse)
async def get_user_stats(user_id: str):
    """사용자 통계 조회"""

    user_histories = [h for h in quiz_history if h['user_id'] == user_id]

    if not user_histories:
        raise HTTPException(status_code=404, detail="사용자 기록이 없습니다.")

    total = len(user_histories)
    correct = sum(1 for h in user_histories if h['is_correct'])
    accuracy = (correct / total * 100) if total > 0 else 0

    by_age = {}
    for age in range(4, 11):
        age_histories = [h for h in user_histories if h['age_group'] == age]
        if age_histories:
            age_correct = sum(1 for h in age_histories if h['is_correct'])
            by_age[str(age)] = {
                "total": len(age_histories),
                "correct": age_correct,
                "accuracy": round(age_correct / len(age_histories) * 100, 1)
            }

    return StatsResponse(
        total_questions=total,
        correct_count=correct,
        accuracy=round(accuracy, 1),
        by_age_group=by_age
    )


@app.get("/api/all-stats")
async def get_all_stats():
    """전체 통계 (모든 사용자)"""
    if not quiz_history:
        return {"message": "아직 제출된 답안이 없습니다."}

    total = len(quiz_history)
    correct = sum(1 for h in quiz_history if h['is_correct'])

    return {
        "total_submissions": total,
        "correct_answers": correct,
        "overall_accuracy": round(correct / total * 100, 1) if total > 0 else 0,
        "unique_users": len(set(h['user_id'] for h in quiz_history))
    }


@app.delete("/api/reset")
async def reset_history():
    """히스토리 초기화 (테스트용)"""
    global quiz_history
    quiz_history = []
    return {"message": "모든 히스토리가 초기화되었습니다."}


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "vocabulary_loaded": len(vocabulary_data) > 0,
        "model_loaded": w2v_model is not None,
        "sentences_loaded": len(sentences_database) > 0,
        "total_words": len(vocabulary_data),
        "total_submissions": len(quiz_history)
    }