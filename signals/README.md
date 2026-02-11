# Signal Service Contract

All Signal Services MUST adhere to the following strict API contract.

## Endpoint: POST /analyze

### Request Payload
```json
{
  "content_hash": "sha256...",
  "text_content": "Full extracted text...",
  "media_urls": ["https://..."],
  "timestamp": "ISO8601",
  "source_url": "https://..."
}
```

### Response Payload (Strict Schema)
```json
{
  "signal_id": "uuid",
  "signal_type": "string (provenance|diffusion|semantic|forensics|source)",
  "risk_score": "float (0.0 - 1.0)",
  "confidence_score": "float (0.0 - 1.0)",
  "evidence_metadata": {
    "key_evidence_1": "value",
    "key_evidence_2": "value"
  },
  "explanation": "string (Human readable summary)",
  "calibrated_uncertainty": "float (0.0 - 1.0)"
}
```

## Rules
1. **Never return binary True/False for trust.**
2. **Always include `calibrated_uncertainty`.**
3. **If a signal fails, return fail-safe defaults with `confidence_score: 0.0`.**
4. **Stateless execution only.**
