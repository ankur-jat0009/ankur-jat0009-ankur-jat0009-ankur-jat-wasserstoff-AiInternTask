from paddleocr import PaddleOCR
import traceback

ocr_engine = PaddleOCR(use_angle_cls=True, lang='en')

def ocr_image(image_path):
    try:
        result = ocr_engine.ocr(image_path)
        lines = []
        for line in result:
            for word_info in line:
                lines.append(word_info[1][0])
        return "\n".join(lines)
    except Exception as e:
        print(f"OCR error for {image_path}: {e}")
        traceback.print_exc()
        return ""