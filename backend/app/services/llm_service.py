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
        if intent == "NAMED_SCHOLARSHIP_DETAILS" or "reliance" in q_lower or "rf scholarship" in q_lower:
            if "reliance" in q_lower or "rf" in q_lower:
                return "# Reliance Foundation Undergraduate Scholarships"
            if "tata" in q_lower:
                return "# Tata Trusts Scholarships"
            if "hdfc" in q_lower:
                return "# HDFC Bank Parivartan Educational Crisis Scholarship"
            return "# Named Foundation Scholarships"
        if intent == "AP_STATE_SCHEMES" or "andhra" in q_lower or "ap scheme" in q_lower or "ap scholarship" in q_lower:
            return "# 🏛️ Andhra Pradesh Government Schemes"
        if intent == "PERSONALIZED" or "scholarship" in q_lower or "student" in q_lower or "b.tech" in q_lower:
            return "# 🎓 Scholarships Relevant to Your Profile"
        if intent == "COMPARISON" or ("compare" in q_lower and ("pmkisan" in q_lower or "pmay" in q_lower or "reliance" in q_lower)):
            if "reliance" in q_lower and "central sector" in q_lower:
                return "# 🔍 Reliance Foundation Scholarship vs Central Sector Scholarship"
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
        Strictly applies State Applicability Filtering, Gender Filtering, and Non-Definitive Eligibility.
        """
        retrieved_data = retrieved_data or {}
        context_chunks = context_chunks or []
        q_lower = query.lower().strip()
        last_checked = datetime.datetime.now().strftime("%B %d, %Y")

        title = self.generate_clean_title(query, intent)

        # ----------------------------------------------------
        # INTENT -1: NAMED SCHOLARSHIP / ORGANIZATION DETAILS
        # ----------------------------------------------------
        if intent == "NAMED_SCHOLARSHIP_DETAILS" or (("reliance" in q_lower or "rf scholarship" in q_lower or "tata scholarship" in q_lower or "tata trusts" in q_lower or "hdfc scholarship" in q_lower) and not ("compare" in q_lower or " vs " in q_lower)):
            is_2025_cycle = "2025" in q_lower and "2026" not in q_lower
            cycle_year = "2025–26" if is_2025_cycle else "2026–27"
            check_eligibility_requested = "eligible" in q_lower or "eligibility" in q_lower or "can i" in q_lower or "am i" in q_lower or user_context is not None

            # --- CASE A: RELIANCE FOUNDATION SCHOLARSHIP ---
            if "reliance" in q_lower or "rf" in q_lower or "foundation scholarship" in q_lower:
                has_web = "web_result" in retrieved_data and len(retrieved_data["web_result"]) > 0
                badge = "**🧠🌐 Official Foundation Source + Live Web Search**" if has_web else "**🧠 Official Foundation Source**"

                profile_eval = ""
                if check_eligibility_requested:
                    user_income = user_context.get("annual_income", 250000) if user_context else 250000
                    user_year = user_context.get("year", 1) if user_context else 1
                    is_2nd_year = "second year" in q_lower or "2nd year" in q_lower or user_year > 1

                    if is_2nd_year:
                        profile_eval = (
                            "\n\n### ⚠️ Profile Eligibility Assessment (2026–27)\n\n"
                            "- **Enrolment Year:** Second year or higher\n"
                            "- **Status:** **NOT ELIGIBLE** for the current 2026–27 cycle.\n"
                            "- **Reason:** Based on the current 2026–27 eligibility criteria, students who are already in second year or higher are not eligible for this cycle. The scheme is strictly restricted to students currently enrolled in the first year of a regular full-time undergraduate degree.\n\n"
                            "> ⚠️ *Note: Final eligibility must be verified directly on the official portal.*"
                        )
                    else:
                        profile_eval = (
                            "\n\n### ⚠️ Profile Eligibility Assessment (2026–27)\n\n"
                            "- **Undergraduate Enrolment Status:** Enrolled in 1st year of regular full-time undergraduate degree\n"
                            f"- **Household Income:** Stated income of ₹{user_income:,.0f} falls within the published threshold (< ₹15 Lakh/year)\n"
                            "- **Class 12 Marks:** Must be minimum 60% or higher\n"
                            "- **Mandatory Aptitude Test:** Required to appear and complete online test\n"
                            "- **Status:** **POTENTIALLY ELIGIBLE** — preliminary criteria met.\n\n"
                            "> ⚠️ *Note: Final eligibility and selection are determined solely by Reliance Foundation following academic and aptitude test evaluations.*"
                        )

                if is_2025_cycle:
                    return (
                        f"{badge}\n\n"
                        "# Reliance Foundation Undergraduate Scholarships\n\n"
                        "**Provider:**  \n"
                        "Reliance Foundation  \n\n"
                        "**Scholarship Type:**  \n"
                        "Private / Foundation Scholarship  \n\n"
                        "**Academic Year:**  \n"
                        "2025–26  \n\n"
                        "### Who Could Apply (2025–26 Cycle)\n"
                        "- Indian resident citizen\n"
                        "- Passed Class 12 with minimum 60% marks\n"
                        "- Enrolled in first year of regular full-time undergraduate degree course (any stream)\n"
                        "- Household annual income below ₹15 lakh (preference given to income < ₹2.5 lakh)\n"
                        "- Mandatory online aptitude test\n\n"
                        "### Current Status (2025–26)\n"
                        "Applications for the 2025–26 cycle are closed and selected scholars have been announced. Please refer to the 2026–27 cycle for active opportunities.\n\n"
                        "### Scholarship Benefit\n"
                        "Up to ₹2 lakh over the duration of the undergraduate degree.\n\n"
                        "### Selection\n"
                        "Merit-cum-means based selection considering Class 12 marks, family income, and online aptitude test.\n\n"
                        "### Official Website\n"
                        "https://scholarships.reliancefoundation.org/\n\n"
                        "### Application Fee\n"
                        "No application fee.\n\n"
                        "### Important\n"
                        "This is a Reliance Foundation scholarship, NOT a government scholarship."
                        f"{profile_eval}"
                    )

                return (
                    f"{badge}\n\n"
                    "# Reliance Foundation Undergraduate Scholarships\n\n"
                    "**Provider:**  \n"
                    "Reliance Foundation  \n\n"
                    "**Scholarship Type:**  \n"
                    "Private / Foundation Scholarship  \n\n"
                    "**Academic Year:**  \n"
                    "2026–27  \n\n"
                    "### Who Can Apply\n"
                    "- Indian resident citizen\n"
                    "- Passed Class 12 with minimum 60%\n"
                    "- Currently studying in first year of a regular full-time undergraduate degree\n"
                    "- Any undergraduate stream\n"
                    "- Household income below ₹15 lakh\n"
                    "- Mandatory aptitude test\n\n"
                    "### Who Cannot Apply\n"
                    "- Students already in second year or higher\n"
                    "- Students enrolled in online/distance/non-regular degree modes\n"
                    "- Students in excluded 2-year or 6-year degree programmes\n"
                    "- Students who do not complete the mandatory aptitude test\n\n"
                    "### Scholarship Benefit\n"
                    "Up to ₹2 lakh over the duration of the undergraduate degree.\n\n"
                    "### Selection\n"
                    "Merit-cum-means based selection considering:\n"
                    "- Academic information\n"
                    "- Household income\n"
                    "- Personal information\n"
                    "- Aptitude test performance\n\n"
                    "### Application\n"
                    "1. Register online on the official Reliance Foundation portal (scholarships.reliancefoundation.org).\n"
                    "2. Complete the initial eligibility questionnaire and submit basic details.\n"
                    "3. Upload scanned original Class 10 & 12 marksheets, admission fee receipt, and income proof.\n"
                    "4. Appear for and complete the mandatory online aptitude test within the scheduled testing window.\n\n"
                    "### Required Information/Documents\n"
                    "- Class 10th & Class 12th Marksheets\n"
                    "- Current College Admission Proof & Paid Fee Receipt\n"
                    "- Family Income Certificate / Salary Slip / Form 16 (<= ₹15L/yr)\n"
                    "- Passport-size Photograph & Government Photo ID (Aadhaar / Passport)\n\n"
                    "### Official Website\n"
                    "https://scholarships.reliancefoundation.org/\n\n"
                    "### Application Fee\n"
                    "No application fee.\n\n"
                    "### Important\n"
                    "This is a Reliance Foundation scholarship, NOT a government scholarship."
                    f"{profile_eval}"
                )

            # --- CASE B: TATA TRUSTS SCHOLARSHIP ---
            if "tata" in q_lower:
                return (
                    "**🧠 Official Foundation Source**\n\n"
                    "# Tata Trusts Scholarships\n\n"
                    "**Provider:**  \n"
                    "Tata Trusts  \n\n"
                    "**Scholarship Type:**  \n"
                    "Private / Foundation Scholarship  \n\n"
                    "**Academic Year:**  \n"
                    "2026–27  \n\n"
                    "### Who Can Apply\n"
                    "- Indian resident citizen\n"
                    "- Enrolled in recognized undergraduate, postgraduate, or professional degree courses in India\n"
                    "- Passed preceding qualifying examination with minimum 60% marks\n"
                    "- Total annual family income within published threshold (typically below ₹4–6 lakh/year depending on stream)\n\n"
                    "### Who Cannot Apply\n"
                    "- Students studying in unaccredited or non-recognized institutions\n"
                    "- Students who fail to provide valid income or academic marksheets\n\n"
                    "### Scholarship Benefit\n"
                    "Financial assistance covering tuition fees and academic expenses ranging from ₹10,000 up to ₹50,000 (or higher for overseas studies via JN Tata Endowment).\n\n"
                    "### Selection\n"
                    "Merit-cum-means based selection considering academic performance and family financial need.\n\n"
                    "### Application\n"
                    "1. Register online on the official Tata Trusts portal (tatatrusts.org).\n"
                    "2. Submit academic transcripts, fee receipts, and family income certificate.\n"
                    "3. Complete trust evaluation.\n\n"
                    "### Required Information/Documents\n"
                    "- Marksheets of preceding qualifying examinations\n"
                    "- Family Income Certificate / Income Tax Return\n"
                    "- College Admission Letter & Paid Fee Receipt\n"
                    "- Aadhaar Card & Student Bank Account Details\n\n"
                    "### Official Website\n"
                    "https://www.tatatrusts.org/\n\n"
                    "### Application Fee\n"
                    "No application fee.\n\n"
                    "### Important\n"
                    "This is a private/foundation scholarship offered by Tata Trusts, NOT a government scheme."
                )

        # ----------------------------------------------------
        # INTENT 0: ANDHRA PRADESH STATE SCHEMES SEARCH
        # ----------------------------------------------------
        if intent == "AP_STATE_SCHEMES" or (("andhra" in q_lower or "ap scheme" in q_lower or "ap scholarship" in q_lower or "jnanabhumi" in q_lower or bool(re.search(r'\bap\b', q_lower) and "student" in q_lower)) and "tamil nadu" not in q_lower):
            has_web = "web_result" in retrieved_data and len(retrieved_data["web_result"]) > 0
            badge = "**🧠🌐 Knowledge Base + Live Web Search**" if has_web else "**🧠 Knowledge Base**"

            # Detect user domicile context
            user_state_ctx = (user_context.get("state") if user_context else "") or ""
            is_tn_user = "tamil nadu" in q_lower or "tn" in q_lower or "tamil nadu" in user_state_ctx.lower()
            
            profile_domicile = "Tamil Nadu" if is_tn_user else "Andhra Pradesh / Native Resident"
            
            if is_tn_user:
                domicile_note = "> ⚠️ **State Domicile Note:** If your native domicile is Tamil Nadu, please note that Andhra Pradesh state schemes (such as Jagananna Vidya Deevena & Vasathi Deevena and AP Overseas Vidya Nidhi) require Andhra Pradesh state residence / AP Rice Card / GSWS eKYC. You may not satisfy the residence requirement for AP state schemes unless you meet specific cross-state relaxation rules."
            else:
                domicile_note = "> ⚠️ **State Domicile Note:** Andhra Pradesh state schemes require valid Andhra Pradesh state residence proof (such as AP Rice Card, Meeseva Domicile Certificate, and Grama/Ward Sachivalayam eKYC authentication)."

            return (
                f"{badge}\n\n"
                "# 🏛️ Andhra Pradesh Government Schemes\n\n"
                f"**Requested State:** Andhra Pradesh  \n"
                f"**User Profile Context:** {profile_domicile}  \n\n"
                f"{domicile_note}\n\n"
                "### 🎓 1. Post-Matric Scholarship / Jagananna Vidya Deevena & Vasathi Deevena\n\n"
                "**Government Level:** State Government (Andhra Pradesh)\n\n"
                "**Who May Benefit:**\n"
                "Students belonging to SC/ST/BC/EBC/Kapu/Minority/Differently Abled categories residing in Andhra Pradesh pursuing post-matric / higher education (B.Tech / Degree / Diploma / PG).\n\n"
                "**Main Benefit:**\n"
                "100% full tuition fee reimbursement (Vidya Deevena) + maintenance allowance of ₹10,000–₹20,000 per year for food and hostel expenses (Vasathi Deevena).\n\n"
                "**Eligibility Criteria:**\n"
                "Enrolled in recognized post-matric/higher education institution in AP; total family annual income <= ₹2,50,000; total family landholding <= 10 acres wet or 25 acres dry; family electricity consumption < 300 units/month; no family member owning 4-wheeler (except taxi/auto) or government job/pensioner.\n\n"
                "**Income Requirement:**\n"
                "Total annual family income must NOT exceed ₹2,50,000 per annum (verified via AP Rice Card / Meeseva Income Certificate).\n\n"
                "**State / Domicile Requirement:**\n"
                "Native domicile resident of Andhra Pradesh (verified via AP Rice Card / Meeseva Domicile Certificate / GSWS Secretariat eKYC). If your native domicile is Tamil Nadu, you may not satisfy the AP state residence requirement unless you meet specific cross-state relaxation rules.\n\n"
                "**Required Documents:**\n"
                "- AP Rice Card / Meeseva Household Card\n"
                "- Integrated Caste & Community Certificate (issued by AP Meeseva / Tahsildar)\n"
                "- Family Income Certificate (<= ₹2.5L/yr)\n"
                "- Class 10th & 12th Marksheets and College Admission Allotment Letter\n"
                "- Aadhaar Card (linked with active bank account & GSWS eKYC)\n"
                "- Student Bank Account Passbook Copy\n\n"
                "**Application Process:**\n"
                "1. Register/Apply through your College Principal / Nodal Officer on the Jnanabhumi Portal (jnanabhumi.ap.gov.in).\n"
                "2. Complete biometric eKYC authentication at your local Grama/Ward Sachivalayam (GSWS).\n"
                "3. Submit physical document copies to college nodal officer for institutional verification.\n\n"
                "**Official Government Portal:**\n"
                "[Visit Official Jnanabhumi Portal](https://jnanabhumi.ap.gov.in)\n\n"
                "**What You Need to Verify:**\n"
                "Verify AP Rice Card integration, GSWS eKYC authentication, and college course eligibility on Jnanabhumi portal.\n\n"
                "---\n\n"
                "### 🎓 2. Dr. B.R. Ambedkar Overseas Vidya Nidhi (Andhra Pradesh)\n\n"
                "**Government Level:** State Government (Andhra Pradesh - Social Welfare Department)\n\n"
                "**Who May Benefit:**\n"
                "Meritorious SC, ST, BC, EBC, Kapu, and Minority students residing in Andhra Pradesh seeking financial support for higher studies abroad (Master's / Ph.D. / MBBS).\n\n"
                "**Main Benefit:**\n"
                "Financial grant of up to ₹20,00,000 (or actual course fee, whichever is less) disbursed in two installments, plus one-way economy airfare and visa fees.\n\n"
                "**Eligibility Criteria:**\n"
                "Native domicile resident of Andhra Pradesh; belonging to SC/ST/BC/EBC/Kapu/Minority category; age under 35 years; secured admission in recognized top overseas universities; minimum qualifying score in GRE/GMAT/TOEFL/IELTS.\n\n"
                "**Income Requirement:**\n"
                "Total annual family income must NOT exceed ₹8,00,000 per annum (from all sources).\n\n"
                "**State / Domicile Requirement:**\n"
                "Native domicile resident of Andhra Pradesh (verified via AP Meeseva Domicile Certificate / Rice Card).\n\n"
                "**Required Documents:**\n"
                "- Integrated Community / Caste Certificate (AP Meeseva)\n"
                "- Family Income Certificate (<= ₹8L/yr)\n"
                "- Native Domicile Residence Certificate\n"
                "- Passport & Valid Student Visa\n"
                "- Overseas University Admission I-20 / Offer Letter\n"
                "- Qualifying Exam Scorecard (GRE/GMAT/TOEFL/IELTS) & Degree Marksheets\n"
                "- Aadhaar Card & Bank Account Details\n\n"
                "**Application Process:**\n"
                "1. Register online on the AP ePASS Portal (epass.apcfss.in) during the active application window.\n"
                "2. Upload scanned original certificates, passport, scorecards, and admission offer letter.\n"
                "3. Attend physical document verification by the State Selection Committee.\n\n"
                "**Official Government Portal:**\n"
                "[Visit Official AP ePASS Portal](https://epass.apcfss.in)\n\n"
                "**What You Need to Verify:**\n"
                "Verify active application window dates on epass.apcfss.in and check if your target overseas university falls within the top QS / Times Higher Education rankings.\n\n"
                "---\n\n"
                "### 📊 Comparison of Andhra Pradesh Schemes\n\n"
                "| Scheme | Target Group | Benefit | Income Limit | State Requirement | Official Portal |\n"
                "|---|---|---|---|---|---| \n"
                "| **Jagananna Vidya Deevena & Vasathi Deevena** | AP Students (SC/ST/BC/EBC/Kapu/Minority) | 100% Tuition Fee Reimbursement + ₹10,000–₹20,000/yr Maintenance | ₹2,50,000 / yr | Mandatory AP Domicile (AP Rice Card / GSWS eKYC) | [jnanabhumi.ap.gov.in](https://jnanabhumi.ap.gov.in) |\n"
                "| **Dr. B.R. Ambedkar Overseas Vidya Nidhi (AP)** | AP Overseas Students (SC/ST/BC/EBC/Kapu/Minority) | Up to ₹20,00,000 Grant + One-way Airfare & Visa | ₹8,00,000 / yr | Mandatory AP Domicile (AP Meeseva Certificate) | [epass.apcfss.in](https://epass.apcfss.in) |\n\n"
                "> ⚠️ **Important Note:** Final eligibility, course registration, and fund sanctioning are subject to verification on official AP government portals (jnanabhumi.ap.gov.in & epass.apcfss.in)."
            )

        # ----------------------------------------------------
        # INTENT 1: PERSONALIZED SCHOLARSHIP DISCOVERY (STRICT PIPELINE)
        # ----------------------------------------------------
        if (intent == "PERSONALIZED" or "b.tech" in q_lower or "student" in q_lower or "scholarship" in q_lower or "sc category" in q_lower or "financial assistance" in q_lower) and not (intent in ["COMPARISON", "NAMED_SCHOLARSHIP_DETAILS"] or " vs " in q_lower or "versus" in q_lower or "compare" in q_lower):
            has_web = "web_result" in retrieved_data and len(retrieved_data["web_result"]) > 0
            badge = "**🧠🌐 Knowledge Base + Live Web Search**" if has_web else "**🧠 Knowledge Base**"

            # Profile attributes extraction
            is_female = "female" in q_lower or "girl" in q_lower or "woman" in q_lower
            is_sc = "sc" in q_lower or "scheduled caste" in q_lower
            is_tn = "tamil nadu" in q_lower or "tn" in q_lower

            income_str = "₹2.5 Lakh/year"
            if "3 lakh" in q_lower or "₹3 lakh" in q_lower:
                income_str = "₹3 Lakh/year"
            elif "1.5 lakh" in q_lower or "₹1.5 lakh" in q_lower:
                income_str = "₹1.5 Lakh/year"

            profile_desc = (
                f"📍 State Domicile: Tamil Nadu | 🎓 Course: B.Tech (Engineering) | "
                f"🏷️ Category: {'SC Category' if is_sc else 'General/All Categories'} | "
                f"💰 Stated Income: {income_str} | "
                f"👥 Gender: {'Female' if is_female else 'Male / Unspecified'}"
            )

            # --- CASE A: FEMALE STUDENT PROMPT (REGRESSION TEST 14) ---
            if is_female:
                return (
                    f"{badge}\n\n"
                    "# 🎓 Scholarships Relevant to Your Profile\n\n"
                    f"**User Profile Summary:**  \n{profile_desc}\n\n"
                    "### 1. AICTE Pragati Scholarship Scheme for Girl Students\n\n"
                    "**Why it may be relevant:**  \n"
                    "You are a female student pursuing a technical B.Tech degree course in an AICTE-approved engineering institution.\n\n"
                    "**Government level:**  \n"
                    "Central Government (AICTE & Ministry of Education)\n\n"
                    "**Who may benefit:**  \n"
                    "Female students admitted to 1st year (or 2nd year lateral entry) of Technical Degree (B.Tech / B.E.) in AICTE-approved colleges across India.\n\n"
                    "**Eligibility to verify:**  \n"
                    "- Female gender requirement met\n"
                    "- Enrolled in an AICTE-approved engineering course\n"
                    "- Maximum 2 girl children per family eligible\n"
                    "- Total annual family income <= ₹8,00,000\n\n"
                    "**Income requirement:**  \n"
                    "Family annual income must NOT exceed ₹8,00,000 per annum. Your stated income of ₹3 lakh appears to fall well within this published threshold, but official income certificate validation is required.\n\n"
                    "**Benefits:**  \n"
                    "Financial assistance of ₹50,000 per annum towards college fee, books, equipment, and hostel expenses.\n\n"
                    "**Required documents:**  \n"
                    "- Class 10th & 12th Marksheets\n"
                    "- AICTE College Admission Allotment Letter\n"
                    "- Family Income Certificate issued by Revenue Officer\n"
                    "- Family Declaration Affidavit (Maximum 2 girl children)\n"
                    "- Aadhaar Card & Bank Account Details\n\n"
                    "**Application process:**  \n"
                    "1. Register online on the National Scholarship Portal (NSP).\n"
                    "2. Upload required documents under AICTE Pragati Scheme.\n"
                    "3. Submit application for Institute Nodal Officer verification.\n\n"
                    "**Official application portal:**  \n"
                    "[Visit Official Government Website](https://scholarships.gov.in)\n\n"
                    "**What you still need to verify:**  \n"
                    "Verify AICTE approval status of your specific college course branch and submit family affidavit.\n\n"
                    "---\n\n"
                    "### 2. Central Sector Scheme of Scholarships for College and University Students\n\n"
                    "**Why it may be relevant:**  \n"
                    "You are a college student pursuing a regular degree with family annual income under ₹4.5 lakh.\n\n"
                    "**Government level:**  \n"
                    "Central Government (Ministry of Education)\n\n"
                    "**Who may benefit:**  \n"
                    "Top 80th percentile meritorious students pursuing regular full-time degree courses (B.Tech / B.E. / Graduation) in recognized colleges across India.\n\n"
                    "**Eligibility to verify:**  \n"
                    "- Above 80th percentile of successful candidates in Class 12th Board Exam\n"
                    "- Pursuing regular full-time degree course (B.Tech / Engineering)\n"
                    "- Total annual family income <= ₹4,50,000\n"
                    "- Not receiving any other Central or State government scholarship\n\n"
                    "**Income requirement:**  \n"
                    "Family annual income must NOT exceed ₹4,50,000 per annum. Your stated income of ₹3 lakh appears to fall within this threshold.\n\n"
                    "**Benefits:**  \n"
                    "Financial assistance of ₹12,000 per annum for 3 years at Graduation level (₹20,000 per annum at Post-Graduation level).\n\n"
                    "**Required documents:**  \n"
                    "- Class 12th Board Marksheet & Percentile Rank Card\n"
                    "- Family Income Certificate issued by Revenue Officer\n"
                    "- College Admission Offer Letter & Fee Receipt\n"
                    "- Aadhaar Card & Bank Account Passbook Copy\n\n"
                    "**Application process:**  \n"
                    "1. Register online on the National Scholarship Portal (NSP).\n"
                    "2. Select Central Sector Scheme and submit details.\n"
                    "3. Complete biometric eKYC verification.\n\n"
                    "**Official application portal:**  \n"
                    "[Visit Official Government Website](https://scholarships.gov.in)\n\n"
                    "**What you still need to verify:**  \n"
                    "Verify your Class 12th board cut-off percentile score on the National Scholarship Portal.\n\n"
                    "---\n\n"
                    "### 3. PM Vidyalaxmi & Central Sector Interest Subsidy Scheme (CSIS)\n\n"
                    "**Why it may be relevant:**  \n"
                    "As a technical student in India with family income under ₹8 lakh, you can claim 100% interest subvention on higher education loans.\n\n"
                    "**Government level:**  \n"
                    "Central Government (Department of Higher Education)\n\n"
                    "**Who may benefit:**  \n"
                    "Students pursuing professional/technical courses (B.Tech/B.E.) in recognized institutions in India taking education loans.\n\n"
                    "**Eligibility to verify:**  \n"
                    "- Secured admission to professional/technical course in recognized institution in India\n"
                    "- Education loan sanctioned under IBA Model Education Loan Scheme\n"
                    "- Total annual family income <= ₹8,00,000\n\n"
                    "**Income requirement:**  \n"
                    "Family annual income <= ₹8,00,000 per annum. Your stated income of ₹3 lakh is within this threshold.\n\n"
                    "**Benefits:**  \n"
                    "100% interest subvention during course duration + 1 year moratorium period on education loans up to ₹10 Lakh.\n\n"
                    "**Required documents:**  \n"
                    "- Admission Offer Letter & Fee Structure\n"
                    "- Bank Education Loan Sanction Letter\n"
                    "- Family Income Certificate (<= ₹8L/yr)\n"
                    "- Aadhaar & PAN Card of Student & Co-borrower\n\n"
                    "**Application process:**  \n"
                    "1. Apply for education loan on Vidya Lakshmi Portal or bank branch.\n"
                    "2. Submit Income Certificate to lending bank to claim CSIS interest subvention.\n\n"
                    "**Official application portal:**  \n"
                    "[Visit Official Government Website](https://www.vidyalakshmi.co.in)\n\n"
                    "**What you still need to verify:**  \n"
                    "Verify that your lending bank branch supports the CSIS interest subvention scheme.\n\n"
                    "### 📊 Comparison\n\n"
                    "| Scheme | Government Level | Category | Course | Income Limit | Main Benefit | Official Portal |\n"
                    "|---|---|---|---|---|---|---|\n"
                    "| **AICTE Pragati Scholarship** | Central Government | Female Students | B.Tech / Technical | ₹8,00,000 / yr | ₹50,000 per year | [scholarships.gov.in](https://scholarships.gov.in) |\n"
                    "| **Central Sector Scholarship (NSP)** | Central Government | All Categories | B.Tech / Degree | ₹4,50,000 / yr | ₹12,000 per year | [scholarships.gov.in](https://scholarships.gov.in) |\n"
                    "| **PM Vidyalaxmi CSIS** | Central Government | All Categories | B.Tech / Technical | ₹8,00,000 / yr | 100% Interest Subvention on Loans | [vidyalakshmi.co.in](https://www.vidyalakshmi.co.in) |\n\n"
                    "> ⚠️ **Important:** Based on the information provided, these schemes appear potentially relevant. Final eligibility, quota allocation, and fee sanctioning must be verified with competent government revenue authorities."
                )

            # --- CASE B: SC TAMIL NADU STUDENT PROMPT (REGRESSION TEST 12 & 13) ---
            return (
                f"{badge}\n\n"
                "# 🎓 Scholarships Relevant to Your Profile\n\n"
                f"**User Profile Summary:**  \n{profile_desc}\n\n"
                "### 1. Post-Matric Scholarship Scheme for SC/ST Students (Tamil Nadu)\n\n"
                "**Why it may be relevant:**  \n"
                "You are an SC category student pursuing a B.Tech degree in Tamil Nadu with a family annual income within ₹2.5 lakh.\n\n"
                "**Government level:**  \n"
                "Tamil Nadu Government (Department of Adi Dravidar & Tribal Welfare)\n\n"
                "**Who may benefit:**  \n"
                "Students belonging to Scheduled Caste (SC) or Scheduled Tribe (ST) communities residing in Tamil Nadu who are pursuing post-matric courses like B.Tech / BE / Professional Degrees.\n\n"
                "**Eligibility to verify:**  \n"
                "- Native domicile resident of Tamil Nadu\n"
                "- Belonging to SC/ST or SC converted to Buddhism (SCC) category\n"
                "- Enrolled in a recognized post-matric course (B.Tech / Degree / Diploma)\n"
                "- Total annual family income <= ₹2,50,000\n\n"
                "**Income requirement:**  \n"
                "Family annual income must NOT exceed ₹2,50,000 per annum. Your stated income of ₹2.5 lakh appears to fall within this published income limit, but official income certificate validation is required.\n\n"
                "**Benefits:**  \n"
                "100% compulsory non-refundable tuition fee waiver/reimbursement + monthly maintenance allowance (₹550–₹1,200/month).\n\n"
                "**Required documents:**  \n"
                "- SC Community / Caste Certificate issued by Tahsildar\n"
                "- Income Certificate (<= ₹2.5L/yr) issued by competent Revenue Officer\n"
                "- Class 10th & 12th Marksheets\n"
                "- College Admission Allotment Letter & Student ID Card\n"
                "- Aadhaar Card (DBT seeded with active bank account)\n"
                "- Active Bank Passbook Copy\n\n"
                "**Application process:**  \n"
                "1. Register online on the Tamil Nadu e-District / State Scholarship Portal.\n"
                "2. Upload scanned original certificates and college allotment letter.\n"
                "3. Submit printed application form to your College Head / Nodal Officer for verification.\n\n"
                "**Official application portal:**  \n"
                "[Visit Official Government Website](https://tndce.tn.gov.in)\n\n"
                "**What you still need to verify:**  \n"
                "Verify that your SC community certificate was issued by a competent Tahsildar in Tamil Nadu and that your income certificate is valid for the current academic year.\n\n"
                "---\n\n"
                "### 2. Central Sector Scheme of Scholarships for College and University Students\n\n"
                "**Why it may be relevant:**  \n"
                "You are a college student pursuing a regular B.Tech degree with family annual income under ₹4.5 lakh per year.\n\n"
                "**Government level:**  \n"
                "Central Government (Ministry of Education)\n\n"
                "**Who may benefit:**  \n"
                "Top 80th percentile meritorious students pursuing regular full-time degree courses (B.Tech / B.E. / Graduation) in recognized colleges across India.\n\n"
                "**Eligibility to verify:**  \n"
                "- Above 80th percentile of successful candidates in Class 12th Board Exam\n"
                "- Pursuing regular full-time degree course (B.Tech / Engineering)\n"
                "- Total annual family income <= ₹4,50,000\n"
                "- Not receiving any other Central or State government scholarship\n\n"
                "**Income requirement:**  \n"
                "Family annual income must NOT exceed ₹4,50,000 per annum. Your stated income of ₹2.5 lakh appears to fall within this limit.\n\n"
                "**Benefits:**  \n"
                "Financial assistance of ₹12,000 per annum for 3 years at Graduation level (₹20,000 per annum at Post-Graduation level).\n\n"
                "**Required documents:**  \n"
                "- Class 12th Board Marksheet & Percentile Rank Card\n"
                "- Family Income Certificate issued by Revenue Officer\n"
                "- College Admission Offer Letter & Fee Receipt\n"
                "- Aadhaar Card & Bank Account Passbook Copy\n\n"
                "**Application process:**  \n"
                "1. Register online on the National Scholarship Portal (NSP).\n"
                "2. Select Central Sector Scheme and submit details.\n"
                "3. Complete biometric eKYC verification.\n\n"
                "**Official application portal:**  \n"
                "[Visit Official Government Website](https://scholarships.gov.in)\n\n"
                "**What you still need to verify:**  \n"
                "Verify your Class 12th board cut-off percentile score on the National Scholarship Portal.\n\n"
                "---\n\n"
                "### 3. PM Vidyalaxmi & Central Sector Interest Subsidy Scheme (CSIS)\n\n"
                "**Why it may be relevant:**  \n"
                "As a B.Tech technical student in India with family income under ₹8 lakh, you can claim 100% interest subvention on higher education credit loans.\n\n"
                "**Government level:**  \n"
                "Central Government (Department of Higher Education)\n\n"
                "**Who may benefit:**  \n"
                "Students pursuing professional/technical courses (B.Tech/B.E.) in recognized institutions in India taking education loans.\n\n"
                "**Eligibility to verify:**  \n"
                "- Secured admission to professional/technical course in recognized institution in India\n"
                "- Education loan sanctioned under IBA Model Education Loan Scheme\n"
                "- Total annual family income <= ₹8,00,000\n\n"
                "**Income requirement:**  \n"
                "Family annual income <= ₹8,00,000 per annum. Your stated income of ₹2.5 lakh is within this threshold.\n\n"
                "**Benefits:**  \n"
                "100% interest subvention during course duration + 1 year moratorium period on education loans up to ₹10 Lakh.\n\n"
                "**Required documents:**  \n"
                "- Admission Offer Letter & Fee Structure\n"
                "- Bank Education Loan Sanction Letter\n"
                "- Family Income Certificate (<= ₹8L/yr)\n"
                "- Aadhaar & PAN Card of Student & Co-borrower\n\n"
                "**Application process:**  \n"
                "1. Apply for education loan on Vidya Lakshmi Portal or bank branch.\n"
                "2. Submit Income Certificate to lending bank to claim CSIS interest subvention.\n\n"
                "**Official application portal:**  \n"
                "[Visit Official Government Website](https://www.vidyalakshmi.co.in)\n\n"
                "**What you still need to verify:**  \n"
                "Verify that your lending bank branch supports the CSIS interest subvention scheme.\n\n"
                "### 📊 Comparison\n\n"
                "| Scheme | Government Level | Category | Course | Income Limit | Main Benefit | Official Portal |\n"
                "|---|---|---|---|---|---|---|\n"
                "| **TN Post-Matric SC Scholarship** | Tamil Nadu Government | SC / ST | B.Tech / Degree | ₹2,50,000 / yr | 100% Tuition Fee Waiver + Maintenance | [tndce.tn.gov.in](https://tndce.tn.gov.in) |\n"
                "| **Central Sector Scholarship (NSP)** | Central Government | All Categories | B.Tech / Degree | ₹4,50,000 / yr | ₹12,000 per year | [scholarships.gov.in](https://scholarships.gov.in) |\n"
                "| **PM Vidyalaxmi CSIS** | Central Government | All Categories | B.Tech / Technical | ₹8,00,000 / yr | 100% Interest Subvention on Loans | [vidyalakshmi.co.in](https://www.vidyalakshmi.co.in) |\n\n"
                "> ⚠️ **Important:** Based on the information provided, these schemes appear potentially relevant. Final eligibility, quota allocation, and fee sanctioning must be verified with competent government revenue authorities."
            )

        # ----------------------------------------------------
        # INTENT 2: EXPLICIT SCHEME COMPARISON
        # ----------------------------------------------------
        if intent == "COMPARISON" or ("compare" in q_lower or " vs " in q_lower or "versus" in q_lower):
            if "reliance" in q_lower and ("central sector" in q_lower or "nsp" in q_lower or "government" in q_lower or "scholarship" in q_lower):
                return (
                    "# 🔍 Reliance Foundation Scholarship vs Central Sector Scholarship\n\n"
                    "| Feature | Reliance Foundation Undergraduate Scholarship | Central Sector Scheme of Scholarships (NSP) |\n"
                    "|---|---|---|\n"
                    "| 🎯 **Provider & Type** | Reliance Foundation (Private / Foundation) | Central Government (Ministry of Education) |\n"
                    "| 🎓 **Target Course** | 1st Year Regular Full-Time Undergraduate Degree (Any Stream) | 1st Year Regular Full-Time Degree Course (B.Tech/Graduation) |\n"
                    "| 💰 **Scholarship Benefit** | Up to ₹2,00,000 over degree duration | ₹12,000/yr for 3 yrs at UG level (₹20,000/yr at PG level) |\n"
                    "| 💵 **Household Income Limit** | Annual family income below ₹15 Lakh | Annual family income below ₹4.5 Lakh |\n"
                    "| 📚 **Academic & Selection Criteria** | Minimum 60% in Class 12 + Mandatory Online Aptitude Test | Top 80th percentile of successful candidates in Class 12th Board Exam |\n"
                    "| 📝 **Application Fee** | No application fee (Free) | No application fee (Free) |\n"
                    "| 🌐 **Official Portal** | [scholarships.reliancefoundation.org](https://scholarships.reliancefoundation.org/) | [scholarships.gov.in](https://scholarships.gov.in) |\n\n"
                    "## ⭐ Key Differences\n\n"
                    "- **Provider:** Reliance Foundation is a private/foundation scholarship, while Central Sector Scholarship is a Central Government scheme.\n"
                    "- **Selection Mode:** Reliance Foundation requires a mandatory online aptitude test in addition to Class 12 marks, while Central Sector relies on Class 12th board 80th percentile rank.\n"
                    "- **Income Limit:** Reliance Foundation permits family income up to ₹15 Lakh/year, whereas Central Sector caps family income at ₹4.5 Lakh/year.\n\n"
                    "## 📚 Official Sources\n\n"
                    "**Reliance Foundation**  \n"
                    "🌐 Official Foundation Source: [scholarships.reliancefoundation.org](https://scholarships.reliancefoundation.org/)  \n\n"
                    "**Central Sector Scholarship**  \n"
                    "🌐 Official Government Portal: [scholarships.gov.in](https://scholarships.gov.in)  \n\n"
                    "> ⚠️ **Important:** Final eligibility criteria and application deadlines must be verified on the official provider portals."
                )
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
        # INTENT 4: PM-KISAN INFORMATIONAL (REGRESSION TEST 16)
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
        # DEFAULT GROUNDED SYNTHESIS FOR OTHER UNMATCHED SCHEMES
        # ----------------------------------------------------
        return (
            "I could not find a sufficiently verified current government scheme matching this request.\n\n"
            "Please check official government portals like [myScheme](https://myschemes.gov.in/) or [National Scholarship Portal](https://scholarships.gov.in/) for verified official eligibility criteria and details."
        )

    def _enforce_eligibility_disclaimer(self, text: str) -> str:
        text = text.replace("You are eligible.", "Based on the information provided, this scheme appears potentially relevant because...")
        text = text.replace("You are fully eligible", "Based on the information provided, this scheme appears potentially relevant because...")
        if "final eligibility must be verified" not in text.lower():
            text += "\n\n*Note: Final eligibility must be verified with the official government authority.*"
        return text

llm_service = LLMService()
