## Output Schema

Produce ONLY this JSON object, with no wrapper:

{
  "components": [
    {
      "name": "string — component name (e.g. 'FastAPI backend')",
      "role": "string — what this component does in the system"
    }
  ],
  "stack_recommendations": ["string — specific technology recommendation with brief justification"],
  "data_flows": ["string — description of how data moves through the system"],
  "security_considerations": ["string — specific security requirement or control"],
  "scalability_notes": "string — how the system scales under increased load",
  "summary": "string — 2-3 sentence summary of the architecture approach"
}

VALIDATION RULES:
- components: must be non-empty, list of objects or strings
- stack_recommendations: must be non-empty, list of specific technology choices
- data_flows: describe end-to-end flows, not abstract categories
- security_considerations: must be non-empty and product-domain-relevant
- Do not wrap output in ```json or any code fence
