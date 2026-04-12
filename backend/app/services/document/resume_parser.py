"""
简历文档解析服务

支持 PDF、Word 文档的文本提取
"""

import logging
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)


class ResumeParser:
    """简历文档解析器"""

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
        """解析 PDF"""
        try:
            import fitz  # PyMuPDF

            text_parts = []
            with fitz.open(path) as doc:
                for page_num, page in enumerate(doc):
                    text = page.get_text()
                    if text.strip():
                        text_parts.append(f"[第{page_num + 1}页]\n{text}")

            result = "\n".join(text_parts)
            logger.info(f"PDF 解析完成: {path.name}, {len(result)} 字符")
            return result

        except ImportError:
            logger.error("PyMuPDF 未安装，请运行: pip install pymupdf")
            raise ValueError("PDF 解析库未安装，请联系管理员")
        except Exception as e:
            logger.error(f"PDF 解析失败: {path.name}, {e}")
            raise ValueError(f"PDF 解析失败: {e}")

    def _parse_docx(self, path: Path) -> str:
        """解析 Word 文档"""
        try:
            from docx import Document

            doc = Document(path)
            paragraphs = []

            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)

            result = "\n".join(paragraphs)
            logger.info(f"Word 解析完成: {path.name}, {len(result)} 字符")
            return result

        except ImportError:
            logger.error("python-docx 未安装，请运行: pip install python-docx")
            raise ValueError("Word 解析库未安装，请联系管理员")
        except Exception as e:
            logger.error(f"Word 解析失败: {path.name}, {e}")
            raise ValueError(f"Word 解析失败: {e}")

    def _parse_txt(self, path: Path) -> str:
        """解析纯文本"""
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


# 导出单例
resume_parser = ResumeParser()
