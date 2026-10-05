import urllib.request
import json
import sys

# Ensure UTF-8 output in Windows console
sys.stdout.reconfigure(encoding='utf-8')

API_URL = "http://127.0.0.1:8000/api/chat"

tests = [
    ("TEST 1", "What is PM-KISAN and who can benefit from it? Give me the official government website."),
    ("TEST 2", "I am a college student from Tamil Nadu with a family income of ₹2.5 lakh per year. What government scholarships may be relevant to me? Give basic details and official application links."),
    ("TEST 3", "Compare PM-KISAN and PMAY based on eligibility, benefits, documents and application process."),
    ("TEST 4", "What is the latest PM-KISAN update? Search official government sources."),
    ("TEST 5", "Create a document checklist for PM-KISAN.")
]

for label, query in tests:
    print(f"\n==================== {label} ====================")
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
    
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode("utf-8"))
            print("RESPONSE MESSAGE:\n")
            print(data.get("message"))
            print("\n--------------------------------------------------")
            print("TOOLS USED:", data.get("agent_steps"))
    except Exception as e:
        print("ERROR:", e)

