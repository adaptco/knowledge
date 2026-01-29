import torch
import torch.nn as nn
import torch.nn.functional as F

class EmbeddingCircuit(nn.Module):
    def __init__(self, input_dim=4, embedding_dim=64, output_dim=3):
        super(EmbeddingCircuit, self).__init__()
        
        # Encoder: Compresses telemetry into a Driver Signature
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, embedding_dim),
            nn.Tanh() # Normalize signature
        )
        
        # Control Plane: Processes the signature
        self.control_plane = nn.Sequential(
            nn.Linear(embedding_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU()
        )
        
        # Action Head: Outputs control actions
        self.action_head = nn.Sequential(
            nn.Linear(128, output_dim),
            nn.Tanh() # Actions are typically bounded
        )
        
    def forward(self, x):
        signature = self.encoder(x)
        features = self.control_plane(signature)
        actions = self.action_head(features)
        
        # Remap actions to specific ranges if necessary
        # Steer: [-1, 1] (Tanh is already [-1, 1])
        # Throttle: [0, 1] (Map Tanh [-1, 1] to [0, 1])
        # Brake: [0, 1] (Map Tanh [-1, 1] to [0, 1])
        
        steer = actions[:, 0]
        throttle = (actions[:, 1] + 1) / 2
        brake = (actions[:, 2] + 1) / 2
        
        return torch.stack([steer, throttle, brake], dim=1), signature

    def export(self, path):
        torch.save(self.state_dict(), path)
