"""
SEO Analyzer - FastAPI Application
Provides REST API endpoints for SEO content analysis.
"""

import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DATABASE_URL, ALLOWED_ORIGINS
from database import SessionLocal, Analysis, Competitor, Term, Guideline, Draft, AnalysisStatus
from config import get_config, get_db
from logger import setup_logger
from modules.serp_fetcher import fetch_serp
from modules.content_extractor import batch_extract_competitors
from modules.semantic_analyzer import analyze_competitors
from modules.guidelines_generator import generate_guidelines
from modules.content_scorer import compute_content_score

# Setup
logger = setup_logger('api')

# SQLite-specific connect args
connect_args = {}
if DATABASE_URL.startswith('sqlite'):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting SEO Analyzer API")
    yield
    logger.info("Shutting down SEO Analyzer API")


# FastAPI app
app = FastAPI(
    title="SEO Analyzer API",
    description="Content analysis and optimization for SEO",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class AnalysisCreateRequest(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=200)
    language: str = Field(default="en", pattern="^(en|uk)$")
    location: str = Field(default="US", max_length=100)
    device: str = Field(default="desktop", pattern="^(desktop|mobile)$")


class AnalysisCreateResponse(BaseModel):
    analysis_id: str
    status: str


class ScoreDraftRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000)
    format: str = Field(default="html", pattern="^(html|markdown)$")


class ToggleCompetitorRequest(BaseModel):
    competitor_url: str
    enabled: bool


class HealthResponse(BaseModel):
    status: str
    timestamp: str


# Background task function
async def process_analysis_task(analysis_id: str):
    """
    Background task to process SEO analysis.
    Fetches SERP, extracts content, analyzes competitors, generates guidelines.
    """
    db: Session = SessionLocal()
    
    try:
        # Get analysis from database
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            logger.error(f"Analysis {analysis_id} not found")
            return
        
        logger.info(f"Processing analysis {analysis_id} for keyword '{analysis.keyword}'")
        
        # Step 1: Fetch SERP results
        serp_data = fetch_serp(analysis.keyword, analysis.language)
        
        if 'error' in serp_data:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = serp_data['error']
            db.commit()
            logger.error(f"SERP fetch failed for {analysis_id}: {serp_data['error']}")
            return
        
        # Step 2: Extract competitor content in batch
        competitor_urls = [result['url'] for result in serp_data['results']]
        extracted_data = await batch_extract_competitors(competitor_urls)
        
        # Filter valid competitors
        valid_competitors = [c for c in extracted_data if c['status'] == 'valid']
        
        if not valid_competitors:
            error_msg = "Не вдалося знайти достатньо конкурентів для аналізу. Спробуйте інший запит."
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = error_msg
            db.commit()
            logger.error(f"Analysis {analysis_id} failed: No valid competitors found")
            return

        # Step 3: Save competitors to database
        for i, comp_data in enumerate(extracted_data):
            competitor = Competitor(
                analysis_id=analysis_id,
                url=comp_data['url'],
                position=i + 1,
                title=comp_data.get('title', ''),
                word_count=comp_data.get('word_count', 0),
                status=comp_data.get('status', 'FAILED'),
                extracted_data={
                    'main_text': comp_data.get('main_text', ''),
                    'headings': comp_data.get('headings', []),
                    'language': comp_data.get('language')
                },
                image_count=comp_data.get('image_count', 0),
                headings_count=len(comp_data.get('headings', []))
            )
            db.add(competitor)
        
        db.commit()
        
        # Step 4: Semantic analysis (extract terms)
        position_weights = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
        terms_data = analyze_competitors(extracted_data, analysis.language, position_weights)
        
        # Step 5: Save terms to database
        for term_info in terms_data:
            term = Term(
                analysis_id=analysis_id,
                term=term_info['term'],
                term_normalized=term_info['term_normalized'],
                type=term_info['type'],
                min_recommended=term_info['min_recommended'],
                max_recommended=term_info['max_recommended'],
                avg_in_competitors=term_info['avg_in_competitors'],
                median_in_competitors=term_info['median_in_competitors'],
                docs_used_in=term_info.get('docs_used_in', 3),
                occurrences_by_position=term_info.get('occurrences_by_position')
            )
            db.add(term)
        
        db.commit()
        
        # Step 6: Generate guidelines
        guidelines_data = generate_guidelines(extracted_data, position_weights)
        
        # Step 7: Save guidelines to database
        guideline = Guideline(
            analysis_id=analysis_id,
            word_count_min=guidelines_data['word_count']['min'],
            word_count_max=guidelines_data['word_count']['max'],
            word_count_median=guidelines_data['word_count']['median'],
            word_count_confidence=guidelines_data.get('confidence', 1.0),
            headings_min=guidelines_data['headings']['min'],
            headings_max=guidelines_data['headings']['max'],
            headings_median=guidelines_data['headings']['median'],
            headings_confidence=guidelines_data.get('confidence', 1.0),
            images_min=guidelines_data['images']['min'],
            images_max=guidelines_data['images']['max'],
            images_median=guidelines_data['images']['median'],
            images_confidence=guidelines_data.get('confidence', 1.0),
            suggested_outline=guidelines_data.get('suggested_outline', []),
            warnings=guidelines_data.get('warnings', []),
            competitors_analyzed=len([c for c in extracted_data if isinstance(c, dict) and c.get('status') == 'valid'])
        )
        db.add(guideline)
        
        # Update analysis status
        analysis.status = AnalysisStatus.COMPLETED
        
        db.commit()
        logger.info(f"Analysis {analysis_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error processing analysis {analysis_id}: {str(e)}", exc_info=True)
        analysis.status = AnalysisStatus.FAILED
        analysis.error_message = str(e)
        db.commit()
        
    finally:
        db.close()


# API Endpoints

@app.post("/api/analysis/create", response_model=AnalysisCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    request: AnalysisCreateRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new SEO analysis for a keyword.
    Triggers background task to fetch SERP and analyze competitors.
    """
    db: Session = SessionLocal()
    
    try:
        # Create analysis record
        import uuid
        analysis = Analysis(
            id=str(uuid.uuid4()),
            keyword=request.keyword,
            language=request.language,
            location=request.location,
            device=request.device,
            status=AnalysisStatus.PROCESSING
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        analysis_id = str(analysis.id)
        
        # Trigger background task - FastAPI handles async automatically
        background_tasks.add_task(process_analysis_task, analysis_id)
        
        logger.info(f"Created analysis {analysis_id} for keyword '{request.keyword}''")
        
        return AnalysisCreateResponse(
            analysis_id=analysis_id,
            status='processing'
        )
        
    except Exception as e:
        logger.error(f"Error creating analysis: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create analysis: {str(e)}"
        )
    finally:
        db.close()


@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """
    Retrieve analysis results by ID.
    Returns full analysis data including terms, guidelines, and competitors.
    """
    db: Session = SessionLocal()
    
    try:
        # Get analysis
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis {analysis_id} not found"
            )
        
        # Build response
        response = {
            "id": str(analysis.id),
            "keyword": analysis.keyword,
            "language": analysis.language,
            "location": analysis.location,
            "device": analysis.device,
            "status": analysis.status.value,  # Ensure string value
            "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
            "updated_at": analysis.updated_at.isoformat() if analysis.updated_at else None,
            "error_message": analysis.error_message
        }
        
        # Only include details if completed
        if analysis.status == AnalysisStatus.COMPLETED:
            response.update({
                "competitors": [
                    {
                        "url": c.url,
                        "position": c.position,
                        "title": c.title,
                        "word_count": c.word_count,
                        "status": c.status.value,
                        "enabled": c.is_enabled
                    }
                    for c in analysis.competitors
                ],
                "terms": [
                    {
                        "term": t.term,
                        "type": t.type,
                        "min_recommended": t.min_recommended,
                        "max_recommended": t.max_recommended,
                        "avg_usage": t.avg_in_competitors
                    }
                    for t in analysis.terms
                ],
                "guidelines": {
                    "word_count": {
                        "min": analysis.guideline.word_count_min,
                        "max": analysis.guideline.word_count_max,
                        "median": analysis.guideline.word_count_median
                    },
                    "headings": {
                        "min": analysis.guideline.headings_min,
                        "max": analysis.guideline.headings_max,
                        "median": analysis.guideline.headings_median
                    },
                    "images": {
                        "min": analysis.guideline.images_min,
                        "max": analysis.guideline.images_max,
                        "median": analysis.guideline.images_median
                    },
                    "warnings": analysis.guideline.warnings
                } if analysis.guideline else None
            })
        
        return response
        
    finally:
        db.close()


@app.post("/api/analysis/{analysis_id}/score")
async def score_draft(analysis_id: str, request: ScoreDraftRequest):
    """
    Score user's draft content against analysis guidelines.
    Returns score breakdown by terms, structure, and headings.
    """
    db: Session = SessionLocal()
    
    try:
        # Get analysis
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis {analysis_id} not found"
            )
        
        if analysis.status != 'completed':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Analysis is not completed yet (status: {analysis.status})"
            )
        
        # Get terms and guidelines
        terms = db.query(Term).filter(Term.analysis_id == analysis_id).all()
        guideline = db.query(Guideline).filter(Guideline.analysis_id == analysis_id).first()
        
        if not terms or not guideline:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Analysis data is incomplete"
            )
        
        # Format data for scorer - flat structure required
        terms_data = [
            {
                "term": t.term,
                "term_normalized": t.term_normalized,
                "min_recommended": t.min_recommended,
                "max_recommended": t.max_recommended,
                "median": t.median_in_competitors
            }
            for t in terms
        ]
        
        guidelines_data = {
            "word_count": {
                "min": guideline.word_count_min,
                "max": guideline.word_count_max,
                "median": guideline.word_count_median
            },
            "headings": {
                "min": guideline.headings_min,
                "max": guideline.headings_max,
                "median": guideline.headings_median
            },
            "images": {
                "min": guideline.images_min,
                "max": guideline.images_max,
                "median": guideline.images_median
            }
        }
        
        # Compute score
        score_result = compute_content_score(
            request.text,
            guidelines_data,
            terms_data,
            request.format
        )
        
        return score_result
        
    finally:
        db.close()


@app.put("/api/analysis/{analysis_id}/competitors")
async def toggle_competitor(analysis_id: str, request: ToggleCompetitorRequest):
    """
    Enable or disable a competitor from analysis.
    """
    db: Session = SessionLocal()
    
    try:
        # Get competitor
        competitor = db.query(Competitor).filter(
            Competitor.analysis_id == analysis_id,
            Competitor.url == request.competitor_url
        ).first()
        
        if not competitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Competitor not found"
            )
        
        # Update enabled status
        competitor.is_enabled = request.enabled
        db.commit()
        
        logger.info(f"Toggled competitor {request.competitor_url} to {request.enabled}")
        
        return {
            "url": competitor.url,
            "enabled": competitor.is_enabled,
            "message": f"Competitor {'enabled' if request.enabled else 'disabled'}"
        }
        
    finally:
        db.close()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat()
    )


# ===== AI Features (Phase 6) =====

class CoachRequest(BaseModel):
    analysis_id: str
    current_score: int = Field(..., ge=0, le=100)
    target_score: int = Field(..., ge=0, le=100)


@app.post("/api/ai/coach", tags=["AI"])
async def get_seo_coaching(
    request: CoachRequest,
    db: Session = Depends(get_db)
):
    """
    Get AI-powered SEO coaching.
    Returns personalized action plan to improve score.
    """
    from config import get_config
    
    # Check if AI is enabled
    if not get_config('ai.enabled', False):
        raise HTTPException(
            status_code=503,
            detail="AI features are disabled. Set AI_ENABLED=true in config."
        )
    
    try:
        # Get analysis
        analysis = db.query(Analysis).filter(Analysis.id == request.analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Ensure analysis is completed
        status_str = analysis.status.value if hasattr(analysis.status, 'value') else str(analysis.status)
        logger.debug(f"Analysis status: {status_str}, type: {type(analysis.status)}")
        
        if status_str.lower() != 'completed':
            raise HTTPException(
                status_code=400,
                detail=f"Analysis not completed yet (status: {status_str})"
            )
        
        # Get score data (we need to re-compute or get from database)
        # For now,let's get terms and guidelines
        terms = db.query(Term).filter(Term.analysis_id == request.analysis_id).all()
        guideline = db.query(Guideline).filter(Guideline.analysis_id == request.analysis_id).first()
        
        # Build breakdown (simplified - in prod you'd recalculate from actual draft)
        breakdown = {
            "terms": {"score": int(request.current_score * 0.6), "max": 60},
            "structure": {"score": int(request.current_score * 0.2), "max": 20},
            "headings": {"score": int(request.current_score * 0.2), "max": 20}
        }
        
        # Build term details
        term_details = []
        for term in terms[:15]:  # Top 15 terms
            # Simulate current usage (in prod, this comes from scoring)
            current = max(0, term.min_recommended - 2)  # Assume user is slightly under
            status = "low" if current < term.min_recommended else "ok"
            
            term_details.append({
                "term": term.term,
                "current": current,
                "recommended_min": term.min_recommended,
                "recommended_max": term.max_recommended,
                "status": status
            })
        
        # Structure details
        structure_details = {
            "word_count": {
                "current": int(guideline.word_count_min * 0.8) if guideline else 500,
                "recommended_min": guideline.word_count_min if guideline else 800,
                "recommended_max": guideline.word_count_max if guideline else 1500
            }
        } if guideline else None
        
        # Headings details  
        headings_details = {
            "has_h1": True,  # Assume yes
            "h2_count": max(1, guideline.headings_min - 2) if guideline else 2,
            "recommended_h2": guideline.headings_median if guideline else 4
        } if guideline else None
        
        # Import and call coach
        from modules.ai.coach import get_seo_coaching
        
        coaching = await get_seo_coaching(
            current_score=request.current_score,
            target_score=request.target_score,
            breakdown=breakdown,
            term_details=term_details,
            structure_details=structure_details,
            headings_details=headings_details
        )
        
        logger.info(f"Generated coaching for analysis {request.analysis_id}")
        return coaching
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Coaching error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class BriefRequest(BaseModel):
    analysis_id: str
    tone: str = "professional"


@app.post("/api/ai/brief", tags=["AI"])
async def generate_content_brief(request: BriefRequest):
    """
    Generate content brief based on analysis.
    """
    from config import get_config
    if not get_config('ai.enabled', False):
        raise HTTPException(status_code=503, detail="AI features disabled")
        
    db: Session = SessionLocal()
    try:
        analysis = db.query(Analysis).filter(Analysis.id == request.analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
            
        # Get data
        terms = db.query(Term).filter(Term.analysis_id == request.analysis_id).all()
        guideline = db.query(Guideline).filter(Guideline.analysis_id == request.analysis_id).first()
        competitors = db.query(Competitor).filter(
            Competitor.analysis_id == request.analysis_id,
            Competitor.is_enabled == True
        ).all()
        
        # Format data
        terms_data = [{"term": t.term} for t in terms]
        competitors_data = [{"extracted_data": c.extracted_data} for c in competitors]
        guidelines_data = {
            "word_count": {"min": guideline.word_count_min, "max": guideline.word_count_max}
        } if guideline else None
        
        from modules.ai.brief_generator import generate_brief
        
        brief = await generate_brief(
            keyword=analysis.keyword,
            language=analysis.language,
            competitors_data=competitors_data,
            terms_data=terms_data,
            guidelines=guidelines_data
        )
        
        return brief
        
    except Exception as e:
        logger.error(f"Brief generation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


from typing import Optional

class ArticleRequest(BaseModel):
    brief: Dict[str, Any]
    tone: str = "professional"
    language: str = "uk"
    coach_actions: Optional[str] = None


@app.post("/api/ai/generate", tags=["AI"])
async def generate_article_content(request: ArticleRequest):
    """
    Generate full article from brief.
    """
    from config import get_config
    if not get_config('ai.enabled', False):
        raise HTTPException(status_code=503, detail="AI features disabled")
        
    try:
        from modules.ai.content_writer import write_article
        
        article_html = await write_article(
            brief=request.brief,
            tone=request.tone,
            language=request.language,
            improvement_instructions=request.coach_actions
        )
        
        return {"article": article_html}
        
    except Exception as e:
        logger.error(f"Content generation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class SitemapRequest(BaseModel):
    url: str


@app.post("/api/tools/sitemap", tags=["Tools"])
async def parse_sitemap_url(request: SitemapRequest):
    """
    Parse sitemap XML and return URLs.
    """
    try:
        from modules.sitemap_parser import parse_sitemap
        urls = parse_sitemap(request.url)
        return {"urls": urls, "count": len(urls)}
    except Exception as e:
        logger.error(f"Sitemap parsing error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/iterate")
async def iterate_content(request: dict):
    """
    Iteratively improve content with score validation.
    
    Request body:
        content: Current content HTML
        analysis_id: Analysis ID for guidelines/terms
        max_iterations: Maximum iterations (default: 5)
        target_score: Target score (default: 85)
    """
    if not get_config('ai.enabled', False):
        raise HTTPException(status_code=503, detail="AI features disabled")
    
    db: Session = SessionLocal()
    try:
        content = request.get('content')
        analysis_id = request.get('analysis_id')
        max_iterations = request.get('max_iterations', 5)
        target_score = request.get('target_score', 85)
        
        if not content or not analysis_id:
            raise HTTPException(status_code=400, detail="Missing content or analysis_id")
        
        # Get analysis data
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get terms and guidelines
        terms = db.query(Term).filter(Term.analysis_id == analysis_id).all()
        guideline = db.query(Guideline).filter(Guideline.analysis_id == analysis_id).first()
        
        if not guideline:
            raise HTTPException(status_code=404, detail="Guidelines not found")
        
        # Format data
        terms_data = [{
            'term': t.term,
            'term_normalized': t.term_normalized,
            'min_recommended': t.min_recommended,
            'max_recommended': t.max_recommended
        } for t in terms]
        
        guidelines_data = {
            'word_count': {
                'min': guideline.word_count_min,
                'max': guideline.word_count_max,
                'median': guideline.word_count_median
            },
            'headings': {
                'min': guideline.headings_min,
                'max': guideline.headings_max,
                'median': guideline.headings_median
            },
            'images': {
                'min': guideline.images_min,
                'max': guideline.images_max,
                'median': guideline.images_median
            }
        }
        
        # Calculate current score
        from modules.content_scorer import compute_content_score
        current_score_result = compute_content_score(
            content,
            guidelines_data,
            terms_data,
            format='html'
        )
        current_score = current_score_result['total_score']
        
        # Run iteration
        from modules.ai.content_iterator import improve_iteratively
        result = await improve_iteratively(
            content,
            guidelines_data,
            terms_data,
            current_score,
            target_score,
            max_iterations
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Iteration error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


# Error handlers
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
