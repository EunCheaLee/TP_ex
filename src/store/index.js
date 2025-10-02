import { configureStore } from '@reduxjs/toolkit';
import puzzleReducer from './puzzleSlice';

export const store = configureStore({
    reducer: {
        puzzle: puzzleReducer,
    },
});

export default store;