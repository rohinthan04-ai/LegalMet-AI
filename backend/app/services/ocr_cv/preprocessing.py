import cv2


def resize_image(image, max_width=1800):
    """
    Resize image while maintaining aspect ratio.

    We don't enlarge small images because artificial
    enlargement can introduce additional noise.
    """

    height, width = image.shape[:2]

    if width <= max_width:
        return image

    scale = max_width / width

    new_width = int(width * scale)
    new_height = int(height * scale)

    return cv2.resize(
        image,
        (new_width, new_height),
        interpolation=cv2.INTER_AREA
    )


def grayscale(image):
    """
    Convert BGR image to grayscale.
    """

    return cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


def enhance_contrast(image):
    """
    Improve local contrast using CLAHE.
    """

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    return clahe.apply(image)


def light_denoise(image):
    """
    Apply gentle denoising.

    We deliberately keep this light so that small
    characters and numbers are not destroyed.
    """

    return cv2.fastNlMeansDenoising(
        image,
        None,
        h=5,
        templateWindowSize=7,
        searchWindowSize=21
    )


def sharpen(image):
    """
    Mild sharpening for text edges.
    """

    blurred = cv2.GaussianBlur(
        image,
        (3, 3),
        0
    )

    return cv2.addWeighted(
        image,
        1.3,
        blurred,
        -0.3,
        0
    )


def adaptive_threshold(image):
    """
    Adaptive thresholding.

    Useful when lighting is uneven across the label.
    """

    return cv2.adaptiveThreshold(
        image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )


def otsu_threshold(image):
    """
    Otsu binary thresholding.
    """

    _, result = cv2.threshold(
        image,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return result


def create_ocr_variants(image):
    """
    Create multiple versions of the same image
    for OCR.

    Returns:
        dict containing several OCR-ready images.
    """

    resized = resize_image(image)

    gray = grayscale(resized)

    contrast = enhance_contrast(gray)

    denoised = light_denoise(contrast)

    sharpened = sharpen(denoised)

    adaptive = adaptive_threshold(
        denoised
    )

    otsu = otsu_threshold(
        denoised
    )

    return {
        "original": resized,
        "grayscale": gray,
        "contrast": contrast,
        "denoised": denoised,
        "sharpened": sharpened,
        "adaptive_threshold": adaptive,
        "otsu_threshold": otsu
    }