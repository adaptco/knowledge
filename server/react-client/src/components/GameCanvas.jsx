import React, { useRef, useEffect } from 'react';
import { LexusAgent } from '../game/LexusAgent';

function GameCanvas() {
    const canvasRef = useRef(null);

    // Game State
    const lexusAgent = useRef(null);
    const particles = useRef([]);

    useEffect(() => {
        // Initialize Agent if not present
        if (!lexusAgent.current) {
            lexusAgent.current = new LexusAgent(50, 300);
        }

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        let animationId;

        // Window Resize Handler
        const resize = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight - 200; // Leave room for terminal
        };
        window.addEventListener('resize', resize);
        resize();

        // Genesis Event Handler
        const onGenesis = () => {
            // Spawn particles
            for (let i = 0; i < 100; i++) {
                particles.current.push({
                    x: canvas.width / 2,
                    y: canvas.height / 2,
                    vx: (Math.random() - 0.5) * 10,
                    vy: (Math.random() - 0.5) * 10,
                    life: 100,
                    color: `hsl(${Math.random() * 360}, 100%, 50%)`
                });
            }
        };
        window.addEventListener('GENESIS_EVENT', onGenesis);

        // Game Loop
        const loop = () => {
            // 1. Update Agent
            if (lexusAgent.current) {
                lexusAgent.current.update();
            }

            // 2. Clear
            ctx.fillStyle = '#0d0d0d';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // 3. Render Agent
            if (lexusAgent.current) {
                const state = lexusAgent.current.getRenderState();

                // Draw Car Body
                ctx.save();
                ctx.translate(state.position.x, state.position.y);
                ctx.rotate(state.rotation);

                ctx.fillStyle = '#0055A4'; // Azure Blue
                ctx.shadowBlur = 15;
                ctx.shadowColor = '#0055A4';
                ctx.fillRect(-20, -10, 40, 20); // Simple car shape

                // Draw "Headlights"
                ctx.fillStyle = '#ffcc00';
                ctx.shadowColor = '#ffcc00';
                ctx.fillRect(15, -8, 5, 16);

                ctx.restore();

                // Draw Info / HUD
                ctx.fillStyle = '#00ff41';
                ctx.font = '12px monospace';
                ctx.fillText(`AGENT: ${state.agentName}`, state.position.x - 20, state.position.y - 25);
                ctx.fillText(`DRIVER: ${state.driverName}`, state.position.x - 20, state.position.y - 15);
                ctx.fillText(`STATE: ${state.driverState}`, state.position.x - 20, state.position.y - 5);
            }

            // 4. Render Particles
            particles.current.forEach((part, index) => {
                part.x += part.vx;
                part.y += part.vy;
                part.life--;

                ctx.fillStyle = part.color;
                ctx.fillRect(part.x, part.y, 4, 4);

                if (part.life <= 0) particles.current.splice(index, 1);
            });

            animationId = requestAnimationFrame(loop);
        };

        loop();

        return () => {
            cancelAnimationFrame(animationId);
            window.removeEventListener('resize', resize);
            window.removeEventListener('GENESIS_EVENT', onGenesis);
        }
    }, []);


    return <canvas ref={canvasRef} />;
}

export default GameCanvas;
