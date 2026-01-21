import WebSocket from 'ws';
import { spawn, ChildProcess } from 'child_process';
import path from 'path';

const PORT = 8081; // Use a different port for testing to avoid conflicts
const SERVER_PATH = path.join(__dirname, '../server/server.js');

describe('QubeAgent System Test', () => {
    let serverProcess: ChildProcess;
    let ws: WebSocket;

    // Start the server before tests
    beforeAll(async () => {
        return new Promise<void>((resolve, reject) => {
            // Pass PORT via env or arg if server supports it. 
            // The current server.js uses hardcoded 8080. 
            // We might need to modify server.js to accept PORT env var.
            // For now, let's assume 8080 or try to modify server.js first?
            // Re-reading server.js: `const PORT = 8080;` hardcoded.
            // I will assume we run on 8080 for this test and fail if occupied.

            console.log('Spawning server...');
            serverProcess = spawn('node', [SERVER_PATH], {
                // env: { ...process.env, PORT: '8081' } // If we fix server.js
                stdio: 'pipe'
            });

            serverProcess.stdout?.on('data', (data) => {
                const output = data.toString();
                // console.log('[Server]:', output);
                if (output.includes('Server started')) {
                    resolve();
                }
            });

            serverProcess.stderr?.on('data', (data) => {
                console.error('[Server Error]:', data.toString());
            });

            serverProcess.on('error', (err) => reject(err));

            // Safety timeout
            setTimeout(() => reject(new Error('Server start timeout')), 5000);
        });
    });

    // Cleanup after tests
    afterAll(() => {
        if (ws) ws.close();
        if (serverProcess) serverProcess.kill();
    });

    test('Agent should trigger Genesis Event via /deploy', (done) => {
        ws = new WebSocket('ws://localhost:8080');

        ws.on('open', () => {
            // console.log('Connected to Game Server');
            ws.send(JSON.stringify({ type: 'COMMAND', payload: '/deploy' }));
        });

        ws.on('message', (data) => {
            const msg = JSON.parse(data.toString());
            // console.log('Received:', msg);

            if (msg.type === 'GENESIS_EVENT') {
                expect(msg.payload).toBeDefined();
                done();
            }
        });

        ws.on('error', (err) => {
            done(err);
        });
    });
});
