import re


def extract_fields(text):
    """
    Extract common packaged-commodity fields
    from OCR text.

    This is the initial rule-based extractor.
    Later we can improve it using more advanced
    NLP/LLM techniques.
    """

    fields = {
        "product_name": None,
        "mrp": None,
        "net_quantity": None,
        "lot_number": None,
        "packaging_date": None,
        "expiry_date": None,
        "manufacturer": None,
        "fssai_number": None
    }

    # Normalize text
    normalized_text = text.replace(
        "\n",
        " "
    )

    # ------------------------------------------------
    # MRP
    # ------------------------------------------------

    mrp_pattern = re.search(
        r"(?:MRP|M\.R\.P)[^\d]{0,20}"
        r"(?:₹|Rs\.?|INR)?\s*"
        r"(\d+(?:\.\d{1,2})?)",
        normalized_text,
        re.IGNORECASE
    )

    if mrp_pattern:
        fields["mrp"] = float(
            mrp_pattern.group(1)
        )

    # ------------------------------------------------
    # NET QUANTITY
    # ------------------------------------------------

    quantity_pattern = re.search(
        r"(?:Net\s*(?:Wt|Weight|Qty|Quantity)?"
        r"|Net\s*Content)"
        r"[^\d]{0,20}"
        r"(\d+(?:\.\d+)?)\s*"
        r"(kg|g|gm|gram|grams|ml|l|litre|liter)",
        normalized_text,
        re.IGNORECASE
    )

    if quantity_pattern:

        value = float(
            quantity_pattern.group(1)
        )

        unit = quantity_pattern.group(2)

        fields["net_quantity"] = {
            "value": value,
            "unit": unit
        }

    # ------------------------------------------------
    # LOT / BATCH NUMBER
    # ------------------------------------------------

    lot_pattern = re.search(
        r"(?:Lot\s*(?:No|Number)?"
        r"|Batch\s*(?:No|Number)?)"
        r"\s*[:\-]?\s*"
        r"([A-Za-z0-9\-\/]+)",
        normalized_text,
        re.IGNORECASE
    )

    if lot_pattern:
        fields["lot_number"] = (
            lot_pattern.group(1)
        )

    # ------------------------------------------------
    # PACKAGING DATE
    # ------------------------------------------------

    packaging_pattern = re.search(
        r"(?:Date\s*of\s*Packaging"
        r"|Packed\s*on"
        r"|Packing\s*Date)"
        r"\s*[:\-]?\s*"
        r"([A-Za-z0-9\/\-\s]+?)(?=\s"
        r"(?:Use|Best|Expiry|MRP|Lot|Batch)"
        r"|$)",
        normalized_text,
        re.IGNORECASE
    )

    if packaging_pattern:

        fields["packaging_date"] = (
            packaging_pattern.group(1).strip()
        )

    # ------------------------------------------------
    # EXPIRY / USE-BY DATE
    # ------------------------------------------------

    expiry_pattern = re.search(
        r"(?:Use\s*By"
        r"|Best\s*Before"
        r"|Expiry"
        r"|Expires)"
        r"\s*[:\-]?\s*"
        r"([A-Za-z0-9\/\-\s]+?)(?=\s"
        r"(?:MRP|Lot|Batch|Net|$)"
        r"|$)",
        normalized_text,
        re.IGNORECASE
    )

    if expiry_pattern:

        fields["expiry_date"] = (
            expiry_pattern.group(1).strip()
        )

    # ------------------------------------------------
    # FSSAI NUMBER
    # ------------------------------------------------

    fssai_pattern = re.search(
        r"(?:FSSAI)"
        r"[^\d]{0,20}"
        r"(\d{14})",
        normalized_text,
        re.IGNORECASE
    )

    if fssai_pattern:

        fields["fssai_number"] = (
            fssai_pattern.group(1)
        )

    # ------------------------------------------------
    # PRODUCT NAME
    # ------------------------------------------------

    # Very simple initial approach:
    # assume the first meaningful OCR line
    # is the product name.

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if lines:
        fields["product_name"] = lines[0]

    return fields