// src/utils/levelCalculator.js
export const calculateFinalLevel = (levelHistory) => {
    if (levelHistory.length === 0) {
        return { age: 4, difficulty: 'easy' };
    }

    // 마지막으로 맞춘 문제의 난이도
    const lastCorrect = [...levelHistory]
        .reverse()
        .find(record => record.passed);

    if (lastCorrect) {
        return {
            age: lastCorrect.age,
            difficulty: lastCorrect.difficulty
        };
    }

    // 모두 틀렸다면 가장 낮은 난이도보다 한 단계 낮춤
    const difficultyOrder = ['easy', 'medium', 'hard'];
    const firstQuestion = levelHistory[0];
    const diffIndex = difficultyOrder.indexOf(firstQuestion.difficulty);

    if (diffIndex > 0) {
        return {
            age: firstQuestion.age,
            difficulty: difficultyOrder[diffIndex - 1]
        };
    } else if (firstQuestion.age > 4) {
        return {
            age: firstQuestion.age - 1,
            difficulty: 'hard'
        };
    }

    return { age: 4, difficulty: 'easy' };
};

export const getLevelDescription = (age, difficulty) => {
    const difficultyKo = {
        'easy': '쉬움',
        'medium': '보통',
        'hard': '어려움'
    };

    return `${age}세 ${difficultyKo[difficulty]} 수준`;
};