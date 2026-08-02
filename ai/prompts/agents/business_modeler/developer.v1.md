## Output Schema

Produce ONLY this JSON object, with no wrapper:

{
  "value_proposition": "string or list — the unique value the startup delivers to customers",
  "customer_segments": "string or list — distinct groups of customers the startup serves",
  "channels": "string or list — how the startup reaches and delivers to customers",
  "customer_relationships": "string — how the startup acquires, retains, and grows customers",
  "revenue_streams": "string or list — how the startup earns money from each segment",
  "key_resources": "string or list — critical assets required to deliver the value proposition",
  "key_activities": "string or list — most important things the startup must do to operate",
  "key_partnerships": "string or list — external parties that help the business model work",
  "cost_structure": "string or list — major costs incurred to operate the business model",
  "summary": "string — 2-3 sentence summary of the business model logic"
}

VALIDATION RULES:
- ALL 9 canvas fields (value_proposition through cost_structure) must be non-empty
- Fields may be strings or arrays — use whichever is more expressive
- summary must be non-empty
- Do not wrap output in ```json or any code fence
