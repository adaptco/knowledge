
/**
 * Alexis - The Driver
 * "Expert at modeling apps as a super app super model application of an Agent from running all the time."
 */
export class AlexisDriver {
    constructor() {
        this.name = "Alexis";
        this.role = "Super App Model Expert";
        this.state = "IDLE"; // IDLE, DRIVING, MODELING, OPTIMIZING
    }

    think(vehicleState) {
        // Alexis decides what to do based on the vehicle state and her "Super App" expertise.

        // Placeholder logic simulating "Running all the time"
        const intent = {
            throttle: 0,
            steering: 0,
            brake: 0
        };

        // She drives aggressively but precisely (Super Model style)
        if (vehicleState.speed < 10) {
            intent.throttle = 1.0; // Floor it
            this.state = "DRIVING";
        } else {
            intent.throttle = 0.5; // Cruise
            this.state = "OPTIMIZING";
        }

        // Simple steering logic (e.g., keep y around 300)
        if (vehicleState.position.y > 350) {
            intent.steering = -0.5;
        } else if (vehicleState.position.y < 250) {
            intent.steering = 0.5;
        } else {
            intent.steering = 0;
        }

        return intent;
    }
}
