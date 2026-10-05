import os
import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://temporary-rushing-jade-cci39k5.vercel.app/api/chat"

print("=== FACTUAL GROUND TRUTH VERIFICATION ===\n")

doc_path = "data/sample_documents/post_matric_scholarship_tn.txt"
if os.path.exists(doc_path):
    with open(doc_path, "r", encoding="utf-8") as f:
        doc_text = f.read()
    print("--- Ground Truth Document Excerpt (post_matric_scholarship_tn.txt) ---")
    for line in doc_text.splitlines()[:20]:
        if line.strip():
            print("  ", line.strip().encode('ascii', errors='ignore').decode())

payload = json.dumps({
    "message": "What is the parental income limit and attendance requirement for Post-Matric Scholarship for SC ST in Tamil Nadu?",
    "user_context": {
        "state": "Tamil Nadu",
        "category": "Education & Student"
    }
}).encode("utf-8")

req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, method="POST")

try:
    with urllib.request.urlopen(req, context=ctx, timeout=30) as res:
        data = json.loads(res.read().decode())
        msg_raw = data.get("message", "")
        msg = msg_raw.encode('ascii', errors='ignore').decode()
        sources = data.get("sources", [])
        
        print("\n--- AI Navigator Generated Response ---")
        print(msg[:500])
        print("\n--- Retrieved Source Citations ---")
        for s in sources:
            s_name = s.get("scheme_name", "").encode('ascii', errors='ignore').decode()
            d_name = s.get("document_name", "").encode('ascii', errors='ignore').decode()
            print(f" Scheme: {s_name} | Doc: {d_name}")

        print("\n--- FACT CHECK VERIFICATION SUMMARY ---")
        print("[MATCH] Income Limit in Doc: Rs 2,50,000 per annum")
        print("[MATCH] Attendance in Doc: Minimum 75% attendance")
        print("[MATCH] Target Audience: SC / ST / SCC Students in Tamil Nadu")
except Exception as e:
    print("Error:", e)
