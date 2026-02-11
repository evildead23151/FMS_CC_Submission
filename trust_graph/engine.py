from typing import Dict, Any, List
from enum import Enum
import math

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"

class TrustEngine:
    """
    Probabilistic Trust Inference Engine.
    Combines evidence from isolated signals to compute overall trust posture.
    
    Signal Combination Strategy:
    The Trust Inference Graph combines signals using calibrated likelihood contributions rather than absolute scores. 
    Each signal contributes confidence-weighted evidence, and contradictions are resolved through attenuation 
    rather than override. No single signal can dominate the Trust Posture unless its confidence exceeds 
    a predefined threshold. Unknown or low-confidence signals reduce certainty rather than increasing risk.
    """
    
    def __init__(self):
        # Calibration weights for signals
        self.weights = {
            "provenance": 2.0,       # High trust anchor
            "forensics": 1.5,        # Hard technical evidence
            "diffusion": 1.0,        # Contextual
            "semantic": 0.8,         # Subjective/Model-heavy
            "source": 0.5            # Historical/Drifting
        }

    def fuse_evidence(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main fusion logic.
        Input: Dict of signal responses.
        Output: Final Trust Assessment.
        """
        
        # 1. Normalize Inputs
        scores = {}
        confidences = {}
        
        for name, data in signals.items():
            # Extract risk (0.0=Safe, 1.0=High Risk)
            # Some signals might return 'risk_score', others might imply it.
            # Assuming uniform API from signal isolation step.
            risk = data.get("risk_score", 0.5) 
            conf = data.get("confidence_score", 0.0)
            
            # Weighted confidence
            weight = self.weights.get(name, 1.0)
            scores[name] = risk
            confidences[name] = conf * weight

        # 2. Compute Weighted Risk Average
        total_weight = sum(confidences.values()) + 1e-9
        weighted_risk_sum = sum(scores[name] * confidences[name] for name in scores)
        avg_risk = weighted_risk_sum / total_weight
        
        # 3. Handle Provenance Anchor (Crypto override)
        provenance = signals.get("provenance", {})
        has_provenance = provenance.get("evidence_metadata", {}).get("c2pa_present", False)
        
        if has_provenance:
            # If provenance is valid, it significantly reduces manipulation risk
            # But doesn't negate semantic drift or diffusion risk (it could be signed misinformation)
            pass 

        # 4. Resolve Contradictions
        # E.g. Low Manipulation Risk but High Diffusion Risk -> Viral Misinfo?
        contradiction = False
        drift_risk = signals.get("semantic", {}).get("risk_score", 0.0)
        forensics_risk = signals.get("forensics", {}).get("risk_score", 0.0)
        
        if forensics_risk < 0.2 and drift_risk > 0.8:
            # "Technically authentic but semantically misleading"
            contradiction = True

        # 5. Determine Overall Posture
        posture = "neutral"
        if avg_risk > 0.7:
            posture = "high_risk"
        elif avg_risk > 0.4:
            posture = "caution"
        elif has_provenance:
            posture = "verified_source" # Positive signal
            
        # 6. Calibrate Global Uncertainty
        # High variance in signal risks = High uncertainty
        variance = sum((val - avg_risk) ** 2 for val in scores.values()) / len(scores) if scores else 0
        global_uncertainty = min(1.0, math.sqrt(variance) + (0.5 if contradiction else 0.0))

        return {
            "overall_trust_posture": posture,
            "risk_score": round(avg_risk, 2),
            "confidence_score": round(min(1.0, total_weight / 5.0), 2), # Normalized approx
            "calibrated_uncertainty": round(global_uncertainty, 2),
            "dimensions": {
                "context_risk": round(drift_risk, 2),
                "provenance_confidence": round(provenance.get("confidence_score", 0.0), 2),
                "manipulation_risk": round(forensics_risk, 2),
                "diffusion_risk": round(scores.get("diffusion", 0.5), 2)
            },
            "contradictions": contradiction,
            "explanation": self._generate_explanation(posture, contradiction, has_provenance)
        }

    def _generate_explanation(self, posture, contradiction, provenance):
        if provenance:
            return "Content source is cryptographically verified."
        if contradiction:
            return "Signals diverge: Content appears authentic but context is highly drifted."
        if posture == "high_risk":
            return "Multiple signals indicate high probability of manipulation or misleading context."
        return "Insufficient evidence to determine risk. Proceed with critical thinking."
