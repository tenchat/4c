"""
文档解析器

支持 PDF、Word、纯文本的解析
"""

import logging
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)


class DocumentParser:
    """文档解析器 - 提取纯文本"""

    SUPPORTED_FORMATS: set[str] = {".pdf", ".docx", ".doc", ".txt"}
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    def parse(self, file_path: str) -> str:
        """
        解析文档，返回纯文本

        Args:
            file_path: 文件路径

        Returns:
            提取的文本内容

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不支持的格式
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        ext = path.suffix.lower()
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"不支持的格式: {ext}. 支持: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        # 检查文件大小
        file_size = path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(f"文件超过 {self.MAX_FILE_SIZE // (1024*1024)}MB 限制")

        if ext == ".pdf":
            return self._parse_pdf(path)
        elif ext in {".docx", ".doc"}:
            return self._parse_docx(path)
        else:
            return self._parse_txt(path)

    def _parse_pdf(self, path: Path) -> str:
        """
        解析 PDF，提取文字（忽略图片）

        Args:
            path: PDF 文件路径

        Returns:
            提取的文本
        """
        import fitz  # PyMuPDF

        text_parts = []

        try:
            with fitz.open(path) as doc:
                for page_num, page in enumerate(doc):
                    text = page.get_text()
                    if text.strip():
                        text_parts.append(f"[第{page_num + 1}页]\n{text}")

            result = "\n".join(text_parts)
            logger.info(f"PDF 解析完成: {path.name}, {len(result)} 字符")
            return result

        except Exception as e:
            logger.error(f"PDF 解析失败: {path.name}, {e}")
            raise ValueError(f"PDF 解析失败: {e}") from e

    def _parse_docx(self, path: Path) -> str:
        """
        解析 Word 文档

        Args:
            path: Word 文件路径

        Returns:
            提取的文本
        """
        from docx import Document

        try:
            doc = Document(path)
            paragraphs = []

            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)

            result = "\n".join(paragraphs)
            logger.info(f"Word 解析完成: {path.name}, {len(result)} 字符")
            return result

        except Exception as e:
            logger.error(f"Word 解析失败: {path.name}, {e}")
            raise ValueError(f"Word 解析失败: {e}") from e

    def _parse_txt(self, path: Path) -> str:
        """
        解析纯文本

        Args:
            path: 文本文件路径

        Returns:
            文件内容
        """
        encodings = ["utf-8", "gbk", "gb2312", "latin-1"]

        for encoding in encodings:
            try:
                with open(path, "r", encoding=encoding) as f:
                    content = f.read()

                logger.info(f"文本解析完成: {path.name}, {len(content)} 字符")
                return content

            except UnicodeDecodeError:
                continue

        raise ValueError(f"无法解析文本文件，尝试的编码: {encodings}")

    def validate_file(self, file_path: str) -> tuple[bool, str]:
        """
        验证文件

        Args:
            file_path: 文件路径

        Returns:
            (是否有效, 错误信息)
        """
        path = Path(file_path)

        if not path.exists():
            return False, "文件不存在"

        ext = path.suffix.lower()
        if ext not in self.SUPPORTED_FORMATS:
            return False, f"不支持的格式: {ext}"

        if path.stat().st_size > self.MAX_FILE_SIZE:
            return False, f"文件超过 {self.MAX_FILE_SIZE // (1024*1024)}MB 限制"

        return True, ""
