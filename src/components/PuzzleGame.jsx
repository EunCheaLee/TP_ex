// src/components/PuzzleGame.jsx
import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import {
    addBlockToAnswer,
    removeBlockFromAnswer,
    resetAnswer,
    submitAnswer,
    getHint,
    clearError,
    proceedToNext,
    restartGame,
    generatePuzzle,
} from '../store/puzzleSlice';
import Settings from './Settings';
import PuzzleBlock from './PuzzleBlock';
import AnswerArea from './AnswerArea';
import Controls from './Controls';
import GameProgress from './GameProgress';
import GameScore from './GameScore';
import './PuzzleGame.css';

const PuzzleGame = () => {
    const dispatch = useAppDispatch();
    const {
        puzzle,
        sourceBlocks,
        answerBlocks,
        result,
        hints,
        loading,
        error,
        age,
        difficulty,
        currentQuestion,
        totalQuestions,
        correctCount,
        score,
        gameFinished,
        attempts,
        maxAttempts,
        levelHistory,
    } = useAppSelector((state) => state.puzzle);

    // 에러 알림
    useEffect(() => {
        if (error) {
            alert(error);
            dispatch(clearError());
        }
    }, [error, dispatch]);

    const handleAddBlock = (block) => {
        dispatch(addBlockToAnswer(block));
    };

    const handleRemoveBlock = (index) => {
        dispatch(removeBlockFromAnswer(index));
    };

    const handleSubmit = () => {
        if (answerBlocks.length === 0) {
            alert('단어를 배치해주세요.');
            return;
        }

        dispatch(
            submitAnswer({
                puzzleId: puzzle.puzzle_id,
                answerBlocks,
            })
        );
    };

    const handleGetHint = () => {
        dispatch(
            getHint({
                puzzleId: puzzle.puzzle_id,
                answerBlocks,
            })
        );
    };

    const handleReset = () => {
        dispatch(resetAnswer());
    };

    // 다음 문제로
    const handleNextQuestion = () => {
        const passed = result?.passed || false;
        dispatch(proceedToNext({ passed }));

        // 게임이 끝나지 않았으면 다음 문제 자동 생성
        if (currentQuestion + 1 < totalQuestions) {
            setTimeout(() => {
                dispatch(generatePuzzle({ age, difficulty }));
            }, 100);
        }
    };

    // 게임 재시작
    const handleRestartGame = () => {
        dispatch(restartGame());
    };

    // 게임 종료 화면
    if (gameFinished) {
        return (
            <GameScore
                correctCount={correctCount}
                totalQuestions={totalQuestions}
                score={score}
                levelHistory={levelHistory}
                onRestart={handleRestartGame}
            />
        );
    }

    return (
        <div className="puzzle-game">
            <h1>🧩 동화 문장 퍼즐</h1>

            {/* 게임이 시작되지 않았을 때만 설정 표시 */}
            {currentQuestion === 0 && !puzzle && <Settings />}

            {/* 게임 진행 상태 */}
            {puzzle && (
                <GameProgress
                    current={currentQuestion + 1}
                    total={totalQuestions}
                    age={age}
                    difficulty={difficulty}
                />
            )}

            {puzzle && (
                <div className="puzzle-info">
                    <div>
                        <strong>동화:</strong> {puzzle.title}
                    </div>
                    <div>
                        <strong>단어 수:</strong> {puzzle.word_count}개
                    </div>
                </div>
            )}

            {puzzle ? (
                <div className="blocks-container">
                    {sourceBlocks.map((block) => (
                        <PuzzleBlock
                            key={block.id}
                            block={block}
                            onClick={() => handleAddBlock(block)}
                            type="source"
                        />
                    ))}
                </div>
            ) : (
                <div className="blocks-container">
                    <div className="loading">
                        {currentQuestion === 0 ? '새 퍼즐을 시작해주세요' : '로딩 중...'}
                    </div>
                </div>
            )}

            {puzzle && (
                <>
                    <AnswerArea
                        blocks={answerBlocks}
                        onRemove={handleRemoveBlock}
                        onDrop={handleAddBlock}
                    />

                    <div className="controls-wrapper">
                        {/* 시도 횟수 표시 추가 */}
                        {result && !result.passed && attempts < maxAttempts && (
                            <div className="attempt-info">
                                남은 시도: {maxAttempts - attempts}회
                            </div>
                        )}

                        <Controls
                            onSubmit={handleSubmit}
                            onHint={handleGetHint}
                            onReset={handleReset}
                            disabled={loading}
                        />

                        {/* 다음 문제 버튼 - 정답이거나 2번 시도 후 */}
                        {result && (result.passed || attempts >= maxAttempts) && (
                            <button
                                className="btn btn-next"
                                onClick={handleNextQuestion}
                            >
                                다음 문제
                            </button>
                        )}
                    </div>
                </>
            )}

            {/* 결과 표시 */}
            {result && (
                <div className={`result ${result.passed ? 'success' : 'error'}`}>
                    <div className="result-message">{result.message}</div>
                    {result.passed ? (
                        <small>정답: {result.original_sentence}</small>
                    ) : (
                        <div className="answer-comparison">
                            <div>당신의 답: {result.user_sentence}</div>
                            {attempts < maxAttempts ? (
                                <p className="retry-message">💪 한 번 더 도전해보세요!</p>
                            ) : (
                                <div>정답: {result.original_sentence}</div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* 힌트 표시 */}
            {hints && (
                <div className="hints">
                    <strong>💡 힌트</strong>
                    {hints.hints && hints.hints.length > 0 ? (
                        <ul>
                            {hints.hints.map((hint, index) => (
                                <li key={index}>{hint.message}</li>
                            ))}
                        </ul>
                    ) : (
                        <p>모든 단어가 올바른 위치에 있습니다!</p>
                    )}
                </div>
            )}
        </div>
    );
};

export default PuzzleGame;