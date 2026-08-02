Your previous output had errors. Please fix the JSON and return ONLY valid JSON.

Requirements:
- projection_12_months must have EXACTLY 12 entries (one per month), each with "month", "revenue" (number), and "costs" (number)
- assumptions must have AT LEAST 5 items, each a clearly stated string assumption
- revenue_drivers and cost_buckets must be non-empty lists
- unit_economics must be an object with ltv, cac, ltv_cac_ratio, and payback_period
- All required fields must be present: revenue_drivers, cost_buckets, projection_12_months, assumptions, unit_economics, summary
- Output ONLY the JSON, no markdown fences, no explanation
