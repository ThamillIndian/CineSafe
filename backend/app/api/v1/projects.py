"""
Projects API Router - CRUD operations for film projects
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select
import logging
import uuid
from datetime import datetime

from app.database import get_db
from app.models.database import Project, Run, ProjectStatus, ScaleTier, RunStatus
from app.models.schemas import ProjectCreate, ProjectResponse

logger = logging.getLogger(__name__)
router = APIRouter()


# ============== CREATE PROJECT ==============
@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    session: AsyncSession = Depends(get_db)
):
    """
    Create a new film project
    
    **Args:**
    - name: Project name
    - language: Shooting language (default: English)
    - base_city: Primary shooting city
    - states: List of states where shooting occurs
    - scale: Budget scale (indie, mid_budget, big_budget)
    
    **Returns:** Created project details with ID
    """
    try:
        new_project = Project(
            id=str(uuid.uuid4()),
            name=project_data.name,
            language=project_data.language,
            base_city=project_data.base_city,
            states=project_data.states,
            scale=project_data.scale,
            status=ProjectStatus.DRAFT
        )
        
        session.add(new_project)
        await session.commit()
        await session.refresh(new_project)
        
        logger.info(f"✅ Project created: {new_project.id} - {new_project.name}")
        
        return new_project
        
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ Project creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create project: {str(e)}"
        )


# ============== GET PROJECT ==============
@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Get project details by ID
    
    **Args:**
    - project_id: UUID of the project
    
    **Returns:** Project details including runs and documents
    """
    try:
        result = await session.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalars().first()
        
        if not project:
            logger.warning(f"⚠️ Project not found: {project_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching project: {str(e)}"
        )


# ============== LIST PROJECTS ==============
@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_db)
):
    """
    List all projects with pagination
    
    **Args:**
    - skip: Number of projects to skip
    - limit: Maximum projects to return
    
    **Returns:** List of projects
    """
    try:
        result = await session.execute(
            select(Project).offset(skip).limit(limit)
        )
        projects = result.scalars().all()
        
        logger.info(f"📋 Listed {len(projects)} projects (skip={skip}, limit={limit})")
        
        return projects
        
    except Exception as e:
        logger.error(f"❌ Error listing projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing projects: {str(e)}"
        )


# ============== UPDATE PROJECT ==============
@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectCreate,
    session: AsyncSession = Depends(get_db)
):
    """
    Update project details
    
    **Args:**
    - project_id: UUID of the project
    - project_data: Updated project data
    
    **Returns:** Updated project details
    """
    try:
        result = await session.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalars().first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        # Update fields
        project.name = project_data.name
        project.language = project_data.language
        project.base_city = project_data.base_city
        project.states = project_data.states
        project.scale = project_data.scale
        project.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(project)
        
        logger.info(f"✅ Project updated: {project_id}")
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ Project update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update project: {str(e)}"
        )


# ============== DELETE PROJECT ==============
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Delete a project and all associated data
    
    **Args:**
    - project_id: UUID of the project
    
    **Returns:** 204 No Content
    """
    try:
        result = await session.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalars().first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        await session.delete(project)
        await session.commit()
        
        logger.info(f"🗑️ Project deleted: {project_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ Project deletion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )


# ============== ACTIVATE PROJECT ==============
@router.post("/{project_id}/activate", response_model=ProjectResponse)
async def activate_project(
    project_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Activate a project (change status from DRAFT to ACTIVE)
    
    **Args:**
    - project_id: UUID of the project
    
    **Returns:** Updated project with status=active
    """
    try:
        result = await session.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalars().first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        project.status = ProjectStatus.ACTIVE
        project.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(project)
        
        logger.info(f"✅ Project activated: {project_id}")
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ Project activation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to activate project: {str(e)}"
        )
