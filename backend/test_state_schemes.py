import urllib.request
import json
import sys

def log(msg):
    sys.stdout.buffer.write((msg + "\n").encode('utf-8'))
    sys.stdout.flush()

def run_http_tests():
    url = "http://localhost:8000/api/chat"
    headers = {"Content-Type": "application/json"}
    
    tests = [
        ("TEST 1", "Tell me the Andhra Pradesh government schemes for students."),
        ("TEST 2", "I am an SC B.Tech student with family income Rs 2.5 lakh. What Andhra Pradesh scholarships may be relevant to me?"),
        ("TEST 3", "What scholarships are available for B.Tech students in Tamil Nadu?"),
        ("TEST 4", "Compare PM-KISAN and PMAY."),
        ("TEST 5", "What is the latest government scholarship information for Andhra Pradesh students in 2026?")
    ]

    all_passed = True

    for name, q in tests:
        log(f"\n==========================================")
        log(f"RUNNING {name}: {q}")
        log(f"==========================================")
        
        payload = {
            "message": q,
            "user_context": {
                "state": "Tamil Nadu",
                "annual_income": 250000,
                "category": "SC",
                "course": "B.Tech"
            }
        }
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                ans = data.get("answer", "")
                
                log(ans)

                # Assertions
                if "Government Scheme Information" in ans and "Official government scheme providing financial support" in ans:
                    log(f"[FAIL] {name}: Generic dummy text detected!")
                    all_passed = False
                
                if name in ["TEST 1", "TEST 2", "TEST 5"]:
                    if "jnanabhumi.ap.gov.in" not in ans or "epass.apcfss.in" not in ans:
                        log(f"[FAIL] {name}: Missing official AP portals!")
                        all_passed = False
                    else:
                        log(f"[PASS] {name}: Official AP Portals found.")

                if name == "TEST 2":
                    if "State Domicile Note" not in ans or "Tamil Nadu" not in ans:
                        log(f"[FAIL] {name}: State Domicile Note missing or domicile not highlighted!")
                        all_passed = False
                    else:
                        log(f"[PASS] {name}: State Domicile Note present.")

                if name == "TEST 3":
                    if "Tamil Nadu" not in ans or ("tndce.tn.gov.in" not in ans and "scholarships.gov.in" not in ans):
                        log(f"[FAIL] {name}: TN scholarships or official links missing!")
                        all_passed = False
                    else:
                        log(f"[PASS] {name}: TN Scholarships found.")

                if name == "TEST 4":
                    if "PM-KISAN" not in ans or "PMAY" not in ans or "|" not in ans:
                        log(f"[FAIL] {name}: Comparison table missing!")
                        all_passed = False
                    else:
                        log(f"[PASS] {name}: Comparison table present.")
        except Exception as e:
            log(f"[FAIL] {name}: HTTP request error: {e}")
            all_passed = False

    if all_passed:
        log("\n==========================================")
        log("ALL 5 REGRESSION TESTS PASSED CLEANLY!")
        log("==========================================")
    else:
        log("\n==========================================")
        log("SOME TESTS FAILED")
        log("==========================================")
        sys.exit(1)

if __name__ == "__main__":
    run_http_tests()
