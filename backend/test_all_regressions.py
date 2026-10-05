import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_URL = "http://127.0.0.1:8000/api/chat"

tests = [
    (
        "REGRESSION TEST 12 (SC Male/Unspecified B.Tech TN Student)",
        "I am a 20-year-old B.Tech student from Tamil Nadu. My family income is ₹2.5 lakh per year. I belong to an SC category and I need financial assistance for my education. Find the most relevant government scholarships or schemes for me, compare the top 3 options, tell me the required documents, application process, and official government website for each. Do not claim that I am definitely eligible; explain what I should verify."
    ),
    (
        "REGRESSION TEST 13 (TN SC Student Focus)",
        "I am a B.Tech student in Tamil Nadu belonging to SC category with annual family income of ₹2.5 lakh. Which government scholarships specifically available to Tamil Nadu students should I check?"
    ),
    (
        "REGRESSION TEST 14 (Female B.Tech TN Student)",
        "I am a female B.Tech student from Tamil Nadu. My family income is ₹3 lakh per year. Which government scholarships might be relevant to me?"
    ),
    (
        "REGRESSION TEST 15 (PM-KISAN vs PMAY Comparison)",
        "Compare PM-KISAN and PMAY based on eligibility, benefits, documents and application process."
    ),
    (
        "REGRESSION TEST 16 (PM-KISAN Informational Query)",
        "What is PM-KISAN and who can benefit from it? Give me the official government website."
    )
]

for label, query in tests:
    print(f"\n==================================================")
    print(f" {label}")
    print(f"==================================================")
    print(f"QUERY: {query}\n")
    
    payload = json.dumps({
        "message": query,
        "user_context": {
            "state": "Tamil Nadu",
            "category": "SC",
            "annual_income": 250000,
            "occupation": "Student"
        }
    }).encode("utf-8")
    
    req = urllib.request.Request(API_URL, data=payload, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode("utf-8"))
            msg = data.get("message", "")
            print("RESPONSE FULL TEXT:\n")
            print(msg)
            print("\n--------------------------------------------------")
            print("AGENT TOOLS USED:", data.get("agent_steps"))
    except Exception as e:
        print("ERROR:", e)

