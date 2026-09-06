import cv2


def analyze_image_quality(image):
    """
    Analyze the basic quality of an image before OCR.

    Returns:
        dict: Image dimensions, sharpness, brightness,
              contrast, status, and warnings.
    """

    # -----------------------------
    # IMAGE DIMENSIONS
    # -----------------------------

    height, width = image.shape[:2]

    # -----------------------------
    # CONVERT TO GRAYSCALE
    # -----------------------------

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # -----------------------------
    # SHARPNESS
    # -----------------------------

    # Variance of Laplacian is a simple
    # blur/sharpness measurement.

    sharpness = cv2.Laplacian(
        gray,
        cv2.CV_64F
    ).var()

    # -----------------------------
    # BRIGHTNESS
    # -----------------------------

    brightness = gray.mean()

    # -----------------------------
    # CONTRAST
    # -----------------------------

    contrast = gray.std()

    # -----------------------------
    # WARNINGS
    # -----------------------------

    warnings = []

    if width < 800 or height < 600:
        warnings.append(
            "Low image resolution"
        )

    if sharpness < 80:
        warnings.append(
            "Image may be blurry"
        )

    if brightness < 45:
        warnings.append(
            "Image may be too dark"
        )

    if brightness > 225:
        warnings.append(
            "Image may be overexposed"
        )

    if contrast < 25:
        warnings.append(
            "Low image contrast"
        )

    # -----------------------------
    # OVERALL STATUS
    # -----------------------------

    if not warnings:
        status = "GOOD"

    elif sharpness >= 40:
        status = "REVIEW"

    else:
        status = "POOR"

    # -----------------------------
    # RESULT
    # -----------------------------

    return {
        "width": width,
        "height": height,
        "sharpness": round(
            float(sharpness),
            2
        ),
        "brightness": round(
            float(brightness),
            2
        ),
        "contrast": round(
            float(contrast),
            2
        ),
        "status": status,
        "warnings": warnings
    }