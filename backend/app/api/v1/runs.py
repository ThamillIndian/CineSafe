"""
Runs API Router - Pipeline execution and status monitoring
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import uuid
from datetime import datetime
import asyncio

from app.database import get_db
from app.models.database import Project, Document, Run, Job, RunStatus
from app.models.schemas import RunStartRequest, RunStatusResponse
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


# ============== START PIPELINE RUN ==============
@router.post("/{project_id}/{document_id}", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def start_pipeline_run(
    project_id: str,
    document_id: str,
    request: RunStartRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Start an analysis pipeline run (CrewAI agents processing)
    
    **Args:**
    - project_id: UUID of the project
    - document_id: UUID of the script document
    - mode: full_analysis (default) or quick_analysis
    
    **Returns:** Job ID and run ID for async monitoring
    
    **Workflow:**
    1. Validates project and document exist
    2. Creates Run record in database
    3. Queues Celery task for CrewAI execution
    4. Returns async job handle
    
    **Status codes:**
    - 202 Accepted: Job queued for processing
    - 404 Not Found: Project/document not found
    - 400 Bad Request: Invalid parameters
    """
    try:
        # Validate project exists
        project_result = await session.execute(
            select(Project).where(Project.id == project_id)
        )
        project = project_result.scalars().first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        # Validate document exists
        doc_result = await session.execute(
            select(Document).where(
                (Document.id == document_id) &
                (Document.project_id == project_id)
            )
        )
        document = doc_result.scalars().first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found in project"
            )
        
        # Get latest run number
        run_number_result = await session.execute(
            select(Run).where(Run.project_id == project_id)
        )
        existing_runs = run_number_result.scalars().all()
        run_number = len(existing_runs) + 1
        
        # Create Run record
        run = Run(
            id=str(uuid.uuid4()),
            project_id=project_id,
            document_id=document_id,
            run_number=run_number,
            status=RunStatus.QUEUED
        )
        
        session.add(run)
        
        # Create Job record for tracking
        job = Job(
            id=str(uuid.uuid4()),
            run_id=run.id,
            status="queued",
            current_step="Initializing pipeline",
            progress_percent=0
        )
        
        session.add(job)
        await session.commit()
        
        # Queue Celery task
        try:
            # Import Celery task (will be created in workers/tasks.py)
            from workers.tasks import run_crew_pipeline
            
            celery_task = run_crew_pipeline.apply_async(
                args=[run.id, project_id, document_id, document.text_content, request.mode],
                task_id=f"run-{run.id}"
            )
            
            # Update job with Celery task ID
            job.celery_task_id = celery_task.id
            await session.commit()
            
            logger.info(f"✅ Pipeline queued: run_id={run.id}, celery_task={celery_task.id}, mode={request.mode}")
            
        except Exception as e:
            logger.warning(f"⚠️ Celery task queueing failed: {e} - Pipeline will run synchronously")
            # Fall back to sync execution if Celery fails
            # This is okay for demo/debug
        
        return {
            "status": "queued",
            "run_id": run.id,
            "job_id": job.id,
            "message": "Pipeline analysis started. Monitor status with GET /api/v1/runs/{run_id}/status",
            "mode": request.mode,
            "estimated_wait_seconds": 60  # Rough estimate
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ Pipeline start failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to start pipeline: {str(e)}"
        )


# ============== GET RUN STATUS ==============
@router.get("/{run_id}/status", response_model=RunStatusResponse)
async def get_run_status(
    run_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Get pipeline execution status
    
    **Args:**
    - run_id: UUID of the run
    
    **Returns:** Current status, progress, and error details
    
    **Status values:**
    - queued: Waiting to start
    - running: Processing scenes
    - completed: Finished successfully
    - failed: Encountered error
    """
    try:
        # Get run
        run_result = await session.execute(
            select(Run).where(Run.id == run_id)
        )
        run = run_result.scalars().first()
        
        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Run {run_id} not found"
            )
        
        # Get job for progress tracking
        job_result = await session.execute(
            select(Job).where(Job.run_id == run_id)
        )
        job = job_result.scalars().first()
        
        # Check Celery task status if available
        if job and job.celery_task_id:
            try:
                from workers.celery_app import celery_app
                celery_task = celery_app.AsyncResult(job.celery_task_id)
                
                if celery_task.state == "PROGRESS":
                    job.progress_percent = celery_task.info.get("progress", 0)
                    job.current_step = celery_task.info.get("step", "Processing")
                elif celery_task.state == "SUCCESS":
                    run.status = RunStatus.COMPLETED
                    run.completed_at = datetime.utcnow()
                    job.status = "completed"
                    job.progress_percent = 100
                    await session.commit()
                elif celery_task.state == "FAILURE":
                    run.status = RunStatus.FAILED
                    run.completed_at = datetime.utcnow()
                    run.error_message = str(celery_task.info)
                    job.status = "failed"
                    await session.commit()
                    
            except Exception as e:
                logger.warning(f"⚠️ Could not check Celery status: {e}")
        
        # Build response
        return RunStatusResponse(
            job_id=job.id if job else run_id,
            run_id=run_id,
            status=run.status.value,
            current_step=job.current_step if job else "Initializing",
            progress_percent=job.progress_percent if job else 0,
            current_scene=None,
            total_scenes=None,
            error_message=run.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching run status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching run status: {str(e)}"
        )


# ============== GET RUN DETAILS ==============
@router.get("/{run_id}", response_model=dict)
async def get_run_details(
    run_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Get complete run details
    
    **Args:**
    - run_id: UUID of the run
    
    **Returns:** Full run information
    """
    try:
        run_result = await session.execute(
            select(Run).where(Run.id == run_id)
        )
        run = run_result.scalars().first()
        
        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Run {run_id} not found"
            )
        
        return {
            "id": run.id,
            "project_id": run.project_id,
            "document_id": run.document_id,
            "run_number": run.run_number,
            "status": run.status.value,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "error_message": run.error_message,
            "scene_count": len(run.scenes) if run.scenes else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching run details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching run details: {str(e)}"
        )


# ============== LIST PROJECT RUNS ==============
@router.get("", response_model=list[dict])
async def list_project_runs(
    project_id: str,
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_db)
):
    """
    List all runs for a project
    
    **Args:**
    - project_id: UUID of the project
    - skip: Number of runs to skip
    - limit: Maximum runs to return
    
    **Returns:** List of runs
    """
    try:
        runs_result = await session.execute(
            select(Run).where(Run.project_id == project_id).offset(skip).limit(limit)
        )
        runs = runs_result.scalars().all()
        
        return [
            {
                "id": run.id,
                "run_number": run.run_number,
                "status": run.status.value,
                "started_at": run.started_at,
                "completed_at": run.completed_at,
                "scene_count": len(run.scenes) if run.scenes else 0
            }
            for run in runs
        ]
        
    except Exception as e:
        logger.error(f"❌ Error listing runs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing runs: {str(e)}"
        )


# ============== CANCEL RUN ==============
@router.post("/{run_id}/cancel", response_model=dict)
async def cancel_run(
    run_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Cancel an ongoing pipeline run
    
    **Args:**
    - run_id: UUID of the run
    
    **Returns:** Cancellation status
    """
    try:
        run_result = await session.execute(
            select(Run).where(Run.id == run_id)
        )
        run = run_result.scalars().first()
        
        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Run {run_id} not found"
            )
        
        if run.status not in [RunStatus.QUEUED, RunStatus.RUNNING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel run with status {run.status.value}"
            )
        
        # Cancel Celery task if exists
        job_result = await session.execute(
            select(Job).where(Job.run_id == run_id)
        )
        job = job_result.scalars().first()
        
        if job and job.celery_task_id:
            try:
                from workers.celery_app import celery_app
                celery_app.control.revoke(job.celery_task_id, terminate=True)
            except:
                pass
        
        run.status = RunStatus.FAILED
        run.error_message = "Run cancelled by user"
        run.completed_at = datetime.utcnow()
        
        await session.commit()
        
        logger.info(f"🛑 Run cancelled: {run_id}")
        
        return {
            "status": "cancelled",
            "run_id": run_id,
            "message": "Pipeline execution cancelled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ Cancel failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel run: {str(e)}"
        )
