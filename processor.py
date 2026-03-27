def build_prompt(data, idea, region, segment):
    limited_data = data[:6]

    combined_text = "\n".join(
        [
            f"Title: {item['title']}\nSnippet: {item['snippet']}\n"
            for item in limited_data
        ]
    )

    prompt = f"""
You are a market research and startup strategy expert.

Startup Idea: {idea}
Region: {region}
Customer Segment: {segment}

Web data:
{combined_text}

Return ONLY valid JSON.

{{
  "market_overview": "short paragraph",
  "competitors": ["item1", "item2", "item3"],
  "pricing_models": ["item1", "item2", "item3"],
  "customer_pain_points": ["item1", "item2", "item3"],
  "entry_strategy": ["item1", "item2", "item3"],
  "income_opportunities": ["item1", "item2", "item3"],
  "investment_needs": ["item1", "item2", "item3"]
}}

Rules:
- Always fill every field.
- Keep answers short and practical.
- Infer reasonable items if exact data is not available.
"""
    return prompt