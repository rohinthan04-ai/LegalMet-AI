import os
import json
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types
from pydantic import BaseModel, Field


# ============================================================
# GEMINI CLIENT
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Please add it to your .env file."
    )

client = genai.Client(api_key=API_KEY)


# ============================================================
# STRUCTURED OUTPUT SCHEMA
# ============================================================

class ProductData(BaseModel):

    product_name: Optional[str] = Field(
        default=None,
        description="Name or description of the packaged product."
    )

    net_quantity_value: Optional[float] = Field(
        default=None,
        description="Numeric net quantity value, for example 50."
    )

    net_quantity_unit: Optional[str] = Field(
        default=None,
        description="Unit of net quantity, for example g, kg, ml, L."
    )

    mrp: Optional[float] = Field(
        default=None,
        description="Maximum Retail Price in Indian Rupees."
    )

    lot_number: Optional[str] = Field(
        default=None,
        description="Batch or lot number printed on the package."
    )

    packaging_date: Optional[str] = Field(
        default=None,
        description="Date of packaging or manufacture as printed."
    )

    expiry_date: Optional[str] = Field(
        default=None,
        description="Use-by or expiry date as printed."
    )

    manufacturer: Optional[str] = Field(
        default=None,
        description="Manufacturer or packer name."
    )

    manufacturer_address: Optional[str] = Field(
        default=None,
        description="Manufacturer or packer address."
    )

    fssai_number: Optional[str] = Field(
        default=None,
        description="FSSAI license or registration number if visible."
    )

    customer_care_email: Optional[str] = Field(
        default=None,
        description="Customer care email address if visible."
    )

    customer_care_phone: Optional[str] = Field(
        default=None,
        description="Customer care phone number if visible."
    )

    website: Optional[str] = Field(
        default=None,
        description="Product/company website if visible."
    )


# ============================================================
# PRODUCT EXTRACTION
# ============================================================

def extract_product_data(image_path: str) -> dict:

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    # --------------------------------------------------------
    # READ IMAGE
    # --------------------------------------------------------

    image_bytes = image_path.read_bytes()

    # --------------------------------------------------------
    # DETECT MIME TYPE
    # --------------------------------------------------------

    suffix = image_path.suffix.lower()

    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }

    mime_type = mime_types.get(
        suffix,
        "image/jpeg"
    )

    # ========================================================
    # PROMPT
    # ========================================================

    prompt = """
You are an expert document and product-label information
extraction system.

Analyze the provided image of a packaged consumer product.

Extract ONLY information that is actually visible in the image.

Do NOT invent, guess, or hallucinate values.

Important rules:

1. Carefully inspect the entire image.
2. Read printed text from the package.
3. Identify the product name.
4. Extract net quantity and its unit.
5. Extract MRP.
6. Extract lot/batch number.
7. Extract packaging/manufacturing date.
8. Extract expiry/use-by date.
9. Extract manufacturer or packer.
10. Extract manufacturer address.
11. Extract FSSAI number if visible.
12. Extract customer-care email and phone if visible.
13. Extract website if visible.

For dates, preserve the date information exactly as printed.

For MRP, return only the numeric value.

For net quantity, separate the numeric value and unit.

If a field cannot be confidently identified from the image,
return null.

Do not use information from outside the image.

Return the result according to the provided JSON schema.
"""

    # ========================================================
    # GEMINI REQUEST
    # ========================================================

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            ),
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ProductData,
        ),
    )

    # ========================================================
    # PARSE STRUCTURED RESPONSE
    # ========================================================

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    data = json.loads(response.text)

    return data