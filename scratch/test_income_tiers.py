import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://temporary-rushing-jade-cci39k5.vercel.app/api/chat"

incomes = [
    {
        "label": "Low Income (Rs 1.5 Lakh / year)",
        "income": 150000,
        "query": "I am a college student from Tamil Nadu. My annual family income is 1.5 lakh per year. What government scholarships am I eligible for?"
    },
    {
        "label": "Middle Income (Rs 4.5 Lakh / year)",
        "income": 450000,
        "query": "I am a college student from Tamil Nadu. My annual family income is 4.5 lakh per year. What government scholarships or education schemes am I eligible for?"
    },
    {
        "label": "High Income (Rs 12 Lakh / year)",
        "income": 1200000,
        "query": "I am a college student from Tamil Nadu. My annual family income is 12 lakh per year. Are there any government scholarships or education schemes for my income level?"
    }
]

print("=== INCOME ELIGIBILITY VARIATION SELF-CHECK ===\n")

for item in incomes:
    print(f"======================================================================")
    print(f"TESTING TIER: {item['label']}")
    print(f"Query: \"{item['query']}\"")
    
    payload = json.dumps({
        "message": item["query"],
        "user_context": {
            "state": "Tamil Nadu",
            "category": "Education & Student",
            "annual_income": item["income"]
        }
    }).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as res:
            data = json.loads(res.read().decode())
            tools = data.get("agent_steps", [])
            sources = data.get("sources", [])
            doc_names = list(set([s.get("document_name") for s in sources]))
            scheme_names = list(set([s.get("scheme_name") for s in sources]))
            raw_msg = data.get("message", "")[:280].replace("\n", " ")
            msg_snippet = raw_msg.encode('ascii', errors='ignore').decode()
            
            print(f"-> Tools Executed: {tools}")
            print(f"-> Schemes Evaluated ({len(scheme_names)}): {scheme_names}")
            print(f"-> Source Files: {doc_names}")
            print(f"-> Response Excerpt: {msg_snippet}...")
            print(f"======================================================================\n")
    except Exception as e:
        print(f"-> ERROR: {e}\n")
