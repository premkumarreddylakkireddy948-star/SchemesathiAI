import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://temporary-rushing-jade-cci39k5.vercel.app/api/chat"

scenarios = [
    {
        "id": "1",
        "title": "Income Tax Payer Farmer (PM-KISAN Exclusion Test)",
        "query": "I am a farmer with 1 hectare of land, but I paid Income Tax last year. Am I eligible for PM-KISAN 6,000 benefit?"
    },
    {
        "id": "2",
        "title": "Institutional Land Holding (PM-KISAN Land Rule Test)",
        "query": "Is an institutional landholder or a person holding non-cultivable commercial land eligible for PM-KISAN Samman Nidhi?"
    },
    {
        "id": "3",
        "title": "Pucca House Ownership (PMAY Housing Exclusions)",
        "query": "I am looking for a home loan subsidy under PMAY-U, but my family already owns a pucca house in my native town. Can I apply?"
    },
    {
        "id": "4",
        "title": "High Tax Payer & Pensioner (Ayushman Bharat 70+ Extension)",
        "query": "I am a retired 72-year-old senior citizen paying income tax and receiving a government pension. Am I eligible for the new 70+ Ayushman Bharat scheme?"
    }
]

print("=== DEEP SELF-CHECK: TAX & LAND HOLDING EXCLUSION SCENARIOS ===\n")

for s in scenarios:
    print("----------------------------------------------------------------------")
    print(f"SCENARIO {s['id']}: {s['title']}")
    print(f"Query: \"{s['query']}\"")
    
    payload = json.dumps({"message": s["query"]}).encode("utf-8")
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
            doc_names = list(set([src.get("document_name") for src in sources]))
            scheme_names = list(set([src.get("scheme_name") for src in sources]))
            raw_msg = data.get("message", "")[:300].replace("\n", " ")
            msg_snippet = raw_msg.encode('ascii', errors='ignore').decode()
            
            print(f"-> Tools Executed: {tools}")
            print(f"-> Cited Schemes ({len(scheme_names)}): {scheme_names}")
            print(f"-> Source Documents: {doc_names}")
            print(f"-> AI Response Excerpt: {msg_snippet}...")
            print("----------------------------------------------------------------------\n")
    except Exception as e:
        print(f"-> ERROR: {e}\n")
