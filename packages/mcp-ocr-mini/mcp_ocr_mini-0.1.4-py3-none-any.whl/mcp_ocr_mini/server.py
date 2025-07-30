"""MCP OCR Server implementation."""

from typing import Union
import cv2
import numpy as np
import pytesseract
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
import httpx
import os
import urllib.parse
from enum import Enum
import subprocess
import sys
from .install_tesseract import install_tesseract, find_tesseract_executable

# Global error message for Tesseract installation issues
TESSERACT_INSTALL_MSG = (
    "For Windows platform, please ensure Tesseract is installed from: https://github.com/UB-Mannheim/tesseract/wiki."
    "After installation, ensure the Tesseract installation directory is in your system PATH by checking \"tesseract --version\" in command prompt.\n"
)

def check_tesseract():
    """Check if Tesseract is available and configure pytesseract."""
    # First try to find and configure Tesseract without PATH
    tesseract_path = find_tesseract_executable()
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        print(f"Configured pytesseract to use: {tesseract_path}")
        return
    
    # Fallback: try PATH version
    try:
        subprocess.run(["tesseract", "--version"], check=True, stdout=sys.stderr, stderr=sys.stderr)
        return
    except (subprocess.CalledProcessError, FileNotFoundError):        
        print("Tesseract not found. Attempting to install...", file=sys.stderr)
        try:
            install_tesseract()
            # Try to configure again after installation
            tesseract_path = find_tesseract_executable()
            if tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                print(f"Configured pytesseract to use: {tesseract_path}")
        except Exception as e:
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"OCR processing failed: {str(e)} {TESSERACT_INSTALL_MSG}"
                )
            )
              

check_tesseract()

# Initialize FastMCP server
mcp = FastMCP("ocr")

class OCRInputType(Enum):
    FILE = "file"
    URL = "url"

async def load_image(input_data: Union[str]) -> np.ndarray:
    """Load image from various sources (file path, URL).
    
    Args:
        input_data: Can be a file path, URL
        
    Returns:
        numpy array of the image
        
    Raises:
        McpError: If image loading fails
    """
    try:
        # Determine input type
        if isinstance(input_data, str):
            # Check if it's a URL
            if urllib.parse.urlparse(input_data).scheme in ('http', 'https'):
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.get(input_data)
                        response.raise_for_status()
                        nparr = np.frombuffer(response.content, np.uint8)
                except httpx.HTTPError as e:
                    raise McpError(
                        ErrorData(
                            code=INTERNAL_ERROR,
                            message=f"Failed to fetch image from URL: {str(e)}"
                        )
                    )
            # Check if it's a file path
            elif os.path.exists(input_data):
                try:
                    nparr = np.fromfile(input_data, np.uint8)
                except Exception as e:
                    raise McpError(
                        ErrorData(
                            code=INTERNAL_ERROR,
                            message=f"Failed to read image file: {str(e)}"
                        )
                    )
            else:
                raise McpError(
                    ErrorData(
                        code=INVALID_PARAMS,
                        message=f"Invalid input: {input_data} is neither a valid URL nor an existing file"
                    )
                )
        else:
            # It's bytes
            raise McpError(
                    ErrorData(
                        code=INVALID_PARAMS,
                        message=f"Invalid input: {input_data} is neither a valid URL nor an existing file"
                    )
                )
        
        # Decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message="Failed to decode image data"
                )
            )
        return img
            
    except McpError:
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Unexpected error loading image: {str(e)}"
            )
        )

@mcp.tool()
async def perform_ocr(
    input_data: Union[str],
    language: str = "eng",
    config: str = "--oem 3 --psm 6"
) -> str:
    """Perform OCR on the provided input.
    
    Args:
        input_data: Can be one of:
            - File path to an image
            - URL to an image
        
    Returns:
        Extracted text from the image
        
    Usage:
        perform_ocr("/path/to/image.jpg")
        perform_ocr("https://example.com/image.jpg")
    """
    try:
        # Validate language
        available_langs = pytesseract.get_languages()
        if language not in available_langs:
            raise McpError(
                ErrorData(
                    code=INVALID_PARAMS,
                    message=f"Unsupported language: {language}. Available languages: {', '.join(available_langs)}"
                )
            )
            
        # Load and process image
        img = await load_image(input_data)
        
        try:
            # Perform OCR
            text = pytesseract.image_to_string(img, lang=language, config=config)
            if not text.strip():
                raise McpError(
                    ErrorData(
                        code=INTERNAL_ERROR,
                        message="No text detected in image"
                    )
                )
            return text.strip()
        except Exception as e:
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"OCR processing failed: {str(e)} {TESSERACT_INSTALL_MSG}"
                )
            )
            
    except McpError:
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Unexpected error during OCR: {str(e)} {TESSERACT_INSTALL_MSG}"
            )
        )



@mcp.tool()
async def get_supported_languages() -> list[str]:
    """Get list of supported OCR languages.
    
    Returns:
        List of supported language codes
        
    Usage:
        get_supported_languages()
    """
    try:
        langs = pytesseract.get_languages()
        if not langs:
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message="No supported languages found. Please check Tesseract installation."
                )
            )
        return langs
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to get supported languages: {str(e)} {TESSERACT_INSTALL_MSG}"
            )
        )

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')