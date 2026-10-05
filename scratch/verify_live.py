import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base_url = "https://temporary-rushing-jade-cci39k5.vercel.app"

print("--- Step 1: Testing Frontend Homepage ---")
req = urllib.request.Request(base_url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
    print(f"Frontend Status: {res.status}")
    assert res.status == 200, "Frontend non-200"

print("\n--- Step 2: Testing Production Health Endpoint via Vercel Proxy ---")
req = urllib.request.Request(f"{base_url}/health", headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
    health_data = json.loads(res.read().decode())
    print(f"Health Status: {res.status}")
    print(f"Health JSON: {health_data}")
    assert res.status == 200
    assert health_data.get("status") == "healthy"
    assert health_data.get("environment") == "production"
    assert health_data.get("database_type") == "postgresql"
    assert health_data.get("vector_db") == "qdrant"
    assert health_data.get("llm_configured") is True

print("\n--- Step 3: Testing Docs Endpoint via Vercel Proxy ---")
req = urllib.request.Request(f"{base_url}/docs", headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
    docs_html = res.read().decode()
    print(f"Docs Status: {res.status}")
    print(f"Docs Swagger UI loaded: {'Swagger' in docs_html or 'FastAPI' in docs_html}")
    assert res.status == 200

print("\n--- Step 4: Testing Schemes API Endpoint via Vercel Proxy ---")
req = urllib.request.Request(f"{base_url}/api/schemes", headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
    schemes = json.loads(res.read().decode())
    print(f"Schemes Status: {res.status}")
    print(f"Loaded {len(schemes)} schemes.")
    assert res.status == 200 and len(schemes) > 0

print("\n--- Step 5: Testing AI Chat Agent End-to-End via Vercel Proxy ---")
payload = json.dumps({
    "message": "I am a college student from Tamil Nadu and my family income is ₹2.5 lakh per year. What government scholarships may be relevant to me?",
    "user_context": {
        "state": "Tamil Nadu",
        "category": "Education & Student",
        "income": 250000
    }
}).encode('utf-8')

req = urllib.request.Request(
    f"{base_url}/api/chat",
    data=payload,
    headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    },
    method="POST"
)

with urllib.request.urlopen(req, context=ctx, timeout=30) as res:
    chat_resp = json.loads(res.read().decode())
    print(f"Chat Response Status: {res.status}")
    snippet = chat_resp.get("message", "")[:180].encode('ascii', errors='ignore').decode()
    print(f"Agent Response Snippet: {snippet}...")
    print("Agent Tools Executed:", chat_resp.get("agent_steps"))
    print("Source Citations Count:", len(chat_resp.get("sources", [])))
    assert res.status == 200 and "message" in chat_resp and len(chat_resp.get("sources", [])) > 0

print("\n>>> ALL PRODUCTION SYSTEM VERIFICATION TESTS PASSED 100% SUCCESSFULLY! <<<")
