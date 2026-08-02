## Output Schema

Produce ONLY this JSON object, with no wrapper:

{
  "slides": [
    {
      "title": "string — slide title",
      "bullets": ["string — key point for this slide"],
      "notes": "string — optional speaker notes"
    }
  ],
  "narrative_flow": "string — description of the logical story arc through the deck (e.g. 'Problem → Solution → Market → ...')",
  "key_metrics": ["string — investor-relevant metric with value (e.g. 'CAC: $150')"],
  "summary": "string — 2-3 sentence summary of the investment thesis"
}

VALIDATION RULES:
- slides: minimum 10 items required
- The slides MUST collectively cover: Problem, Market Opportunity, Solution/Product, Business Model, Financials, and Funding Ask
- Each slide must have a non-empty title and at least 1 bullet point
- narrative_flow must describe the story arc, not just list slide names
- key_metrics: minimum 4 items required
- Do not wrap output in ```json or any code fence
