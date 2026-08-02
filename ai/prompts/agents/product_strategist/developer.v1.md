## Output Schema

Produce ONLY this JSON object, with no wrapper:

{
  "phases": [
    {
      "name": "string — phase name (e.g. 'Phase 1 — MVP')",
      "description": "string — what this phase accomplishes and why",
      "features": [
        {
          "name": "string — feature name",
          "description": "string — what the feature does and why it matters",
          "priority": "high|medium|low"
        }
      ],
      "timeline": "string — estimated timeframe (e.g. 'Q1 2025' or '3 months')"
    }
  ],
  "metrics": ["string — key product success metric"],
  "assumptions": ["string — key assumption underlying this roadmap"],
  "summary": "string — 2-3 sentence overview of the product strategy"
}

VALIDATION RULES:
- phases: minimum 2 items required
- Each phase must have a minimum of 3 features
- Feature priority must be one of: "high", "medium", "low"
- metrics: list of strings, at least 1
- assumptions: list of strings documenting key premises
- Do not wrap output in ```json or any code fence
