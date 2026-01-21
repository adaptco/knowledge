
export class ISFModel {
    constructor(startX = 0, startY = 0) {
        this.position = { x: startX, y: startY };
        this.velocity = { x: 0, y: 0 };
        this.rotation = 0; // radians
        this.speed = 0;

        // Vehicle Physical Properties (IS-F specs approx)
        this.mass = 1700; // kg
        this.maxSpeed = 270; // km/h
        this.acceleration = 15; // arbitrary unit
        this.friction = 0.98;
    }

    update(controlInput) {
        // controlInput: { throttle: 0-1, steering: -1 to 1, brake: 0-1 }

        // 1. Apply Throttle
        if (controlInput.throttle > 0) {
            this.speed += controlInput.throttle * this.acceleration * 0.1;
        }

        // 2. Apply Brake / Friction
        if (controlInput.brake > 0) {
            this.speed -= controlInput.brake * 0.5;
        }
        this.speed *= this.friction;

        // 3. Apply Steering
        // Steering effectiveness depends on speed (simplified)
        if (Math.abs(this.speed) > 0.1) {
            this.rotation += controlInput.steering * 0.05;
        }

        // 4. Update Physics
        this.velocity.x = Math.cos(this.rotation) * this.speed;
        this.velocity.y = Math.sin(this.rotation) * this.speed;

        this.position.x += this.velocity.x;
        this.position.y += this.velocity.y;
    }

    getState() {
        return {
            position: this.position,
            velocity: this.velocity,
            rotation: this.rotation,
            speed: this.speed
        };
    }
}
