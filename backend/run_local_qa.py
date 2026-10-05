import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

print("==================================================")
print("     SCHEMESATHI AI - LOCAL QA SUITE             ")
print("==================================================\n")

# 1. System & API Health Checks
def check_endpoint(name, url, method="GET", body=None):
    try:
        req = urllib.request.Request(
            f"{BASE_URL}{url}",
            data=json.dumps(body).encode('utf-8') if body else None,
            headers={"Content-Type": "application/json"} if body else {}
        )
        req.get_method = lambda: method
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode('utf-8'))
            print(f"[SUCCESS] {name} -> Status: {res.status}")
            return True, data
    except Exception as e:
        print(f"[FAILED] {name} -> Error: {e}")
        return False, None

print("--- SECTION A: SYSTEM & API ENDPOINT HEALTH ---")
b_health, _ = check_endpoint("Root Endpoint", "/")
s_health, schemes = check_endpoint("Schemes API", "/api/schemes")
d_health, docs = check_endpoint("Documents API", "/api/documents")
sv_health, saved = check_endpoint("Saved Schemes API", "/api/saved-schemes")
c_health, compare = check_endpoint("Compare API", "/api/compare", method="POST", body={"scheme_ids": [1, 2]})

print("\n--- SECTION B: AI NAVIGATOR 5 CORE TEST QUERIES ---")

tests = [
    ("TEST 1 (PM-KISAN Info & Web)", "What is PM-KISAN and who can benefit from it? Give me the official government website."),
    ("TEST 2 (Personalized TN Scholarships)", "I am a college student from Tamil Nadu with a family income of ₹2.5 lakh per year. What government scholarships may be relevant to me? Give basic details and official application links."),
    ("TEST 3 (PM-KISAN vs PMAY Comparison)", "Compare PM-KISAN and PMAY based on eligibility, benefits, documents and application process."),
    ("TEST 4 (Latest 2026 Info & Live Web)", "What is the latest information about PM-KISAN in 2026?"),
    ("TEST 5 (Document Checklist)", "What documents do I need to apply for PM-KISAN?")
]

test_results = {}

for label, query in tests:
    print(f"\n==================== {label} ====================")
    print(f"QUERY: {query}\n")
    body = {
        "message": query,
        "user_context": {
            "state": "Tamil Nadu",
            "category": "SC",
            "annual_income": 250000,
            "occupation": "Student"
        }
    }
    
    ok, res = check_endpoint("Chat Endpoint", "/api/chat", method="POST", body=body)
    if ok and res:
        msg = res.get("message", "")
        steps = res.get("agent_steps", [])
        print("AI RESPONSE PREVIEW (First 400 chars):\n")
        print(msg[:400] + "...\n")
        print("AGENT TOOLS USED:", steps)
        
        # Validations for each test
        if label.startswith("TEST 1"):
            pass_condition = ("PM-KISAN" in msg or "Pm-Kisan" in msg) and "https://pmkisan.gov.in" in msg and "Agent Tools Invoked" not in msg
        elif label.startswith("TEST 2"):
            pass_condition = "Scholarships for College Students in Tamil Nadu" in msg and "tndce.tn.gov.in" in msg
        elif label.startswith("TEST 3"):
            pass_condition = "| Feature | PM-KISAN | PMAY" in msg and "Key Differences" in msg
        elif label.startswith("TEST 4"):
            pass_condition = ("Latest Updates" in msg or "Live Web Search" in msg) and "pmkisan.gov.in" in msg
        elif label.startswith("TEST 5"):
            pass_condition = "Document Checklist" in msg and "[ ]" in msg
        
        test_results[label] = "PASS" if pass_condition else "FAIL"
    else:
        test_results[label] = "FAIL"

print("\n==================================================")
print("               TEST SUMMARY RESULT                ")
print("==================================================")
for t, status in test_results.items():
    print(f"{t}: {status}")

