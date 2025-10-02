// src/store/puzzleSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { puzzleAPI } from '../services/api';

// 비동기 액션들
export const generatePuzzle = createAsyncThunk(
    'puzzle/generate',
    async ({ age, difficulty }, { rejectWithValue }) => {
        try {
            const data = await puzzleAPI.generatePuzzle(age, difficulty);
            return data;
        } catch (error) {
            return rejectWithValue(error.message);
        }
    }
);

export const submitAnswer = createAsyncThunk(
    'puzzle/submit',
    async ({ puzzleId, answerBlocks }, { rejectWithValue }) => {
        try {
            const userAnswer = answerBlocks.map((block, index) => ({
                id: block.id,
                word: block.word,
                position: index,
            }));

            const data = await puzzleAPI.submitAnswer(puzzleId, userAnswer);
            return data;
        } catch (error) {
            return rejectWithValue(error.message);
        }
    }
);

export const getHint = createAsyncThunk(
    'puzzle/hint',
    async ({ puzzleId, answerBlocks }, { rejectWithValue }) => {
        try {
            const currentAnswer = answerBlocks.map((block, index) => ({
                id: block.id,
                word: block.word,
                position: index,
            }));

            const data = await puzzleAPI.getHint(puzzleId, currentAnswer);
            return data;
        } catch (error) {
            return rejectWithValue(error.message);
        }
    }
);

const initialState = {
    // 설정
    age: 4,
    difficulty: 'easy',

    // 퍼즐 데이터
    puzzle: null,
    sourceBlocks: [],
    answerBlocks: [],

    // 결과 및 힌트
    result: null,
    hints: null,

    // 게임 진행 상태
    currentQuestion: 0,
    totalQuestions: 10,
    correctCount: 0,
    score: 0,
    gameFinished: false,

    // 재도전 관련
    attempts: 0,
    maxAttempts: 2,

    // 난이도 기록 (측정용)
    levelHistory: [],

    // 로딩 상태
    loading: false,
    error: null,
};

// 난이도 순서 정의
const difficultyOrder = ['easy', 'medium', 'hard'];
const maxAge = 13;

// 난이도 낮추기
const getLowerLevel = (currentAge, currentDifficulty) => {
    const currentDiffIndex = difficultyOrder.indexOf(currentDifficulty);

    if (currentDiffIndex === 0) {
        const prevAge = currentAge - 1;
        return {
            age: prevAge < 4 ? 4 : prevAge,
            difficulty: 'hard'
        };
    }

    return {
        age: currentAge,
        difficulty: difficultyOrder[currentDiffIndex - 1]
    };
};

// 난이도 올리기
const getNextLevel = (currentAge, currentDifficulty) => {
    const currentDiffIndex = difficultyOrder.indexOf(currentDifficulty);

    if (currentDiffIndex === 2) {
        const nextAge = currentAge + 1;
        return {
            age: nextAge > maxAge ? maxAge : nextAge,
            difficulty: 'easy'
        };
    }

    return {
        age: currentAge,
        difficulty: difficultyOrder[currentDiffIndex + 1]
    };
};

const puzzleSlice = createSlice({
    name: 'puzzle',
    initialState,
    reducers: {
        setAge: (state, action) => {
            state.age = action.payload;
        },

        setDifficulty: (state, action) => {
            state.difficulty = action.payload;
        },

        addBlockToAnswer: (state, action) => {
            state.answerBlocks.push(action.payload);
            state.result = null;
            state.hints = null;
        },

        removeBlockFromAnswer: (state, action) => {
            state.answerBlocks.splice(action.payload, 1);
        },

        resetAnswer: (state) => {
            state.answerBlocks = [];
        },

        proceedToNext: (state, action) => {
            const { passed } = action.payload || { passed: false };

            // 레벨 기록 저장
            state.levelHistory.push({
                age: state.age,
                difficulty: state.difficulty,
                passed: passed,
                question: state.currentQuestion + 1
            });

            state.currentQuestion += 1;
            state.attempts = 0;

            if (state.currentQuestion >= state.totalQuestions) {
                state.gameFinished = true;
                state.puzzle = null;
                state.sourceBlocks = [];
            } else {
                if (passed) {
                    const nextLevel = getNextLevel(state.age, state.difficulty);
                    state.age = nextLevel.age;
                    state.difficulty = nextLevel.difficulty;
                } else {
                    const lowerLevel = getLowerLevel(state.age, state.difficulty);
                    state.age = lowerLevel.age;
                    state.difficulty = lowerLevel.difficulty;
                }
            }

            state.answerBlocks = [];
            state.result = null;
            state.hints = null;
        },

        restartGame: (state) => {
            state.age = 4;
            state.difficulty = 'easy';
            state.currentQuestion = 0;
            state.correctCount = 0;
            state.score = 0;
            state.attempts = 0;
            state.gameFinished = false;
            state.levelHistory = [];
            state.puzzle = null;
            state.sourceBlocks = [];
            state.answerBlocks = [];
            state.result = null;
            state.hints = null;
        },

        resetPuzzle: (state) => {
            state.puzzle = null;
            state.sourceBlocks = [];
            state.answerBlocks = [];
            state.result = null;
            state.hints = null;
        },

        clearError: (state) => {
            state.error = null;
        },
    },
    extraReducers: (builder) => {
        // 퍼즐 생성
        builder
            .addCase(generatePuzzle.pending, (state) => {
                state.loading = true;
                state.error = null;
                state.result = null;
                state.hints = null;
            })
            .addCase(generatePuzzle.fulfilled, (state, action) => {
                state.loading = false;
                state.puzzle = action.payload;
                state.sourceBlocks = action.payload.blocks;
                state.answerBlocks = [];
            })
            .addCase(generatePuzzle.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || '퍼즐 생성에 실패했습니다.';
            });

        // 답안 제출 (중복 제거)
        builder
            .addCase(submitAnswer.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(submitAnswer.fulfilled, (state, action) => {
                state.loading = false;
                state.result = action.payload;
                state.attempts += 1;

                if (action.payload.passed) {
                    state.correctCount += 1;
                    state.score += 10;
                }
            })
            .addCase(submitAnswer.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || '답안 제출에 실패했습니다.';
            });

        // 힌트 요청
        builder
            .addCase(getHint.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(getHint.fulfilled, (state, action) => {
                state.loading = false;
                state.hints = action.payload;
            })
            .addCase(getHint.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || '힌트 요청에 실패했습니다.';
            });
    },
});

export const {
    setAge,
    setDifficulty,
    addBlockToAnswer,
    removeBlockFromAnswer,
    resetAnswer,
    proceedToNext,
    restartGame,
    resetPuzzle,
    clearError,
} = puzzleSlice.actions;

export default puzzleSlice.reducer;