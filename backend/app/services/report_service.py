from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.models.structured_data import StructuredData
from app.models.checklist import Checklist
from app.models.evaluation import Evaluation
from app.models.rule_evaluation import RuleEvaluation


def generate_report_data(
    inspection_id: int,
    db: Session
) -> dict:

    # Get inspection
    inspection = db.query(Inspection).filter(
        Inspection.id == inspection_id
    ).first()

    if not inspection:
        raise ValueError("Inspection not found")

    # Get structured product data
    structured_data = db.query(StructuredData).filter(
        StructuredData.inspection_id == inspection_id
    ).first()

    if not structured_data:
        raise ValueError("Structured data not found")

    # Get checklist
    checklist = db.query(Checklist).filter(
        Checklist.inspection_id == inspection_id
    ).first()

    if not checklist:
        raise ValueError("Checklist not found")

    # Get evaluation
    evaluation = db.query(Evaluation).filter(
        Evaluation.inspection_id == inspection_id
    ).first()

    if not evaluation:
        raise ValueError("Evaluation not found")

    # Get all rule evaluations
    rule_evaluations = db.query(RuleEvaluation).filter(
        RuleEvaluation.evaluation_id == evaluation.id
    ).all()

    # Count results
    total_rules = len(rule_evaluations)

    passed_rules = sum(
        1 for rule in rule_evaluations
        if rule.status.upper() == "PASS"
    )

    failed_rules = sum(
        1 for rule in rule_evaluations
        if rule.status.upper() == "FAIL"
    )

    # Build rule-by-rule report
    rule_results = []

    for rule in rule_evaluations:
        rule_results.append({
            "rule_id": rule.rule_id,
            "status": rule.status,
            "evidence": rule.evidence,
            "details": rule.details
        })

    # Build final report
    report_data = {
        "inspection_id": inspection.id,

        "inspection": {
            "inspector_id": inspection.inspector_id,
            "status": inspection.status,
            "created_at": inspection.created_at.isoformat()
            if inspection.created_at else None
        },

        "product_data": structured_data.ocr_data,

        "checklist": checklist.rules,

        "compliance_summary": {
            "overall_status": evaluation.result,
            "total_rules": total_rules,
            "passed_rules": passed_rules,
            "failed_rules": failed_rules
        },

        "rule_evaluations": rule_results,

        "final_conclusion": (
            "The product complies with all evaluated rules."
            if evaluation.result.upper() == "PASS"
            else "The product has one or more non-compliant rules."
        )
    }

    return report_data