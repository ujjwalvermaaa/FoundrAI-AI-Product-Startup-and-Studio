## Output Schema

Produce ONLY this JSON object, with no wrapper:

{
  "problem": "string — the core problem the startup addresses",
  "solution": "string — the proposed solution",
  "target_customer": {
    "description": "string — who the customer is",
    "pain_points": ["string", "..."],
    "demographics": "string — optional demographic info"
  },
  "risks": [
    {
      "risk": "string — description of the risk",
      "severity": "high|medium|low",
      "mitigation": "string — how to address this risk"
    }
  ],
  "validation_score": 0-100,
  "recommendations": ["string", "..."],
  "summary": "string — 2-3 sentence summary of the validation"
}

VALIDATION RULES:
- risks: minimum 3 items required
- validation_score: integer, 0-100 inclusive
- All string fields must be non-empty
- Do not wrap output in ```json or any code fence
