import pytesseract


# ------------------------------------------------
# TESSERACT PATH
# ------------------------------------------------

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# ------------------------------------------------
# OCR CONFIGURATIONS
# ------------------------------------------------

OCR_CONFIGS = [
    "--psm 6",
    "--psm 11",
]


# ------------------------------------------------
# OCR WITH CONFIDENCE
# ------------------------------------------------

def extract_text_with_confidence(
    image,
    config="--psm 6"
):
    """
    Extract text, confidence and bounding boxes
    from an image.
    """

    data = pytesseract.image_to_data(
        image,
        config=config,
        output_type=pytesseract.Output.DICT
    )

    words = []

    for i in range(len(data["text"])):

        text = data["text"][i].strip()

        if not text:
            continue

        try:
            confidence = float(
                data["conf"][i]
            )
        except (ValueError, TypeError):
            continue

        if confidence < 0:
            continue

        words.append({
            "text": text,
            "confidence": round(
                confidence,
                2
            ),
            "x": int(data["left"][i]),
            "y": int(data["top"][i]),
            "width": int(data["width"][i]),
            "height": int(data["height"][i])
        })

    # --------------------------------------------
    # AVERAGE CONFIDENCE
    # --------------------------------------------

    if words:

        average_confidence = (
            sum(
                word["confidence"]
                for word in words
            )
            / len(words)
        )

    else:

        average_confidence = 0

    text = " ".join(
        word["text"]
        for word in words
    )

    return {
        "text": text,
        "average_confidence": round(
            average_confidence,
            2
        ),
        "words": words
    }


# ------------------------------------------------
# MULTI-VARIANT OCR
# ------------------------------------------------

def run_multiple_ocr(variants):
    """
    Run OCR on multiple preprocessing variants
    and select the result with the highest
    average confidence.
    """

    results = []

    for variant_name, image in variants.items():

        for config in OCR_CONFIGS:

            result = extract_text_with_confidence(
                image,
                config=config
            )

            results.append({
                "variant": variant_name,
                "config": config,
                "text": result["text"],
                "average_confidence":
                    result["average_confidence"],
                "words": result["words"]
            })

    # --------------------------------------------
    # SELECT BEST RESULT
    # --------------------------------------------

    if not results:
        return {
            "best_result": None,
            "all_results": []
        }

    best_result = max(
        results,
        key=lambda item:
            item["average_confidence"]
    )

    return {
        "best_result": best_result,
        "all_results": results
    }