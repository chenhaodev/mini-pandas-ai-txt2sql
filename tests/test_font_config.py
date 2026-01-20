"""Unit tests for font configuration module."""

from unittest.mock import patch

import matplotlib


class TestGetChineseFont:
    """Tests for get_chinese_font function."""

    @patch("platform.system")
    @patch("matplotlib.font_manager.get_font_names")
    def test_get_chinese_font_macos_with_songti(self, mock_get_fonts, mock_system):
        """Test Chinese font detection on macOS with Songti SC available."""
        mock_system.return_value = "Darwin"
        mock_get_fonts.return_value = [
            "Songti SC",
            "PingFang SC",
            "Heiti SC",
            "Arial",
        ]

        from src.utils.font_config import get_chinese_font

        result = get_chinese_font()

        assert result == "Songti SC"

    @patch("platform.system")
    @patch("matplotlib.font_manager.get_font_names")
    def test_get_chinese_font_macos_with_pingfang(self, mock_get_fonts, mock_system):
        """Test Chinese font detection on macOS with PingFang SC available."""
        mock_system.return_value = "Darwin"
        mock_get_fonts.return_value = [
            "PingFang SC",
            "Arial",
            "Helvetica",
        ]

        from src.utils.font_config import get_chinese_font

        result = get_chinese_font()

        assert result == "PingFang SC"

    @patch("platform.system")
    @patch("matplotlib.font_manager.get_font_names")
    def test_get_chinese_font_windows(self, mock_get_fonts, mock_system):
        """Test Chinese font detection on Windows."""
        mock_system.return_value = "Windows"
        mock_get_fonts.return_value = [
            "SimHei",
            "Microsoft YaHei",
            "Arial",
        ]

        from src.utils.font_config import get_chinese_font

        result = get_chinese_font()

        assert result == "SimHei"

    @patch("platform.system")
    @patch("matplotlib.font_manager.get_font_names")
    def test_get_chinese_font_windows_microsoft_yahei(
        self, mock_get_fonts, mock_system
    ):
        """Test Chinese font detection on Windows with Microsoft YaHei."""
        mock_system.return_value = "Windows"
        mock_get_fonts.return_value = [
            "Microsoft YaHei",
            "KaiTi",
            "Arial",
        ]

        from src.utils.font_config import get_chinese_font

        result = get_chinese_font()

        assert result == "Microsoft YaHei"

    @patch("platform.system")
    @patch("matplotlib.font_manager.get_font_names")
    def test_get_chinese_font_linux(self, mock_get_fonts, mock_system):
        """Test Chinese font detection on Linux."""
        mock_system.return_value = "Linux"
        mock_get_fonts.return_value = [
            "WenQuanYi Micro Hei",
            "Noto Sans CJK SC",
            "Arial",
        ]

        from src.utils.font_config import get_chinese_font

        result = get_chinese_font()

        assert result == "WenQuanYi Micro Hei"

    @patch("platform.system")
    @patch("matplotlib.font_manager.get_font_names")
    def test_get_chinese_font_no_chinese_fonts(self, mock_get_fonts, mock_system):
        """Test fallback when no Chinese fonts are available."""
        mock_system.return_value = "Darwin"
        mock_get_fonts.return_value = [
            "Arial",
            "Helvetica",
            "Times New Roman",
        ]

        from src.utils.font_config import get_chinese_font

        result = get_chinese_font()

        assert result is None

    @patch("platform.system")
    @patch("matplotlib.font_manager.get_font_names")
    def test_get_chinese_font_unsupported_platform(self, mock_get_fonts, mock_system):
        """Test font detection on unsupported platform."""
        mock_system.return_value = "FreeBSD"
        mock_get_fonts.return_value = [
            "WenQuanYi Micro Hei",
            "Arial",
        ]

        from src.utils.font_config import get_chinese_font

        result = get_chinese_font()

        assert result == "WenQuanYi Micro Hei"

    @patch("platform.system")
    @patch("matplotlib.font_manager.get_font_names")
    def test_get_chinese_font_case_insensitive(self, mock_get_fonts, mock_system):
        """Test font name matching is case-insensitive."""
        mock_system.return_value = "Darwin"
        mock_get_fonts.return_value = [
            "SONGTI SC",  # uppercase
            "pingfang sc",  # lowercase
        ]

        from src.utils.font_config import get_chinese_font

        result = get_chinese_font()

        # Should match despite case difference
        assert result is not None


class TestConfigureMatplotlibFonts:
    """Tests for configure_matplotlib_fonts function."""

    @patch("src.utils.font_config.get_chinese_font")
    @patch("matplotlib.font_manager._load_fontmanager")
    def test_configure_matplotlib_fonts_with_chinese_font(
        self, mock_load_manager, mock_get_font
    ):
        """Test matplotlib configuration with Chinese font available."""
        mock_get_font.return_value = "Songti SC"

        from src.utils.font_config import configure_matplotlib_fonts

        result = configure_matplotlib_fonts()

        assert result == "Songti SC"
        assert "Songti SC" in matplotlib.rcParams["font.sans-serif"]
        assert "DejaVu Sans" in matplotlib.rcParams["font.sans-serif"]
        assert matplotlib.rcParams["axes.unicode_minus"] is False
        mock_load_manager.assert_called_once_with(try_read_cache=False)

    @patch("src.utils.font_config.get_chinese_font")
    @patch("matplotlib.font_manager._load_fontmanager")
    def test_configure_matplotlib_fonts_without_chinese_font(
        self, mock_load_manager, mock_get_font
    ):
        """Test matplotlib configuration without Chinese font."""
        mock_get_font.return_value = None

        from src.utils.font_config import configure_matplotlib_fonts

        result = configure_matplotlib_fonts()

        assert result is None
        # Font list should not be modified
        mock_load_manager.assert_not_called()

    @patch("src.utils.font_config.get_chinese_font")
    @patch("matplotlib.font_manager._load_fontmanager")
    def test_configure_matplotlib_fonts_sets_correct_font_list(
        self, mock_load_manager, mock_get_font
    ):
        """Test that font list includes Chinese font and fallbacks."""
        mock_get_font.return_value = "PingFang SC"

        from src.utils.font_config import configure_matplotlib_fonts

        configure_matplotlib_fonts()

        font_list = matplotlib.rcParams["font.sans-serif"]
        assert "PingFang SC" == font_list[0]
        assert "DejaVu Sans" in font_list
        assert "Arial" in font_list

    @patch("src.utils.font_config.get_chinese_font")
    @patch("matplotlib.font_manager._load_fontmanager")
    def test_configure_matplotlib_fonts_clears_cache(
        self, mock_load_manager, mock_get_font
    ):
        """Test that font cache is cleared."""
        mock_get_font.return_value = "Songti SC"

        from src.utils.font_config import configure_matplotlib_fonts

        configure_matplotlib_fonts()

        mock_load_manager.assert_called_once_with(try_read_cache=False)


class TestGetFontWarning:
    """Tests for get_font_warning function."""

    def test_get_font_warning_returns_string(self):
        """Test that warning message is returned."""
        from src.utils.font_config import get_font_warning

        warning = get_font_warning()

        assert isinstance(warning, str)
        assert len(warning) > 0
        assert "Warning" in warning or "⚠️" in warning

    def test_get_font_warning_mentions_chinese(self):
        """Test that warning mentions Chinese fonts."""
        from src.utils.font_config import get_font_warning

        warning = get_font_warning()

        assert "Chinese" in warning or "chinese" in warning

    def test_get_font_warning_mentions_platforms(self):
        """Test that warning mentions macOS and Windows."""
        from src.utils.font_config import get_font_warning

        warning = get_font_warning()

        assert "macOS" in warning or "Windows" in warning or "PingFang" in warning
