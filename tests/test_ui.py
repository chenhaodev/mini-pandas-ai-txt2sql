"""Unit tests for UI components module."""

from unittest.mock import MagicMock, patch

import pandas as pd


class TestDisplayMessage:
    """Tests for _display_message function."""

    def test_display_text_message(self):
        """Test displaying a text message."""
        with (
            patch("streamlit.chat_message") as mock_chat_msg,
            patch("streamlit.write") as mock_write,
        ):
            mock_chat_msg.return_value.__enter__ = MagicMock()
            mock_chat_msg.return_value.__exit__ = MagicMock()

            from src.ui.chat import _display_message

            message = {"role": "user", "content": "Hello", "type": "text"}
            _display_message(message)

            mock_chat_msg.assert_called_once_with("user")
            mock_write.assert_called_once_with("Hello")

    def test_display_error_message(self):
        """Test displaying an error message."""
        with (
            patch("streamlit.chat_message") as mock_chat_msg,
            patch("streamlit.error") as mock_error,
        ):
            mock_chat_msg.return_value.__enter__ = MagicMock()
            mock_chat_msg.return_value.__exit__ = MagicMock()

            from src.ui.chat import _display_message

            message = {
                "role": "assistant",
                "content": "Error occurred",
                "type": "error",
            }
            _display_message(message)

            mock_chat_msg.assert_called_once_with("assistant")
            mock_error.assert_called_once_with("Error occurred")

    def test_display_dataframe_message(self):
        """Test displaying a dataframe message."""
        df = pd.DataFrame({"a": [1, 2, 3]})

        with (
            patch("streamlit.chat_message") as mock_chat_msg,
            patch("streamlit.dataframe") as mock_df,
        ):
            mock_chat_msg.return_value.__enter__ = MagicMock()
            mock_chat_msg.return_value.__exit__ = MagicMock()

            from src.ui.chat import _display_message

            message = {"role": "assistant", "content": df, "type": "dataframe"}
            _display_message(message)

            mock_chat_msg.assert_called_once_with("assistant")
            mock_df.assert_called_once()

    def test_display_message_defaults_to_assistant(self):
        """Test that missing role defaults to assistant."""
        with patch("streamlit.chat_message") as mock_chat_msg:
            mock_chat_msg.return_value.__enter__ = MagicMock()
            mock_chat_msg.return_value.__exit__ = MagicMock()

            from src.ui.chat import _display_message

            message = {"content": "Test message"}
            _display_message(message)

            mock_chat_msg.assert_called_once_with("assistant")


class TestDisplayResponse:
    """Tests for _display_response function."""

    def test_display_error_response(self):
        """Test displaying an error response."""
        with patch("streamlit.error") as mock_error:
            from src.ui.chat import _display_response

            response = MagicMock()
            response.success = False
            response.content = "Something went wrong"

            _display_response(response)

            mock_error.assert_called_once_with("Error: Something went wrong")

    def test_display_dataframe_response(self):
        """Test displaying a dataframe response."""
        df = pd.DataFrame({"a": [1, 2, 3]})

        with patch("streamlit.dataframe") as mock_df:
            from src.ui.chat import _display_response

            response = MagicMock()
            response.success = True
            response.type = "dataframe"
            response.content = df

            _display_response(response)

            mock_df.assert_called_once_with(df, use_container_width=True)

    def test_display_text_response_with_explanation(self):
        """Test displaying a text response with explanation."""
        with patch("streamlit.markdown") as mock_markdown:
            from src.ui.chat import _display_response

            response = MagicMock()
            response.success = True
            response.type = "text"
            response.explanation = "Here is the explanation"
            response.content = "Result"

            _display_response(response)

            mock_markdown.assert_called_once_with("Here is the explanation")

    def test_display_text_response_without_explanation(self):
        """Test displaying a text response without explanation."""
        with patch("streamlit.write") as mock_write:
            from src.ui.chat import _display_response

            response = MagicMock()
            response.success = True
            response.type = "text"
            response.explanation = None
            response.content = "Simple result"

            _display_response(response)

            mock_write.assert_called_once_with("Simple result")


class TestDisplayChart:
    """Tests for _display_chart function."""

    def test_display_matplotlib_figure_with_figure_attr(self):
        """Test displaying a matplotlib figure with figure attribute."""
        with patch("streamlit.pyplot") as mock_pyplot:
            from src.ui.chat import _display_chart

            mock_chart = MagicMock()
            mock_chart.figure = "mock_figure"

            _display_chart(mock_chart)

            mock_pyplot.assert_called_once_with("mock_figure")

    def test_display_matplotlib_figure_with_savefig(self):
        """Test displaying a matplotlib figure with savefig method."""
        with patch("streamlit.pyplot") as mock_pyplot:
            from src.ui.chat import _display_chart

            mock_chart = MagicMock(spec=["savefig"])

            _display_chart(mock_chart)

            mock_pyplot.assert_called_once_with(mock_chart)

    def test_display_plotly_figure(self):
        """Test displaying a plotly figure."""
        with patch("streamlit.plotly_chart") as mock_plotly:
            from src.ui.chat import _display_chart

            mock_chart = MagicMock(spec=["show"])

            _display_chart(mock_chart)

            mock_plotly.assert_called_once_with(mock_chart, use_container_width=True)

    def test_display_fallback_for_unknown_chart(self):
        """Test fallback display for unknown chart type."""
        with patch("streamlit.write") as mock_write:
            from src.ui.chat import _display_chart

            mock_chart = MagicMock(spec=[])

            _display_chart(mock_chart)

            mock_write.assert_called_once_with(mock_chart)

    def test_display_chart_handles_exception(self):
        """Test chart display handles exceptions gracefully."""
        with (
            patch("streamlit.pyplot") as mock_pyplot,
            patch("streamlit.warning") as mock_warning,
            patch("streamlit.write") as mock_write,
        ):
            mock_pyplot.side_effect = Exception("Display error")

            from src.ui.chat import _display_chart

            mock_chart = MagicMock()
            mock_chart.figure = "mock_figure"

            _display_chart(mock_chart)

            mock_warning.assert_called_once()
            mock_write.assert_called_once_with(mock_chart)


class TestRenderWelcomeMessage:
    """Tests for render_welcome_message function."""

    def test_render_welcome_without_data(self):
        """Test rendering welcome message when no data is loaded."""
        with patch("streamlit.info") as mock_info:
            from src.ui.chat import render_welcome_message

            render_welcome_message(has_data=False)

            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            assert "Welcome" in call_args
            assert "Upload" in call_args

    def test_render_welcome_with_data(self):
        """Test rendering welcome message when data is loaded."""
        with patch("streamlit.success") as mock_success:
            from src.ui.chat import render_welcome_message

            render_welcome_message(has_data=True)

            mock_success.assert_called_once()
            call_args = mock_success.call_args[0][0]
            assert "loaded" in call_args.lower()


class TestUIExports:
    """Tests for UI module exports."""

    def test_render_sidebar_is_exported(self):
        """Test that render_sidebar is exported from ui module."""
        from src.ui import render_sidebar

        assert callable(render_sidebar)

    def test_render_chat_interface_is_exported(self):
        """Test that render_chat_interface is exported from ui module."""
        from src.ui import render_chat_interface

        assert callable(render_chat_interface)


class TestSidebarValidation:
    """Tests for sidebar input validation."""

    def test_model_options_contains_expected_models(self):
        """Test that model options contain expected models."""
        # Read the source to verify model options
        import inspect

        import src.ui.sidebar as sidebar_module

        source = inspect.getsource(sidebar_module.render_sidebar)

        assert "deepseek-chat" in source
        assert "deepseek-reasoner" in source
