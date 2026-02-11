# TrustLens Dataset Architecture: "The Messy Internet"

> **Philosophy**: Data supports reasoning, not truth. Labels represent risk tendencies, not correctness.
> **Status**: Synthetic Design Phase
> **Target**: Evaluate S2-S5 under partial observability and high uncertainty.

## 1. Meta-Architecture

**Objective**: Simulate real-world content lifecycle behaviors to train TrustLens signals on ambiguity, calibration, and failure modes.

**Real-World Behaviors Simulated**:
- **Organic Virality**: Bursty but log-normal distribution (rapid rise, long tail), heavily redundant.
- **Coordinated Inauthentic Behavior (CIB)**: Tight temporal clustering, low variance in messaging, potentially high volume.
- **Journalistic Correction**: High initial trust, occasional error (risk spike), followed by transparency (correction) -> recovery.
- **Satire/Parody**: High semantic drift (exaggeration) but distinct intent markers (if detected).
- **Technical Artifacts**: Benign manipulation (compression, cropping) vs. Malicious tampering (splicing).

**Explicitly Out of Scope**:
- Attribution to specific actors (e.g., "State Actor X").
- Binary truth labels ("Fake News" vs "Real News").
- Private encrypted channels (WhatsApp/Telegram propagation).

---

## 2. Global Dataset Governance

### Partial Observability Strategy
The dataset must NOT be perfect. The "Internet" is broken.
- **30% Missing Signals**: Content missing timestamps, source history, or metadata.
- **10% Contradictory Signals**: Metadata says X, Content says Y.
- **20-40% "Unknown" Outcome**: The system must say "I don't know" often.

### Noise Budget (Mandatory)
Every signal generator must inject:
1.  **Measurement Noise**: +/- 5% confidence jitter.
2.  **Timing Jitter**: +/- seconds to hours (simulating crawling delays).
3.  **Metadata Corruption**: Stripped headers (common in social media).

### Label Philosophy
- **No Classes**: Labels are `risk_tendency` (0.0 to 1.0) and `uncertainty` (0.0 to 1.0).
- **Fuzzy Boundaries**: A "satire" article might have `risk=0.4` (medium) if context is missing, not `0.0` or `1.0`.

---

## 3. Signal-Wise Data Design

### 🔹 Signal 2: Observable Diffusion (Bursts & Echoes)
- **Generator**: `DiffusionEventGenerator`
- **Behaviors**:
    - *Organic*: Log-normal inter-arrival times. High variance.
    - *Coordinated*: Low variance (bot-like). Tight clusters.
    - *Mixed*: Organic pickup of coordinated content (hardest case).
- **Hard Constraint**: If bursts always imply maliciousness, the dataset is failed.

### 🔹 Signal 3: Intent & Semantic Drift (Context)
- **Generator**: `SemanticContextGenerator`
- **Behaviors**:
    - *Factual*: Low drift, high intent confidence.
    - *Opinion*: High drift, high intent confidence (Opinion). -> **STOP**.
    - *Satire*: Extreme drift, specific stylistic markers. -> **STOP**.
    - *Malicious*: High drift, mimicked factual intent (Deceptive). -> **RISK**.
- **Failure-Safe**: If `intent_confidence < 0.7`, `drift_risk` is undefined (NULL).

### 🔹 Signal 4: media Forensics (Artifacts)
- **Generator**: `MediaArtifactGenerator`
- **Behaviors**:
    - *Benign Transcoding*: Re-compression, resizing (90% of data).
    - *Malicious Tampering*: Localized noise inconsistency, splicing.
    - *Ambiguous*: High compression masking potential tampering.
- **Rule**: High compression = High Uncertainty, NOT High Risk.

### 🔹 Signal 5: Source Behavior (Reputation Dynamics)
- **Generator**: `SourceHistoryGenerator`
- **Behaviors**:
    - *Steady*: Consistent behavior (Good or Bad).
    - *Redemption*: History of errors, recent transparent corrections -> Improving Trust.
    - *Decay*: Good history, sudden drift into anomaly -> Increasing Uncertainty.
- **Constraint**: No permanent blacklists.

---

## 4. Cross-Signal Interactions (The "Fusion Test")

The dataset must explicitly generate conflict scenarios:
1.  **" The Viral Satire"**: S2 (High Burst) + S3 (Satire Intent) -> Neutral Risk, High Diffusion.
2.  **"The Compressed Leak"**: S4 (High Artifacts/Compression) + S3 (High Drift) -> Low Confidence (Technical limitation overriding content risk).
3.  **"The Reformed Source"**: S5 (Historical Risk) + S5 (Recent Correction) -> Low Risk (Recovery).

---

## 5. Calibration Targets

A "Healthy" Dataset Distribution:
- **Low Confidence / Unknown**: ~35%
- **Low Risk / Neutral**: ~40%
- **Medium Risk / Caution**: ~20%
- **High Risk / Alert**: ~5%

*If High Risk > 10%, the internet is unusable.* 
*If Unknown < 20%, the sensor is hallucinating visibility.*

---

## 6. Validation Sanity Checks
Before accepting a batch:
1.  Are there samples where S2=High Risk and S3=Low Risk?
2.  Is the average uncertainty > 0.3?
3.  Do timestamps have non-uniform jitter?
