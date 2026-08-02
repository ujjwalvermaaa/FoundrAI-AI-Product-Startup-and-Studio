## Output Schema

Produce ONLY this JSON object, with no wrapper:

{
  "tam": {
    "value": "string — estimated total addressable market size (e.g. '50B')",
    "unit": "USD",
    "notes": "string — methodology or source notes"
  },
  "sam": {
    "value": "string — serviceable addressable market size (e.g. '5B')",
    "unit": "USD",
    "notes": "string — how SAM was derived from TAM"
  },
  "som": {
    "value": "string — serviceable obtainable market size (e.g. '500M')",
    "unit": "USD",
    "notes": "string — realistic near-term capture estimate"
  },
  "segments": [
    "string — named market segment"
  ],
  "competitors": [
    {
      "name": "string — competitor name",
      "strengths": "string — key competitive advantages",
      "weaknesses": "string — key limitations or gaps",
      "market_position": "string — their current position in the market"
    }
  ],
  "trends": [
    "string — emerging trend relevant to this market"
  ],
  "summary": "string — 2-3 sentence summary of the market landscape"
}

VALIDATION RULES:
- competitors: minimum 3 items required
- tam, sam, som: must each include non-empty "value" and "unit" fields
- segments: minimum 1 item
- trends: minimum 3 items
- All string fields must be non-empty
- Do not wrap output in ```json or any code fence
