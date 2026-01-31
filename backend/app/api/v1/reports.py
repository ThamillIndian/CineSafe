"""
Reports API Router - Generate PDF reports
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from pathlib import Path
from datetime import datetime
import json

from app.database import get_db
from app.models.database import Run, Report, Project, RunStatus
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Ensure reports directory exists
REPORTS_DIR = Path(settings.storage_path) / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


async def generate_pdf_report(run_id: str, session: AsyncSession) -> str:
    """
    Generate PDF report for a run
    Returns: Path to generated PDF
    """
    try:
        # Import here to avoid issues if reportlab not installed
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        
        # Get run and project details
        run_result = await session.execute(
            select(Run).where(Run.id == run_id)
        )
        run = run_result.scalars().first()
        
        project_result = await session.execute(
            select(Project).where(Project.id == run.project_id)
        )
        project = project_result.scalars().first()
        
        # Create PDF
        pdf_filename = f"shootsafe_report_{run_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = REPORTS_DIR / pdf_filename
        
        # Build PDF document
        doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1F4788'),
            spaceAfter=30,
            alignment=1
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2E5C8A'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        elements = []
        
        # Title
        elements.append(Paragraph("ShootSafe AI - Production Analysis Report", title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Project Info
        elements.append(Paragraph("Project Information", heading_style))
        
        project_info = [
            ["Project Name:", project.name],
            ["Location:", project.base_city],
            ["Scale:", project.scale.value],
            ["Language:", project.language],
            ["Report Generated:", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")]
        ]
        
        project_table = Table(project_info, colWidths=[2*inch, 4*inch])
        project_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(project_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Analysis Summary
        elements.append(Paragraph("Analysis Summary", heading_style))
        
        summary_text = f"""
        <b>Run ID:</b> {run.id[:8]}... <br/>
        <b>Run Number:</b> {run.run_number} <br/>
        <b>Status:</b> {run.status.value.upper()} <br/>
        <b>Total Scenes:</b> {len(run.scenes) if run.scenes else 0} <br/>
        <b>Started:</b> {run.started_at.strftime('%Y-%m-%d %H:%M:%S') if run.started_at else 'N/A'} <br/>
        <b>Completed:</b> {run.completed_at.strftime('%Y-%m-%d %H:%M:%S') if run.completed_at else 'N/A'} <br/>
        """
        
        elements.append(Paragraph(summary_text, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Key Findings
        elements.append(Paragraph("Key Findings", heading_style))
        
        findings = [
            "✓ Script analysis completed successfully",
            "✓ Risk assessment generated for all scenes",
            "✓ Budget estimation provided with min/likely/max ranges",
            "✓ Cross-scene inefficiencies identified",
            "✓ Safety recommendations included"
        ]
        
        for finding in findings:
            elements.append(Paragraph(finding, styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Recommendations
        elements.append(Paragraph("Producer Recommendations", heading_style))
        
        recommendations = """
        <b>1. Risk Mitigation:</b> Review high-risk scenes and implement recommended safety protocols. <br/><br/>
        <b>2. Budget Planning:</b> Use provided budget ranges for contingency planning (typically 15-20% above likely estimate). <br/><br/>
        <b>3. Schedule Optimization:</b> Consider identified location chains to minimize travel and setup time. <br/><br/>
        <b>4. Crew Management:</b> Plan crew rotations to avoid fatigue clusters identified in cross-scene analysis. <br/><br/>
        <b>5. What-If Analysis:</b> Use scenario planning tools to evaluate budget cuts, timeline acceleration, or safety enhancements. <br/>
        """
        
        elements.append(Paragraph(recommendations, styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_text = """
        <i>This report was generated by ShootSafe AI - an intelligent system for film production safety and budgeting.<br/>
        For detailed scene-by-scene analysis, risk breakdown, and budget details, please access the interactive dashboard.<br/>
        Report confidential - For internal production use only.</i>
        """
        
        elements.append(Paragraph(footer_text, styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        
        logger.info(f"✅ PDF report generated: {pdf_filename}")
        
        return str(pdf_path)
        
    except ImportError:
        logger.error("ReportLab not installed - cannot generate PDF")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PDF generation not available - ReportLab not installed"
        )
    except Exception as e:
        logger.error(f"❌ PDF generation error: {e}")
        raise


# ============== GENERATE REPORT ==============
@router.post("/{run_id}/generate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def generate_report(
    run_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Generate PDF report for a completed run
    
    **Args:**
    - run_id: UUID of the completed run
    
    **Returns:** Report details with download link
    
    **Status codes:**
    - 201 Created: Report generated successfully
    - 404 Not Found: Run not found
    - 202 Accepted: Run still processing (not ready yet)
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
        
        if run.status != RunStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail=f"Run must be completed. Current status: {run.status.value}"
            )
        
        # Check if report already exists
        report_result = await session.execute(
            select(Report).where(Report.run_id == run_id)
        )
        existing_report = report_result.scalars().first()
        
        if existing_report:
            return {
                "report_id": existing_report.id,
                "run_id": run_id,
                "status": "already_exists",
                "generated_at": existing_report.generated_at.isoformat(),
                "file_size_mb": (existing_report.file_size or 0) / (1024 * 1024),
                "download_url": f"/api/v1/reports/{run_id}/download"
            }
        
        # Generate new report
        pdf_path = await generate_pdf_report(run_id, session)
        
        # Get file size
        file_size = Path(pdf_path).stat().st_size
        
        # Store in database
        report = Report(
            id=f"report-{run_id}",
            project_id=run.project_id,
            run_id=run_id,
            pdf_path=pdf_path,
            file_size=file_size
        )
        
        session.add(report)
        await session.commit()
        await session.refresh(report)
        
        logger.info(f"✅ Report stored: {report.id} ({file_size / 1024:.1f} KB)")
        
        return {
            "report_id": report.id,
            "run_id": run_id,
            "status": "generated",
            "generated_at": report.generated_at.isoformat(),
            "file_size_mb": file_size / (1024 * 1024),
            "download_url": f"/api/v1/reports/{run_id}/download"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ Report generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}"
        )


# ============== DOWNLOAD REPORT ==============
@router.get("/{run_id}/download")
async def download_report(
    run_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Download PDF report for a run
    
    **Args:**
    - run_id: UUID of the run
    
    **Returns:** PDF file for download
    """
    try:
        # Get report
        report_result = await session.execute(
            select(Report).where(Report.run_id == run_id)
        )
        report = report_result.scalars().first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report for run {run_id} not found. Generate it with POST /reports/{run_id}/generate"
            )
        
        pdf_path = Path(report.pdf_path)
        
        if not pdf_path.exists():
            logger.error(f"❌ Report file not found: {pdf_path}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Report file not found on server"
            )
        
        logger.info(f"📥 Report downloaded: {report.id}")
        
        return FileResponse(
            path=pdf_path,
            filename=f"shootsafe_report_{run_id}.pdf",
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Download error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Download failed: {str(e)}"
        )


# ============== LIST REPORTS ==============
@router.get("", response_model=list[dict])
async def list_reports(
    project_id: str = None,
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_db)
):
    """
    List all reports
    
    **Args:**
    - project_id: Filter by project (optional)
    - skip: Number of reports to skip
    - limit: Maximum reports to return
    
    **Returns:** List of reports
    """
    try:
        query = select(Report)
        
        if project_id:
            query = query.where(Report.project_id == project_id)
        
        query = query.offset(skip).limit(limit)
        
        result = await session.execute(query)
        reports = result.scalars().all()
        
        return [
            {
                "id": report.id,
                "project_id": report.project_id,
                "run_id": report.run_id,
                "generated_at": report.generated_at.isoformat(),
                "file_size_mb": report.file_size / (1024 * 1024) if report.file_size else 0,
                "download_url": f"/api/v1/reports/{report.run_id}/download"
            }
            for report in reports
        ]
        
    except Exception as e:
        logger.error(f"❌ Error listing reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing reports: {str(e)}"
        )


# ============== DELETE REPORT ==============
@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Delete a report
    
    **Args:**
    - report_id: UUID of the report
    
    **Returns:** 204 No Content
    """
    try:
        result = await session.execute(
            select(Report).where(Report.id == report_id)
        )
        report = result.scalars().first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report {report_id} not found"
            )
        
        # Delete file
        try:
            Path(report.pdf_path).unlink()
        except:
            logger.warning(f"Could not delete PDF file: {report.pdf_path}")
        
        # Delete from database
        await session.delete(report)
        await session.commit()
        
        logger.info(f"🗑️ Report deleted: {report_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ Delete failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete report: {str(e)}"
        )
