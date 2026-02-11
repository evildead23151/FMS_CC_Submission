"""
TRUSTLENS: SYNTHETIC BEHAVIOR ENGINE
Generates realistic user, source, and content behaviors (NOT samples).
Injects "The Messy Internet" philosophy: Ambiguity, noise, and partial signals.
"""

import numpy as np
import pandas as pd
import random
import uuid
from datetime import datetime, timedelta

class BehaviorEngine:
    def __init__(self):
        self.rng = np.random.default_rng(42)

    def generate_id(self):
        return str(uuid.uuid4())[:8]

    def _apply_partial_observability(self, value, missing_prob=0.3):
        """Simulate missing data (broken scrapers, API limits)."""
        return None if self.rng.random() < missing_prob else value

    # 🔹 SIGNAL 2: DIFFUSION BEHAVIORS
    def generate_diffusion_event(self):
        """
        Generates diffusion metadata (IATs, Cluster Size).
        Distinguishes Organic (Log-Normal) vs Coordinated (Exponential/Low-Variance).
        """
        is_coordinated = self.rng.random() < 0.15 # 15% Malicious Coordinated
        
        if is_coordinated:
            # Coordinated: Tight bursts, machine-like timing
            iat_mean = self.rng.uniform(0.1, 2.0) # Fast
            iat_sigma = 0.1 # Low variance (The "Tell")
            cluster_size = int(self.rng.power(5) * 500) # Heavy tail
            risk_tendency = self.rng.uniform(0.7, 1.0)
        else:
            # Organic: Slower, human variance
            iat_mean = self.rng.uniform(5.0, 60.0) # Slower
            iat_sigma = 1.5 # High variance (Human)
            cluster_size = int(self.rng.power(2) * 100) # Normal tail
            risk_tendency = self.rng.uniform(0.0, 0.4)

        # Measurement Noise (Timing Jitter)
        measured_iat_mean = iat_mean + self.rng.normal(0, iat_mean * 0.1)

        return {
            "signal_type": "S2_Diffusion",
            "is_coordinated": is_coordinated,
            "cluster_size": self._apply_partial_observability(cluster_size, 0.2), # 20% missing size
            "avg_iat_seconds": measured_iat_mean,
            "iat_variance": self._apply_partial_observability(iat_sigma, 0.4), # Variance hard to measure
            "measured_risk": risk_tendency,
            "confidence": self.rng.uniform(0.3, 0.9) if cluster_size else 0.1
        }

    # 🔹 SIGNAL 3: INTENT & DRIFT
    def generate_semantic_event(self):
        """
        Generates intent classification and drift vectors.
        Enforces Failure-Safe Logic: Only Factual content gets high drift risk.
        """
        intents = ["Factual", "Opinion", "Satire", "Personal"]
        weights = [0.4, 0.3, 0.1, 0.2]
        intent = self.rng.choice(intents, p=weights)
        
        intent_conf = self.rng.uniform(0.5, 0.99)
        
        # Drift Logic
        if intent == "Factual":
            # Malicious drift or innocent paraphrase?
            is_malicious = self.rng.random() < 0.2
            drift_magnitude = self.rng.uniform(0.6, 1.0) if is_malicious else self.rng.uniform(0.0, 0.4)
            risk = drift_magnitude if intent_conf > 0.8 else 0.0 # High confidence required
        elif intent == "Satire":
             # Satire has EXTREME drift but SHOULD NOT be risk if intent is caught
             drift_magnitude = self.rng.uniform(0.8, 1.0)
             risk = 0.1 # Neutral
        else:
            # Opinion / Personal -> No Drift Signal
            drift_magnitude = self.rng.uniform(0.2, 0.8) # Random noise
            risk = 0.0 # Not applicable

        # Failure Safe: If intent weak, drift is unknown
        if intent_conf < 0.7:
            drift_magnitude = None
            risk = None

        return {
            "signal_type": "S3_Semantic",
            "intent_class": intent,
            "intent_confidence": intent_conf,
            "drift_magnitude": drift_magnitude,
            "measured_risk": risk,
            "uncertainty": 1.0 - intent_conf
        }

    # 🔹 SIGNAL 4: MEDIA FORENSICS
    def generate_forensics_event(self):
        """
        Generates artifacts. Distinguishes Compression (Benign) vs Tampering (Malicious).
        """
        scenario = self.rng.choice(["Clean", "Compressed", "Tampered"], p=[0.5, 0.4, 0.1])
        
        if scenario == "Clean":
            ela_score = self.rng.uniform(0, 0.2)
            noise_residual = self.rng.uniform(0, 0.1)
            risk = 0.0
        elif scenario == "Compressed":
            # High artifacts globally, consistent noise
            ela_score = self.rng.uniform(0.3, 0.7)
            noise_residual = self.rng.uniform(0.0, 0.2) # Consistent
            risk = 0.1 # Benign
        else: # Tampered
            # Localized anomalies
            ela_score = self.rng.uniform(0.6, 0.9)
            noise_residual = self.rng.uniform(0.5, 0.9) # Inconsistent
            risk = self.rng.uniform(0.7, 1.0)

        # Uncertainty scales with compression
        uncertainty = 0.8 if scenario == "Compressed" else 0.2

        return {
            "signal_type": "S4_Forensics",
            "scenario": scenario,
            "ela_score": ela_score,
            "noise_residual": noise_residual,
            "measured_risk": risk,
            "uncertainty": uncertainty
        }

    # 🔹 SIGNAL 5: SOURCE BEHAVIOR
    def generate_source_event(self):
        """
        Generates source history dynamics.
        Enforces Recovery: Recent corrections reduce risk.
        """
        history_length = self.rng.integers(1, 1000) # Days active
        base_reputation = self.rng.choice(["Reliable", "Mixed", "Unreliable"], p=[0.6, 0.3, 0.1])
        
        has_recent_correction = False
        if base_reputation == "Mixed":
            has_recent_correction = self.rng.random() < 0.4 # 40% chance of redemption arc
        
        # Risk Calculation
        if base_reputation == "Reliable":
            risk = self.rng.uniform(0.0, 0.2)
        elif base_reputation == "Unreliable":
            risk = self.rng.uniform(0.7, 1.0)
        else: # Mixed
            # If corrected, risk drops significantly
            risk = self.rng.uniform(0.2, 0.4) if has_recent_correction else self.rng.uniform(0.4, 0.7)

        # Cold Start Rule: Short history = High Uncertainty
        uncertainty = 1.0 if history_length < 30 else 0.2

        return {
            "signal_type": "S5_Source",
            "history_days": self._apply_partial_observability(history_length, 0.1),
            "reputation_tier": base_reputation,
            "recent_correction": has_recent_correction,
            "measured_risk": risk,
            "uncertainty": uncertainty
        }

    def generate_full_sample(self):
        """Fusion of signals for a single content item."""
        return {
            "id": self.generate_id(),
            "timestamp": datetime.now().isoformat(),
            "signals": {
                "S2": self.generate_diffusion_event(),
                "S3": self.generate_semantic_event(),
                "S4": self.generate_forensics_event(),
                "S5": self.generate_source_event()
            }
        }
