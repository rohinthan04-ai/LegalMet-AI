from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


def generate_pdf(report_data: dict) -> BytesIO:
    """
    Generate a PDF from the report_data stored in the database.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "NormalCustom",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
    )

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "LEGAL METROLOGY INSPECTION REPORT",
            title_style
        )
    )

    story.append(Spacer(1, 10))

    # --------------------------------------------------
    # INSPECTION INFORMATION
    # --------------------------------------------------

    inspection = report_data.get("inspection", {})

    inspection_table = Table(
        [
            ["Inspection ID", str(report_data.get("inspection_id", ""))],
            ["Inspector ID", str(inspection.get("inspector_id", ""))],
            ["Inspection Status", str(inspection.get("status", ""))],
            ["Created At", str(inspection.get("created_at", ""))],
        ],
        colWidths=[150, 330],
    )

    inspection_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )

    story.append(inspection_table)

    # --------------------------------------------------
    # COMPLIANCE SUMMARY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Compliance Summary",
            heading_style
        )
    )

    summary = report_data.get(
        "compliance_summary",
        {}
    )

    summary_table = Table(
        [
            ["Overall Status", str(summary.get("overall_status", ""))],
            ["Total Rules", str(summary.get("total_rules", 0))],
            ["Passed Rules", str(summary.get("passed_rules", 0))],
            ["Failed Rules", str(summary.get("failed_rules", 0))],
        ],
        colWidths=[150, 330],
    )

    summary_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )

    story.append(summary_table)

    # --------------------------------------------------
    # PRODUCT DATA
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Product Information",
            heading_style
        )
    )

    product_data = report_data.get(
        "product_data",
        {}
    )

    product_rows = []

    for key, value in product_data.items():
        product_rows.append([
            Paragraph(str(key), normal_style),
            Paragraph(str(value), normal_style),
        ])

    if product_rows:
        product_table = Table(
            product_rows,
            colWidths=[150, 330],
        )

        product_table.setStyle(
            TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ])
        )

        story.append(product_table)

    # --------------------------------------------------
    # RULE EVALUATIONS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Rule-by-Rule Evaluation",
            heading_style
        )
    )

    rule_evaluations = report_data.get(
        "rule_evaluations",
        []
    )

    for index, rule in enumerate(rule_evaluations, start=1):

        rule_id = rule.get("rule_id", "")
        status = rule.get("status", "")
        evidence = rule.get("evidence", "")
        details = rule.get("details", "")

        story.append(
            Paragraph(
                f"<b>Rule {rule_id}</b>",
                styles["Heading3"]
            )
        )

        rule_table = Table(
            [
                ["Status", str(status)],
                ["Evidence", Paragraph(str(evidence), normal_style)],
                ["Details", Paragraph(str(details), normal_style)],
            ],
            colWidths=[100, 380],
        )

        rule_table.setStyle(
            TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ])
        )

        story.append(rule_table)
        story.append(Spacer(1, 10))

    # --------------------------------------------------
    # FINAL CONCLUSION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Final Conclusion",
            heading_style
        )
    )

    conclusion = report_data.get(
        "final_conclusion",
        ""
    )

    story.append(
        Paragraph(
            str(conclusion),
            normal_style
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer