import React, { useEffect, useState, useRef } from 'react';
import GameCanvas from './components/GameCanvas';
import Terminal from './components/Terminal';

function App() {
    const [messages, setMessages] = useState(['> System initialized.', '> Connected to Ghost Void Shell.']);
    const ws = useRef(null);

    useEffect(() => {
        ws.current = new WebSocket('ws://localhost:8080');

        ws.current.onopen = () => {
            addLog('Connection established to Mainframe.');
        };

        ws.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'SYSTEM_MESSAGE') {
                addLog(`[SYS] ${data.payload}`);
            } else if (data.type === 'GENESIS_EVENT') {
                addLog('!!! GENESIS EVENT PROTOCOL INITIATED !!!');
                // Dispatch event to window so GameCanvas can pick it up
                window.dispatchEvent(new CustomEvent('GENESIS_EVENT'));
            }
        };

        ws.current.onclose = () => {
            addLog('Connection lost.');
        };

        return () => {
            ws.current.close();
        };
    }, []);

    const addLog = (msg) => {
        setMessages(prev => [...prev, `> ${msg}`]);
    };

    const sendCommand = (cmd) => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: 'COMMAND', payload: cmd }));
            addLog(`User: ${cmd}`);
        } else {
            addLog('Error: Offline.');
        }
    };

    return (
        <>
            <GameCanvas />
            <Terminal messages={messages} onCommand={sendCommand} />
        </>
    );
}

export default App;
