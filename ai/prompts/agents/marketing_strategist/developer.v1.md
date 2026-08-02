## Output Schema

Produce ONLY this JSON object, with no wrapper:

{
  "icp": {
    "role": "string — target job title or role",
    "stage": "string — company or career stage of the customer",
    "pain": "string — primary pain point this product solves for them"
  },
  "messaging": {
    "headline": "string — primary marketing headline (value proposition in one line)",
    "tagline": "string — short memorable tagline",
    "value_prop": "string — 1-2 sentence value proposition for marketing copy"
  },
  "channels": ["string — marketing channel with brief rationale"],
  "launch_checklist": ["string — concrete actionable pre-launch or launch task"],
  "calendar": {
    "week_1": "string — activities in week 1",
    "week_2": "string — activities in week 2",
    "week_3": "string — activities in week 3",
    "week_4": "string — activities in week 4"
  },
  "summary": "string — 2-3 sentence summary of the go-to-market strategy"
}

VALIDATION RULES:
- channels: minimum 3 items required
- launch_checklist: minimum 5 items required
- icp must include role, stage, and pain
- messaging must include headline, tagline, and value_prop
- Do not wrap output in ```json or any code fence
