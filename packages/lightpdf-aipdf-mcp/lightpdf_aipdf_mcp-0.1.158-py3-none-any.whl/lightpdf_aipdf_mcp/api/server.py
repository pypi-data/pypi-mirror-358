"""LightPDF Agent FastMCP Server模块"""
import asyncio
import os
import sys
import argparse
from typing import List, Optional, Literal, Annotated

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# FastMCP相关导入
from fastmcp import FastMCP, Context

# Pydantic导入用于参数描述
from pydantic import Field

# 本地导入
from ..models.schemas import FileObject
from ..utils.common import Logger
from .adapter import (
    process_tool_call_adapter, generate_operation_config,
    create_pdf_adapter, merge_pdfs_adapter
)

# 创建FastMCP实例
mcp = FastMCP(
    name="LightPDF_AI_tools",
    instructions="LightPDF Document Processing Tools powered by FastMCP."
)

# ==================== 文档转换工具 ====================

@mcp.tool
async def convert_document(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of files to convert, each containing path and optional password")],
    format: Annotated[Literal["pdf", "docx", "xlsx", "pptx", "jpg", "jpeg", "png", "webp", "svg", "html", "txt", "csv", "md", "tex", "rtf", "tiff", "tif"], Field(..., description="Target output format")],
    merge_all: Annotated[int, Field(description="Only effective in specific scenarios: PDF to Image (1=merge all pages into one long image), Image to PDF (1=merge all images into single PDF), PDF to Excel (1=merge all pages into one sheet)", ge=0, le=1)] = 0,
    one_page_per_sheet: Annotated[bool, Field(description="Only effective when converting Excel to PDF. If true, each sheet fits into single PDF page")] = False,
    image_quality: Annotated[Optional[int], Field(description="Image quality setting, 0-200. Only effective when converting PDF to image formats", ge=0, le=200)] = None
) -> Annotated[str, "JSON formatted result report with converted file download URLs and conversion details"]:
    """
    Document format conversion tool.

    **FROM PDF - Supported output formats when converting from PDF:**
    - Documents: DOCX, XLSX, PPTX, HTML, TXT, CSV, MD (Markdown), RTF, TEX (LaTeX)
    - Images: JPG, JPEG, PNG, TIFF, SVG
    
    **TO PDF - Supported input formats that can be converted to PDF:**
    - Documents: DOCX, XLSX, PPTX, HTML, TXT, MD, RTF, ODT
    - Images: JPG (includes .jpeg files), PNG, HEIC, SVG, TIFF (includes .tif files), WEBP
    - Graphics: CAD (DWG), ODG (OpenDocument Graphics)
    - Office: ODS (OpenDocument Spreadsheet), ODP (OpenDocument Presentation)
    - Special: CAJ, OFD
    
    **Image format conversions - Direct image-to-image conversions:**
    - HEIC → JPG, JPEG, PNG
    - WEBP → PNG
    - PNG → WEBP
    
    PDF to PDF conversion is not supported.
    Only entire files can be converted.

    Important distinctions:
    - For HTML to PDF, both local HTML files and any web page URL are supported
    - For content-based PDF creation from LaTeX code, use create_pdf tool instead
    - For extracting embedded images from PDFs, use extract_images tool instead
    - For text recognition from scanned/image PDFs, use ocr_document tool instead
    - For IMAGE files to TEXT formats (JPG/PNG/GIF/BMP → TXT/DOCX/XLSX/PPTX), use ocr_document tool instead
    - PDF to TXT conversion here extracts existing text; for scanned documents use ocr_document tool instead
    - PDF-to-image conversion creates images of PDF pages; extract_images gets embedded images

    This tool is strictly for file format conversion only.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始转换 {len(files)} 个文件到 {format} 格式...")
    
    # 构建操作配置
    extra_params = {
        "merge_all": merge_all,
        "one_page_per_sheet": one_page_per_sheet
    }
    
    # 处理image_quality参数
    # 如果是PDF转图片格式且没有指定image_quality，默认使用100
    image_formats = {"jpg", "jpeg", "png", "tiff", "tif", "svg"}
    if format in image_formats and image_quality is None:
        image_quality = 100
    
    # 添加image_quality参数（如果有值）
    if image_quality is not None:
        extra_params["image_quality"] = image_quality
        extra_params["image-quality"] = image_quality
    
    operation_config = generate_operation_config(
        operation_type="convert",
        format_value=format,
        extra_params=extra_params
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "转换完成")
    return result

@mcp.tool
async def add_page_numbers(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to add page numbers to")],
    start_num: Annotated[int, Field(description="Starting page number", ge=1)] = 1,
    position: Annotated[Literal["1", "2", "3", "4", "5", "6"], Field(description="Page number position: 1(top-left), 2(top-center), 3(top-right), 4(bottom-left), 5(bottom-center), 6(bottom-right)")] = "5",
    margin: Annotated[Literal[10, 30, 60], Field(description="Page number margin")] = 30
) -> Annotated[str, "JSON formatted result report with PDF files containing added page numbers"]:
    """
    Add page numbers to each page of a PDF document.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始为 {len(files)} 个PDF文件添加页码...")
    
    # 构建操作配置
    extra_params = {
        "start_num": start_num,
        "position": position,
        "margin": margin
    }
    
    operation_config = generate_operation_config(
        operation_type="convert",
        format_value="number-pdf",
        extra_params=extra_params
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "页码添加完成")
    return result

@mcp.tool
async def remove_watermark(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to remove watermarks from")]
) -> Annotated[str, "JSON formatted result report with watermark-free PDF files"]:
    """
    Remove watermarks from PDF files. Watermarks are overlaid text or images added for copyright protection, branding, or document security (e.g., "DRAFT", "CONFIDENTIAL", logos). This tool uses specialized algorithms to detect and remove these overlay elements.
    
    Note: This is specifically for watermarks and overlay elements, not regular document text. For editing or deleting normal document text content, use replace_text instead.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始为 {len(files)} 个PDF文件去除水印...")
    
    # 构建操作配置
    operation_config = generate_operation_config(
        operation_type="convert",
        format_value="doc-repair"
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "水印去除完成")
    return result

# ==================== PDF编辑工具 ====================

@mcp.tool
async def compress_pdf(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to compress")],
    image_quantity: Annotated[int, Field(description="Image quality, 1-100, lower values result in higher compression", ge=1, le=100)] = 60
) -> Annotated[str, "JSON formatted result report containing success/failure counts, file information, and download URLs or error messages"]:
    """
    Reduce the size of PDF files.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始压缩 {len(files)} 个PDF文件...")
    
    # 构建操作配置
    extra_params = {
        "image_quantity": image_quantity
    }
    
    operation_config = generate_operation_config(
        operation_type="edit",
        edit_type="compress",
        extra_params=extra_params
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "PDF压缩完成")
    return result

@mcp.tool
async def merge_pdfs(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to merge (must be at least two)", min_length=2)]
) -> Annotated[str, "JSON formatted result report with merged PDF file download URL"]:
    """
    Merge multiple PDF files into a single PDF file. You must provide at least two files in the 'files' array, otherwise the operation will fail.
    """
    logger = Logger(ctx, collect_info=False)
    if len(files) < 2:
        await logger.log("error", "合并PDF至少需要两个文件")
        return '{"total": 0, "success_count": 0, "failed_count": 1, "success_files": [], "failed_files": [{"error_message": "合并PDF至少需要两个文件"}]}'
    
    await logger.log("info", f"开始合并 {len(files)} 个PDF文件...")
    
    # 使用特殊的合并适配器
    result = await merge_pdfs_adapter(logger, files)
    
    await logger.log("info", "PDF合并完成")
    return result

# ==================== 水印工具 ====================

@mcp.tool
async def add_text_watermark(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to add text watermarks to")],
    text: Annotated[str, Field(..., description="Watermark text content", min_length=1)],
    position: Annotated[Literal["topleft", "top", "topright", "left", "center", "right", "bottomleft", "bottom", "bottomright", "diagonal", "reverse-diagonal"], Field(description="Text watermark position")] = "center",
    opacity: Annotated[float, Field(description="Opacity, 0.0-1.0", ge=0.0, le=1.0)] = 1.0,
    range: Annotated[str, Field(description="Page range, e.g. '1,3,5-7' or empty string for all pages")] = "",
    layout: Annotated[Literal["on", "under"], Field(description="Layout position: on top of content(on) or under content(under)")] = "on",
    font_family: Annotated[Optional[str], Field(description="Font family")] = None,
    font_size: Annotated[Optional[int], Field(description="Font size", ge=1)] = None,
    font_color: Annotated[Optional[str], Field(description="Font color, e.g. '#ff0000' for red")] = None
) -> Annotated[str, "JSON formatted result report with text watermarked PDF files"]:
    """
    Add text watermarks to PDF files.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始为 {len(files)} 个PDF文件添加文本水印...")
    
    # 构建操作配置
    extra_params = {
        "text": text,
        "position": position,
        "opacity": opacity,
        "range": range,
        "layout": layout
    }
    
    # 添加可选参数
    if font_family:
        extra_params["font_family"] = font_family
    if font_size:
        extra_params["font_size"] = font_size
    if font_color:
        extra_params["font_color"] = font_color
    
    operation_config = generate_operation_config(
        operation_type="edit",
        edit_type="add_text_watermark",
        extra_params=extra_params
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "文本水印添加完成")
    return result

@mcp.tool
async def add_image_watermark(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to add image watermarks to")],
    image_url: Annotated[str, Field(..., description="Image URL for the watermark, must include protocol, supports http/https/oss", min_length=1)],
    position: Annotated[Literal["topleft", "top", "topright", "left", "center", "right", "bottomleft", "bottom", "bottomright", "diagonal", "reverse-diagonal"], Field(description="Image watermark position")] = "center",
    opacity: Annotated[float, Field(description="Opacity, 0.0-1.0", ge=0.0, le=1.0)] = 0.7,
    range: Annotated[str, Field(description="Page range, e.g. '1,3,5-7' or empty string for all pages")] = "",
    layout: Annotated[Literal["on", "under"], Field(description="Layout position: on top of content(on) or under content(under)")] = "on"
) -> Annotated[str, "JSON formatted result report with image watermarked PDF files"]:
    """
    Add image watermarks to PDF files.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始为 {len(files)} 个PDF文件添加图片水印...")
    
    # 构建操作配置
    extra_params = {
        "image_url": image_url,
        "position": position,
        "opacity": opacity,
        "range": range,
        "layout": layout
    }
    
    operation_config = generate_operation_config(
        operation_type="edit",
        edit_type="add_image_watermark",
        extra_params=extra_params
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "图片水印添加完成")
    return result

@mcp.tool
async def unlock_pdf(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to decrypt, each must contain password")]
) -> Annotated[str, "JSON formatted result report with decrypted PDF files (password removed)"]:
    """
    Remove password protection from PDF files.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始解密 {len(files)} 个PDF文件...")
    
    # 构建操作配置
    operation_config = generate_operation_config(
        operation_type="edit",
        edit_type="decrypt"
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "PDF解密完成")
    return result

@mcp.tool
async def protect_pdf(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to encrypt")],
    password: Annotated[str, Field(..., description="New password to set", min_length=1)]
) -> Annotated[str, "JSON formatted result report with password-protected PDF files"]:
    """
    Add password protection to PDF files. This sets a user password (open password) that is required to open and view the PDF document. Users cannot access the document content without this password.
    
    Note: This is different from restrict_printing which allows viewing but restricts specific actions like printing. Use protect_pdf to prevent unauthorized access, use restrict_printing to control usage permissions.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始加密 {len(files)} 个PDF文件...")
    
    # 构建操作配置
    extra_params = {
        "password": password
    }
    
    operation_config = generate_operation_config(
        operation_type="edit",
        edit_type="encrypt",
        extra_params=extra_params
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "PDF加密完成")
    return result

@mcp.tool
async def split_pdf(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to split")],
    split_type: Annotated[Literal["every", "page", "bookmark"], Field(..., description="Split type: 'every' (split each page into a separate file), 'page' (split by page ranges), or 'bookmark' (split by PDF bookmarks/outlines/table of contents/headings)")],
    pages: Annotated[str, Field(description="Page ranges to split, e.g. '1,3,5-7' or '' (empty for all pages). Required and only valid when split_type is 'page'")] = "",
    merge_all: Annotated[Literal[0, 1], Field(description="Whether to merge results into a single PDF file: 1=yes, 0=no (will return a zip package of multiple files). Only valid when split_type is 'page'")] = 0
) -> Annotated[str, "JSON formatted result report with split PDF files or zip package"]:
    """
    Split PDF documents to extract and keep wanted pages. Use this when you know which pages you want to keep and create new PDF files from them. You can split each page separately, extract specific page ranges, or split by document bookmarks.
    
    Use case: Creating new PDF files from selected pages.
    Note: This extracts and keeps specified pages. For permanently removing unwanted pages from the original document, use delete_pdf_pages instead.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始拆分 {len(files)} 个PDF文件...")
    
    # 构建操作配置
    extra_params = {
        "split_type": split_type,
        "pages": pages,
        "merge_all": merge_all
    }
    
    operation_config = generate_operation_config(
        operation_type="edit",
        edit_type="split",
        extra_params=extra_params
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "PDF拆分完成")
    return result

@mcp.tool
async def rotate_pdf(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to rotate")],
    rotates: Annotated[List[dict], Field(..., description="Parameter list, each containing rotation angle and page range. Example: [{\"angle\": 90, \"pages\": \"1-3\"}, {\"angle\": 180, \"pages\": \"all\"}]", min_length=1)]
) -> Annotated[str, "JSON formatted result report with rotated PDF files"]:
    """
    Rotate pages in PDF files.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始旋转 {len(files)} 个PDF文件...")
    
    # 构建操作配置
    extra_params = {
        "rotates": rotates
    }
    
    operation_config = generate_operation_config(
        operation_type="edit",
        edit_type="rotate",
        extra_params=extra_params
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "PDF旋转完成")
    return result

# ==================== AI功能工具 ====================

@mcp.tool
async def translate_pdf(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to translate")],
    target: Annotated[Literal["ar", "bg", "cz", "da", "de", "el", "en", "es", "fi", "fr", "hbs", "hi", "hu", "id", "it", "ja", "ko", "ms", "nl", "no", "pl", "pt", "ru", "sl", "sv", "th", "tr", "vi", "zh", "zh-tw"], Field(..., description="Target language. Must be specified")],
    source: Annotated[Literal["auto", "ar", "bg", "cz", "da", "de", "el", "en", "es", "fi", "fr", "hbs", "hi", "hu", "id", "it", "ja", "ko", "ms", "nl", "no", "pl", "pt", "ru", "sl", "sv", "th", "tr", "vi", "zh", "zh-tw"], Field(description="Source language. Supports 'auto' for automatic detection")] = "auto",
    output_type: Annotated[Literal["mono", "dual"], Field(description="Output type: 'mono' for target language only, 'dual' for source/target bilingual output")] = "mono"
) -> Annotated[str, "JSON formatted result report with translated PDF files in target language"]:
    """
    Translate only the text in a PDF file into a specified target language and output a new PDF file. All non-text elements (such as images, tables, and layout) will remain unchanged.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始翻译 {len(files)} 个PDF文件...")
    
    # 构建操作配置
    extra_params = {
        "source": source,
        "target": target,
        "output_type": output_type
    }
    
    operation_config = generate_operation_config(
        operation_type="translate",
        extra_params=extra_params
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "PDF翻译完成")
    return result

@mcp.tool
async def ocr_document(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of files to be recognized. Supports: PDF, PPT, PPTX, XLS, XLSX, DOC, DOCX, JPEG, JPG, PNG, GIF, BMP")],
    format: Annotated[Literal["pdf", "docx", "pptx", "xlsx", "txt"], Field(description="Output format, supports pdf/docx/pptx/xlsx/txt, default is pdf")] = "pdf",
    language: Annotated[str, Field(description="Specify the language(s) or type(s) to recognize, multiple values can be selected and separated by commas")] = "English,Digits,ChinesePRC"
) -> Annotated[str, "JSON formatted result report with OCR-processed files in specified format"]:
    """
    Perform OCR (Optical Character Recognition) on documents and images to recognize and extract text.Supported input file types:
    - Documents: PDF, PPT, PPTX, XLS, XLSX, DOC, DOCX
    - Images: JPEG, JPG, PNG, GIF, BMP
    
    Supported output formats:
    - Documents: PDF, DOCX, PPTX, XLSX
    - Plain Text: TXT
    
    Note: Use this tool for scanned documents, image-based PDFs, or image files where text needs to be recognized. For regular PDF text extraction, use convert_document PDF-to-TXT conversion instead.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始OCR识别 {len(files)} 个文件...")
    
    # 构建操作配置
    extra_params = {
        "format": format,
        "language": language
    }
    
    operation_config = generate_operation_config(
        operation_type="ocr",
        extra_params=extra_params
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "OCR识别完成")
    return result

@mcp.tool
async def summarize_document(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of files to summarize")],
    prompt: Annotated[str, Field(..., description="User's requirement or instruction for the summary", min_length=1)],
    language: Annotated[Literal["af","am","ar","as","az","ba","be","bg","bn","bo","br","bs","ca","cs","cy","da","de","el","en","es","et","eu","fa","fi","fo","fr","gl","gu","ha","haw","he","hi","hr","ht","hu","hy","id","is","it","ja","jw","ka","kk","km","kn","ko","la","lb","ln","lo","lt","lv","mg","mi","mk","ml","mn","mr","ms","mt","my","ne","nl","nn","no","oc","pa","pl","ps","pt","ro","ru","sa","sd","si","sk","sl","sn","so","sq","sr","su","sv","sw","ta","te","tg","th","tk","tl","tr","tt","uk","ur","uz","vi","yi","yo","zh"], Field(..., description="The language in which the summary should be generated")]
) -> Annotated[str, "JSON formatted result report with document summary in the 'summary' field"]:
    """
    Summarize the content of documents and generate a concise abstract based on the user's prompt. The tool extracts and condenses the main ideas or information from the document(s) according to the user's requirements.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始摘要 {len(files)} 个文件...")
    
    # 构建操作配置
    extra_params = {
        "prompt": prompt,
        "language": language
    }
    
    operation_config = generate_operation_config(
        operation_type="summarize",
        extra_params=extra_params
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "文档摘要完成")
    return result

@mcp.tool
async def create_pdf(
    ctx: Context,
    prompt: Annotated[str, Field(..., description="A text-only description or instruction of what PDF content to generate", min_length=1)],
    filename: Annotated[str, Field(..., description="The filename for the generated PDF", min_length=1)],
    language: Annotated[Literal["zh", "en", "de", "es", "fr", "ja", "pt", "zh-tw", "ar", "cs", "da", "fi", "el", "hu", "it", "nl", "no", "pl", "sv", "tr"], Field(..., description="The language for the generated PDF content")],
    enable_web_search: Annotated[bool, Field(description="Whether to enable web search to gather additional information for content generation")] = False
) -> Annotated[str, "JSON formatted result report with generated PDF download URL and file information"]:
    """
    Generate PDF documents from text-only instructions or descriptions. The tool creates PDFs based on written prompts such as 'create a business report', 'generate meeting minutes', etc. Only accepts plain text input - no file uploads or multimedia content supported.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始根据提示生成PDF：{prompt[:50]}...")
    
    # 使用PDF创建适配器
    result = await create_pdf_adapter(logger, prompt, filename, language, enable_web_search)
    
    await logger.log("info", "PDF生成完成")
    return result

# ==================== 专业工具 ====================

@mcp.tool
async def remove_margin(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to remove margins from")]
) -> Annotated[str, "JSON formatted result report with margin-cropped PDF files"]:
    """
    Remove white margins from PDF files (crop page margins).
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始去除 {len(files)} 个PDF文件的白边...")
    
    # 构建操作配置
    operation_config = generate_operation_config(
        operation_type="edit",
        edit_type="remove_margin"
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "PDF白边去除完成")
    return result

@mcp.tool
async def extract_images(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to extract images from")],
    format: Annotated[Literal["bmp", "png", "gif", "tif", "jpg"], Field(description="Extracted image format")] = "png"
) -> Annotated[str, "JSON formatted result report with extracted image files in zip package"]:
    """
    Extract embedded image resources from PDF files. This tool finds and extracts actual image files (photos, logos, graphics) that are embedded within the PDF document, saving them as separate image files.
    
    Use case: Getting the original images that were inserted into the PDF document.
    Note: This is different from convert_document PDF-to-image conversion, which converts entire PDF pages into image format. Use convert_document if you want to convert PDF pages to images, use extract_images if you want to get embedded pictures from the PDF.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始从 {len(files)} 个PDF文件提取图片...")
    
    # 构建操作配置
    extra_params = {
        "format": format
    }
    
    operation_config = generate_operation_config(
        operation_type="edit",
        edit_type="extract_image",
        extra_params=extra_params
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "图片提取完成")
    return result

@mcp.tool
async def flatten_pdf(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to flatten")]
) -> Annotated[str, "JSON formatted result report with flattened PDF files (non-editable content)"]:
    """
    Flatten PDF files (convert editable elements such as form fields, annotations, and layers into non-editable static content). This preserves the visual appearance while making interactive elements non-functional.
    
    Note: For converting text characters to vector curves/outlines, use curve_pdf instead. Flattening affects form fields and annotations, while curving affects text editability.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始展平 {len(files)} 个PDF文件...")
    
    # 构建操作配置
    operation_config = generate_operation_config(
        operation_type="convert",
        format_value="flatten-pdf"
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "PDF展平完成")
    return result

@mcp.tool
async def repair_pdf(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to repair")]
) -> Annotated[str, "JSON formatted result report with repaired PDF files"]:
    """
    Repair corrupted or damaged PDF files to restore readability and functionality.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始修复 {len(files)} 个PDF文件...")
    
    # 构建操作配置
    operation_config = generate_operation_config(
        operation_type="convert",
        format_value="pdf-repair"
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "PDF修复完成")
    return result

@mcp.tool
async def curve_pdf(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to convert to curves")]
) -> Annotated[str, "JSON formatted result report with curve-converted PDF files"]:
    """
    Convert PDF text characters to vector curves (outlines), making text unselectable and unsearchable while maintaining exact visual appearance. This is commonly used for font protection and preventing text extraction.
    
    Note: This specifically converts text to curves. For making form fields and annotations non-editable, use flatten_pdf instead.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始转曲 {len(files)} 个PDF文件...")
    
    # 构建操作配置
    operation_config = generate_operation_config(
        operation_type="convert",
        format_value="curve-pdf"
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "PDF转曲完成")
    return result

@mcp.tool
async def double_layer_pdf(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to convert to double layer")],
    language: Annotated[str, Field(..., description="Language of the text in the document using ISO 639-1 standard language codes (e.g., 'en' for English, 'zh' for Chinese, 'ja' for Japanese, 'es' for Spanish)", min_length=2, max_length=2)]
) -> Annotated[str, "JSON formatted result report with double-layer PDF files"]:
    """
    Convert scanned PDF to double-layer PDF, adding a text layer beneath the original image while preserving exact visual appearance. This makes scanned documents searchable and selectable without changing how they look.
    
    Note: This adds a text layer to image-based PDFs. For extracting text from scanned documents into editable formats, use ocr_document instead.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始转换 {len(files)} 个PDF文件为双层PDF...")
    
    # 构建操作配置
    extra_params = {
        "language": language
    }
    
    operation_config = generate_operation_config(
        operation_type="convert",
        format_value="double-pdf",
        extra_params=extra_params
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "PDF双层转换完成")
    return result

@mcp.tool
async def delete_pdf_pages(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to delete pages from")],
    range: Annotated[str, Field(..., description="Page range to delete, e.g. '1,3,5-7'", min_length=1)]
) -> Annotated[str, "JSON formatted result report with page-deleted PDF files"]:
    """
    Delete unwanted pages from PDF files. Use this when you want to permanently remove specific pages from the document. 
    
    Note: This is different from split_pdf which extracts and keeps wanted pages. Use delete_pdf_pages when you know which pages to remove, use split_pdf when you know which pages to keep.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始删除 {len(files)} 个PDF文件的指定页面...")
    
    # 构建操作配置
    extra_params = {
        "range": range
    }
    
    operation_config = generate_operation_config(
        operation_type="edit",
        edit_type="pdf-delete-page",
        extra_params=extra_params
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "PDF页面删除完成")
    return result

@mcp.tool
async def restrict_printing(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to restrict printing")],
    password: Annotated[str, Field(..., description="New permission password to set", min_length=1)]
) -> Annotated[str, "JSON formatted result report with print-restricted PDF files"]:
    """
    Restrict PDF printing permissions. This sets an owner password that prevents users from printing the document while still allowing them to view it. The document can be opened and read normally, but printing is blocked.
    
    Note: This is different from protect_pdf which requires a password to open the document. Use restrict_printing to control usage permissions while allowing viewing, use protect_pdf to prevent unauthorized access entirely.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始限制 {len(files)} 个PDF文件的打印权限...")
    
    # 构建操作配置
    extra_params = {
        "password": password,
        "provider": "printpermission"
    }
    
    operation_config = generate_operation_config(
        operation_type="edit",
        edit_type="encrypt",
        extra_params=extra_params
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "PDF打印权限限制完成")
    return result

@mcp.tool
async def resize_pdf(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to resize")],
    page_size: Annotated[Optional[str], Field(description="Target page size. Any valid page size name is supported (e.g., a4, letter, legal, etc.), or use width,height in points (pt, e.g., 595,842). If not set, page size will not be changed")] = None,
    resolution: Annotated[Optional[int], Field(description="Image resolution (dpi), e.g., 72. If not set, resolution will not be changed", ge=1)] = None
) -> Annotated[str, "JSON formatted result report with resized PDF files"]:
    """
    Resize PDF pages. You can specify the target page size (a0/a1/a2/a3/a4/a5/a6/letter) and/or the image resolution (dpi, e.g., 72). If not set, the corresponding property will not be changed.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始调整 {len(files)} 个PDF文件的大小...")
    
    # 构建操作配置
    extra_params = {}
    if page_size:
        extra_params["page_size"] = page_size
    if resolution:
        extra_params["resolution"] = resolution
    
    operation_config = generate_operation_config(
        operation_type="convert",
        format_value="resize-pdf",
        extra_params=extra_params
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "PDF大小调整完成")
    return result

@mcp.tool
async def replace_text(
    ctx: Context,
    files: Annotated[List[FileObject], Field(..., description="List of PDF files to replace text in")],
    old_text: Annotated[str, Field(..., description="The text to be replaced or deleted", min_length=1)],
    new_text: Annotated[str, Field(description="The replacement text. If empty, the old_text will be deleted")]
) -> Annotated[str, "JSON formatted result report with text-modified PDF files"]:
    """
    Replace, edit, or delete regular document text content in PDF files. Use this for modifying normal text within the document body, such as correcting names, dates, or other content. When new_text is empty, the specified text will be permanently deleted.
    
    Note: This is for regular document text content only. For removing watermarks, security overlays, or branding elements, use remove_watermark instead.
    """
    logger = Logger(ctx, collect_info=False)
    await logger.log("info", f"开始替换 {len(files)} 个PDF文件中的文本...")
    
    # 构建操作配置
    extra_params = {
        "old_text": old_text,
        "new_text": new_text
    }
    
    operation_config = generate_operation_config(
        operation_type="convert",
        format_value="pdf-replace-text",
        extra_params=extra_params
    )
    
    # 调用适配器
    result = await process_tool_call_adapter(logger, files, operation_config)
    
    await logger.log("info", "文本替换完成")
    return result

# ==================== 启动逻辑 ====================

def main():
    """应用主入口"""
    # 打印版本号
    try:
        import importlib.metadata
        version = importlib.metadata.version("lightpdf-aipdf-mcp")
        print(f"LightPDF AI-PDF FastMCP Server v{version}", file=sys.stderr)
    except Exception:
        print("LightPDF AI-PDF FastMCP Server (FastMCP版本)", file=sys.stderr)
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="LightPDF AI-PDF FastMCP Server")
    parser.add_argument("-p", "--port", type=int, default=0, help="指定服务器端口号，默认使用HTTP模式，加--sse使用SSE模式")
    parser.add_argument("--sse", action="store_true", help="使用SSE传输模式（需要配合--port）")
    args = parser.parse_args()
    
    if args.port:
        if args.sse:
            print(f"启动SSE服务器，端口号：{args.port}", file=sys.stderr)
            mcp.run(transport="sse", host="0.0.0.0", port=args.port)
        else:
            print(f"启动HTTP服务器，端口号：{args.port}", file=sys.stderr)
            mcp.run(transport="streamable-http", host="0.0.0.0", port=args.port)
    else:
        print("启动stdio服务器", file=sys.stderr)
        mcp.run()  # 默认使用stdio

def cli_main():
    try:
        main()
    except KeyboardInterrupt:
        print("服务器被用户中断", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"服务器发生错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    cli_main() 