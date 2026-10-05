import os
import glob
import logging
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import Scheme, DocumentModel
from app.services.rag_engine import rag_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_data")

SEED_SCHEMES = [
    {
        "scheme_code": "TN-HE-PMS-2024",
        "name": "Post-Matric Scholarship for SC/ST/SCC Students (Tamil Nadu)",
        "ministry_or_department": "Department of Adi Dravidar and Tribal Welfare, Govt of Tamil Nadu",
        "category": "Education & Scholarships",
        "state": "Tamil Nadu",
        "summary": "100% tuition fee waiver and monthly maintenance allowance for SC, ST, and SCC students pursuing higher education degree and diploma courses in Tamil Nadu.",
        "eligibility_criteria": "- Domicile of Tamil Nadu belonging to SC, ST, or SC Converted to Buddhism (SCC).\n- Annual Family Income <= ₹2,50,000.\n- Pursuing post-matric courses (Class 11, Class 12, ITI, Diploma, BE/BTech, MBBS, BA/BSc, MA/MSc, PhD).\n- Minimum 75% class attendance.",
        "benefits": "100% Tuition Fee Waiver for government and self-financing quota seats + Monthly Maintenance Allowance of ₹740 to ₹1,200/month for hostellers and ₹380 to ₹550/month for day scholars.",
        "income_limit": 250000.0,
        "required_documents": "- Community Certificate (Tahsildar issued)\n- Income Certificate (Issued within last 12 months)\n- Mark Sheets (10th/12th/Semester)\n- Aadhaar Card (Active & DBTL seeded)\n- Bank Passbook Copy (showing Account No & IFSC)\n- College Admission Fee Receipt & Bonafide Certificate\n- Passport Size Photo",
        "application_process": "1. Apply online on Tamil Nadu State Scholarship Portal (TNPASS).\n2. Submit printed application copy to College Nodal Officer.\n3. Institutional verification followed by District Welfare Officer sanction directly to DBTL account.",
        "official_portal_url": "https://tnpass.tn.gov.in"
    },
    {
        "scheme_code": "GOI-AGRI-PMKISAN-2024",
        "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "ministry_or_department": "Ministry of Agriculture & Farmers Welfare, Govt of India",
        "category": "Agriculture & Farmer Welfare",
        "state": "All India",
        "summary": "Direct financial support of ₹6,000 per year paid in three equal installments to eligible landholding farmer families across India.",
        "eligibility_criteria": "- All landholding farmer families owning cultivable land up to 2 hectares (5 acres) in land revenue records.\n- Excludes institutional landholders, high-income taxpayers, pensioners receiving >= ₹10,000/month, and constitutional post holders.",
        "benefits": "₹6,000 per year transferred directly into Aadhaar-seeded bank accounts in 3 equal quarterly installments of ₹2,000.",
        "income_limit": None,
        "required_documents": "- Land ownership document (Khasra / Khatauni / RoR / Patta)\n- Aadhaar Card (Mandatory eKYC)\n- Active Bank Passbook (Aadhaar linked for DBT)\n- Mobile Number linked with Aadhaar",
        "application_process": "1. Register online via Farmers Corner on pmkisan.gov.in or PM-KISAN App.\n2. Complete mandatory eKYC (OTP or face auth).\n3. State Nodal Officer approval and PFMS verification.",
        "official_portal_url": "https://pmkisan.gov.in"
    },
    {
        "scheme_code": "GOI-HOUS-PMAY-2024",
        "name": "Pradhan Mantri Awas Yojana (PMAY - Housing for All)",
        "ministry_or_department": "Ministry of Housing and Urban Affairs, Govt of India",
        "category": "Housing & Urban Development",
        "state": "All India",
        "summary": "Financial support and interest subsidy up to ₹2.67 Lakh for constructing or purchasing a pucca house for EWS and LIG families.",
        "eligibility_criteria": "- Beneficiary family must NOT own a pucca house anywhere in India.\n- EWS Income Limit <= ₹3,00,000/year.\n- LIG Income Limit ₹3,00,001 to ₹6,00,000/year.\n- Female ownership mandatory for EWS/LIG households.",
        "benefits": "Credit Linked Subsidy (CLSS) interest subsidy up to ₹2.67 Lakh on home loan + Direct financial assistance of ₹1.20 Lakh to ₹1.50 Lakh for house construction.",
        "income_limit": 600000.0,
        "required_documents": "- Income Certificate / Salary Slip / Revenue Officer certificate\n- Aadhaar Cards of all family members\n- Affidavit of Not Owning Pucca House\n- Land ownership / Site Patta document\n- Bank Account Passbook\n- Approved Construction Plan & Estimate",
        "application_process": "1. Apply online via pmaymis.gov.in or visit nearest Common Service Center (CSC).\n2. For home loan subsidy, apply directly through participating banks/HFCs.\n3. Geo-tagging verification by local body inspectors.",
        "official_portal_url": "https://pmaymis.gov.in"
    },
    {
        "scheme_code": "GOI-HLTH-PMJAY-2024",
        "name": "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (PM-JAY)",
        "ministry_or_department": "National Health Authority (NHA), Ministry of Health & Family Welfare",
        "category": "Healthcare & Insurance",
        "state": "All India",
        "summary": "Cashless health insurance cover of up to ₹5,00,000 per family per year for secondary and tertiary hospitalization across empanelled hospitals.",
        "eligibility_criteria": "- Families listed in SECC 2011 database (rural deprived & urban occupational categories).\n- All senior citizens aged 70 years and above (Ayushman Vaya Vandana Card).\n- No restriction on family size or age.",
        "benefits": "Cashless health cover up to ₹5,00,000 per family per year covering over 1,900 medical procedures, diagnostics, and 15-day post-hospitalization costs.",
        "income_limit": None,
        "required_documents": "- Aadhaar Card (eKYC verification)\n- Ration Card / Family ID / SECC HHID Letter\n- Ayushman Golden Card",
        "application_process": "1. Check eligibility on beneficiary.nha.gov.in.\n2. Complete eKYC at any Empanelled Hospital (Ayushman Mitradesk) or CSC.\n3. Instant Ayushman Card generation.",
        "official_portal_url": "https://beneficiary.nha.gov.in"
    },
    {
        "scheme_code": "GOI-EDU-NMMSS-2024",
        "name": "National Means-cum-Merit Scholarship Scheme (NMMSS)",
        "ministry_or_department": "Department of School Education & Literacy, Ministry of Education",
        "category": "School Education & Scholarships",
        "state": "All India",
        "summary": "Scholarship of ₹12,000 per year for meritorious Class 8 students from economically weaker sections to continue secondary school education.",
        "eligibility_criteria": "- Class 8 student studying in Govt / Govt-aided / Local Body school.\n- Minimum 55% marks in Class 7 exam (50% for SC/ST).\n- Parental annual income <= ₹3,50,000.",
        "benefits": "Scholarship of ₹12,000 per annum (₹1,000/month) for 4 years from Class 9 to Class 12.",
        "income_limit": 350000.0,
        "required_documents": "- Income Certificate of parents\n- Class 7 Mark Sheet\n- Caste Certificate (SC/ST/OBC if applicable)\n- Aadhaar Card of student\n- Bank Account Passbook",
        "application_process": "1. Clear State Level NMMSS Selection Exam (MAT & SAT).\n2. Register online on National Scholarship Portal (scholarships.gov.in).\n3. Verification by School Nodal Officer.",
        "official_portal_url": "https://scholarships.gov.in"
    },
    {
        "scheme_code": "GUJ-EDU-MYSY-2024",
        "name": "Mukhyamantri Yuva Swavalamban Yojana (MYSY - Gujarat)",
        "ministry_or_department": "Education Department, Government of Gujarat",
        "category": "Higher Education & State Scholarship",
        "state": "Gujarat",
        "summary": "Financial assistance covering 50% tuition fees, hostel allowances, and book stipends for bright students in Gujarat pursuing higher education.",
        "eligibility_criteria": "- Resident of Gujarat.\n- Secured 80+ percentile in 10th or 12th Board Exam.\n- Annual family income <= ₹6,00,000.",
        "benefits": "50% Tuition Fee Subsidy up to ₹2 Lakh for Medical/Dental, ₹50,000 for Engineering/Pharmacy + ₹12,000/year Hostel Stipend + ₹5,000 Book Allowance.",
        "income_limit": 600000.0,
        "required_documents": "- 10th and 12th Mark Sheets\n- Admission Letter & Fee Receipts\n- Income Certificate from Mamlatdar\n- Domicile Certificate of Gujarat\n- Aadhaar Card & Bank Passbook",
        "application_process": "1. Register online on mysy.guj.nic.in.\n2. Document verification at designated Help Centers (Govt Colleges).\n3. Direct bank transfer sanction.",
        "official_portal_url": "https://mysy.guj.nic.in"
    },
    {
        "scheme_code": "GOI-FIN-STANDUP-2024",
        "name": "Stand Up India Scheme for SC/ST and Women Entrepreneurs",
        "ministry_or_department": "Department of Financial Services, Ministry of Finance / SIDBI",
        "category": "Entrepreneurship & Business Credit",
        "state": "All India",
        "summary": "Bank loans between ₹10 Lakh and ₹1 Crore for SC, ST, and Women entrepreneurs to establish new greenfield business enterprises.",
        "eligibility_criteria": "- SC/ST and/or Woman entrepreneur above 18 years.\n- Setting up a Greenfield Enterprise in manufacturing, trading, or services.\n- Must hold at least 51% controlling stake in non-individual entities.",
        "benefits": "Bank loans from ₹10 Lakh to ₹1 Crore at lowest commercial bank interest rates + 7-year repayment tenure with 18-month moratorium + CGFSIL collateral guarantee.",
        "income_limit": None,
        "required_documents": "- Identity & Address Proof (Aadhaar/PAN/Voter ID)\n- SC/ST Caste Certificate (if applicable)\n- Business Plan / Detailed Project Report\n- MSME Udyam & GST Registration\n- 6 Months Bank Statements\n- Rent/Lease Deed for business location",
        "application_process": "1. Apply online via Stand Up Mitra portal (standupmitra.in) or bank branch.\n2. Hand-holding support by SIDBI, NABARD, and DIC.\n3. Credit appraisal and sanction by Lead District Manager bank branch.",
        "official_portal_url": "https://www.standupmitra.in"
    },
    {
        "scheme_code": "CORP-EDU-AIRTEL-2024",
        "name": "Bharti Airtel Scholarship Scheme (Bharti Airtel Foundation)",
        "ministry_or_department": "Bharti Airtel Foundation / Bharti Enterprises",
        "category": "Education & Scholarships",
        "state": "All India",
        "summary": "100% merit-cum-means scholarship for underprivileged students, with focus on girl students, pursuing technology & engineering degrees in top recognized tech institutes.",
        "eligibility_criteria": "- Pursuing first-year B.Tech/B.E. in Technology, Computer Science, AI, Data Science, or Telecom in top institutes (IITs, NITs, top tech colleges).\n- Total annual family income <= ₹6,00,000.\n- Preference given to female students and SC/ST/PwD applicants.",
        "benefits": "100% tuition fee waiver paid directly to college + Hostel/mess allowance + One-time laptop grant + Mentorship by Bharti Airtel executives.",
        "income_limit": 600000.0,
        "required_documents": "- JEE Advanced / JEE Main Rank Card & Allotment Letter\n- Family Income Certificate / Form 16\n- Class 10 & 12 Mark Sheets\n- Aadhaar Card & Student Bank Passbook",
        "application_process": "1. Register online on Bharti Airtel Foundation Scholarship Portal (bhartifoundation.org).\n2. Upload documents and pass online panel interview.\n3. Scholarship disbursed directly to college and student DBTL account.",
        "official_portal_url": "https://bhartifoundation.org"
    },
    {
        "scheme_code": "GOI-ENRG-SURYAGHAR-2024",
        "name": "PM Surya Ghar: Muft Bijli Yojana",
        "ministry_or_department": "Ministry of New and Renewable Energy (MNRE), Govt of India",
        "category": "Clean Energy & Rooftop Solar Subsidies",
        "state": "All India",
        "summary": "Free solar electricity up to 300 units per month for households across India with direct financial subsidy up to ₹78,000 for rooftop solar installations.",
        "eligibility_criteria": "- Resident household in India with a suitable roof for solar panel installation.\n- Electricity connection in applicant's name.\n- Subsidy Tiers: ₹30,000 for 1 kW system; ₹60,000 for 2 kW system; ₹78,000 max subsidy for 3 kW+ system.",
        "benefits": "Free electricity up to 300 units/month + Central financial assistance subsidy up to ₹78,000 credited directly into bank account.",
        "income_limit": None,
        "required_documents": "- Recent Electricity Bill\n- Aadhaar Card\n- Bank Account Passbook (Aadhaar seeded)\n- Roof Ownership / Residence Proof",
        "application_process": "1. Apply online at pmsuryaghar.gov.in.\n2. Feasibility approval by DISCOM.\n3. Installation by registered vendor & net meter inspection.",
        "official_portal_url": "https://pmsuryaghar.gov.in"
    },
    {
        "scheme_code": "GOI-MSME-VISHWAKARMA-2024",
        "name": "PM Vishwakarma Scheme",
        "ministry_or_department": "Ministry of Micro, Small & Medium Enterprises (MSME), Govt of India",
        "category": "Artisans & Traditional Craftsmen",
        "state": "All India",
        "summary": "Comprehensive support for traditional artisans and craftspeople across 18 trades, including collateral-free loans up to ₹3 Lakh at 5% interest, ₹15,000 toolkit incentive, and stipend during skill training.",
        "eligibility_criteria": "- Artisan/Craftsperson working with hands and tools in one of 18 traditional trades (e.g. Carpenter, Blacksmith, Goldsmith, Potter, Weaver, Tailor, Cobbler, Mason, Sculptor, Barber, Washerman, etc.).\n- Minimum age 18 years.",
        "benefits": "Collateral-free enterprise loan up to ₹3 Lakh (₹1 Lakh 1st tranche + ₹2 Lakh 2nd tranche) at 5% interest + ₹15,000 e-voucher for toolkit + ₹500/day skill training stipend.",
        "income_limit": None,
        "required_documents": "- Aadhaar Card\n- Active Mobile Number linked with Aadhaar\n- Bank Passbook Copy\n- Skill / Trade Proof",
        "application_process": "1. Register at CSC or pmvishwakarma.gov.in.\n2. Three-tier verification (Gram Panchayat/ULB, District Implementation Committee, Screening Committee).\n3. PM Vishwakarma Digital ID Card issued.",
        "official_portal_url": "https://pmvishwakarma.gov.in"
    },
    {
        "scheme_code": "GOI-FIN-SUKANYA-2024",
        "name": "Sukanya Samriddhi Yojana (SSY)",
        "ministry_or_department": "Ministry of Finance / Department of Posts, Govt of India",
        "category": "Girl Child & Small Savings",
        "state": "All India",
        "summary": "High-interest government savings scheme for girl children offering 8.2% p.a. interest rate with triple tax exemptions (EEE status under Section 80C).",
        "eligibility_criteria": "- Account opened by parent/legal guardian for a girl child under 10 years of age.\n- Maximum 2 accounts per family (except in case of twins/triplets).\n- Deposit Limit: Minimum ₹250 to Maximum ₹1.5 Lakh per financial year.",
        "benefits": "8.2% p.a. compounding interest + Tax deduction under Sec 80C + 50% partial withdrawal for higher education after age 18 + Full maturity at 21 years.",
        "income_limit": None,
        "required_documents": "- Birth Certificate of Girl Child\n- Identity & Address Proof of Parent/Guardian (Aadhaar/PAN Card)\n- Passport Size Photographs",
        "application_process": "1. Visit any Post Office or authorized commercial bank branch.\n2. Submit account opening form with initial deposit (min ₹250).\n3. Passbook issued for tracking contributions.",
        "official_portal_url": "https://www.indiapost.gov.in"
    },
    {
        "scheme_code": "GOI-FIN-MUDRA-2024",
        "name": "Pradhan Mantri Mudra Yojana (PMMY)",
        "ministry_or_department": "Department of Financial Services, Ministry of Finance, Govt of India",
        "category": "Micro-Business & MSME Credit",
        "state": "All India",
        "summary": "Collateral-free business loans up to ₹10 Lakh for non-corporate, non-farm small/micro enterprises across three categories: Shishu (up to ₹50,000), Kishore (₹50,000 to ₹5 Lakh), and Tarun (₹5 Lakh to ₹10 Lakh).",
        "eligibility_criteria": "- Small business owners, shopkeepers, artisans, fruit/vegetable vendors, small manufacturers, service providers, and startup entrepreneurs.",
        "benefits": "Collateral-free loans up to ₹10 Lakh + Mudra Debit Card for working capital drawdown + Low interest rates.",
        "income_limit": None,
        "required_documents": "- Identity & Address Proof (Aadhaar/Voter ID/PAN)\n- Business Registration / Udyam MSME Certificate\n- 6 Months Bank Statement\n- Project Report / Quotations",
        "application_process": "1. Apply online via JanSamarth portal (jansamarth.in) or any commercial/RRB/cooperative bank.\n2. Bank credit appraisal and sanction.",
        "official_portal_url": "https://www.mudra.org.in"
    },
    {
        "scheme_code": "OD-WCD-SUBHADRA-2024",
        "name": "Subhadra Yojana (Odisha)",
        "ministry_or_department": "Women and Child Development Department, Govt of Odisha",
        "category": "Women Empowerment & Financial Support",
        "state": "Odisha",
        "summary": "Financial assistance of ₹50,000 over 5 years (₹10,000 per year paid in two installments of ₹5,000 on Raksha Bandhan and International Women's Day) transferred directly to eligible women in Odisha.",
        "eligibility_criteria": "- Female resident of Odisha aged between 21 and 60 years from economically weaker households.\n- Excludes government employees, taxpayers, and women receiving >= ₹1,500/month in other cash schemes.",
        "benefits": "Direct bank transfer of ₹50,000 over 5 years (₹10,000/year) + Subhadra ATM Debit Card + Digital transaction incentives.",
        "income_limit": 250000.0,
        "required_documents": "- Aadhaar Card (single name, eKYC completed)\n- Active Aadhaar-seeded Bank Account (DBTL enabled)\n- Subhadra Application Form / Online Registration",
        "application_process": "1. Apply online at subhadra.odisha.gov.in or via Mo Seba Kendra / Anganwadi Centers.\n2. Aadhaar eKYC verification and direct benefit transfer.",
        "official_portal_url": "https://subhadra.odisha.gov.in"
    }
]

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        logger.info("Seeding structured schemes into database...")
        for data in SEED_SCHEMES:
            existing = db.query(Scheme).filter(Scheme.scheme_code == data["scheme_code"]).first()
            if not existing:
                scheme = Scheme(**data)
                db.add(scheme)
                logger.info(f"Added scheme: {data['name']}")
        db.commit()

        # Ingest document files into RAG engine & vector DB
        doc_files = glob.glob("../data/sample_documents/*.txt") + glob.glob("../data/sample_documents/*.pdf") + glob.glob("data/sample_documents/*.txt") + glob.glob("data/sample_documents/*.pdf")
        logger.info(f"Found {len(doc_files)} sample document files to index into RAG vector store.")
        
        for file_path in doc_files:
            filename = os.path.basename(file_path)
            # Find matching scheme by category or name
            scheme = None
            if "tn" in filename.lower() or "post_matric" in filename.lower():
                scheme = db.query(Scheme).filter(Scheme.scheme_code == "TN-HE-PMS-2024").first()
            elif "kisan" in filename.lower():
                scheme = db.query(Scheme).filter(Scheme.scheme_code == "GOI-AGRI-PMKISAN-2024").first()
            elif "awas" in filename.lower():
                scheme = db.query(Scheme).filter(Scheme.scheme_code == "GOI-HOUS-PMAY-2024").first()
            elif "ayushman" in filename.lower():
                scheme = db.query(Scheme).filter(Scheme.scheme_code == "GOI-HLTH-PMJAY-2024").first()
            elif "nmmss" in filename.lower():
                scheme = db.query(Scheme).filter(Scheme.scheme_code == "GOI-EDU-NMMSS-2024").first()
            elif "mysy" in filename.lower():
                scheme = db.query(Scheme).filter(Scheme.scheme_code == "GUJ-EDU-MYSY-2024").first()
            elif "stand_up" in filename.lower():
                scheme = db.query(Scheme).filter(Scheme.scheme_code == "GOI-FIN-STANDUP-2024").first()
            elif "airtel" in filename.lower() or "bharti" in filename.lower():
                scheme = db.query(Scheme).filter(Scheme.scheme_code == "CORP-EDU-AIRTEL-2024").first()

            sname = scheme.name if scheme else "Government Scheme Guideline"
            scat = scheme.category if scheme else "General"
            sid = scheme.id if scheme else None

            # Index document with RAG engine
            res = rag_engine.process_and_index_document(
                file_path=file_path,
                document_name=filename,
                scheme_name=sname,
                category=scat,
                source_url=scheme.official_portal_url if scheme else "https://myschemes.gov.in"
            )

            # Record document in SQL DB if not exists
            existing_doc = db.query(DocumentModel).filter(DocumentModel.document_name == filename).first()
            if not existing_doc:
                doc_record = DocumentModel(
                    document_name=filename,
                    file_path=file_path,
                    scheme_id=sid,
                    category=scat,
                    file_size=os.path.getsize(file_path),
                    chunk_count=res.get("chunks_indexed", 0)
                )
                db.add(doc_record)
                logger.info(f"Indexed document '{filename}' into vector store ({res.get('chunks_indexed', 0)} chunks).")

        db.commit()
        logger.info("Database seeding and RAG document indexing completed successfully!")

    except Exception as e:
        logger.error(f"Seeding error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
