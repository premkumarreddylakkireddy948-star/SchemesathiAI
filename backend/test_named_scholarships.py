import urllib.request
import json
import sys

def log(msg):
    sys.stdout.buffer.write((msg + "\n").encode('utf-8'))
    sys.stdout.flush()

def run_named_scholarship_tests():
    url = "https://chair-estimated-commodity-delivering.trycloudflare.com/api/chat"
    headers = {"Content-Type": "application/json"}
    
    tests = [
        ("TEST 1", "reliance foundation scholarship details", {"year": 1, "course": "B.Tech", "annual_income": 250000}),
        ("TEST 2", "Reliance Foundation scholarship eligibility", {"year": 1, "course": "B.Tech", "annual_income": 250000}),
        ("TEST 3", "Reliance Foundation scholarship 2026-27", {"year": 1, "course": "B.Tech", "annual_income": 250000}),
        ("TEST 4", "Am I eligible for Reliance Foundation scholarship?", {"year": 2, "course": "B.Tech", "annual_income": 250000}),
        ("TEST 5", "Reliance Foundation scholarship vs Central Sector Scholarship", {"year": 1, "course": "B.Tech", "annual_income": 250000}),
        ("TEST 6", "Find scholarships for me", {"state": "Tamil Nadu", "category": "SC", "annual_income": 250000, "course": "B.Tech"}),
        ("TEST 7", "Tata scholarship details", {"year": 1, "course": "B.Tech", "annual_income": 250000})
    ]

    all_passed = True
    results = {}

    for name, q, ctx in tests:
        log(f"\n==========================================")
        log(f"RUNNING {name}: {q}")
        log(f"==========================================")
        
        payload = {
            "message": q,
            "user_context": ctx
        }
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                ans = data.get("answer", "")
                log(ans)

                test_passed = True

                # Debug check
                if "Agent Tools Invoked" in ans or "intent" in ans.lower() and "named_scholarship" in ans.lower():
                    log(f"[FAIL] {name}: Internal debug information detected!")
                    test_passed = False

                if name == "TEST 1":
                    if "Reliance Foundation Undergraduate Scholarships" not in ans or "Private / Foundation Scholarship" not in ans or "scholarships.reliancefoundation.org" not in ans:
                        test_passed = False
                    if "Post-Matric" in ans or "PM-KISAN" in ans or "PMAY" in ans:
                        log(f"[FAIL] {name}: Unrelated government scheme list leaked!")
                        test_passed = False

                elif name == "TEST 2":
                    if "Who Can Apply" not in ans or "60%" not in ans or "aptitude test" not in ans.lower():
                        test_passed = False

                elif name == "TEST 3":
                    if "2026–27" not in ans and "2026-27" not in ans:
                        test_passed = False

                elif name == "TEST 4":
                    if "NOT ELIGIBLE" not in ans or "second year" not in ans.lower():
                        log(f"[FAIL] {name}: 2nd year ineligibility not highlighted!")
                        test_passed = False

                elif name == "TEST 5":
                    if "Reliance Foundation" not in ans or "Central Sector" not in ans or "|" not in ans:
                        test_passed = False

                elif name == "TEST 6":
                    if "Scholarships Relevant to Your Profile" not in ans or "Tamil Nadu" not in ans:
                        test_passed = False

                elif name == "TEST 7":
                    if "Tata Trusts Scholarships" not in ans or "tatatrusts.org" not in ans or "Private / Foundation Scholarship" not in ans:
                        test_passed = False

                if test_passed:
                    log(f"[PASS] {name}: Verified successfully!")
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
    log("NAMED SCHOLARSHIP TEST RESULTS SUMMARY:")
    for k, v in results.items():
        log(f"{k} — {v}")
    log("==========================================")
    
    if all_passed:
        log("ALL NAMED SCHOLARSHIP TESTS PASSED CLEANLY!")
    else:
        log("SOME TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    run_named_scholarship_tests()
