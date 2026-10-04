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
