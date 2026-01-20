"""Font configuration utilities for matplotlib Chinese character support."""

import logging
import platform
from typing import List, Optional

import matplotlib
import matplotlib.font_manager

logger = logging.getLogger(__name__)


def get_chinese_font() -> Optional[str]:
    """Get the best available Chinese font for the current platform.

    Returns:
        Optional[str]: Name of available Chinese font, or None if not found.
    """
    # Reason: Platform-specific font priority lists
    system = platform.system()

    font_priority: List[str] = []

    if system == "Darwin":  # macOS
        font_priority = [
            "Songti SC",  # 宋体-简 (serif)
            "PingFang SC",  # 苹方-简 (sans-serif)
            "Heiti SC",  # 黑体-简
            "STHeiti",  # 黑体
        ]
    elif system == "Windows":
        font_priority = [
            "SimSun",  # 宋体
            "SimHei",  # 黑体
            "Microsoft YaHei",  # 微软雅黑
            "KaiTi",  # 楷体
        ]
    else:  # Linux or other
        font_priority = [
            "WenQuanYi Micro Hei",
            "Noto Sans CJK SC",
            "Noto Sans CJK",
        ]

    # Reason: Get all available system fonts and normalize to lowercase for case-insensitive matching
    available_fonts = matplotlib.font_manager.get_font_names()
    available_fonts_lower = [f.lower() for f in available_fonts]

    # Reason: Find first available Chinese font (case-insensitive)
    for font_name in font_priority:
        if font_name.lower() in available_fonts_lower:
            # Return the original case version from available fonts
            for avail_font in available_fonts:
                if avail_font.lower() == font_name.lower():
                    return avail_font

    return None


def configure_matplotlib_fonts() -> Optional[str]:
    """Configure matplotlib to use Chinese fonts for chart rendering.

    Sets matplotlib rcParams to use available Chinese fonts for better
    support of CJK characters in charts. Falls back to default fonts
    if no Chinese font is available.

    Returns:
        Optional[str]: Name of configured Chinese font, or None if not found.
    """
    chinese_font = get_chinese_font()

    if chinese_font:
        # Reason: Configure matplotlib to use Chinese font
        font_list = [chinese_font, "DejaVu Sans", "Arial"]
        matplotlib.rcParams["font.sans-serif"] = font_list

        # Reason: Fix minus sign display in matplotlib
        matplotlib.rcParams["axes.unicode_minus"] = False

        # Reason: Clear font cache to ensure changes take effect
        matplotlib.font_manager._load_fontmanager(try_read_cache=False)

        return chinese_font

    return None


def get_font_warning() -> str:
    """Get warning message for when Chinese font is not available.

    Returns:
        str: Warning message to display in Streamlit UI.
    """
    return (
        "⚠️ Warning: Chinese characters may not display correctly in charts. "
        "Please install Chinese fonts (PingFang SC on macOS, Microsoft YaHei on Windows) "
        "for better support."
    )
