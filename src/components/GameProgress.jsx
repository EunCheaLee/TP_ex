// src/components/GameProgress.jsx
import React from 'react';
import './GameProgress.css';

const GameProgress = ({ current, total, age, difficulty }) => {
    const progress = (current / total) * 100;

    const difficultyKo = {
        'easy': '쉬움',
        'medium': '보통',
        'hard': '어려움'
    };

    return (
        <div className="game-progress">
            <div className="progress-info">
        <span className="progress-text">
          문제 {current} / {total}
        </span>
                <span className="level-text">
          {age}세 · {difficultyKo[difficulty]}
        </span>
            </div>
            <div className="progress-bar">
                <div
                    className="progress-fill"
                    style={{ width: `${progress}%` }}
                />
            </div>
        </div>
    );
};

export default GameProgress;