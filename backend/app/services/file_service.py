"""File service for handling file uploads and storage."""

import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional, Tuple


# Upload directory relative to backend root
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
RESUME_DIR = UPLOAD_DIR / "resumes"

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx'}
# Maximum file size: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024


def ensure_upload_dirs() -> None:
    """Ensure upload directories exist."""
    RESUME_DIR.mkdir(parents=True, exist_ok=True)


def validate_file(file_content: bytes, filename: str) -> Tuple[bool, str]:
    """Validate file size and extension.

    Args:
        file_content: Raw bytes of the uploaded file.
        filename: Original filename.

    Returns:
        Tuple of (is_valid, error_message).
    """
    # Check file size
    if len(file_content) > MAX_FILE_SIZE:
        return False, f"文件大小超过限制 ({MAX_FILE_SIZE // (1024 * 1024)}MB)"

    # Check extension
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"不支持的文件格式，仅支持: {', '.join(ALLOWED_EXTENSIONS)}"

    return True, ""


def generate_resume_filename(original_filename: str, account_id: str) -> str:
    """Generate a unique filename for resume storage.

    Args:
        original_filename: Original uploaded filename.
        account_id: The account ID of the uploader.

    Returns:
        Generated unique filename.
    """
    ext = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4().hex[:8]
    return f"resume_{account_id}_{unique_id}{ext}"


async def save_resume_file(
    file_content: bytes,
    filename: str,
    account_id: str
) -> Tuple[bool, str, str]:
    """Save uploaded resume file to disk.

    Args:
        file_content: Raw bytes of the uploaded file.
        filename: Original filename.
        account_id: The account ID of the uploader.

    Returns:
        Tuple of (success, stored_filename, error_message).
    """
    ensure_upload_dirs()

    # Validate
    is_valid, error = validate_file(file_content, filename)
    if not is_valid:
        return False, "", error

    # Generate unique filename
    stored_filename = generate_resume_filename(filename, account_id)
    file_path = RESUME_DIR / stored_filename

    try:
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        return True, stored_filename, ""
    except Exception as e:
        return False, "", f"保存文件失败: {str(e)}"


def get_resume_path(filename: str) -> Optional[Path]:
    """Get the full path to a resume file.

    Args:
        filename: The stored filename.

    Returns:
        Full path if file exists, None otherwise.
    """
    if not filename:
        return None

    file_path = RESUME_DIR / filename
    if file_path.exists():
        return file_path

    return None


def delete_resume_file(filename: str) -> bool:
    """Delete a resume file from disk.

    Args:
        filename: The stored filename.

    Returns:
        True if deleted, False otherwise.
    """
    file_path = get_resume_path(filename)
    if file_path:
        try:
            os.remove(file_path)
            return True
        except Exception:
            return False
    return False


def get_resume_url(filename: str, base_url: str = "/api/v1/student/resumes") -> str:
    """Get the download URL for a resume.

    Args:
        filename: The stored filename.
        base_url: Base API URL for resume downloads.

    Returns:
        Full download URL.
    """
    if not filename:
        return ""
    return f"{base_url}/{filename}"