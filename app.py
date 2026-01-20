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

# Reason: Configure logging with UTF-8 encoding for Chinese character support
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    encoding="utf-8",
    force=True,
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

    # Reason: Validate and initialize session state
    from src.utils.session import validate_session_state

    validate_session_state()
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
        """Handle file upload or removal.

        Args:
            uploaded_files: List of uploaded files (empty if all removed).
        """
        try:
            if uploaded_files:
                # Files uploaded - load them with best-effort strategy
                from src.data_loader import load_excel_files_with_result

                result = load_excel_files_with_result(uploaded_files)

                # Display warnings for failed files
                if result.failed:
                    for filename, error in result.failed.items():
                        st.warning(f"⚠️ Failed to load '{filename}': {error}")
                    logger.warning(
                        f"Failed to load {len(result.failed)} files: "
                        f"{list(result.failed.keys())}"
                    )

                # Load successful files
                if result.successful:
                    chat_agent.load_data(result.successful)
                    set_loaded_data(result.successful)
                    logger.info(
                        f"Loaded {len(result.successful)} files successfully, "
                        f"{len(result.failed)} failed"
                    )
                    st.success(
                        f"✅ Loaded {len(result.successful)} file(s) successfully"
                    )
                else:
                    # All files failed
                    chat_agent.load_data([])
                    set_loaded_data([])
                    st.error("❌ All files failed to load. Please check file formats.")
            else:
                # All files removed - clear data
                chat_agent.load_data([])
                set_loaded_data([])
                logger.info("All files removed - cleared loaded data")
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

                # Reason: Organize and display visualizations by category with tabs
                viz_by_cat = report["visualizations_by_category"]

                # Show summary of what was found
                summary_msg = "**Auto Insights Generated:**\n\n"
                if viz_by_cat["trending"]:
                    summary_msg += (
                        f"- 📈 {len(viz_by_cat['trending'])} Trending Analysis\n"
                    )
                if viz_by_cat["correlation"]:
                    summary_msg += (
                        f"- 🔗 {len(viz_by_cat['correlation'])} Correlation Analysis\n"
                    )
                if viz_by_cat["distribution"]:
                    summary_msg += f"- 📊 {len(viz_by_cat['distribution'])} Distribution Analysis\n"
                if viz_by_cat["categorical"]:
                    summary_msg += (
                        f"- 📋 {len(viz_by_cat['categorical'])} Categorical Analysis\n"
                    )

                add_message("assistant", summary_msg, "text")

                # Add visualizations in priority order
                for viz in report["visualizations"]:
                    add_message("assistant", viz["figure"], "chart")

                logger.info(
                    f"Generated {len(report['visualizations'])} visualizations "
                    f"({len(viz_by_cat['trending'])} trending, "
                    f"{len(viz_by_cat['correlation'])} correlation, "
                    f"{len(viz_by_cat['distribution'])} distribution, "
                    f"{len(viz_by_cat['categorical'])} categorical)"
                )
                st.rerun()

        except Exception as e:
            st.error(f"Failed to generate insights: {e}")
            logger.error(f"Auto insights error: {e}", exc_info=True)

    # Reason: Render sidebar
    # Check if data is loaded (either in chat_agent or session state)
    has_data = chat_agent.is_data_loaded() or len(get_loaded_data()) > 0
    render_sidebar(
        config_api_key=api_key,
        config_model=model,
        on_api_key_change=on_api_key_change,
        on_model_change=on_model_change,
        on_file_upload=on_file_upload,
        on_clear_chat=on_clear_chat,
        on_auto_insights=on_auto_insights,
        has_data=has_data,
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
