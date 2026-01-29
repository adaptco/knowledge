import numpy as np

def calculate_pace_reward(speed):
    """
    Reward for speed.
    """
    return speed * 0.1

def calculate_smoothness_penalty(steer_rate):
    """
    Penalty for jerky steering (Kawaii Constraint).
    """
    return -np.abs(steer_rate) * 0.5

def calculate_stability_penalty(slip_angle):
    """
    Severe penalty for slip angle > 0.1 rad.
    """
    if np.abs(slip_angle) > 0.1:
        return -10.0
    return 0.0

def calculate_total_reward(speed, steer_rate, slip_angle):
    p = calculate_pace_reward(speed)
    s = calculate_smoothness_penalty(steer_rate)
    st = calculate_stability_penalty(slip_angle)
    return p + s + st
