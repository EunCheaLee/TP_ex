import React from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { setAge, setDifficulty, generatePuzzle } from '../store/puzzleSlice';
import './Settings.css';

const Settings = () => {
    const dispatch = useAppDispatch();
    const { age, difficulty, loading } = useAppSelector((state) => state.puzzle);

    const handleGeneratePuzzle = () => {
        dispatch(generatePuzzle({ age, difficulty }));
    };

    return (
        <div className="settings">
            <select
                value={age}
                onChange={(e) => dispatch(setAge(Number(e.target.value)))}
                disabled={loading}
            >
                {[4, 5, 6, 7, 8, 9, 10, 11, 12, 13].map((a) => (
                    <option key={a} value={a}>
                        {a}세
                    </option>
                ))}
            </select>

            <select
                value={difficulty}
                onChange={(e) => dispatch(setDifficulty(e.target.value))}
                disabled={loading}
            >
                <option value="easy">쉬움</option>
                <option value="medium">보통</option>
                <option value="hard">어려움</option>
            </select>

            <button onClick={handleGeneratePuzzle} disabled={loading}>
                {loading ? '로딩 중...' : '새 퍼즐 시작'}
            </button>
        </div>
    );
};

export default Settings;