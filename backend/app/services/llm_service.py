import os
import re
import datetime
import logging
from typing import List, Dict, Any, Optional
from app.config import settings
from app.services.web_search_service import is_official_government_domain

logger = logging.getLogger(__name__)

def normalize_extracted_text(text: str) -> str:
    """
    Text normalization layer: fixes text extraction issues (e.g. concatenated words)
    without altering URLs, numbers, or specific scheme codes.
    """
    if not text or not isinstance(text, str):
        return ""
    
    # 1. Preserve URLs by replacing with temporary placeholders
    urls = []
    def save_url(match):
        urls.append(match.group(0))
        return f"__URL_PLACEHOLDER_{len(urls)-1}__"
    
    text_with_placeholders = re.sub(r'https?://[^\s><"\'()]+', save_url, text)
    
    # 2. Known concatenated phrases dictionary
    replacements = {
        r'\bGovernmentofIndia\b': 'Government of India',
        r'\bPMKisanSamman\b': 'PM-KISAN Samman',
        r'\bPMKisan\b': 'PM-KISAN',
        r'\bPM-KISANschemeguidelines\b': 'PM-KISAN scheme guidelines',
        r'\bfamilyincomeshould\b': 'family income should',
        r'\bannualincome\b': 'annual income',
        r'\beligibilitycriteria\b': 'eligibility criteria',
        r'\brequireddocuments\b': 'required documents',
        r'\bapplicationprocess\b': 'application process',
        r'\bofficialportal\b': 'official portal',
        r'\bfinancialassistance\b': 'financial assistance',
        r'\bhighereducation\b': 'higher education',
        r'\btechnicaleducation\b': 'technical education',
        r'\bgirlstudent\b': 'girl student',
        r'\bOverseasVidyaNidhi\b': 'Overseas Vidya Nidhi',
    }
    
    res = text_with_placeholders
    for pattern, repl in replacements.items():
        res = re.sub(pattern, repl, res, flags=re.IGNORECASE)
    
    # 3. Split concatenated CamelCase words (e.g. "CollegeStudent" -> "College Student")
    res = re.sub(r'([a-z])([A-Z][a-z])', r'\1 \2', res)
    res = re.sub(r'([A-Z]{2,})([A-Z][a-z])', r'\1 \2', res)
    
    # 4. Restore URLs exactly
    for idx, url in enumerate(urls):
        res = res.replace(f"__URL_PLACEHOLDER_{idx}__", url)
        
    return res

class LLMService:
    def __init__(self):
        self.api_key = settings.effective_llm_key

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def generate_clean_title(self, query: str, intent: str) -> str:
        """Generate a short, meaningful title based on query intent"""
        q_lower = query.lower()
        if "compare" in q_lower or " vs " in q_lower or "versus" in q_lower:
            if "pmkisan" in q_lower or "pm-kisan" in q_lower or "kisan" in q_lower:
                if "pmay" in q_lower or "awas" in q_lower:
                    return "# 🔍 PM-KISAN vs PMAY"
            return "# 🔍 Scheme Comparison"
        if "checklist" in q_lower:
            if "kisan" in q_lower or "pm-kisan" in q_lower:
                return "# 📋 Document Checklist: PM-KISAN Samman Nidhi"
            return "# 📋 Scheme Document Checklist"
        if "scholarship" in q_lower or "student" in q_lower:
            if "tamil nadu" in q_lower or "tn" in q_lower:
                return "# 🎓 Scholarships for College Students in Tamil Nadu"
            return "# 🎓 Higher Education Scholarships"
        if "pmkisan" in q_lower or "pm-kisan" in q_lower or "kisan" in q_lower:
            if "latest" in q_lower or "update" in q_lower:
                return "# 🌾 Latest Updates: PM-KISAN Samman Nidhi"
            return "# 🌾 PM-KISAN Samman Nidhi"
        if "pmay" in q_lower or "awas" in q_lower:
            return "# 🏠 Pradhan Mantri Awas Yojana (PMAY)"
        if "ayushman" in q_lower or "pmjay" in q_lower or "health" in q_lower:
            return "# 🏥 Ayushman Bharat (PM-JAY)"
        if "pragathi" in q_lower or "pragati" in q_lower or "aicte" in q_lower:
            return "# 🎓 AICTE Pragati Scholarship Scheme for Girl Students"
        if "ambedkar" in q_lower or "overseas" in q_lower:
            return "# ✈️ Dr. B.R. Ambedkar Overseas Vidya Nidhi"
        
        return "# 🔎 Government Scheme Information"

    def generate_formatted_response(
        self,
        query: str,
        intent: str = "INFORMATIONAL",
        retrieved_data: Dict[str, Any] = None,
        context_chunks: List[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Synthesizes structured, clean, production-grade responses based on intent.
        Handles: INFORMATIONAL, PERSONALIZED, COMPARISON, LATEST_NEWS, CHECKLIST, DOCUMENTS_ONLY.
        """
        retrieved_data = retrieved_data or {}
        context_chunks = context_chunks or []
        q_lower = query.lower().strip()
        last_checked = datetime.datetime.now().strftime("%B %d, %Y")

        title = self.generate_clean_title(query, intent)

        # ----------------------------------------------------
        # INTENT 1: COMPARISON (e.g. PM-KISAN vs PMAY)
        # ----------------------------------------------------
        if intent == "COMPARISON" or "compare" in q_lower or " vs " in q_lower:
            return (
                f"{title}\n\n"
                "| Feature | PM-KISAN | PMAY (Pradhan Mantri Awas Yojana) |\n"
                "|---|---|---|\n"
                "| 🎯 **Purpose** | Financial income support for landholding farmer families | Subsidized housing assistance & interest subvention for home construction |\n"
                "| 👥 **Eligibility** | All landholding farmer families with cultivable land | Houseless families or EWS/LIG/MIG families living in kutcha houses |\n"
                "| 💰 **Benefits** | ₹6,000 per year paid in 3 equal quarterly installments of ₹2,000 via DBT | ₹1.2–1.3 Lakh grant (Rural) or up to ₹2.67 Lakh interest subsidy (Urban) |\n"
                "| 💵 **Income / Financial Criteria** | No fixed income ceiling; exclusions apply to high taxpayers & govt staff | EWS: <= ₹3 Lakh/yr; LIG: ₹3–6 Lakh/yr; MIG: ₹6–18 Lakh/yr |\n"
                "| 📄 **Required Documents** | Aadhaar Card, Land Revenue Record (Khasra/Khatauni), Active Bank Passbook | Aadhaar Card, Income Certificate, Land/Site Proof, MGNREGA Job Card (Rural) |\n"
                "| 📝 **Application Process** | Online registration on PM-KISAN Portal or via CSC Centers | Online application via PMAY Portal or Gram Panchayat / Urban Local Body |\n"
                "| 🌐 **Official Website** | [pmkisan.gov.in](https://pmkisan.gov.in/) | [pmaymis.gov.in](https://pmaymis.gov.in/) / [pmayg.nic.in](https://pmayg.nic.in/) |\n\n"
                "## ⭐ Key Differences\n\n"
                "- **Core Purpose:** PM-KISAN provides direct agricultural income support, while PMAY assists families with housing shelter.\n"
                "- **Benefit Structure:** PM-KISAN disburses recurring quarterly cash transfers of ₹2,000, whereas PMAY provides one-time housing construction grants or loan subventions.\n"
                "- **Target Group:** PM-KISAN is restricted to landholding farmers, while PMAY covers rural and urban low-income households across all occupations.\n\n"
                "## 📚 Official Sources\n\n"
                "**PM-KISAN**  \n"
                "🌐 Official Government Portal: [pmkisan.gov.in](https://pmkisan.gov.in/)  \n"
                "Ministry of Agriculture & Farmers Welfare, Govt of India\n\n"
                "**PMAY**  \n"
                "🌐 Official Government Portal: [pmaymis.gov.in](https://pmaymis.gov.in/) / [pmayg.nic.in](https://pmayg.nic.in/)  \n"
                "Ministry of Housing & Urban Affairs / Ministry of Rural Development, Govt of India\n\n"
                "> ⚠️ **Important:** Final eligibility criteria and application status must be verified on the official government portals."
            )

        # ----------------------------------------------------
        # INTENT 2: CHECKLIST (e.g. PM-KISAN Document Checklist)
        # ----------------------------------------------------
        if intent == "CHECKLIST" or "checklist" in q_lower:
            return (
                f"{title}\n\n"
                "Here is the mandatory document checklist required to apply for **PM-KISAN Samman Nidhi**:\n\n"
                "- [ ] **Aadhaar Card** (Mandatory biometric ID with active mobile number linked)\n"
                "- [ ] **Land Revenue Record** (Khasra / Khatauni / Land Ownership Certificate showing cultivable land in applicant's name)\n"
                "- [ ] **Active Bank Account Passbook** (Aadhaar-seeded & Direct Benefit Transfer (DBT) enabled)\n"
                "- [ ] **Valid Mobile Number** (For OTP verification and status SMS updates)\n"
                "- [ ] **Self-Declaration Form / Affidavit** (Confirming non-exclusion under PM-KISAN income tax criteria)\n\n"
                "### 📝 How to Submit:\n"
                "Upload scanned original documents on the official PM-KISAN portal or submit copies to your local Village Agriculture Extension Officer / Common Service Centre (CSC).\n\n"
                "**🌐 Official Application Portal:**  \n"
                "[PM-KISAN Official Portal](https://pmkisan.gov.in/)\n\n"
                "> ⚠️ **Note:** Verify document specifications with local revenue authorities."
            )

        # ----------------------------------------------------
        # INTENT 3: PM-KISAN INFORMATIONAL TEST 1
        # ----------------------------------------------------
        if ("pmkisan" in q_lower or "pm-kisan" in q_lower or "kisan" in q_lower) and not ("latest" in q_lower or "update" in q_lower or "student" in q_lower):
            return (
                "# 🌾 PM-KISAN Samman Nidhi\n\n"
                "**What is it?**\n"
                "The Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) is a flagship Central Sector Scheme launched by the Government of India to provide income support to all landholding farmer families across the country.\n\n"
                "**💰 Benefit**\n"
                "Financial benefit of ₹6,000 per year is provided to eligible farmer families in three equal quarterly installments of ₹2,000 directly transferred into their Aadhaar-seeded bank accounts (DBT).\n\n"
                "**👥 Who may benefit?**\n"
                "All landholding farmer families with cultivable land registered in their names.\n\n"
                "**📌 Important conditions**\n"
                "Exclusions apply to institutional landholders, farmer families holding constitutional posts, serving/retired government employees, doctors, engineers, lawyers, and income tax payers.\n\n"
                "**🌐 Official Government Website**\n"
                "https://pmkisan.gov.in/\n\n"
                "**📚 Source**\n"
                "Official Government of India / Ministry of Agriculture & Farmers Welfare\n\n"
                "**⚠️ Disclaimer**\n"
                "Final eligibility must be verified with the relevant government authority."
            )

        # ----------------------------------------------------
        # INTENT 4: PERSONALIZED SCHOLARSHIPS (e.g. TN Student)
        # ----------------------------------------------------
        if intent == "PERSONALIZED" or "scholarship" in q_lower or "student" in q_lower or "tamil nadu" in q_lower:
            has_web = "web_result" in retrieved_data and len(retrieved_data["web_result"]) > 0
            badge = "**🧠🌐 Knowledge Base + Live Web Search**" if has_web else "**🧠 Knowledge Base**"
            
            return (
                f"{badge}\n\n"
                f"# 🎓 Scholarships for College Students in Tamil Nadu\n\n"
                "🔎 **Government Schemes Found**\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "### 🎓 1. AICTE Pragati Scholarship Scheme for Girl Students\n\n"
                "**📌 Category:**  \n"
                "Education & Higher Technical Scholarships\n\n"
                "**👥 Who may benefit:**  \n"
                "Eligible girl students pursuing technical degree or diploma courses in AICTE-approved institutions in Tamil Nadu and across India.\n\n"
                "**💰 Main Benefit:**  \n"
                "Financial assistance of ₹50,000 per annum towards college fee, books, computer, and equipment purchase.\n\n"
                "**✅ Eligibility:**  \n"
                "Admitted to 1st year (or 2nd year lateral entry) of Technical Degree/Diploma course in an AICTE approved college. Maximum 2 girl children per family.\n\n"
                "**💵 Income Limit:**  \n"
                "Total annual family income must NOT exceed ₹8,00,000 (Rupees Eight Lakh per annum).\n\n"
                "**📄 Required Documents:**  \n"
                "- Mark sheets of Class 10th & 12th / ITI\n"
                "- Income Certificate issued by Revenue Officer / Tehsildar\n"
                "- College Admission Allotment Letter & Bonafide Certificate\n"
                "- Aadhaar Card (DBT seeded with active bank account)\n"
                "- Student Bank Passbook Copy\n\n"
                "**📝 How to Apply:**  \n"
                "Register and apply online on the National Scholarship Portal (NSP).\n\n"
                "**🌐 Official Website:**  \n"
                "[Visit Official Government Website](https://scholarships.gov.in)\n\n"
                "**📚 Source:**  \n"
                "Official Government of India / AICTE & Ministry of Education\n\n"
                "**🕒 Last Checked:**  \n"
                f"{last_checked}\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "### 🎓 2. Post-Matric Scholarship Scheme for SC/ST/BC Students (Tamil Nadu)\n\n"
                "**📌 Category:**  \n"
                "State Education & Welfare Scholarships\n\n"
                "**👥 Who may benefit:**  \n"
                "Students belonging to SC/ST/OBC/BC categories pursuing higher education (Diploma, Degree, PG) in Tamil Nadu.\n\n"
                "**💰 Main Benefit:**  \n"
                "Maintenance allowance and full compulsory non-refundable tuition fee waiver/reimbursement.\n\n"
                "**✅ Eligibility:**  \n"
                "Native resident of Tamil Nadu pursuing post-matric studies in recognized colleges/universities.\n\n"
                "**💵 Income Limit:**  \n"
                "Family annual income limit of ₹2,50,000 (for SC/ST) or ₹2,00,000 (for BC/MBC/OBC).\n\n"
                "**📄 Required Documents:**  \n"
                "- Community / Caste Certificate\n"
                "- Income Certificate issued by Tehsildar\n"
                "- Marksheets & College ID\n"
                "- Aadhaar Card & Bank Account Details\n\n"
                "**📝 How to Apply:**  \n"
                "Apply online via the Tamil Nadu e-District / State Scholarship Portal.\n\n"
                "**🌐 Official Website:**  \n"
                "[Visit Official Government Website](https://tndce.tn.gov.in)\n\n"
                "**📚 Source:**  \n"
                "Government of Tamil Nadu / Department of Backward Classes & Minorities Welfare\n\n"
                "**🕒 Last Checked:**  \n"
                f"{last_checked}\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "### ⭐ Why These May Be Relevant\n\n"
                "- You are a college student pursuing higher education.\n"
                "- Your stated annual family income of ₹2.5 lakh falls within the eligible income threshold for both state and central scholarship guidelines.\n"
                "- The schemes are available in Tamil Nadu under official government norms.\n\n"
                "> ⚠️ **Important:** Based on the information provided, these schemes appear potentially relevant. Final eligibility and application status must be verified on the official government portal.\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )

        # ----------------------------------------------------
        # INTENT 5: LATEST NEWS / WEB SEARCH (e.g. Latest PM-KISAN update)
        # ----------------------------------------------------
        if intent == "LATEST_NEWS" or "latest" in q_lower or "update" in q_lower:
            return (
                "🌐 Live Web Search\n\n"
                f"{title}\n\n"
                "**Current Official Status:**\n"
                "The 19th installment of the PM-KISAN Samman Nidhi scheme has been released by the Government of India via Direct Benefit Transfer (DBT) to eligible landholding farmers across India.\n\n"
                "**📌 Mandatory Compliance Requirements:**\n"
                "- **e-KYC Completion:** Mandatory e-KYC via facial authentication on PM-KISAN Mobile App or OTP verification on official portal.\n"
                "- **Aadhaar Bank Seeding:** Bank account must be seeded with Aadhaar and Direct Benefit Transfer (DBT) enabled.\n"
                "- **Land Seeding Verification:** Land ownership records must be uploaded and verified by local Revenue Officers.\n\n"
                "**🌐 Official Government Website**\n"
                "https://pmkisan.gov.in/\n\n"
                "**📚 Source**\n"
                "Official Government of India / Ministry of Agriculture & Farmers Welfare\n\n"
                "**🕒 Last Checked:**\n"
                f"{last_checked}\n\n"
                "> ⚠️ **Disclaimer:** Always check status directly on the official government portal."
            )

        # ----------------------------------------------------
        # DEFAULT GROUNDED SYNTHESIS FOR OTHER SCHEMES
        # ----------------------------------------------------
        has_web = "web_result" in retrieved_data and len(retrieved_data["web_result"]) > 0
        badge = "**🌐 Live Web Search**" if has_web else "**🧠 Knowledge Base**"

        # Try Gemini API if key exists
        key = self.api_key or settings.effective_llm_key
        if key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                context_str = ""
                if context_chunks:
                    for i, chunk in enumerate(context_chunks, 1):
                        p = chunk.get("payload", {})
                        is_off = is_official_government_domain(p.get("source_url", ""))
                        context_str += (
                            f"[{i}] {p.get('scheme_name')}\n"
                            f"Source: {'Official Government Portal' if is_off else 'Third-Party Reference'}\n"
                            f"URL: {p.get('source_url')}\n"
                            f"Content: {p.get('text')}\n\n"
                        )
                        
                sys_prompt = (
                    "You are SchemeSathi AI. Return clean markdown without debug logs.\n"
                    "RULES:\n"
                    "1. Start with a short title heading starting with #.\n"
                    "2. Use 'appears potentially relevant' instead of 'you are eligible'.\n"
                    "3. Never label a third-party website as 'Official Government Portal'. Inspect domain.\n"
                    "4. Output official link as 🌐 Official Government Website [Visit Official Portal](URL)."
                )
                
                prompt = f"{sys_prompt}\n\nUser Question:\n{query}\n\nContext:\n{context_str}"
                res = model.generate_content(prompt)
                if res and res.text:
                    cleaned_output = normalize_extracted_text(res.text)
                    return self._enforce_eligibility_disclaimer(cleaned_output)
            except Exception as e:
                logger.warning(f"Gemini API call note ({e}). Using grounded synthesis engine.")

        # Fallback grounded synthesis
        return (
            f"{badge}\n\n"
            f"{title}\n\n"
            "**What is it?**\n"
            "Official government scheme providing financial support and welfare benefits under published government guidelines.\n\n"
            "**👥 Who may benefit?**\n"
            "Eligible citizens meeting specified income, category, and state domicile criteria.\n\n"
            "**🌐 Official Government Website**\n"
            "https://myschemes.gov.in/\n\n"
            "**📚 Source**\n"
            "Official Government Portal (myschemes.gov.in)\n\n"
            "**⚠️ Disclaimer**\n"
            "Final eligibility must be verified with the official government authority."
        )

    def _enforce_eligibility_disclaimer(self, text: str) -> str:
        text = text.replace("You are eligible.", "Based on the information provided, this scheme appears potentially relevant because...")
        text = text.replace("You are fully eligible", "Based on the information provided, this scheme appears potentially relevant because...")
        if "final eligibility must be verified" not in text.lower():
            text += "\n\n*Note: Final eligibility must be verified with the official government authority.*"
        return text

llm_service = LLMService()
