import easyocr

# Load OCR model once (so it doesn’t reload every time)
READER = easyocr.Reader(['en'])


def predict_equation(image):
    """
    Use OCR (EasyOCR) to detect text in a handwritten math equation image.
    Returns the recognized text as a string.
    """
    global READER

    try:
        # Perform OCR
        result = READER.readtext(image)

        # Extract text parts and join them
        detected_text = " ".join([res[1] for res in result])

        return detected_text.strip()

    except Exception as e:
        return f"Error in OCR: {e}"
