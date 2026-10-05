import urllib.request
import json
import sys

def log(msg):
    sys.stdout.buffer.write((msg + "\n").encode('utf-8'))
    sys.stdout.flush()

def run_live_production_tests():
    url = "https://rose-naval-fairy-preceding.trycloudflare.com/api/chat"
    headers = {"Content-Type": "application/json"}
    
    tests = [
        ("TEST 1", "What is PM-KISAN and who can benefit from it? Give me the official government website."),
        ("TEST 2", "I am a 20-year-old B.Tech student from Tamil Nadu. My family income is Rs 2.5 lakh per year. I belong to an SC category and I need financial assistance for my education. Find the most relevant government scholarships or schemes for me, compare the top 3 options, tell me the required documents, application process, and official government website for each. Do not claim that I am definitely eligible; explain what I should verify."),
        ("TEST 3", "Tell me the Andhra Pradesh government schemes for students."),
        ("TEST 4", "I am an SC B.Tech student with family income Rs 2.5 lakh. What Andhra Pradesh scholarships may be relevant to me?"),
        ("TEST 5", "Compare PM-KISAN and PMAY based on eligibility, benefits, documents and application process."),
        ("TEST 6", "What is the latest government scholarship information for Andhra Pradesh students in 2026?"),
        ("TEST 7", "What documents do I need to apply for PM-KISAN?")
    ]

    all_passed = True
    results = {}

    for name, q in tests:
        log(f"\n==========================================")
        log(f"RUNNING LIVE {name}: {q}")
        log(f"==========================================")
        
        payload = {
            "message": q,
            "user_context": {
                "state": "Tamil Nadu",
                "annual_income": 250000,
                "category": "SC",
                "course": "B.Tech",
                "age": 20
            }
        }
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                ans = data.get("answer", "")
                log(ans)

                test_passed = True
                
                if "Government Scheme Information" in ans and "Official government scheme providing financial support" in ans:
                    log(f"[FAIL] {name}: Generic dummy text detected!")
                    test_passed = False
                
                if name == "TEST 1":
                    if "PM-KISAN" not in ans or "pmkisan.gov.in" not in ans:
                        test_passed = False

                elif name == "TEST 2":
                    if "Tamil Nadu" not in ans or "tndce.tn.gov.in" not in ans or "scholarships.gov.in" not in ans:
                        test_passed = False

                elif name in ["TEST 3", "TEST 4", "TEST 6"]:
                    if "jnanabhumi.ap.gov.in" not in ans or "epass.apcfss.in" not in ans:
                        test_passed = False
                    if name == "TEST 4" and "State Domicile Note" not in ans:
                        test_passed = False

                elif name == "TEST 5":
                    if "PM-KISAN" not in ans or "PMAY" not in ans or "|" not in ans:
                        test_passed = False

                elif name == "TEST 7":
                    if "Aadhaar" not in ans or "Land" not in ans or "pmkisan.gov.in" not in ans:
                        test_passed = False

                if test_passed:
                    log(f"[PASS] {name}: Verified successfully on live production!")
                    results[name] = "PASS"
                else:
                    log(f"[FAIL] {name}: Validation criteria failed!")
                    results[name] = "FAIL"
                    all_passed = False

        except Exception as e:
            log(f"[FAIL] {name}: HTTP request error: {e}")
            results[name] = "FAIL"
            all_passed = False

    log("\n==========================================")
    log("LIVE PRODUCTION TEST RESULTS SUMMARY:")
    for k, v in results.items():
        log(f"{k} — {v}")
    log("==========================================")
    
    if all_passed:
        log("PRODUCTION DEPLOYMENT SUCCESSFUL")
    else:
        log("PRODUCTION DEPLOYMENT FAILED")
        sys.exit(1)

if __name__ == "__main__":
    run_live_production_tests()
