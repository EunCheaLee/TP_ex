// src/components/AnswerArea.jsx
import React, { useState } from 'react';
import PuzzleBlock from './PuzzleBlock';
import './AnswerArea.css';

const AnswerArea = ({ blocks, onRemove, onDrop }) => {
    const [isDragOver, setIsDragOver] = useState(false);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragOver(true);
    };

    const handleDragLeave = () => {
        setIsDragOver(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragOver(false);

        const blockData = e.dataTransfer.getData('block');
        if (blockData) {
            const block = JSON.parse(blockData);
            onDrop(block);
        }
    };

    return (
        <div
            className={`answer-area ${blocks.length === 0 ? 'empty' : ''} ${isDragOver ? 'drag-over' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
        >
            {blocks.length === 0 ? (
                <div className="placeholder">
                    여기에 단어를 드래그하여 문장을 완성하세요
                </div>
            ) : (
                blocks.map((block, index) => (
                    <PuzzleBlock
                        key={`${block.id}-${index}`}
                        block={block}
                        type="answer"
                        onClick={() => onRemove(index)}
                    />
                ))
            )}
        </div>
    );
};

export default AnswerArea;