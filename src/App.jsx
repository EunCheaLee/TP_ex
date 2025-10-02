import React from 'react';
import { Provider } from 'react-redux';
import store from './store';
import PuzzleGame from './components/PuzzleGame';
import './App.css';

function App() {
    return (
        <>
            <Provider store={store}>
                <div className="App">
                    <PuzzleGame />
                </div>
            </Provider>
        </>
    );
}

export default App;