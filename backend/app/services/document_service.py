import os
from PyPDF2 import PdfReader
from backend.app.core.ocr_utils import ocr_image

# Extracts all text from a PDF. Uses OCR as fallback if the page has no text layer.
def extract_text_from_pdf(pdf_path):
    text = ""
    pdf_reader = PdfReader(pdf_path)

    for i, page in enumerate(pdf_reader.pages):
        page_text = page.extract_text()

        # If no text is found (e.g., scanned image), use OCR
        if not page_text or page_text.strip() == "":
            img_path = f"{pdf_path}_page_{i}.png"
            try:
                import fitz  # PyMuPDF for rendering PDF page as image
                doc = fitz.open(pdf_path)
                pix = doc[i].get_pixmap()       # Convert page to image
                pix.save(img_path)              # Save image temporarily
                page_text = ocr_image(img_path) # Perform OCR
                doc.close()
            except Exception as e:
                page_text = ""  # Skip page if OCR fails

            # Clean up the temporary image file
            if os.path.exists(img_path):
                os.remove(img_path)

        # Append the text (from PDF or OCR) to overall output
        text += (page_text or "") + "\n"

    return text

# Extracts all embedded images from a PDF and saves them as files
def extract_images_from_pdf(pdf_path, output_folder="backend/data/images"):
    import fitz  # PyMuPDF for image handling
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]                 # Image reference ID
            pix = fitz.Pixmap(doc, xref) # Get image data
            img_path = os.path.join(
                output_folder,
                f"{os.path.basename(pdf_path)}_page{page_num+1}_img{img_index+1}.png"
            )

            # Handle grayscale/RGB vs CMYK images
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
