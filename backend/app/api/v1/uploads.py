"""
File Upload API Router - Direct script upload (no project needed)
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import uuid
from pathlib import Path
import pdfplumber
from docx import Document as DocxDocument

from app.database import get_db
from app.models.database import Document
from app.models.schemas import UploadResponse
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = Path(settings.storage_path) / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def extract_text_from_pdf(file_path: str) -> tuple[str, int]:
    """Extract text and page count from PDF"""
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            return text, len(pdf.pages)
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise


def extract_text_from_docx(file_path: str) -> tuple[str, int]:
    """Extract text and page count from DOCX"""
    try:
        doc = DocxDocument(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        estimated_pages = max(1, len(text) // 3000)
        return text, estimated_pages
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        raise


# ============== UPLOAD SCRIPT (NO PROJECT NEEDED) ==============
@router.post("/upload", response_model=UploadResponse)
async def upload_script(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db)
):
    """
    Upload a film script directly (PDF or DOCX)
    No project creation needed - ready to analyze immediately!
    
    **Args:**
    - file: Script file (PDF or DOCX)
    
    **Returns:** Document ID + upload details
    **Supported:** .pdf, .docx
    **Max size:** 100 MB
    """
    try:
        # Validate file format
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.pdf', '.docx']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF and DOCX files are supported"
            )
        
        # Validate file size
        file_size_mb = len(await file.read()) / (1024 * 1024)
        await file.seek(0)
        
        if file_size_mb > settings.upload_max_size_mb:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds limit of {settings.upload_max_size_mb}MB"
            )
        
        # Save file
        document_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{document_id}{file_ext}"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Extract text
        if file_ext == '.pdf':
            text_content, page_count = extract_text_from_pdf(str(file_path))
            file_format = "pdf"
        else:
            text_content, page_count = extract_text_from_docx(str(file_path))
            file_format = "docx"
        
        # Store in database
        document = Document(
            id=document_id,
            filename=file.filename,
            file_path=str(file_path),
            format=file_format,
            text_content=text_content,
            page_count=page_count
        )
        
        session.add(document)
        await session.commit()
        await session.refresh(document)
        
        logger.info(f"✅ Script uploaded: {document_id} - {file.filename} ({page_count} pages)")
        
        return UploadResponse(
            document_id=document_id,
            filename=file.filename,
            format=file_format,
            page_count=page_count,
            uploaded_at=document.uploaded_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ Upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


# ============== GET SCRIPT ==============
@router.get("/{document_id}")
async def get_script(
    document_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Get uploaded script details
    """
    try:
        result = await session.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalars().first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        return {
            "id": document.id,
            "filename": document.filename,
            "format": document.format,
            "page_count": document.page_count,
            "uploaded_at": document.uploaded_at,
            "text_length": len(document.text_content) if document.text_content else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching script: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


# ============== DELETE SCRIPT ==============
@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_script(
    document_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Delete an uploaded script
    """
    try:
        result = await session.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalars().first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        # Delete file
        try:
            Path(document.file_path).unlink()
        except:
            logger.warning(f"Could not delete file: {document.file_path}")
        
        # Delete from database
        await session.delete(document)
        await session.commit()
        
        logger.info(f"🗑️ Document deleted: {document_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ Delete failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete: {str(e)}"
        )
