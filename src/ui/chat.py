"""Streamlit chat interface component."""

import logging
from typing import Callable, Optional

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)


def render_chat_interface(
    chat_agent,
    on_message_add: Optional[Callable[[str, str, str], None]] = None,
) -> None:
    """Render the chat interface and handle user interactions.

    Args:
        chat_agent: The PandasAIAgent instance for queries.
        on_message_add: Callback when a message is added to history.
    """
    # Reason: Display existing chat history
    if "messages" in st.session_state:
        for idx, message in enumerate(st.session_state.messages):
            _display_message(message, message_idx=idx)

    # Reason: Handle new user input
    if prompt := st.chat_input("Ask about your data..."):
        # Reason: Add user message to history
        user_message = {
            "role": "user",
            "content": prompt,
            "type": "text",
        }
        st.session_state.messages.append(user_message)

        # Display user message
        with st.chat_message("user"):
            st.write(prompt)

        # Reason: Process query and display response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = chat_agent.query(prompt)

            # Display response based on type
            # Use timestamp-based key for new responses
            import time

            _display_response(response, key_suffix=f"new_{int(time.time() * 1000)}")

            # Reason: Add assistant response to history
            assistant_message = response.to_dict()
            st.session_state.messages.append(assistant_message)

        if on_message_add:
            on_message_add(
                response.type,
                response.content,
                "assistant" if response.success else "error",
            )


def _display_message(message: dict, message_idx: int = 0) -> None:
    """Display a single message from chat history.

    Args:
        message: Message dictionary with role, content, and type keys.
        message_idx: Index of the message in session state for unique keys.
    """
    role = message.get("role", "assistant")
    content = message.get("content")
    type_ = message.get("type", "text")

    with st.chat_message(role):
        if type_ == "dataframe" and isinstance(content, pd.DataFrame):
            st.dataframe(content, use_container_width=True)
        elif type_ == "chart":
            _display_chart(content, key_suffix=f"msg_{message_idx}")
        elif type_ == "auto_insights":
            _display_auto_insights(content, key_suffix=f"msg_{message_idx}")
        elif type_ == "deep_insights":
            _display_deep_insights(content, key_suffix=f"msg_{message_idx}")
        elif type_ == "error":
            st.error(str(content))
        else:
            # Reason: Check if content is markdown (starts with #)
            if isinstance(content, str) and content.strip().startswith("#"):
                st.markdown(content)
            else:
                st.write(content)


def _display_response(response, key_suffix: str = "new") -> None:
    """Display a PandasAI response.

    Args:
        response: QueryResponse object with type and content.
        key_suffix: Unique suffix for widget keys.
    """
    if not response.success:
        st.error(f"Error: {response.content}")
        return

    if response.type == "dataframe":
        st.dataframe(response.content, use_container_width=True)
    elif response.type == "chart":
        _display_chart(response.content, key_suffix=key_suffix)
    elif response.type == "auto_insights":
        _display_auto_insights(response.content, key_suffix=key_suffix)
    elif response.type == "deep_insights":
        _display_deep_insights(response.content, key_suffix=key_suffix)
    elif response.explanation:
        # Reason: Show explanation if available
        st.markdown(response.explanation)
    elif isinstance(response.content, str):
        st.write(response.content)
    else:
        st.write(str(response.content))


def _display_chart(chart_obj, key_suffix: str = "") -> None:
    """Display a chart/plot object with download option.

    Args:
        chart_obj: The chart object to display.
        key_suffix: Unique suffix for widget keys to avoid duplicates.
    """
    import io
    from pathlib import Path

    try:
        # Reason: Check if it's a file path string (PandasAI saves charts)
        if isinstance(chart_obj, str) and Path(chart_obj).exists():
            st.image(chart_obj, use_column_width=True)
            # Add download button
            with open(chart_obj, "rb") as f:
                st.download_button(
                    label="Download Chart",
                    data=f.read(),
                    file_name=Path(chart_obj).name,
                    mime="image/png",
                    key=f"download_chart_{Path(chart_obj).stem}_{key_suffix}",
                )
            return

        # Reason: Check for matplotlib Figure object
        import matplotlib.figure

        if isinstance(chart_obj, matplotlib.figure.Figure):
            st.pyplot(chart_obj)
            # Add download button for matplotlib
            buf = io.BytesIO()
            chart_obj.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            st.download_button(
                label="Download Chart",
                data=buf,
                file_name="chart.png",
                mime="image/png",
                key=f"download_mpl_{key_suffix}",
            )
            return

        # Reason: Check if it's a matplotlib Axes object
        if hasattr(chart_obj, "figure"):
            fig = chart_obj.figure
            st.pyplot(fig)
            # Add download button
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            st.download_button(
                label="Download Chart",
                data=buf,
                file_name="chart.png",
                mime="image/png",
                key=f"download_axes_{key_suffix}",
            )
            return

        # Reason: Check for matplotlib pyplot state
        if hasattr(chart_obj, "savefig"):
            st.pyplot(chart_obj)
            buf = io.BytesIO()
            chart_obj.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            st.download_button(
                label="Download Chart",
                data=buf,
                file_name="chart.png",
                mime="image/png",
            )
            return

        # Reason: Check for plotly figures
        try:
            import plotly.graph_objs as go

            if isinstance(chart_obj, (go.Figure, go.Scatter, go.Bar)):
                st.plotly_chart(chart_obj, use_container_width=True)
                # Add download button for plotly
                buf = io.BytesIO()
                chart_obj.write_image(buf, format="png")
                buf.seek(0)
                st.download_button(
                    label="Download Chart",
                    data=buf,
                    file_name="chart.png",
                    mime="image/png",
                )
                return
        except ImportError:
            pass

        # Reason: Check for seaborn objects (returns matplotlib axes)
        if hasattr(chart_obj, "get_figure"):
            fig = chart_obj.get_figure()
            st.pyplot(fig)
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            st.download_button(
                label="Download Chart",
                data=buf,
                file_name="chart.png",
                mime="image/png",
                key=f"download_seaborn_{key_suffix}",
            )
            return

        # Reason: Fallback - try to display as generic object
        st.write(chart_obj)

    except Exception as e:
        logger.error(f"Failed to display chart: {e}", exc_info=True)
        st.warning(f"Could not display chart: {e}")
        st.write(chart_obj)


def _display_auto_insights(content: dict, key_suffix: str = "") -> None:
    """Display auto-generated insights with text and visualizations.

    Args:
        content: Dictionary with 'text', 'visualizations', and 'summaries' keys.
        key_suffix: Unique suffix for widget keys.
    """
    import matplotlib.pyplot as plt

    # Reason: Display the insights text
    if isinstance(content, dict):
        text = content.get("text", "")
        visualizations = content.get("visualizations", [])

        if text:
            st.markdown(text)

        # Reason: Display visualizations in expandable sections
        if visualizations:
            st.markdown("### Visualizations")
            # Show top 4 most interesting visualizations
            for idx, viz in enumerate(visualizations[:4]):
                title = viz.get("title", f"Chart {idx + 1}")
                fig = viz.get("figure")

                with st.expander(title, expanded=(idx < 2)):
                    if fig is not None:
                        _display_chart(fig, key_suffix=f"{key_suffix}_viz_{idx}")
                    else:
                        st.write("Chart not available")

            # Reason: Close all figures to prevent memory warnings
            plt.close("all")
    else:
        # Fallback for unexpected content format
        st.write(str(content))


def _display_deep_insights(content: dict, key_suffix: str = "") -> None:
    """Display deep insights with hypothesis testing results.

    Args:
        content: Dictionary with 'text', 'hypotheses_results', etc.
        key_suffix: Unique suffix for widget keys.
    """
    if isinstance(content, dict):
        text = content.get("text", "")
        hypothesis_count = content.get("hypothesis_count", 0)
        successful_count = content.get("successful_count", 0)

        # Reason: Show summary metrics
        if hypothesis_count > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Hypotheses Tested", hypothesis_count)
            with col2:
                st.metric("Successfully Analyzed", successful_count)

        # Reason: Display the insights text (markdown formatted)
        if text:
            st.markdown(text)
    else:
        # Fallback for unexpected content format
        st.write(str(content))


def render_welcome_message(has_data: bool) -> None:
    """Render welcome message for the main interface.

    Args:
        has_data: Whether data has been loaded.
    """
    if not has_data:
        st.info(
            """
            👋 Welcome to PandasAI TXT2SQL!

            To get started:
            1. 📤 Upload your data files using the sidebar
            2. 💬 Ask questions about your data in natural language
            3. 📊 View results, tables, and charts

            Supported file formats: .xlsx, .xls, .csv
            """
        )
    else:
        st.success(
            """
            🎉 Data loaded successfully!

            You can now ask questions about your data.
            Try queries like:
            - "Show me the top 5 rows"
            - "What is the average of [column]?"
            - "Create a bar chart of [column]"
            """
        )
