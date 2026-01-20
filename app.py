"""Main Streamlit application for PandasAI TXT2SQL system."""

import logging
import sys
from pathlib import Path

import streamlit as st

# Reason: Add src directory to path for imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.auto_insights import AutoInsight
from src.chat_agent import PandasAIAgent
from src.config import get_config
from src.data_loader import load_excel_files
from src.llm_client import DeepSeekClient
from src.ui import render_chat_interface, render_sidebar
from src.utils import (
    add_message,
    clear_chat_history,
    configure_matplotlib_fonts,
    get_api_key,
    get_font_warning,
    get_loaded_data,
    get_model,
    init_session_state,
    set_api_key,
    set_loaded_data,
    set_model,
)

# Reason: Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Reason: Configure matplotlib for Chinese character support
configured_font = configure_matplotlib_fonts()


def main() -> None:
    """Main application entry point."""
    # Reason: Load configuration
    try:
        config = get_config()
    except Exception as e:
        st.error(f"Configuration error: {e}")
        logger.error(f"Configuration error: {e}", exc_info=True)
        st.stop()

    # Reason: Configure Streamlit page
    st.set_page_config(
        page_title=config.app_title,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Reason: Initialize session state
    init_session_state()

    # Reason: Show warning if Chinese font is not available
    if not configured_font:
        st.warning(get_font_warning())

    # Reason: Get or use session API key
    api_key = get_api_key() or config.deepseek_api_key

    # Reason: Get or use session model
    model = get_model() or config.deepseek_model

    # Reason: Initialize LLM client
    llm_client = DeepSeekClient(
        api_key=api_key,
        model=model,
        base_url=config.deepseek_base_url,
        temperature=0.0,
        max_retries=3,
    )

    # Reason: Initialize PandasAI agent
    chat_agent = PandasAIAgent(llm_client=llm_client)

    # Reason: Reload data from session state if available
    loaded_data = get_loaded_data()
    if loaded_data:
        chat_agent.load_data(loaded_data)
        logger.info(f"Reloaded {len(loaded_data)} DataFrames from session state")

    # Reason: Handle callback functions
    def on_api_key_change(new_key: str) -> None:
        """Handle API key change."""
        set_api_key(new_key)
        logger.info("API key updated in session")

    def on_model_change(new_model: str) -> None:
        """Handle model change."""
        set_model(new_model)
        logger.info(f"Model changed to {new_model}")

    def on_file_upload(uploaded_files: list) -> None:
        """Handle file upload."""
        try:
            loaded_data = load_excel_files(uploaded_files)
            chat_agent.load_data(loaded_data)
            set_loaded_data(loaded_data)
            logger.info(f"Loaded {len(loaded_data)} Excel files")
        except Exception as e:
            st.error(f"Failed to load files: {e}")
            logger.error(f"Failed to load files: {e}", exc_info=True)

    def on_clear_chat() -> None:
        """Handle chat clear."""
        clear_chat_history()
        set_loaded_data([])
        logger.info("Chat history and loaded data cleared")

    def on_auto_insights() -> None:
        """Handle auto insights generation."""
        if not chat_agent.is_data_loaded():
            st.error("Please upload data files first.")
            return

        try:
            with st.spinner("🔍 Generating auto insights..."):
                # Reason: Get DataFrames from loaded data
                dataframes = [ld.data for ld in chat_agent.loaded_data]
                names = [ld.filename for ld in chat_agent.loaded_data]

                # Reason: Generate insights
                auto_insight = AutoInsight(dataframes, names)
                report = auto_insight.generate_full_report()

                # Reason: Add insights text to chat
                add_message("user", "Generate auto insights", "text")
                add_message("assistant", report["insights_text"], "text")

                # Reason: Add visualizations to chat
                for viz in report["visualizations"]:
                    add_message("assistant", viz["figure"], "chart")

                logger.info(f"Generated {len(report['visualizations'])} visualizations")
                st.rerun()

        except Exception as e:
            st.error(f"Failed to generate insights: {e}")
            logger.error(f"Auto insights error: {e}", exc_info=True)

    # Reason: Render sidebar
    uploaded_files = render_sidebar(
        config_api_key=api_key,
        config_model=model,
        on_api_key_change=on_api_key_change,
        on_model_change=on_model_change,
        on_file_upload=on_file_upload,
        on_clear_chat=on_clear_chat,
        on_auto_insights=on_auto_insights,
        has_data=chat_agent.is_data_loaded(),
    )

    # Reason: Render main content area
    st.title(f"📊 {config.app_title}")
    st.caption("Analyze your Excel data with natural language")

    # Reason: Display welcome message if needed
    if not chat_agent.is_data_loaded():
        render_welcome_message(has_data=False)
    else:
        render_welcome_message(has_data=True)
        st.divider()

        # Reason: Display data summary
        with st.expander("📋 Data Summary", expanded=False):
            for i, summary in enumerate(chat_agent.get_data_summary()):
                st.write(f"**File {i + 1}:**")
                st.json(
                    {
                        "Rows": summary["rows"],
                        "Columns": summary["columns"],
                        "Column Names": summary["column_names"],
                        "Has Null Values": summary["has_nulls"],
                    }
                )

        st.divider()

    # Reason: Render chat interface
    render_chat_interface(chat_agent=chat_agent)


def render_welcome_message(has_data: bool) -> None:
    """Render welcome message.

    Args:
        has_data: Whether data has been loaded.
    """
    if not has_data:
        st.info("""
        👋 Welcome to PandasAI TXT2SQL!

        To get started:
        1. 📤 Upload your data files using the sidebar
        2. 💬 Ask questions about your data in natural language
        3. 📊 View results, tables, and charts

        Supported file formats: .xlsx, .xls, .csv
        """)
    else:
        st.success("""
        🎉 Data loaded successfully!

        You can now ask questions about your data.
        Try queries like:
        - "Show me the top 5 rows"
        - "What is the average of [column]?"
        - "Create a bar chart of [column]"
        """)


if __name__ == "__main__":
    main()
