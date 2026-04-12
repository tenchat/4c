"""
简历 PDF 导出服务

使用 reportlab 生成 PDF 文件
"""

import io
import re
import os
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def _get_font():
    """获取中文字体"""
    # 尝试多个可能的中文字体路径
    font_paths = [
        # Windows
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
        # Linux
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        # macOS
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
    ]

    for path in font_paths:
        if os.path.exists(path):
            return path
    return None


# 尝试注册中文字体
CHINESE_FONT = None
try:
    font_path = _get_font()
    if font_path:
        # 注册字体族
        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
        CHINESE_FONT = 'ChineseFont'
except Exception:
    pass


def parse_markdown_to_paragraphs(markdown_text: str) -> list:
    """
    解析 Markdown 格式文本为 reportlab 可处理的段落列表

    Args:
        markdown_text: Markdown 格式的简历文本

    Returns:
        段落元素列表
    """
    elements = []

    # 获取字体名称
    font_name = CHINESE_FONT if CHINESE_FONT else 'Helvetica'

    # 定义样式
    title_style = ParagraphStyle(
        'ResumeTitle',
        fontName=font_name,
        fontSize=18,
        leading=24,
        spaceAfter=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1a1a1a')
    )

    section_style = ParagraphStyle(
        'SectionTitle',
        fontName=font_name,
        fontSize=14,
        leading=18,
        spaceBefore=16,
        spaceAfter=8,
        textColor=colors.HexColor('#2563eb')
    )

    normal_style = ParagraphStyle(
        'ResumeNormal',
        fontName=font_name,
        fontSize=10,
        leading=14,
        spaceAfter=4,
        textColor=colors.HexColor('#333333')
    )

    # 按行分割处理
    lines = markdown_text.split('\n')
    in_section = False
    current_section = ""
    current_content = []

    def flush_section():
        nonlocal current_section, current_content
        if current_section or current_content:
            if current_section:
                elements.append(Paragraph(current_section, section_style))
            for line in current_content:
                if line.strip():
                    # 处理 Markdown 强调
                    line = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
                    line = re.sub(r'\*(.+?)\*', r'<i>\1</i>', line)
                    elements.append(Paragraph(line, normal_style))
            if current_content:
                elements.append(Spacer(1, 4))
        current_section = ""
        current_content = []

    for line in lines:
        stripped = line.strip()

        # 跳过空行
        if not stripped:
            if current_section or current_content:
                flush_section()
            continue

        # 检测章节标题 (## 标题)
        if stripped.startswith('## '):
            flush_section()
            current_section = stripped[3:].strip()
            in_section = True
            continue

        # 检测分隔线
        if stripped.startswith('---') or stripped.startswith('***'):
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey, spaceAfter=8, spaceBefore=8))
            continue

        # 普通内容行
        if in_section:
            current_content.append(stripped)
        else:
            # 开头的非标题内容作为个人信息处理
            if stripped.startswith('# '):
                # 主标题
                elements.append(Paragraph(stripped[2:].strip(), title_style))
            else:
                elements.append(Paragraph(stripped, normal_style))

    # 处理最后一部分
    flush_section()

    return elements


def export_resume_to_pdf(resume_text: str, filename: str = "resume.pdf") -> bytes:
    """
    将 Markdown 格式的简历文本导出为 PDF

    Args:
        resume_text: Markdown 格式的简历文本
        filename: 文件名

    Returns:
        PDF 文件的字节数据
    """
    buffer = io.BytesIO()

    # 创建 PDF 文档
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    # 解析 Markdown 并构建 PDF 元素
    elements = parse_markdown_to_paragraphs(resume_text)

    # 构建 PDF
    doc.build(elements)

    # 获取 PDF 数据
    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data
