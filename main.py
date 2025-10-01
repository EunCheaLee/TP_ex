# main.py
from fastapi import FastAPI
from pydantic import BaseModel
import pickle

from open_data.train_embedding import FairytalePuzzleGenerator

app = FastAPI()

# 전처리된 문장 로드
with open('processed_sentences.pkl', 'rb') as f:
    train_sentences = pickle.load(f)
    val_sentences = pickle.load(f)

puzzle_gen = FairytalePuzzleGenerator(train_sentences)


class AnswerRequest(BaseModel):
    puzzle_id: int
    user_answer: str
    original_sentence: str


@app.post("/puzzle/generate")
async def generate_puzzle(difficulty: str = "easy"):
    puzzle = puzzle_gen.generate_puzzle(difficulty)
    # DB에 저장
    # puzzle_id = save_to_db(puzzle)
    return puzzle


@app.post("/puzzle/verify")
async def verify_answer(request: AnswerRequest):
    result = puzzle_gen.verify_answer(
        request.original_sentence,
        request.user_answer
    )

    # DB에 결과 저장
    if result['passed']:
        # user_stats 업데이트
        pass

    return result