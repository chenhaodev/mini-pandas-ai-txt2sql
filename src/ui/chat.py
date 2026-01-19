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
        for message in st.session_state.messages:
            _display_message(message)

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
            _display_response(response)

            # Reason: Add assistant response to history
            assistant_message = response.to_dict()
            st.session_state.messages.append(assistant_message)

        if on_message_add:
            on_message_add(
                response.type,
                response.content,
                "assistant" if response.success else "error",
            )


def _display_message(message: dict) -> None:
    """Display a single message from chat history.

    Args:
        message: Message dictionary with role, content, and type keys.
    """
    role = message.get("role", "assistant")
    content = message.get("content")
    type_ = message.get("type", "text")

    with st.chat_message(role):
        if type_ == "dataframe" and isinstance(content, pd.DataFrame):
            st.dataframe(content, use_container_width=True)
        elif type_ == "chart":
            _display_chart(content)
        elif type_ == "error":
            st.error(str(content))
        else:
            st.write(content)


def _display_response(response) -> None:
    """Display a PandasAI response.

    Args:
        response: QueryResponse object with type and content.
    """
    if not response.success:
        st.error(f"Error: {response.content}")
        return

    if response.type == "dataframe":
        st.dataframe(response.content, use_container_width=True)
    elif response.type == "chart":
        _display_chart(response.content)
    elif response.explanation:
        # Reason: Show explanation if available
        st.markdown(response.explanation)
    elif isinstance(response.content, str):
        st.write(response.content)
    else:
        st.write(str(response.content))


def _display_chart(chart_obj) -> None:
    """Display a chart/plot object.

    Args:
        chart_obj: The chart object to display.
    """
    try:
        # Reason: Check if it's a matplotlib figure
        if hasattr(chart_obj, "figure"):
            st.pyplot(chart_obj.figure)
        # Reason: Check for matplotlib pyplot state
        elif hasattr(chart_obj, "savefig"):
            st.pyplot(chart_obj)
        # Reason: Check for plotly figures
        elif hasattr(chart_obj, "show"):
            st.plotly_chart(chart_obj, use_container_width=True)
        else:
            # Reason: Fallback - try to display as generic object
            st.write(chart_obj)
    except Exception as e:
        logger.error(f"Failed to display chart: {e}", exc_info=True)
        st.warning(f"Could not display chart: {e}")
        st.write(chart_obj)


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
