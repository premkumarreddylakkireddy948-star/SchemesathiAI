import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_URL = "http://127.0.0.1:8000/api/chat"

print("==================================================")
print("   TESTING CONSECUTIVE CONVERSATION MESSAGES      ")
print("==================================================\n")

# Step 1: Send Message 1
m1 = "Compare PM-KISAN and PMAY based on eligibility, benefits, documents and application process."
print(f"--> SENDING MESSAGE 1: {m1}\n")

payload1 = json.dumps({
    "message": m1,
    "user_context": {
        "state": "Tamil Nadu",
        "category": "SC",
        "annual_income": 250000,
        "occupation": "Student"
    }
}).encode("utf-8")

req1 = urllib.request.Request(API_URL, data=payload1, headers={"Content-Type": "application/json"})

cid = None
with urllib.request.urlopen(req1, timeout=15) as res1:
    data1 = json.loads(res1.read().decode("utf-8"))
    cid = data1.get("conversation_id")
    print("=== MESSAGE 1 RESPONSE PREVIEW ===")
    print(data1.get("message")[:300])
    print("==================================\n")

# Step 2: Send Message 2 in SAME Conversation ID
m2 = "I am a 20-year-old B.Tech student from Tamil Nadu. My family income is ₹2.5 lakh per year. I belong to an SC category and I need financial assistance for my education. Find the most relevant government scholarships or schemes for me, compare the top 3 options, tell me the required documents, application process, and official government website for each. Do not claim that I am definitely eligible; explain what I should verify."

print(f"--> SENDING MESSAGE 2 (Conversation ID: {cid}): {m2}\n")

payload2 = json.dumps({
    "conversation_id": cid,
    "message": m2,
    "user_context": {
        "state": "Tamil Nadu",
        "category": "SC",
        "annual_income": 250000,
        "occupation": "Student"
    }
}).encode("utf-8")

req2 = urllib.request.Request(API_URL, data=payload2, headers={"Content-Type": "application/json"})

with urllib.request.urlopen(req2, timeout=15) as res2:
    data2 = json.loads(res2.read().decode("utf-8"))
    print("=== MESSAGE 2 RESPONSE OUTPUT ===")
    print(data2.get("message"))
    print("\n--------------------------------------------------")
    print("AGENT TOOLS USED:", data2.get("agent_steps"))
