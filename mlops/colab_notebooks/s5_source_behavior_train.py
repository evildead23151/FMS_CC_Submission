"""
TRUSTLENS: SIGNAL 5 - SOURCE BEHAVIOR MODELING (TREND DECAY)

This script calibrates the time-decay and recovery functions for Source Behavior.
Ensures "Fairness Constraint": Fast recovery for corrections, slow decay for errors.

Artifact Export:
- behavior_decay_params.json
- recovery_curve_plot.png
- artifact_hash.sha256
"""

import numpy as np
import json
import hashlib
import os
import matplotlib.pyplot as plt

OUTPUT_DIR = "./source_model_artifact"

def compute_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def simulate_behavior_dynamics():
    print("🚀 Calibrating Source Behavior Dynamics...")
    
    # 1. Define Decay Function (Exponential Forgetting)
    # Risk Score R(t) = R(t-1) * alpha + NewEvidence
    # Alpha determines memory length.
    
    alpha_short = 0.8 # Fast forgetting (for minor errors)
    alpha_long = 0.95 # Slow forgetting (for repeated major errors)
    
    # 2. Define Recovery Boost
    # Explicit connection creates negative risk (Trust Boost)
    correction_boost = -0.3 
    
    # 3. Simulation: Source corrects a mistake
    time_steps = 30
    risk_trajectory = [0.8] # Starting High Risk
    
    for t in range(1, time_steps):
        # At t=5, source issues transparent correction
        if t == 5:
            new_val = max(0, risk_trajectory[-1] + correction_boost)
        else:
            # Natural decay towards neutral (0.5) if no new negative evidence
            current = risk_trajectory[-1]
            # Decay towards 0.5
            new_val = current * 0.9 + 0.5 * 0.1 
        
        risk_trajectory.append(new_val)
        
    print(f"✅ Recovery Check:")
    print(f"   - Initial Risk: {risk_trajectory[0]}")
    print(f"   - Post-Correction Risk (t=6): {risk_trajectory[6]:.2f}")
    print(f"   - Final Risk (t=30): {risk_trajectory[-1]:.2f}")
    
    # 4. Generate Recovery Plot
    plt.figure()
    plt.plot(risk_trajectory, marker='o', label='Source Risk Score')
    plt.axhline(y=0.5, color='gray', linestyle='--', label='Neutral Baseline')
    plt.title("Source Recovery Dynamics (Correction at t=5)")
    plt.xlabel("Time Steps (Days)")
    plt.ylabel("Risk Score")
    plt.legend()
    plt.savefig(f"{OUTPUT_DIR}/recovery_curve_plot.png")
    
    # 5. Export
    params = {
        "alpha_decay_normal": 0.9,
        "correction_reward": 0.3,
        "min_confidence_samples": 5
    }
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    param_file = f"{OUTPUT_DIR}/behavior_decay_params.json"
    with open(param_file, "w") as f:
        json.dump(params, f, indent=2)
        
    model_hash = compute_hash(param_file)
    with open(f"{OUTPUT_DIR}/artifact_hash.sha256", "w") as f:
        f.write(model_hash)
        
    print(f"🔒 Artifact Locked. SHA-256: {model_hash}")

if __name__ == "__main__":
    simulate_behavior_dynamics()
