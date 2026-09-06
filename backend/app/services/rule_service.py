from sqlalchemy import text
from sqlalchemy.orm import Session


def get_rules_for_category(
    category_code: str,
    db: Session
):
    query = text("""
        SELECT
            r.rule_id,
            r.rule_code,
            r.rule_name,
            r.rule_json,
            crm.applicability,
            crm.notes
        FROM product_categories pc
        JOIN category_rule_mapping crm
            ON pc.category_id = crm.category_id
        JOIN rules r
            ON crm.rule_id = r.rule_id
        WHERE pc.category_code = :category_code
          AND r.is_active = TRUE
        ORDER BY r.rule_id
    """)

    result = db.execute(
        query,
        {"category_code": category_code}
    )

    rules = []

    for row in result:
        rules.append({
            "rule_id": row.rule_id,
            "rule_code": row.rule_code,
            "rule_name": row.rule_name,
            "rule": row.rule_json,
            "applicability": row.applicability,
            "notes": row.notes
        })

    return rules