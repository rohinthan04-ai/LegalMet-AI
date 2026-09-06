import os
import json

from google import genai
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in .env")

client = genai.Client(api_key=API_KEY)


# ============================================================
# GEMINI PRODUCT DATA EXTRACTION
# ============================================================

def extract_product_data(
    image_path: str
) -> dict:
    """
    Extract structured product information from a product image
    using Gemini Vision.

    Input:
        image_path -> path to the uploaded product image

    Output:
        Structured product JSON as a Python dictionary.
    """

    prompt = """
You are an AI assistant for a Legal Metrology
Packaged Commodity inspection system.

Analyze the provided product image and extract all
visible product information into structured JSON.

IMPORTANT RULES:

1. Extract ONLY information that is visible in the image.

2. Do NOT invent, assume, or guess information.

3. If a field is not visible or cannot be determined,
   return null.

4. Preserve the information as accurately as possible.

5. Identify the product category when possible.

6. Extract mandatory packaged commodity declarations
   when visible.

7. For each important declaration, provide the visible
   value.

8. Return ONLY valid JSON.

9. Do NOT return markdown.

10. Do NOT wrap the JSON in ```json blocks.

11. Do not include explanations outside the JSON.

12. If a declaration is missing from the visible product
    image, represent it as null.

REQUIRED JSON STRUCTURE:

{
    "product_category": null,
    "product_name": null,
    "brand_name": null,
    "manufacturer_name": null,
    "manufacturer_address": null,
    "packer_name": null,
    "packer_address": null,
    "importer_name": null,
    "importer_address": null,
    "net_quantity": null,
    "mrp": null,
    "unit_sale_price": null,
    "date_of_packing": null,
    "best_before": null,
    "consumer_care_details": {
        "telephone": null,
        "email": null,
        "address": null
    },
    "country_of_origin": null,
    "other_declarations": []
}
"""

    try:

        # Upload image to Gemini
        uploaded_file = client.files.upload(
            file=image_path
        )

        # Send image + prompt to Gemini
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                uploaded_file,
                prompt
            ]
        )

        output_text = response.text

        if not output_text:
            raise ValueError(
                "Gemini returned an empty response"
            )

        # Remove accidental markdown fences
        output_text = output_text.strip()

        if output_text.startswith("```json"):
            output_text = output_text[7:]

        elif output_text.startswith("```"):
            output_text = output_text[3:]

        if output_text.endswith("```"):
            output_text = output_text[:-3]

        output_text = output_text.strip()

        # Convert JSON text → Python dictionary
        result = json.loads(output_text)

        return result

    except json.JSONDecodeError as exc:
        raise Exception(
            f"Gemini returned invalid product JSON: {exc}"
        ) from exc

    except Exception as exc:
        raise Exception(
            f"Gemini product extraction failed: {exc}"
        ) from exc


# ============================================================
# GEMINI COMPLIANCE EVALUATION
# ============================================================

def evaluate_product(
    structured_data: dict,
    checklist: dict
) -> dict:
    """
    Evaluate a product against the Legal Metrology checklist.

    Input:
        structured_data -> Gemini structured product data
        checklist      -> Rules applicable to the product category

    Output:
        {
            "overall_status": "PASS" or "FAIL",
            "rule_evaluations": [
                {
                    "rule_id": ...,
                    "status": "PASS" or "FAIL",
                    "evidence": ...,
                    "details": ...
                }
            ]
        }
    """

    prompt = f"""
You are an AI assistant for a Legal Metrology
Packaged Commodity inspection system.

You will receive:

1. STRUCTURED PRODUCT DATA
2. CHECKLIST containing the rules applicable to the product.

Your task is to evaluate the product against EVERY rule
in the checklist.

========================
IMPORTANT RULES
========================

1. Evaluate EVERY rule individually.

2. For EVERY rule return:
   - rule_id
   - status
   - evidence
   - details

3. status MUST be exactly one of:
   "PASS"
   "FAIL"

4. Evidence must be based ONLY on the provided
   structured product data.

5. DO NOT invent information.

6. If information required by a rule is missing from
   the structured product data, mark that rule as FAIL.

7. Evidence must clearly explain WHY the rule passed
   or failed.

8. The "details" field must explain the rule evaluation
   in a little more detail.

9. If the rule passes:
   - status = "PASS"
   - evidence should identify the data that satisfies
     the rule.
   - details should explain why the available data
     satisfies the rule.

10. If the rule fails:
    - status = "FAIL"
    - evidence should identify exactly what is missing
      or incorrect.
    - details should explain what the rule requires
      and why the available data does not satisfy it.

11. If even ONE rule fails, the overall_status MUST be:
    "FAIL"

12. Only if ALL rules pass, overall_status MUST be:
    "PASS"

13. Do not skip any rule.

14. Return ONLY valid JSON.

15. Do NOT return markdown.

16. Do NOT wrap the JSON inside ```json blocks.

========================
STRUCTURED PRODUCT DATA
========================

{json.dumps(structured_data, indent=2)}

========================
CHECKLIST
========================

{json.dumps(checklist, indent=2)}

========================
REQUIRED OUTPUT FORMAT
========================

Return exactly this JSON structure:

{{
    "overall_status": "PASS",
    "rule_evaluations": [
        {{
            "rule_id": "LM001",
            "status": "PASS",
            "evidence": "Evidence from the structured product data.",
            "details": "Detailed explanation of why this rule passes."
        }},
        {{
            "rule_id": "LM002",
            "status": "FAIL",
            "evidence": "Evidence showing the required declaration is missing.",
            "details": "Detailed explanation of why this rule fails."
        }}
    ]
}}
"""

    try:

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt
        )

        output_text = interaction.output_text

        if not output_text:
            raise ValueError(
                "Gemini returned an empty response"
            )

        output_text = output_text.strip()

        if output_text.startswith("```json"):
            output_text = output_text[7:]

        elif output_text.startswith("```"):
            output_text = output_text[3:]

        if output_text.endswith("```"):
            output_text = output_text[:-3]

        output_text = output_text.strip()

        result = json.loads(output_text)

        # Validate overall structure

        if "overall_status" not in result:
            raise ValueError(
                "Gemini response missing overall_status"
            )

        if "rule_evaluations" not in result:
            raise ValueError(
                "Gemini response missing rule_evaluations"
            )

        if result["overall_status"] not in ["PASS", "FAIL"]:
            raise ValueError(
                "Invalid overall_status returned by Gemini"
            )

        # Validate every rule

        for rule in result["rule_evaluations"]:

            required_fields = [
                "rule_id",
                "status",
                "evidence",
                "details"
            ]

            for field in required_fields:
                if field not in rule:
                    raise ValueError(
                        f"Rule evaluation missing field: {field}"
                    )

            if rule["status"] not in ["PASS", "FAIL"]:
                raise ValueError(
                    f"Invalid rule status for rule "
                    f"{rule['rule_id']}"
                )

        # Enforce overall status ourselves

        if any(
            rule["status"] == "FAIL"
            for rule in result["rule_evaluations"]
        ):
            result["overall_status"] = "FAIL"
        else:
            result["overall_status"] = "PASS"

        return result

    except json.JSONDecodeError as exc:
        raise Exception(
            f"Gemini returned invalid JSON: {exc}"
        ) from exc

    except Exception as exc:
        raise Exception(
            f"Gemini evaluation failed: {exc}"
        ) from exc