const WebSocket = require('ws');
const fs = require('fs');
const crypto = require('crypto');
const path = require('path');

const PORT = 8080;
const wss = new WebSocket.Server({ port: PORT });

// ADK Event Log Path (permanent knowledge)
const EVENT_LOG_PATH = path.join(__dirname, '../adk/output/event_log.jsonl');

// Ensure output directory exists
fs.mkdirSync(path.dirname(EVENT_LOG_PATH), { recursive: true });

/**
 * Embed an event into permanent knowledge (ADK Event Log).
 * Adheres to contracts/v0/schemas/event.schema.json
 */
function embedEvent(type, payload, context = {}) {
    const event = {
        id: crypto.randomUUID(),
        type: type,
        timestamp: new Date().toISOString(),
        payload: payload,
        context: context
    };

    const line = JSON.stringify(event) + '\n';
    fs.appendFileSync(EVENT_LOG_PATH, line);
    console.log(`[ADK] Event embedded: ${event.id} (type: ${type})`);
    return event;
}

console.log(`Ghost Void Server started on http://localhost:${PORT}`);
console.log('Waiting for the Big Boss to trigger the Genesis Event...');

// Game State
let clients = [];

wss.on('connection', (ws) => {
    clients.push(ws);
    console.log('New client connected. Total:', clients.length);

    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            console.log('Received:', data);

            // Handle Terminal Commands
            if (data.type === 'COMMAND') {
                handleCommand(ws, data.payload);
            }
        } catch (e) {
            console.error('Invalid message format:', message);
        }
    });

    ws.on('close', () => {
        clients = clients.filter(c => c !== ws);
        console.log('Client disconnected. Total:', clients.length);
    });
});

function handleCommand(sender, command) {
    const cmd = command.trim().toLowerCase();

    if (cmd === '/deploy') {
        console.log('!!! GENESIS EVENT TRIGGERED !!!');
        broadcast({
            type: 'SYSTEM_MESSAGE',
            payload: 'Genesis Event initiated by Big Boss...'
        });
        const genesisPayload = { timestamp: Date.now(), trigger: 'deploy_command' };
        broadcast({
            type: 'GENESIS_EVENT',
            payload: genesisPayload
        });

        // Embed to permanent knowledge (ADK Event Log)
        embedEvent('emit', genesisPayload, { source: 'ghost_void_server', command: '/deploy' });
    } else {
        sender.send(JSON.stringify({
            type: 'SYSTEM_MESSAGE',
            payload: `Unknown command: ${command}`
        }));
    }
}

function broadcast(msgObj) {
    const msg = JSON.stringify(msgObj);
    clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(msg);
        }
    });
}
