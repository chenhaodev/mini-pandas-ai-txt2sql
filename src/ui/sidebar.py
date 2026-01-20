"""Streamlit sidebar component for file upload and settings."""

import logging
from typing import Callable, Optional

import streamlit as st

logger = logging.getLogger(__name__)


def render_sidebar(
    config_api_key: str,
    config_model: str,
    on_api_key_change: Optional[Callable[[str], None]] = None,
    on_model_change: Optional[Callable[[str], None]] = None,
    on_file_upload: Optional[Callable[[list], None]] = None,
    on_clear_chat: Optional[Callable[[], None]] = None,
    on_auto_insights: Optional[Callable[[], None]] = None,
    has_data: bool = False,
) -> list:
    """Render the sidebar with file upload and settings.

    Args:
        config_api_key: Default API key from config.
        config_model: Default model from config.
        on_api_key_change: Callback when API key changes.
        on_model_change: Callback when model changes.
        on_file_upload: Callback when files are uploaded.
        on_clear_chat: Callback when clear chat is clicked.
        on_auto_insights: Callback when auto insights is clicked.
        has_data: Whether data is currently loaded.

    Returns:
        list: List of uploaded file objects.
    """
    with st.sidebar:
        st.header("Settings")

        # Reason: API key input with type='password' for security
        api_key_input = st.text_input(
            "DeepSeek API Key",
            type="password",
            help="Enter your DeepSeek API key. Leave empty to use .env file.",
            value=config_api_key,
        )

        if on_api_key_change and api_key_input != config_api_key:
            on_api_key_change(api_key_input)

        # Reason: Model selection dropdown
        model_options = ["deepseek-chat", "deepseek-reasoner"]
        model_input = st.selectbox(
            "Model",
            options=model_options,
            index=model_options.index(config_model)
            if config_model in model_options
            else 0,
            help="deepseek-chat: Standard mode | deepseek-reasoner: Thinking mode",
        )

        if on_model_change and model_input != config_model:
            on_model_change(model_input)

        st.divider()

        # Reason: File upload widget with multi-file support
        st.header("Data Upload")
        uploaded_files = st.file_uploader(
            "Upload data files",
            type=["xlsx", "xls", "csv"],
            accept_multiple_files=True,
            help="Upload Excel (.xlsx, .xls) or CSV (.csv) files to analyze.",
        )

        if on_file_upload and uploaded_files:
            on_file_upload(uploaded_files)

        # Reason: Display uploaded files summary
        if uploaded_files:
            st.success(f"Loaded {len(uploaded_files)} file(s)")
            for file in uploaded_files:
                st.caption(f"📄 {file.name}")
        else:
            st.info("No files uploaded yet.")

        st.divider()

        # Reason: Action buttons
        st.header("Actions")

        # Reason: Auto insights button
        if st.button(
            "🔍 Generate Auto Insights",
            use_container_width=True,
            disabled=not has_data,
            help="Automatically generate statistics and visualizations"
            if has_data
            else "Upload data first",
        ):
            if on_auto_insights:
                on_auto_insights()

        # Reason: Clear chat button
        if st.button("Clear Chat History", use_container_width=True):
            if on_clear_chat:
                on_clear_chat()
                st.rerun()

        st.divider()

        # Reason: Display example queries
        with st.expander("💡 Example Queries"):
            st.markdown("""
            **Quick Start:**
            - Click "🔍 Generate Auto Insights" for automatic analysis
            
            **Simple Queries:**
            - How many rows are in the data?
            - What are the column names?
            - Show me the top 5 rows.

            **Aggregation Queries:**
            - What is the total by [column]?
            - Show me the average of [column] grouped by [column].
            - Count the occurrences of [column].

            **Visualization Requests:**
            - Create a bar chart of [column] vs [column].
            - Plot a pie chart showing [column] distribution.
            - Create a histogram of [column].
            """)

        # Reason: Display app info
        st.divider()
        st.caption("Built with PandasAI + Streamlit")
        st.caption("Powered by DeepSeek")

    return uploaded_files
