"""Text extraction utility for PDF and Word documents."""

import io
from typing import Optional

# Try to import pdfminer for PDF extraction
try:
    from pdfminer.high_level import extract_text as extract_pdf_text
    HAS_PDFMINER = True
except ImportError:
    HAS_PDFMINER = False

# Try to import python-docx for Word extraction
try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file content.

    Args:
        file_content: Raw bytes of the PDF file.

    Returns:
        Extracted text content.
    """
    if not HAS_PDFMINER:
        return "[PDF text extraction not available - pdfminer not installed]"

    try:
        pdf_file = io.BytesIO(file_content)
        text = extract_pdf_text(pdf_file)
        return text.strip() if text else ""
    except Exception as e:
        return f"[Error extracting PDF text: {str(e)}]"


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file content.

    Args:
        file_content: Raw bytes of the DOCX file.

    Returns:
        Extracted text content.
    """
    if not HAS_DOCX:
        return "[Word text extraction not available - python-docx not installed]"

    try:
        docx_file = io.BytesIO(file_content)
        doc = docx.Document(docx_file)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        return f"[Error extracting Word text: {str(e)}]"


def extract_text_from_doc(file_content: bytes) -> str:
    """Extract text from legacy DOC file content.

    Args:
        file_content: Raw bytes of the DOC file.

    Returns:
        Extracted text content or error message.
    """
    # python-docx doesn't support legacy .doc format
    # In production, you might want to use antiword or catdoc
    return "[Legacy .doc format not supported - please convert to PDF or .docx]"


def extract_text(filename: str, file_content: bytes) -> str:
    """Extract text from a file based on its extension.

    Args:
        filename: The original filename.
        file_content: Raw bytes of the file.

    Returns:
        Extracted text content.
    """
    filename_lower = filename.lower()

    if filename_lower.endswith('.pdf'):
        return extract_text_from_pdf(file_content)
    elif filename_lower.endswith('.docx'):
        return extract_text_from_docx(file_content)
    elif filename_lower.endswith('.doc'):
        return extract_text_from_doc(file_content)
    else:
        return f"[Unsupported file format: {filename}]"