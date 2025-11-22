"""
Pydantic models for API request/response validation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


# Enums
class DeviceType(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"


class ContentType(str, Enum):
    BLOG = "blog"
    CATEGORY = "category"
    LANDING = "landing"


class ToneType(str, Enum):
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"
    EXPERT = "expert"


class FormatType(str, Enum):
    HTML = "html"
    MARKDOWN = "markdown"


# Request Models
class AnalysisCreateRequest(BaseModel):
    keyword: str = Field(..., min_length=2, max_length=100)
    language: str = Field(..., min_length=2, max_length=10)
    location: str = Field(..., min_length=2, max_length=100)
    device: DeviceType = DeviceType.DESKTOP
    draft_text: Optional[str] = None
    draft_url: Optional[str] = None
    
    @validator('keyword')
    def validate_keyword(cls, v):
        # Remove extra whitespace
        return ' '.join(v.split())


class ScoreRequest(BaseModel):
    draft_text: str = Field(..., max_length=50000)
    format: FormatType = FormatType.HTML


class CompetitorToggleRequest(BaseModel):
    competitor_urls: List[str]
    enabled: bool


class DraftSaveRequest(BaseModel):
    draft_text: str = Field(..., max_length=50000)


class AIBriefRequest(BaseModel):
    content_type: ContentType = ContentType.BLOG
    tone: ToneType = ToneType.NEUTRAL


class AIEnhanceRequest(BaseModel):
    fragment_text: str = Field(..., max_length=10000)
    target_terms: List[str]
    max_words: int = Field(default=200, ge=50, le=1000)
    style: str = "neutral"


class AICoachRequest(BaseModel):
    target_score: int = Field(..., ge=0, le=100)


# Response Models
class CompetitorResponse(BaseModel):
    position: int
    url: str
    title: str
    domain: str
    word_count: Optional[int]
    is_enabled: bool
    status: str


class TermResponse(BaseModel):
    term: str
    type: str
    min_recommended: int
    max_recommended: int
    avg_in_competitors: float


class GuidelineResponse(BaseModel):
    word_count: Dict[str, int]
    headings: Dict[str, int]
    images: Dict[str, int]
    suggested_outline: List[str]
    competitors_analyzed: int


class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    keyword: str
    language: str
    location: str
    device: str
    competitors: Optional[List[CompetitorResponse]] = None
    guidelines: Optional[GuidelineResponse] = None
    terms: Optional[List[TermResponse]] = None
    created_at: str
    updated_at: str


class TermDetailResponse(BaseModel):
    term: str
    recommended_min: int
    recommended_max: int
    current: int
    status: str  # ok | low | high
    term_score: float
    positions: List[int]


class ScoreBreakdownResponse(BaseModel):
    score: int
    max: int


class ScoreResponse(BaseModel):
    total_score: int
    breakdown: Dict[str, ScoreBreakdownResponse]
    term_details: List[TermDetailResponse]
    structure_details: Dict[str, Any]
    headings_details: Dict[str, Any]


class ErrorResponse(BaseModel):
    error: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
