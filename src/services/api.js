const API_URL = 'http://localhost:8000';

export const puzzleAPI = {
    // 퍼즐 생성
    generatePuzzle: async (age, difficulty) => {
        const response = await fetch(`${API_URL}/api/puzzle/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ age, difficulty }),
        });

        if (!response.ok) {
            throw new Error('퍼즐 생성에 실패했습니다.');
        }

        return await response.json();
    },

    // 답안 제출
    submitAnswer: async (puzzleId, userAnswer) => {
        const response = await fetch(`${API_URL}/api/puzzle/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                puzzle_id: puzzleId,
                user_answer: userAnswer,
            }),
        });

        if (!response.ok) {
            throw new Error('답안 제출에 실패했습니다.');
        }

        return await response.json();
    },

    // 힌트 요청
    getHint: async (puzzleId, currentAnswer) => {
        const response = await fetch(`${API_URL}/api/puzzle/hint`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                puzzle_id: puzzleId,
                current_answer: currentAnswer,
            }),
        });

        if (!response.ok) {
            throw new Error('힌트 요청에 실패했습니다.');
        }

        return await response.json();
    },
};