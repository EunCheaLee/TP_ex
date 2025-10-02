// src/components/GameScore.jsx
import React from 'react';
import { calculateFinalLevel, getLevelDescription } from '../utils/levelCalculator';
import './GameScore.css';

const GameScore = ({
                       correctCount,
                       totalQuestions,
                       score,
                       levelHistory,
                       onRestart
                   }) => {
    const accuracy = ((correctCount / totalQuestions) * 100).toFixed(1);
    const finalLevel = calculateFinalLevel(levelHistory);
    const levelDesc = getLevelDescription(finalLevel.age, finalLevel.difficulty);

    return (
        <div className="game-score-container">
            <div className="game-score">
                <h2>🎉 게임 종료!</h2>

                <div className="final-level">
                    <h3>측정된 난이도</h3>
                    <p className="level-result">{levelDesc}</p>
                </div>

                <div className="score-details">
                    <div className="score-item">
                        <span className="score-label">총 문제 수</span>
                        <span className="score-value">{totalQuestions}개</span>
                    </div>

                    <div className="score-item highlight">
                        <span className="score-label">맞춘 문제</span>
                        <span className="score-value">{correctCount}개</span>
                    </div>

                    <div className="score-item">
                        <span className="score-label">정답률</span>
                        <span className="score-value">{accuracy}%</span>
                    </div>

                    <div className="score-item highlight">
                        <span className="score-label">최종 점수</span>
                        <span className="score-value big">{score}점</span>
                    </div>
                </div>

                <div className="score-message">
                    {correctCount === totalQuestions ? (
                        <p className="perfect">완벽해요! 모든 문제를 맞혔어요!</p>
                    ) : correctCount >= totalQuestions * 0.8 ? (
                        <p className="excellent">훌륭해요! 정말 잘했어요!</p>
                    ) : correctCount >= totalQuestions * 0.6 ? (
                        <p className="good">잘했어요! 조금만 더 노력하면 완벽해요!</p>
                    ) : (
                        <p className="tryagain">괜찮아요! 다시 도전해봐요!</p>
                    )}
                </div>

                <button className="restart-btn" onClick={onRestart}>
                    다시 시작하기
                </button>
            </div>
        </div>
    );
};

export default GameScore;