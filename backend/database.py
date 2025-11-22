"""
Database models and ORM setup for SEO Analyzer.
Uses SQLAlchemy with support for SQLite (dev) and PostgreSQL (prod).
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum

from config import DATABASE_URL
from logger import setup_logger

logger = setup_logger(__name__)

# Create database engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True  # Verify connections before using
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Enums
class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CompetitorStatus(str, enum.Enum):
    VALID = "valid"
    WEAK = "weak"
    FAILED = "failed"


# Models
class Analysis(Base):
    """Main analysis record."""
    __tablename__ = "analyses"
    
    id = Column(String(36), primary_key=True)  # UUID
    keyword = Column(String(200), nullable=False, index=True)
    language = Column(String(10), nullable=False)
    location = Column(String(100), nullable=False)
    device = Column(String(20), nullable=False)  # desktop | mobile
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    competitors = relationship("Competitor", back_populates="analysis", cascade="all, delete-orphan")
    terms = relationship("Term", back_populates="analysis", cascade="all, delete-orphan")
    guideline = relationship("Guideline", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    draft = relationship("Draft", back_populates="analysis", uselist=False, cascade="all, delete-orphan")


class Competitor(Base):
    """Competitor page data."""
    __tablename__ = "competitors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
    
    position = Column(Integer, nullable=False)
    url = Column(String(500), nullable=False)
    title = Column(String(300), nullable=True)
    domain = Column(String(200), nullable=True)
    
    word_count = Column(Integer, nullable=True)
    paragraph_count = Column(Integer, nullable=True)
    image_count = Column(Integer, nullable=True)
    headings_count = Column(Integer, nullable=True)
    
    is_enabled = Column(Boolean, default=True, nullable=False)  # User can toggle
    status = Column(SQLEnum(CompetitorStatus), default=CompetitorStatus.VALID, nullable=False)
    error_message = Column(String(500), nullable=True)
    
    # Store extracted data as JSON
    extracted_data = Column(JSON, nullable=True)  # headings, main_text, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="competitors")


class Term(Base):
    """Extracted terms with frequency recommendations."""
    __tablename__ = "terms"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
    
    term = Column(String(200), nullable=False)
    term_normalized = Column(String(200), nullable=False)  # Lowercased/lemmatized
    type = Column(String(20), nullable=False)  # phrase | entity
    
    min_recommended = Column(Integer, nullable=False)
    max_recommended = Column(Integer, nullable=False)
    avg_in_competitors = Column(Float, nullable=False)
    median_in_competitors = Column(Float, nullable=False)
    docs_used_in = Column(Integer, nullable=False)
    
    # Store occurrence details as JSON
    occurrences_by_position = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="terms")


class Guideline(Base):
    """Content guidelines derived from competitors."""
    __tablename__ = "guidelines"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Word count
    word_count_min = Column(Integer, nullable=False)
    word_count_max = Column(Integer, nullable=False)
    word_count_median = Column(Integer, nullable=False)
    word_count_confidence = Column(Float, default=1.0, nullable=False)
    
    # Headings
    headings_min = Column(Integer, nullable=False)
    headings_max = Column(Integer, nullable=False)
    headings_median = Column(Integer, nullable=False)
    headings_confidence = Column(Float, default=1.0, nullable=False)
    
    # Images
    images_min = Column(Integer, nullable=False)
    images_max = Column(Integer, nullable=False)
    images_median = Column(Integer, nullable=False)
    images_confidence = Column(Float, default=1.0, nullable=False)
    
    # Suggested outline as JSON
    suggested_outline = Column(JSON, nullable=True)
    
    # Warnings (if any)
    warnings = Column(JSON, nullable=True)
    
    competitors_analyzed = Column(Integer, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="guideline")


class Draft(Base):
    """User's draft content (autosaved)."""
    __tablename__ = "drafts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    content = Column(Text, nullable=True)
    format = Column(String(20), default="html", nullable=False)  # html | markdown
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="draft")


# Database initialization
def init_db():
    """Create all tables."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database tables created successfully")


def get_db():
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables on import (for development)
if __name__ == "__main__":
    init_db()
