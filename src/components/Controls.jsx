import React from 'react';
import './Controls.css';

const Controls = ({ onSubmit, onHint, onReset, disabled }) => {
    return (
        <div className="controls">
            <button
                className="btn btn-submit"
                onClick={onSubmit}
                disabled={disabled}
            >
                정답 확인
            </button>
            <button
                className="btn btn-hint"
                onClick={onHint}
                disabled={disabled}
            >
                힌트
            </button>
            <button
                className="btn btn-reset"
                onClick={onReset}
            >
                다시하기
            </button>
        </div>
    );
};

export default Controls;