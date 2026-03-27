import requests

def generate_response(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3:mini",
                "prompt": prompt,
                "stream": False
            },
            timeout=300
        )
        return response.json()["response"]
    except Exception as e:
        return f'{{"market_overview":"Error connecting to LLM: {str(e)}","competitors":[],"pricing_models":[],"customer_pain_points":[],"entry_strategy":[],"income_opportunities":[],"investment_needs":[]}}'