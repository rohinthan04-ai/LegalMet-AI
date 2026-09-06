from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    Body
)
from sqlalchemy.orm import Session
import os
import shutil

from app.core.security import verify_access_token
from app.db.database import get_db

from app.models.inspection import Inspection
from app.models.inspection_image import InspectionImage
from app.models.structured_data import StructuredData
from app.models.checklist import Checklist
from app.models.evaluation import Evaluation
from app.models.rule_evaluation import RuleEvaluation
from app.models.product_category import ProductCategory
from app.models.report import Report

from app.services.rule_service import get_rules_for_category
from app.services.gemini_service import (
    evaluate_product,
    extract_product_data
)
from app.services.report_service import generate_report_data
from app.services.pdf_service import generate_pdf

from fastapi.responses import StreamingResponse


router = APIRouter(
    prefix="/inspections",
    tags=["Inspections"]
)


# ============================================================
# CREATE INSPECTION
# ============================================================

@router.post("/")
def create_inspection(
    inspector_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db)
):
    new_inspection = Inspection(
        inspector_id=inspector_id
    )

    db.add(new_inspection)
    db.commit()
    db.refresh(new_inspection)

    return {
        "id": new_inspection.id,
        "inspector_id": new_inspection.inspector_id,
        "status": new_inspection.status,
        "created_at": new_inspection.created_at
    }


# ============================================================
# GET ALL INSPECTIONS
# ============================================================

@router.get("/")
def get_inspections(
    inspector_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db)
):
    inspections = db.query(Inspection).filter(
        Inspection.inspector_id == inspector_id
    ).all()

    return inspections


# ============================================================
# GET PRODUCT CATEGORIES
# IMPORTANT:
# This MUST come before /{inspection_id}
# ============================================================

@router.get("/rule-categories")
def get_rule_categories(
    inspector_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db)
):
    categories = db.query(ProductCategory).order_by(
        ProductCategory.category_id
    ).all()

    return categories


# ============================================================
# GET SINGLE INSPECTION
# ============================================================

@router.get("/{inspection_id}")
def get_inspection(
    inspection_id: int,
    inspector_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db)
):
    inspection = db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.inspector_id == inspector_id
    ).first()

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found"
        )

    return inspection


# ============================================================
# UPLOAD IMAGE + GEMINI PRODUCT EXTRACTION
# ============================================================

@router.post("/{inspection_id}/images")
def upload_inspection_image(
    inspection_id: int,
    image_type: str = Form(...),
    image: UploadFile = File(...),
    inspector_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db)
):

    # ==========================================
    # 1. Verify inspection
    # ==========================================

    inspection = db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.inspector_id == inspector_id
    ).first()

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found"
        )

    # ==========================================
    # 2. Save image
    # ==========================================

    upload_folder = "uploads"

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    file_path = os.path.join(
        upload_folder,
        image.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            image.file,
            buffer
        )

    # ==========================================
    # 3. Save image record
    # ==========================================

    new_image = InspectionImage(
        inspection_id=inspection_id,
        image_path=file_path,
        image_type=image_type
    )

    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    # ==========================================
    # 4. Send image to Gemini
    # ==========================================

    try:

        structured_product_data = extract_product_data(
            file_path
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Gemini extraction failed: {str(exc)}"
        )

    # ==========================================
    # 5. Check if structured data already exists
    # ==========================================

    existing_data = db.query(
        StructuredData
    ).filter(
        StructuredData.inspection_id == inspection_id
    ).first()

    if existing_data:

        # Update existing structured data
        existing_data.ocr_data = structured_product_data

        db.commit()
        db.refresh(existing_data)

        structured_data_record = existing_data

    else:

        # Create new structured data record
        new_structured_data = StructuredData(
            inspection_id=inspection_id,
            ocr_data=structured_product_data
        )

        db.add(new_structured_data)

        db.commit()
        db.refresh(new_structured_data)

        structured_data_record = new_structured_data

    # ==========================================
    # 6. Return everything
    # ==========================================

    return {
        "message": "Image uploaded and product data extracted successfully",

        "image": {
            "image_id": new_image.id,
            "inspection_id": new_image.inspection_id,
            "image_type": new_image.image_type,
            "image_path": new_image.image_path,
            "uploaded_at": new_image.uploaded_at
        },

        "structured_data": {
            "id": structured_data_record.id,
            "inspection_id": structured_data_record.inspection_id,
            "ocr_data": structured_data_record.ocr_data,
            "created_at": structured_data_record.created_at
        }
    }


# ============================================================
# GET INSPECTION IMAGES
# ============================================================

@router.get("/{inspection_id}/images")
def get_inspection_images(
    inspection_id: int,
    inspector_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db)
):

    inspection = db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.inspector_id == inspector_id
    ).first()

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found"
        )

    images = db.query(
        InspectionImage
    ).filter(
        InspectionImage.inspection_id == inspection_id
    ).all()

    return images


# ============================================================
# CREATE / UPDATE STRUCTURED DATA
# ============================================================

@router.post("/{inspection_id}/structured-data")
def create_structured_data(
    inspection_id: int,
    ocr_data: dict = Body(...),
    inspector_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db)
):

    inspection = db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.inspector_id == inspector_id
    ).first()

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found"
        )

    existing_data = db.query(
        StructuredData
    ).filter(
        StructuredData.inspection_id == inspection_id
    ).first()

    if existing_data:

        # Update existing Gemini data
        existing_data.ocr_data = ocr_data

        db.commit()
        db.refresh(existing_data)

        return existing_data

    # Create structured data if it does not exist

    new_data = StructuredData(
        inspection_id=inspection_id,
        ocr_data=ocr_data
    )

    db.add(new_data)
    db.commit()
    db.refresh(new_data)

    return new_data


# ============================================================
# CREATE CHECKLIST
# ============================================================

@router.post("/{inspection_id}/checklist")
def create_checklist(
    inspection_id: int,
    category_code: str = Body(..., embed=True),
    inspector_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db)
):

    inspection = db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.inspector_id == inspector_id
    ).first()

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found"
        )

    existing_checklist = db.query(
        Checklist
    ).filter(
        Checklist.inspection_id == inspection_id
    ).first()

    if existing_checklist:
        raise HTTPException(
            status_code=400,
            detail="Checklist already exists for this inspection"
        )

    rules = get_rules_for_category(
        category_code,
        db
    )

    if not rules:
        raise HTTPException(
            status_code=404,
            detail="No rules found for this category"
        )

    new_checklist = Checklist(
        inspection_id=inspection_id,
        rules={
            "category_code": category_code,
            "rules": rules
        }
    )

    db.add(new_checklist)
    db.commit()
    db.refresh(new_checklist)

    return new_checklist


# ============================================================
# GET CHECKLIST
# ============================================================

@router.get("/{inspection_id}/checklist")
def get_checklist(
    inspection_id: int,
    inspector_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db)
):

    inspection = db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.inspector_id == inspector_id
    ).first()

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found"
        )

    checklist = db.query(
        Checklist
    ).filter(
        Checklist.inspection_id == inspection_id
    ).first()

    if not checklist:
        raise HTTPException(
            status_code=404,
            detail="Checklist not found for this inspection"
        )

    return checklist


# ============================================================
# GET STRUCTURED DATA
# ============================================================

@router.get("/{inspection_id}/structured-data")
def get_structured_data(
    inspection_id: int,
    inspector_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db)
):

    inspection = db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.inspector_id == inspector_id
    ).first()

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found"
        )

    structured_data = db.query(
        StructuredData
    ).filter(
        StructuredData.inspection_id == inspection_id
    ).first()

    if not structured_data:
        raise HTTPException(
            status_code=404,
            detail="Structured data not found"
        )

    return structured_data


# ============================================================
# CREATE EVALUATION
# ============================================================

@router.post("/{inspection_id}/evaluation")
def create_evaluation(
    inspection_id: int,
    inspector_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db)
):

    # ==========================================
    # 1. Verify inspection belongs to inspector
    # ==========================================

    inspection = db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.inspector_id == inspector_id
    ).first()

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found"
        )

    # ==========================================
    # 2. Check if evaluation already exists
    # ==========================================

    existing_evaluation = db.query(
        Evaluation
    ).filter(
        Evaluation.inspection_id == inspection_id
    ).first()

    if existing_evaluation:
        raise HTTPException(
            status_code=400,
            detail="Evaluation already exists for this inspection"
        )

    # ==========================================
    # 3. Get structured data
    # ==========================================

    structured_data = db.query(
        StructuredData
    ).filter(
        StructuredData.inspection_id == inspection_id
    ).first()

    if not structured_data:
        raise HTTPException(
            status_code=404,
            detail="Structured data not found"
        )

    # ==========================================
    # 4. Get checklist
    # ==========================================

    checklist = db.query(
        Checklist
    ).filter(
        Checklist.inspection_id == inspection_id
    ).first()

    if not checklist:
        raise HTTPException(
            status_code=404,
            detail="Checklist not found"
        )

    # ==========================================
    # 5. Send structured data + checklist to Gemini
    # ==========================================

    gemini_result = evaluate_product(
        structured_data=structured_data.ocr_data,
        checklist=checklist.rules
    )

    # ==========================================
    # 6. Get overall result
    # ==========================================

    overall_status = gemini_result.get(
        "overall_status"
    )

    if not overall_status:
        raise HTTPException(
            status_code=500,
            detail="Gemini did not return overall_status"
        )

    # ==========================================
    # 7. Create Evaluation record
    # ==========================================

    new_evaluation = Evaluation(
        inspection_id=inspection_id,
        result=overall_status
    )

    db.add(new_evaluation)
    db.flush()

    # ==========================================
    # 8. Get rule evaluations from Gemini
    # ==========================================

    rule_evaluations = gemini_result.get(
        "rule_evaluations",
        []
    )

    # ==========================================
    # 9. Store every rule evaluation
    # ==========================================

    for rule in rule_evaluations:

        rule_id = rule.get("rule_id")
        status = rule.get("status")
        evidence = rule.get("evidence")
        details = rule.get("details")

        if rule_id is None:
            continue

        if status is None:
            continue

        if evidence is None:
            evidence = ""

        if details is None:
            details = ""

        new_rule_evaluation = RuleEvaluation(
            evaluation_id=new_evaluation.id,
            rule_id=str(rule_id),
            status=status,
            evidence=evidence,
            details=details
        )

        db.add(new_rule_evaluation)

    # ==========================================
    # 10. Save everything
    # ==========================================

    db.commit()

    # ==========================================
    # 11. Refresh evaluation
    # ==========================================

    db.refresh(new_evaluation)

    return {
        "inspection_id": inspection_id,
        "evaluation_id": new_evaluation.id,
        "overall_status": overall_status,
        "rule_evaluations": rule_evaluations
    }


# ============================================================
# CREATE INDIVIDUAL RULE EVALUATION
# ============================================================

@router.post("/{inspection_id}/evaluation/rules")
def create_rule_evaluation(
    inspection_id: int,
    rule_result: dict = Body(...),
    inspector_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db)
):

    inspection = db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.inspector_id == inspector_id
    ).first()

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found"
        )

    evaluation = db.query(
        Evaluation
    ).filter(
        Evaluation.inspection_id == inspection_id
    ).first()

    if not evaluation:
        raise HTTPException(
            status_code=404,
            detail="Evaluation not found for this inspection"
        )

    rule_id = rule_result.get("rule_id")
    status = rule_result.get("status")
    evidence = rule_result.get("evidence")
    details = rule_result.get("details")

    if (
        not rule_id
        or not status
        or evidence is None
        or not details
    ):
        raise HTTPException(
            status_code=400,
            detail="rule_id, status, evidence and details are required"
        )

    new_rule_evaluation = RuleEvaluation(
        evaluation_id=evaluation.id,
        rule_id=rule_id,
        status=status,
        evidence=evidence,
        details=details
    )

    db.add(new_rule_evaluation)
    db.commit()
    db.refresh(new_rule_evaluation)

    return new_rule_evaluation


# ============================================================
# CREATE REPORT
# ============================================================

@router.post("/{inspection_id}/report")
def create_report(
    inspection_id: int,
    inspector_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db)
):

    inspection = db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.inspector_id == inspector_id
    ).first()

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found"
        )

    existing_report = db.query(
        Report
    ).filter(
        Report.inspection_id == inspection_id
    ).first()

    if existing_report:
        raise HTTPException(
            status_code=400,
            detail="Report already exists for this inspection"
        )

    try:

        report_data = generate_report_data(
            inspection_id,
            db
        )

        new_report = Report(
            inspection_id=inspection_id,
            report_data=report_data
        )

        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        return new_report

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )


# ============================================================
# GET REPORT
# ============================================================

@router.get("/{inspection_id}/report")
def get_report(
    inspection_id: int,
    inspector_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db)
):

    inspection = db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.inspector_id == inspector_id
    ).first()

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found"
        )

    report = db.query(
        Report
    ).filter(
        Report.inspection_id == inspection_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return report


# ============================================================
# DOWNLOAD REPORT PDF
# ============================================================

@router.get("/{inspection_id}/report/pdf")
def download_report_pdf(
    inspection_id: int,
    inspector_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db)
):

    inspection = db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.inspector_id == inspector_id
    ).first()

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found"
        )

    report = db.query(
        Report
    ).filter(
        Report.inspection_id == inspection_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    pdf_buffer = generate_pdf(
        report.report_data
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f"attachment; filename=inspection_report_{inspection_id}.pdf"
        }
    )