import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    saved_schemes = relationship("SavedScheme", back_populates="user")
    checklists = relationship("Checklist", back_populates="user")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    state = Column(String(100), default="All India")
    category = Column(String(50), default="General")  # SC, ST, OBC, General, EWS
    occupation = Column(String(100), default="Student") # Student, Farmer, Worker, Entrepreneur
    annual_income = Column(Float, default=0.0)
    education_level = Column(String(100), default="Undergraduate")
    age = Column(Integer, default=20)
    gender = Column(String(20), default="Any")

    user = relationship("User", back_populates="profile")


class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)
    scheme_code = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    ministry_or_department = Column(String(255), nullable=False)
    category = Column(String(100), index=True, nullable=False)  # Education, Agriculture, Housing, Healthcare, etc.
    state = Column(String(100), default="All India", index=True)
    summary = Column(Text, nullable=False)
    eligibility_criteria = Column(Text, nullable=False)
    benefits = Column(Text, nullable=False)
    income_limit = Column(Float, nullable=True)  # Upper income limit in INR
    required_documents = Column(Text, nullable=False)  # JSON or newline list
    application_process = Column(Text, nullable=False)
    official_portal_url = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    documents = relationship("DocumentModel", back_populates="scheme")
    saved_by = relationship("SavedScheme", back_populates="scheme")
    checklists = relationship("Checklist", back_populates="scheme")


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=True)
    category = Column(String(100), default="General")
    file_size = Column(Integer, default=0)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    chunk_count = Column(Integer, default=0)

    scheme = relationship("Scheme", back_populates="documents")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(100), primary_key=True, index=True)
    title = Column(String(255), default="New Search Conversation")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), ForeignKey("conversations.id"), nullable=False)
    sender = Column(String(50), nullable=False)  # "user" or "agent"
    content = Column(Text, nullable=False)
    sources_json = Column(Text, nullable=True)  # JSON array of source citations
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class SavedScheme(Base):
    __tablename__ = "saved_schemes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    saved_at = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="saved_schemes")
    scheme = relationship("Scheme", back_populates="saved_by")


class Checklist(Base):
    __tablename__ = "checklists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    scheme = relationship("Scheme", back_populates="checklists")
    user = relationship("User", back_populates="checklists")
    items = relationship("ChecklistItem", back_populates="checklist", cascade="all, delete-orphan")


class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    checklist_id = Column(Integer, ForeignKey("checklists.id"), nullable=False)
    document_name = Column(String(255), nullable=False)
    status = Column(String(50), default="Missing")  # Available, Missing, Not Applicable
    notes = Column(Text, nullable=True)

    checklist = relationship("Checklist", back_populates="items")
