"""
Reports API Router - Generate PDF reports
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging
from pathlib import Path
from datetime import datetime
import json

from app.database import get_db
from app.models.database import Run, Report, Project, RunStatus, Scene, SceneExtraction, SceneRisk, SceneCost, CrossSceneInsight
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Ensure reports directory exists
REPORTS_DIR = Path(settings.storage_path) / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


async def generate_pdf_report(run_id: str, session: AsyncSession) -> str:
    """
    Generate comprehensive PDF report for a run with all analysis data
    Returns: Path to generated PDF
    """
    try:
        # Import here to avoid issues if reportlab not installed
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        
        # Get run details with scenes relationship eagerly loaded
        run_result = await session.execute(
            select(Run)
            .options(selectinload(Run.scenes))  # Eagerly load scenes to avoid async greenlet error
            .where(Run.id == run_id)
        )
        run = run_result.scalars().first()
        
        if not run:
            raise ValueError(f"Run {run_id} not found")
        
        # Parse enhanced result JSON
        enhanced_data = run.enhanced_result_json or {}
        executive_summary = enhanced_data.get("LAYER_12_executive_summary", {})
        scenes_analysis = enhanced_data.get("scenes_analysis", {})
        risk_intelligence = enhanced_data.get("risk_intelligence", {})
        production_recommendations = enhanced_data.get("production_recommendations", {})
        
        # Fetch all scenes with their data
        scenes_result = await session.execute(
            select(Scene).where(Scene.run_id == run_id).order_by(Scene.scene_number)
        )
        all_scenes = scenes_result.scalars().all()
        
        # Fetch scene data (extractions, risks, costs)
        scene_data_list = []
        for scene in all_scenes:
            extraction_result = await session.execute(
                select(SceneExtraction).where(SceneExtraction.scene_id == scene.id)
            )
            extraction = extraction_result.scalars().first()
            
            risk_result = await session.execute(
                select(SceneRisk).where(SceneRisk.scene_id == scene.id)
            )
            risk = risk_result.scalars().first()
            
            cost_result = await session.execute(
                select(SceneCost).where(SceneCost.scene_id == scene.id)
            )
            cost = cost_result.scalars().first()
            
            scene_data_list.append({
                'scene': scene,
                'extraction': extraction,
                'risk': risk,
                'cost': cost
            })
        
        # Fetch cross-scene insights
        insights_result = await session.execute(
            select(CrossSceneInsight).where(CrossSceneInsight.run_id == run_id)
        )
        insights = insights_result.scalars().all()
        
        # Helper function to format currency
        def format_currency(amount):
            if amount is None or amount == 0:
                return "₹0"
            if amount >= 10000000:  # >= 1 crore
                return f"₹{amount/10000000:.2f}Cr"
            elif amount >= 100000:  # >= 1 lakh
                return f"₹{amount/100000:.2f}L"
            else:
                return f"₹{amount:,.0f}"
        
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
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#2E5C8A'),
            spaceAfter=8,
            spaceBefore=8
        )
        
        elements = []
        
        # ========== TITLE PAGE ==========
        elements.append(Paragraph("ShootSafe AI - Production Analysis Report", title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Project Info
        elements.append(Paragraph("Project Information", heading_style))
        
        project_info = [
            ["Project Name:", "Film Production"],
            ["Location:", "India"],
            ["Scale:", "Standard"],
            ["Language:", "English"],
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
        
        total_scenes = len(all_scenes) if all_scenes else 0
        high_risk_count = risk_intelligence.get("high_risk_count", 0)
        
        summary_text = f"""
        <b>Run ID:</b> {run.id[:8]}... <br/>
        <b>Status:</b> {run.status.value.upper() if run.status else 'UNKNOWN'} <br/>
        <b>Total Scenes:</b> {total_scenes} <br/>
        <b>High-Risk Scenes:</b> {high_risk_count} <br/>
        <b>Started:</b> {run.started_at.strftime('%Y-%m-%d %H:%M:%S') if run.started_at else 'N/A'} <br/>
        <b>Completed:</b> {run.completed_at.strftime('%Y-%m-%d %H:%M:%S') if run.completed_at else 'N/A'} <br/>
        """
        
        elements.append(Paragraph(summary_text, styles['Normal']))
        elements.append(PageBreak())
        
        # ========== EXECUTIVE SUMMARY ==========
        elements.append(Paragraph("Executive Summary", heading_style))
        
        original_budget = executive_summary.get("original_budget_likely", run.optimized_budget_likely or 0)
        optimized_budget = executive_summary.get("optimized_budget_likely", run.optimized_budget_likely or 0)
        total_savings = executive_summary.get("total_savings", run.total_optimization_savings or 0)
        savings_percent = executive_summary.get("savings_percent", 0)
        schedule_original = executive_summary.get("schedule_original_days", 0)
        schedule_optimized = executive_summary.get("schedule_optimized_days", 0)
        schedule_compression = executive_summary.get("schedule_savings_percent", run.schedule_savings_percent or 0)
        
        exec_summary_data = [
            ["Metric", "Value"],
            ["Original Budget (Likely)", format_currency(original_budget)],
            ["Optimized Budget (Likely)", format_currency(optimized_budget)],
            ["Total Savings", format_currency(total_savings)],
            ["Savings Percentage", f"{savings_percent:.1f}%"],
            ["Original Schedule", f"{schedule_original} days"],
            ["Optimized Schedule", f"{schedule_optimized} days"],
            ["Schedule Compression", f"{schedule_compression:.1f}%"],
        ]
        
        exec_table = Table(exec_summary_data, colWidths=[3*inch, 3*inch])
        exec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(exec_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # ========== BUDGET ANALYSIS ==========
        elements.append(Paragraph("Budget Analysis", heading_style))
        
        budget_min = executive_summary.get("optimized_budget_min", run.optimized_budget_min or 0)
        budget_likely = optimized_budget
        budget_max = executive_summary.get("optimized_budget_max", run.optimized_budget_max or 0)
        
        budget_data = [
            ["Budget Type", "Amount"],
            ["Minimum Budget", format_currency(budget_min)],
            ["Likely Budget", format_currency(budget_likely)],
            ["Maximum Budget", format_currency(budget_max)],
            ["Budget Range", format_currency(budget_max - budget_min)],
        ]
        
        budget_table = Table(budget_data, colWidths=[3*inch, 3*inch])
        budget_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E5C8A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(budget_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # ========== RISK ASSESSMENT ==========
        elements.append(Paragraph("Risk Assessment", heading_style))
        
        # High-risk scenes
        high_risk_scenes = []
        for scene_data in scene_data_list:
            if scene_data['risk'] and scene_data['risk'].total_risk_score > 65:
                high_risk_scenes.append({
                    'number': scene_data['scene'].scene_number,
                    'heading': scene_data['scene'].heading or 'N/A',
                    'risk_score': scene_data['risk'].total_risk_score,
                    'location': scene_data['scene'].location or 'N/A'
                })
        
        if high_risk_scenes:
            elements.append(Paragraph(f"High-Risk Scenes ({len(high_risk_scenes)})", subheading_style))
            
            risk_table_data = [["Scene", "Heading", "Risk Score", "Location"]]
            for hr in high_risk_scenes[:10]:  # Limit to top 10
                risk_table_data.append([
                    str(hr['number']),
                    hr['heading'][:30] + '...' if len(hr['heading']) > 30 else hr['heading'],
                    f"{hr['risk_score']:.0f}",
                    hr['location'][:20] + '...' if len(hr['location']) > 20 else hr['location']
                ])
            
            risk_table = Table(risk_table_data, colWidths=[0.8*inch, 2*inch, 1*inch, 2.2*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DC2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            elements.append(risk_table)
        else:
            elements.append(Paragraph("No high-risk scenes identified.", styles['Normal']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # ========== SCHEDULE OPTIMIZATION ==========
        elements.append(Paragraph("Schedule Optimization", heading_style))
        
        schedule_data = [
            ["Metric", "Value"],
            ["Original Schedule", f"{schedule_original} days"],
            ["Optimized Schedule", f"{schedule_optimized} days"],
            ["Days Saved", f"{schedule_original - schedule_optimized} days"],
            ["Compression Percentage", f"{schedule_compression:.1f}%"],
        ]
        
        schedule_table = Table(schedule_data, colWidths=[3*inch, 3*inch])
        schedule_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(schedule_table)
        elements.append(PageBreak())
        
        # ========== SCENE-BY-SCENE ANALYSIS ==========
        elements.append(Paragraph("Scene-by-Scene Analysis", heading_style))
        
        # Limit to first 20 scenes to avoid PDF being too large
        scenes_to_show = scene_data_list[:20]
        
        scene_table_data = [["Scene", "Location", "Budget (Likely)", "Risk Score", "Status"]]
        for scene_data in scenes_to_show:
            scene = scene_data['scene']
            cost = scene_data['cost']
            risk = scene_data['risk']
            
            budget_val = format_currency(cost.cost_likely) if cost and cost.cost_likely else "N/A"
            risk_val = f"{risk.total_risk_score:.0f}" if risk and risk.total_risk_score else "N/A"
            location = scene.location or "N/A"
            status = "High Risk" if (risk and risk.total_risk_score > 65) else "Normal"
            
            scene_table_data.append([
                str(scene.scene_number),
                location[:25] + '...' if len(location) > 25 else location,
                budget_val,
                risk_val,
                status
            ])
        
        scene_table = Table(scene_table_data, colWidths=[0.8*inch, 2*inch, 1.2*inch, 1*inch, 1*inch])
        scene_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(scene_table)
        if len(scene_data_list) > 20:
            elements.append(Paragraph(f"<i>Showing first 20 of {len(scene_data_list)} scenes. See dashboard for complete list.</i>", styles['Normal']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # ========== LOCATION INTELLIGENCE ==========
        if insights:
            elements.append(Paragraph("Location Intelligence", heading_style))
            
            location_insights = [i for i in insights if i.insight_type == "LOCATION_CHAIN"]
            
            if location_insights:
                location_data = [["Location", "Scenes", "Recommendation"]]
                for insight in location_insights[:5]:  # Top 5
                    scene_ids = json.loads(insight.scene_ids) if isinstance(insight.scene_ids, str) else insight.scene_ids
                    location_data.append([
                        insight.problem_description[:30] + '...' if len(insight.problem_description) > 30 else insight.problem_description,
                        str(len(scene_ids)),
                        insight.recommendation[:40] + '...' if len(insight.recommendation) > 40 else insight.recommendation
                    ])
                
                location_table = Table(location_data, colWidths=[2*inch, 1*inch, 3*inch])
                location_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7C3AED')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey)
                ]))
                
                elements.append(location_table)
            else:
                elements.append(Paragraph("No location clustering insights available.", styles['Normal']))
            
            elements.append(Spacer(1, 0.3*inch))
        
        # ========== PRODUCER RECOMMENDATIONS ==========
        elements.append(Paragraph("Producer Recommendations", heading_style))
        
        recommendations_list = production_recommendations.get("recommendations", [])
        if recommendations_list:
            for idx, rec in enumerate(recommendations_list[:10], 1):  # Top 10
                priority = rec.get("priority", "Medium")
                recommendation = rec.get("recommendation", "")
                impact = rec.get("budget_impact", "")
                risk_reduction = rec.get("risk_reduction", "")
                
                rec_text = f"""
                <b>{idx}. [{priority}]</b> {recommendation} <br/>
                <i>Budget Impact: {impact} | Risk Reduction: {risk_reduction}</i>
                """
                elements.append(Paragraph(rec_text, styles['Normal']))
                elements.append(Spacer(1, 0.15*inch))
        else:
            # Fallback generic recommendations
            generic_recs = [
                "Review high-risk scenes and implement recommended safety protocols.",
                "Use provided budget ranges for contingency planning (typically 15-20% above likely estimate).",
                "Consider identified location chains to minimize travel and setup time.",
                "Plan crew rotations to avoid fatigue clusters identified in cross-scene analysis.",
                "Use scenario planning tools to evaluate budget cuts, timeline acceleration, or safety enhancements."
            ]
            for idx, rec in enumerate(generic_recs, 1):
                elements.append(Paragraph(f"{idx}. {rec}", styles['Normal']))
                elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # ========== FOOTER ==========
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
            project_id=run_id,  # Use run_id as project_id (Run model doesn't have project_id)
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
