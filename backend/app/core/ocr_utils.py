# Import PaddleOCR for Optical Character Recognition
from paddleocr import PaddleOCR
import traceback  # For detailed error logging

# Initialize the OCR engine with English language and angle detection
ocr_engine = PaddleOCR(use_angle_cls=True, lang='en')

# Function to perform OCR on a given image path
def ocr_image(image_path):
    try:
        # Run OCR on the image (returns list of text boxes)
        result = ocr_engine.ocr(image_path)
        lines = []

        # Iterate through recognized lines and extract text
        for line in result:
            for word_info in line:
                lines.append(word_info[1][0])  # word_info[1][0] contains the detected text

        # Combine all recognized lines into a single string
        return "\n".join(lines)

    except Exception as e:
        # Print error message and full traceback for debugging
        print(f"OCR error for {image_path}: {e}")
        traceback.print_exc()
        return ""
