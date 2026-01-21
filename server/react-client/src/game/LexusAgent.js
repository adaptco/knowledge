
import { ISFModel } from './ISFModel';
import { AlexisDriver } from './AlexisDriver';

/**
 * Lexus - The Avatar Agent
 * Represents the "Super App Super Model" instantiation.
 */
export class LexusAgent {
    constructor(startX, startY) {
        this.name = "Lexus";
        this.description = "A Super App Super Model Avatar";

        // Container
        this.body = new ISFModel(startX, startY);

        // Driver
        this.driver = new AlexisDriver();
    }

    /**
     * Main update loop for the Agent.
     */
    update() {
        // 1. Sense: Get state from the body (Container)
        const state = this.body.getState();

        // 2. Think: Driver (Alexis) processes state and decides controls
        const controls = this.driver.think(state);

        // 3. Act: Apply controls to the body (Container)
        this.body.update(controls);
    }

    getRenderState() {
        return {
            ...this.body.getState(),
            agentName: this.name,
            driverName: this.driver.name,
            driverState: this.driver.state
        };
    }
}
