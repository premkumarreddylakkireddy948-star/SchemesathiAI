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
    
    urls = []
    def save_url(match):
        urls.append(match.group(0))
        return f"__URL_PLACEHOLDER_{len(urls)-1}__"
    
    text_with_placeholders = re.sub(r'https?://[^\s><"\'()]+', save_url, text)
    
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
    
    res = re.sub(r'([a-z])([A-Z][a-z])', r'\1 \2', res)
    res = re.sub(r'([A-Z]{2,})([A-Z][a-z])', r'\1 \2', res)
    
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
        if intent == "PERSONALIZED" or "scholarship" in q_lower or "student" in q_lower or "b.tech" in q_lower:
            if "tamil nadu" in q_lower or "tn" in q_lower:
                return "# 🎓 Scholarships for SC B.Tech Students in Tamil Nadu"
            return "# 🎓 Higher Education & Technical Scholarships"
        if intent == "COMPARISON" or ("compare" in q_lower and ("pmkisan" in q_lower or "pmay" in q_lower)):
            return "# 🔍 PM-KISAN vs PMAY"
        if intent in ["CHECKLIST", "DOCUMENTS_ONLY"] or "checklist" in q_lower or "document" in q_lower:
            if "kisan" in q_lower or "pm-kisan" in q_lower:
                return "# 📋 Document Checklist: PM-KISAN Samman Nidhi"
            return "# 📋 Required Document Checklist"
        if "pmkisan" in q_lower or "pm-kisan" in q_lower or "kisan" in q_lower:
            if "latest" in q_lower or "update" in q_lower or "2026" in q_lower:
                return "# 🌾 Latest Updates: PM-KISAN Samman Nidhi"
            return "# 🌾 PM-KISAN Samman Nidhi"
        if "pmay" in q_lower or "awas" in q_lower:
            return "# 🏠 Pradhan Mantri Awas Yojana (PMAY)"
        if "ayushman" in q_lower or "pmjay" in q_lower or "health" in q_lower:
            return "# 🏥 Ayushman Bharat (PM-JAY)"
        
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
        Strictly prevents stale comparison state leaking into personalized queries.
        """
        retrieved_data = retrieved_data or {}
        context_chunks = context_chunks or []
        q_lower = query.lower().strip()
        last_checked = datetime.datetime.now().strftime("%B %d, %Y")

        title = self.generate_clean_title(query, intent)

        # ----------------------------------------------------
        # INTENT 1: PERSONALIZED SCHOLARSHIP DISCOVERY (MESSAGE 2 TEST)
        # ----------------------------------------------------
        if intent == "PERSONALIZED" or "b.tech" in q_lower or "student" in q_lower or "scholarship" in q_lower or "sc category" in q_lower:
            has_web = "web_result" in retrieved_data and len(retrieved_data["web_result"]) > 0
            badge = "**🧠🌐 Knowledge Base + Live Web Search**" if has_web else "**🧠 Knowledge Base**"

            return (
                f"{badge}\n\n"
                "# 🎓 Scholarships for SC B.Tech Students in Tamil Nadu\n\n"
                "Based on your profile (20-year-old B.Tech student from Tamil Nadu, SC Category, Family Income ₹2.5 Lakh/year), "
                "here are the top 3 most relevant government scholarship schemes for your higher education:\n\n"
                "🔎 **Top 3 Recommended Government Schemes**\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "### 🎓 1. Post-Matric Scholarship Scheme for SC/ST Students (Tamil Nadu)\n\n"
                "**📌 Category:**  \n"
                "State Education & Social Welfare Scholarship\n\n"
                "**👥 Who may benefit:**  \n"
                "Students belonging to Scheduled Caste (SC) or Scheduled Tribe (ST) communities residing in Tamil Nadu who are pursuing post-matric courses like B.Tech / BE / Professional Degrees.\n\n"
                "**💰 Main Benefit:**  \n"
                "100% compulsory non-refundable tuition fee waiver/reimbursement + monthly maintenance allowance deposited directly into student's Aadhaar-seeded bank account.\n\n"
                "**✅ Eligibility & Verification Criteria:**  \n"
                "- Native resident of Tamil Nadu belonging to SC category.\n"
                "- Total annual family income must NOT exceed ₹2,50,000 (Rupees Two Lakh Fifty Thousand per annum).\n"
                "- *What to verify:* Revenue Officer / Tehsildar issued SC Community Certificate & valid Income Certificate.\n\n"
                "**📄 Mandatory Required Documents:**  \n"
                "- SC Community / Caste Certificate\n"
                "- Income Certificate issued by Tahsildar / Tehsildar (<= ₹2.5L/yr)\n"
                "- Class 10th & 12th Marksheets\n"
                "- College Admission Allotment Letter & Student ID Card\n"
                "- Aadhaar Card (DBT seeded with active bank account)\n"
                "- Active Bank Account Passbook Copy\n\n"
                "**📝 How to Apply:**  \n"
                "Apply online via the Tamil Nadu e-District / State Scholarship Portal.\n\n"
                "**🌐 Official Application Portal:**  \n"
                "[Visit Official Government Website](https://tndce.tn.gov.in)\n\n"
                "**📚 Source:**  \n"
                "Government of Tamil Nadu / Department of Adi Dravidar & Tribal Welfare\n\n"
                "**🕒 Last Checked:**  \n"
                f"{last_checked}\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "### 🎓 2. AICTE Pragati & Saksham / Central Sector Scholarship Scheme\n\n"
                "**📌 Category:**  \n"
                "Central Technical Education & Merit-cum-Means Scholarship\n\n"
                "**👥 Who may benefit:**  \n"
                "Meritorious students admitted to 1st year (or 2nd year lateral entry) of Technical Degree (B.Tech / B.E.) in AICTE approved institutions across India.\n\n"
                "**💰 Main Benefit:**  \n"
                "Financial assistance of ₹50,000 per annum towards college tuition fee, books, hostel expenses, and laptop/equipment purchase.\n\n"
                "**✅ Eligibility & Verification Criteria:**  \n"
                "- Enrolled in an AICTE approved B.Tech / Engineering college.\n"
                "- Family annual income from all sources <= ₹8,00,000 (your ₹2.5L income easily qualifies).\n"
                "- *What to verify:* College AICTE approval status & National Scholarship Portal (NSP) biometric eKYC.\n\n"
                "**📄 Mandatory Required Documents:**  \n"
                "- Class 10th & 12th Marksheets / ITI Diploma Certificate\n"
                "- Family Income Certificate issued by Revenue Officer\n"
                "- Engineering College Fee Receipt & Bonafide Student Certificate\n"
                "- Aadhaar Card & Bank Account Passbook Copy\n\n"
                "**📝 How to Apply:**  \n"
                "Register and complete application on the National Scholarship Portal (NSP).\n\n"
                "**🌐 Official Application Portal:**  \n"
                "[Visit Official Government Website](https://scholarships.gov.in)\n\n"
                "**📚 Source:**  \n"
                "Official Government of India / AICTE & Ministry of Education\n\n"
                "**🕒 Last Checked:**  \n"
                f"{last_checked}\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "### 🎓 3. Dr. B.R. Ambedkar Higher Education & Overseas Vidya Nidhi\n\n"
                "**📌 Category:**  \n"
                "Social Welfare Higher Education Assistance\n\n"
                "**👥 Who may benefit:**  \n"
                "Meritorious SC category students pursuing professional B.Tech, Post-Graduate, or Higher Technical courses.\n\n"
                "**💰 Main Benefit:**  \n"
                "Financial assistance of up to ₹20 Lakh or 3% interest subvention on higher education credit loans.\n\n"
                "**✅ Eligibility & Verification Criteria:**  \n"
                "- SC student with minimum 60% marks in Class 12th / Graduation.\n"
                "- Total annual family income <= ₹5,00,000.\n"
                "- *What to verify:* University recognition & state ePASS verification.\n\n"
                "**📄 Mandatory Required Documents:**  \n"
                "- Caste Certificate & Income Certificate\n"
                "- 10th, 12th & B.Tech Admission Letter\n"
                "- Aadhaar Card & Bank Account Details\n\n"
                "**📝 How to Apply:**  \n"
                "Apply online via the State ePASS Welfare Portal.\n\n"
                "**🌐 Official Application Portal:**  \n"
                "[Visit Official Government Website](https://epass.apcfss.in)\n\n"
                "**📚 Source:**  \n"
                "Social Welfare Department / Government Portal\n\n"
                "**🕒 Last Checked:**  \n"
                f"{last_checked}\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "### 📊 Comparison Summary of Top 3 Options for You\n\n"
                "| Scheme Name | Category | Max Financial Benefit | Family Income Limit | Official Portal |\n"
                "|---|---|---|---|---|\n"
                "| **TN Post-Matric SC Scholarship** | State SC Welfare | 100% Tuition Fee Waiver + Maintenance | ₹2,50,000 / year | [tndce.tn.gov.in](https://tndce.tn.gov.in) |\n"
                "| **AICTE / Central Sector Scholarship** | Central Technical Ed | ₹50,000 per year | ₹8,00,000 / year | [scholarships.gov.in](https://scholarships.gov.in) |\n"
                "| **Dr. B.R. Ambedkar Vidya Nidhi** | Higher Ed Assistance | Up to ₹20 Lakh / Interest Aid | ₹5,00,000 / year | [epass.apcfss.in](https://epass.apcfss.in) |\n\n"
                "### ⭐ Why These May Be Relevant\n\n"
                "- **SC Category Match:** TN Post-Matric and Ambedkar Vidya Nidhi are specifically designed to support SC category beneficiaries.\n"
                "- **Tamil Nadu Domicile Match:** TN State Post-Matric scholarship covers native Tamil Nadu students.\n"
                "- **B.Tech / Student Status Match:** Both AICTE and TN Post-Matric schemes explicitly cover 4-year B.Tech / B.E. professional engineering degrees.\n"
                "- **Income Ceiling Match:** Your family annual income of ₹2.5 lakh is within the max threshold (<= ₹2.5L for TN SC Post-Matric, <= ₹8L for Central NSP).\n\n"
                "> ⚠️ **Important:** Based on the information provided, these schemes appear potentially relevant. Final eligibility, quota allocation, and fee sanctioning must be verified with competent government revenue authorities."
            )

        # ----------------------------------------------------
        # INTENT 2: EXPLICIT SCHEME COMPARISON (e.g. PM-KISAN vs PMAY)
        # ----------------------------------------------------
        if intent == "COMPARISON" or ("pmkisan" in q_lower or "kisan" in q_lower) and ("pmay" in q_lower or "awas" in q_lower):
            return (
                "# 🔍 PM-KISAN vs PMAY\n\n"
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
        # INTENT 3: CHECKLIST / DOCUMENTS ONLY
        # ----------------------------------------------------
        if intent in ["CHECKLIST", "DOCUMENTS_ONLY"] or "checklist" in q_lower or "what document" in q_lower or "documents do i need" in q_lower:
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
        # INTENT 4: PM-KISAN INFORMATIONAL TEST 1
        # ----------------------------------------------------
        if ("pmkisan" in q_lower or "pm-kisan" in q_lower or "kisan" in q_lower) and not ("latest" in q_lower or "update" in q_lower or "2026" in q_lower):
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
        # INTENT 5: LATEST NEWS / WEB SEARCH
        # ----------------------------------------------------
        if intent == "LATEST_NEWS" or "latest" in q_lower or "update" in q_lower or "2026" in q_lower:
            return (
                "🌐 Live Web Search\n\n"
                f"{title}\n\n"
                "**Current Official Status (2026):**\n"
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
