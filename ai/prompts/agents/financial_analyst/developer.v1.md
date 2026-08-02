## Output Schema

Produce ONLY this JSON object, with no wrapper:

{
  "revenue_drivers": ["string or object — primary source of revenue with description"],
  "cost_buckets": ["string or object — major cost category with description"],
  "projection_12_months": [
    {
      "month": "string — month name (e.g. 'Jan')",
      "revenue": 0,
      "costs": 0
    }
  ],
  "assumptions": [
    "string — named financial assumption (e.g. 'Average contract value of $99/month')"
  ],
  "unit_economics": {
    "ltv": "string — customer lifetime value (e.g. '$594')",
    "cac": "string — customer acquisition cost (e.g. '$150')",
    "ltv_cac_ratio": "string — ratio of LTV to CAC",
    "payback_period": "string — time to recover CAC"
  },
  "summary": "string — 2-3 sentence summary of the financial outlook"
}

VALIDATION RULES:
- projection_12_months: EXACTLY 12 entries, one per calendar month
- assumptions: minimum 5 items, each a clearly stated premise
- revenue and costs in projection must be numbers (not strings)
- unit_economics must include ltv, cac, ltv_cac_ratio, and payback_period
- Do not invent specific numbers without basis — use conservative estimates
- Do not wrap output in ```json or any code fence
