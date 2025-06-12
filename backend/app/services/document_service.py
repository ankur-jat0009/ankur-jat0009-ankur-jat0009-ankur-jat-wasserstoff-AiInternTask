import os
from PyPDF2 import PdfReader
from backend.app.core.ocr_utils import ocr_image

def extract_text_from_pdf(pdf_path):
    text = ""
    pdf_reader = PdfReader(pdf_path)
    for i, page in enumerate(pdf_reader.pages):
        page_text = page.extract_text()
        if not page_text or page_text.strip() == "":
            # OCR fallback for scanned pages
            img_path = f"{pdf_path}_page_{i}.png"
            try:
                import fitz
                doc = fitz.open(pdf_path)
                pix = doc[i].get_pixmap()
                pix.save(img_path)
                page_text = ocr_image(img_path)
                doc.close()
            except Exception as e:
                page_text = ""
            if os.path.exists(img_path):
                os.remove(img_path)
        text += (page_text or "") + "\n"
    return text

def extract_images_from_pdf(pdf_path, output_folder="backend/data/images"):
    import fitz  # PyMuPDF
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            img_path = os.path.join(
                output_folder,
                f"{os.path.basename(pdf_path)}_page{page_num+1}_img{img_index+1}.png"
            )
            if pix.n < 5:
                pix.save(img_path)
            else:
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                pix1.save(img_path)
                pix1 = None
            pix = None
            image_paths.append(img_path)
    doc.close()
    return image_paths