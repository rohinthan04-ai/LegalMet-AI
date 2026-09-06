import cv2

from .quality import analyze_image_quality
from .preprocessing import create_ocr_variants
from .ocr_engine import run_multiple_ocr
from .extraction import extract_fields


def process_image(image_path):
    """
    Complete LegalMet AI OCR/CV pipeline.

    Pipeline:

        Load image
             ↓
        Quality analysis
             ↓
        Multiple preprocessing variants
             ↓
        Multiple OCR passes
             ↓
        Confidence comparison
             ↓
        Best OCR result
             ↓
        Field extraction
    """

    # ------------------------------------------------
    # 1. LOAD IMAGE
    # ------------------------------------------------

    image = cv2.imread(
        image_path
    )

    if image is None:
        raise FileNotFoundError(
            f"Could not load image: {image_path}"
        )

    # ------------------------------------------------
    # 2. QUALITY ANALYSIS
    # ------------------------------------------------

    quality = analyze_image_quality(
        image
    )

    # ------------------------------------------------
    # 3. CREATE OCR VARIANTS
    # ------------------------------------------------

    variants = create_ocr_variants(
        image
    )

    # ------------------------------------------------
    # 4. RUN MULTIPLE OCR PASSES
    # ------------------------------------------------

    ocr_results = run_multiple_ocr(
        variants
    )

    best_result = ocr_results[
        "best_result"
    ]

    # ------------------------------------------------
    # 5. FIELD EXTRACTION
    # ------------------------------------------------

    if best_result:

        fields = extract_fields(
            best_result["text"]
        )

    else:

        fields = {}

    # ------------------------------------------------
    # 6. FINAL RESULT
    # ------------------------------------------------

    return {

        "image": {
            "path": image_path,
            "width": quality["width"],
            "height": quality["height"]
        },

        "quality": quality,

        "ocr": {

            "best_variant":
                best_result["variant"]
                if best_result
                else None,

            "best_config":
                best_result["config"]
                if best_result
                else None,

            "text":
                best_result["text"]
                if best_result
                else "",

            "average_confidence":
                best_result["average_confidence"]
                if best_result
                else 0,

            "words":
                best_result["words"]
                if best_result
                else [],

            "all_results":
                ocr_results["all_results"]
        },

        "fields": fields
    }