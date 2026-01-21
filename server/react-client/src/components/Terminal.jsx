import React, { useState, useRef, useEffect } from 'react';

function Terminal({ messages, onCommand }) {
    const [input, setInput] = useState('');
    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            onCommand(input);
            setInput('');
        }
    };

    return (
        <div className="terminal-container">
            <div className="history">
                {messages.map((msg, i) => (
                    <div key={i} className="line">{msg}</div>
                ))}
            </div>
            <div className="input-line">
                <span>$ </span>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    autoFocus
                    placeholder="Enter command (/deploy)..."
                />
            </div>
            <div ref={bottomRef} />
        </div>
    );
}

export default Terminal;
