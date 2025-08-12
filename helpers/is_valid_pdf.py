import fitz  # PyMuPDF
import io

def is_valid_pdf(content):
    try:
        # Basic signature check
        if not content.startswith(b"%PDF"):
            return False

        # Try opening with PyMuPDF
        doc = fitz.open(stream=content, filetype="pdf")
        
        # Optionally: ensure it has at least 1 page
        if doc.page_count == 0:
            return False
        
        return True
    except Exception:
        return False
