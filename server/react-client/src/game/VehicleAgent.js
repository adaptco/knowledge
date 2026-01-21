
export class VehicleAgent {
    constructor(id) {
        this.id = id;
        this.name = 'Standard Driver';
        this.intents = {
            throttle: 0,
            steering: 0,
            brake: 0
        };
    }

    /**
     * Called by the container (IS-F Model) to get control inputs.
     * @param {ISFModel} vehicle - The vehicle instance being controlled.
     */
    update(vehicle) {
        // Basic logic: drive forward
        this.intents.throttle = 0.5;

        // Example: steer towards center if too far out
        if (vehicle.position.x > 100) {
            this.intents.steering = -0.1;
        } else if (vehicle.position.x < -100) {
            this.intents.steering = 0.1;
        } else {
            this.intents.steering = 0;
        }
    }

    getControls() {
        return this.intents;
    }
}
