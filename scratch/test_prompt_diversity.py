import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://temporary-rushing-jade-cci39k5.vercel.app/api/chat"

prompts = [
    {
        "id": "A",
        "category": "Education & Student",
        "query": "I am a college student from Tamil Nadu with annual family income of 2.5 lakh. What scholarships apply to me?"
    },
    {
        "id": "B",
        "category": "Agriculture & Farmers",
        "query": "What is PM-KISAN Samman Nidhi scheme and how much financial installment do small farmers receive?"
    },
    {
        "id": "C",
        "category": "Business & Entrepreneurship",
        "query": "I am a woman starting a greenfield business and need a bank loan between 10 lakh to 1 crore. Which scheme applies?"
    },
    {
        "id": "D",
        "category": "Healthcare & Senior Citizens",
        "query": "How does Ayushman Bharat PM-JAY health insurance work for senior citizens aged 70 and above?"
    }
]

print("=== DEEP SELF-CHECK: PROMPT DIVERSITY & DYNAMIC RETRIEVAL ===\n")

for p in prompts:
    print(f"----------------------------------------------------------------------")
    print(f"PROMPT {p['id']} [{p['category']}]:")
    print(f"Query: \"{p['query']}\"")
    
    payload = json.dumps({"message": p["query"]}).encode("utf-8")
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
            raw_msg = data.get("message", "")[:220].replace("\n", " ")
            msg_snippet = raw_msg.encode('ascii', errors='ignore').decode()
            
            print(f"-> Executed Tools: {tools}")
            print(f"-> Cited Schemes ({len(scheme_names)}): {scheme_names}")
            print(f"-> Source Files ({len(doc_names)}): {doc_names}")
            print(f"-> AI Response Excerpt: {msg_snippet}...")
            print(f"----------------------------------------------------------------------\n")
    except Exception as e:
        print(f"-> ERROR: {e}\n")
