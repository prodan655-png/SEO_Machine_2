from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from database import get_db, Project
from models import ProjectCreateRequest, ProjectResponse

router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"]
)

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(request: ProjectCreateRequest, db: Session = Depends(get_db)):
    project = Project(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.description,
        target_audience=request.target_audience,
        tone_of_voice=request.tone_of_voice,
        sitemap_url=request.sitemap_url,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Manually serialize to match Pydantic model
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        target_audience=project.target_audience,
        tone_of_voice=project.tone_of_voice,
        sitemap_url=project.sitemap_url,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat()
    )

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.updated_at.desc()).all()
    return [
        ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            target_audience=p.target_audience,
            tone_of_voice=p.tone_of_voice,
            sitemap_url=p.sitemap_url,
            created_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat()
        )
        for p in projects
    ]

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        target_audience=project.target_audience,
        tone_of_voice=project.tone_of_voice,
        sitemap_url=project.sitemap_url,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat()
    )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
