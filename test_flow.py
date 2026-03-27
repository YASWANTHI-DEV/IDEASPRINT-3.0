from scraper import search_web
from processor import build_prompt

# Step 0: Define inputs
idea = "Food Delivery Startup"
region = "India"
segment = "Students"

# Step 1: Create query
query = f"{idea} market size {region}"

print("\n STEP 1: CALLING SCRAPER...\n")

# Step 2: Call scraper
data = search_web(query)

print("\n SCRAPER OUTPUT:\n")
for item in data:
    print(item)

print("\n STEP 2: PASSING DATA TO PROCESSOR...\n")

# Step 3: Call processor
prompt = build_prompt(data, idea, region, segment)

print("\n PROCESSOR OUTPUT (PROMPT):\n")
print(prompt)