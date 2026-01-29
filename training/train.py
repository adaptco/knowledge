import torch
import torch.optim as optim
import yaml
import json
import os
import numpy as np
from circuit import EmbeddingCircuit
from reward import calculate_total_reward

def load_config():
    with open("training/config.yaml", "r") as f:
        return yaml.safe_load(f)

def load_contract():
    with open("training/suzuki_v1.contract.json", "r") as f:
        return json.load(f)

def mock_tsukuba_simulation(state, action):
    """
    Simulates a single step in the Tsukuba circuit.
    This is a simplified mock physics model.
    """
    yaw, speed, lat_g, slip = state
    steer, throttle, brake = action
    
    # Update state based on action
    # This is a very basic kinematic update for demonstration
    speed += (throttle * 5.0) - (brake * 10.0)
    speed = max(0, min(speed, 300)) # Clamp speed
    
    steer_rate = steer # Simplifying assumption
    
    yaw += steer * 0.1
    lat_g = steer * speed * 0.01
    slip = steer * 0.05 # Simplified slip
    
    next_state = [yaw, speed, lat_g, slip]
    return next_state, steer_rate

def train():
    print("Initializing Tsukuba Trial...")
    
    config = load_config()
    contract = load_contract()
    
    print(f"Algorithm: {config['algorithm']['name']}")
    print(f"Contract: {contract['name']}")
    
    # Initialize Circuit
    circuit = EmbeddingCircuit(
        input_dim=len(contract['inputs']),
        embedding_dim=config['algorithm']['embedding_dim'],
        output_dim=len(contract['outputs'])
    )
    
    optimizer = optim.Adam(circuit.parameters(), lr=0.001)
    
    # Timesteps from config
    timesteps = 1000 # config['algorithm']['timesteps'] # Reduced for demo speed
    
    print(f"Starting training loop ({timesteps} steps)...")
    
    # Initial state
    state = [0.0, 0.0, 0.0, 0.0] # Yaw, Speed, LatG, Slip
    
    for i in range(timesteps):
        # Prepare input
        input_tensor = torch.tensor([state], dtype=torch.float32)
        
        # Forward pass
        actions, signature = circuit(input_tensor)
        
        # Decode actions
        steer = actions[0, 0].item()
        throttle = actions[0, 1].item()
        brake = actions[0, 2].item()
        
        # Simulate environment
        next_state, steer_rate = mock_tsukuba_simulation(state, [steer, throttle, brake])
        
        # Calculate Reward
        reward = calculate_total_reward(next_state[1], steer_rate, next_state[3])
        
        # Optimization step (Simplified: Maximizing reward directly via dummy loss for demo)
        # In a real PPO, we would collect trajectories and compute policy gradients.
        # Here we just show the loop structure.
        loss = -torch.tensor(reward, requires_grad=True) # Minimize negative reward
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        state = next_state
        
        if i % 100 == 0:
            print(f"Step {i}: Reward={reward:.4f}, Speed={state[1]:.2f}")
            
    # Export Artifact
    output_path = "training/suzuki_r32_circuit.pt"
    circuit.export(output_path)
    print(f"Circuit minted to {output_path}")

if __name__ == "__main__":
    train()
