// src/components/PuzzleBlock.jsx
import React from 'react';
import './PuzzleBlock.css';

const PuzzleBlock = ({ block, onClick, onDragStart, onDragEnd, type = 'source' }) => {
    const handleDragStart = (e) => {
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('block', JSON.stringify(block));
        if (onDragStart) onDragStart(e);
    };

    const handleDragEnd = (e) => {
        if (onDragEnd) onDragEnd(e);
    };

    return (
        <div
            className={`puzzle-block ${type}`}
            onClick={onClick}
            draggable={true}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
        >
            {block.word}
        </div>
    );
};

export default PuzzleBlock;