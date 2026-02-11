# TrustLens: Multi-Signal Trust Intelligence System

> **TRUST ≠ DETECTION.**
> **TRUST = STRUCTURED EVIDENCE + CALIBRATED UNCERTAINTY.**

This repository contains the source code for **TrustLens**, a browser-based trust intelligence system that evaluates content trustworthiness using multi-signal evidence fusion.

## Core Philosophy (Non-Negotiable)

1.  **NEVER outputs truth labels.**
2.  **NEVER outputs “AI / not AI”.**
3.  **NEVER blocks content.**
4.  **ALWAYS exposes uncertainty.**
5.  **Absence of evidence ≠ risk.**
6.  **Unknown is a valid output.**

## Cold-Start Rule
For previously unseen content or sources, TrustLens defaults to low confidence rather than elevated risk. Confidence increases only as evidence accumulates.


## System Layers

The system is split into 5 strictly isolated layers:

1.  **Browser Extension (Client)**: Lightweight signal extraction + UI rendering.
2.  **API Gateway**: Routing + orchestration only.
3.  **Signal Services (ML-backed)**: Cryptographic provenance, diffusion risk, semantic drift, media forensics, source behavior.
4.  **Trust Inference Graph Engine**: Probabilistic signal combination.
5.  **Sentinel Oversight Agent**: Infrastructure guardian.

## Execution Order (Strict)

- [ ] Architecture diagram
- [ ] Signal isolation
- [ ] Colab models
- [ ] Backend inference
- [ ] Trust graph
- [ ] UI wiring
- [ ] Sentinel agent
- [ ] Deployment
- [ ] Validation
- [ ] Demo
