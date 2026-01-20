"""Session state management for Streamlit."""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Session state keys
KEY_MESSAGES = "messages"
KEY_UPLOADED_FILES = "uploaded_files"
KEY_LOADED_DATA = "loaded_data"
KEY_API_KEY = "api_key"
KEY_MODEL = "model"


def init_session_state() -> None:
    """Initialize all session state keys with default values.

    This should be called at the start of the Streamlit app
    to ensure all session state keys exist.
    """
    import streamlit as st

    # Reason: Initialize chat history
    if KEY_MESSAGES not in st.session_state:
        st.session_state[KEY_MESSAGES] = []

    # Reason: Initialize uploaded files list
    if KEY_UPLOADED_FILES not in st.session_state:
        st.session_state[KEY_UPLOADED_FILES] = []

    # Reason: Initialize loaded data (DataFrames)
    if KEY_LOADED_DATA not in st.session_state:
        st.session_state[KEY_LOADED_DATA] = []

    # Reason: Initialize API key (may be empty if using .env)
    if KEY_API_KEY not in st.session_state:
        st.session_state[KEY_API_KEY] = ""

    # Reason: Initialize model selection
    if KEY_MODEL not in st.session_state:
        st.session_state[KEY_MODEL] = "deepseek-chat"


def add_message(
    role: str,
    content: Any,
    type_: str = "text",
) -> None:
    """Add a message to the chat history.

    Args:
        role: The message role (user or assistant).
        content: The message content.
        type_: The content type (text, dataframe, chart, error).
    """
    import streamlit as st

    message: Dict[str, Any] = {
        "role": role,
        "content": content,
        "type": type_,
    }
    st.session_state[KEY_MESSAGES].append(message)
    logger.debug(f"Added {role} message of type {type_}")


def get_chat_history() -> List[Dict[str, Any]]:
    """Get the current chat history.

    Returns:
        List[Dict[str, Any]]: List of message dictionaries.
    """
    import streamlit as st

    return st.session_state.get(KEY_MESSAGES, [])


def clear_chat_history() -> None:
    """Clear all messages from the chat history."""
    import streamlit as st

    st.session_state[KEY_MESSAGES] = []
    logger.info("Chat history cleared")


def set_uploaded_files(files: List[Any]) -> None:
    """Set the uploaded files in session state.

    Args:
        files: List of uploaded file objects.
    """
    import streamlit as st

    st.session_state[KEY_UPLOADED_FILES] = files
    logger.info(f"Set {len(files)} uploaded files in session state")


def get_uploaded_files() -> List[Any]:
    """Get the uploaded files from session state.

    Returns:
        List[Any]: List of uploaded file objects.
    """
    import streamlit as st

    return st.session_state.get(KEY_UPLOADED_FILES, [])


def set_loaded_data(loaded_data: List[Any]) -> None:
    """Set loaded data (DataFrames) in session state.

    Args:
        loaded_data: List of LoadedData objects with DataFrames.
    """
    import streamlit as st

    st.session_state[KEY_LOADED_DATA] = loaded_data
    logger.info(f"Set {len(loaded_data)} loaded DataFrames in session state")


def get_loaded_data() -> List[Any]:
    """Get loaded data (DataFrames) from session state.

    Returns:
        List[Any]: List of LoadedData objects with DataFrames.
    """
    import streamlit as st

    return st.session_state.get(KEY_LOADED_DATA, [])


def set_api_key(api_key: str) -> None:
    """Set the API key in session state.

    Args:
        api_key: The DeepSeek API key.
    """
    import streamlit as st

    st.session_state[KEY_API_KEY] = api_key


def get_api_key() -> Optional[str]:
    """Get the API key from session state.

    Returns:
        Optional[str]: The API key if set, None otherwise.
    """
    import streamlit as st

    return st.session_state.get(KEY_API_KEY) or None


def set_model(model: str) -> None:
    """Set the model in session state.

    Args:
        model: The model name (deepseek-chat or deepseek-reasoner).
    """
    import streamlit as st

    st.session_state[KEY_MODEL] = model


def get_model() -> str:
    """Get the model from session state.

    Returns:
        str: The model name.
    """
    import streamlit as st

    return st.session_state.get(KEY_MODEL, "deepseek-chat")


def validate_session_state() -> bool:
    """Validate session state integrity and recover from corruption.

    Checks that all session state keys exist and have valid types.
    Resets any corrupted values to defaults.

    Returns:
        bool: True if session state was valid, False if corruption was detected and fixed.
    """
    import streamlit as st

    corruption_detected = False

    # Validate messages
    if KEY_MESSAGES in st.session_state:
        messages = st.session_state[KEY_MESSAGES]
        if not isinstance(messages, list):
            logger.warning(
                f"Session state corruption: {KEY_MESSAGES} is not a list, resetting"
            )
            st.session_state[KEY_MESSAGES] = []
            corruption_detected = True
        else:
            # Validate each message structure
            valid_messages = []
            for msg in messages:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    valid_messages.append(msg)
                else:
                    logger.warning(f"Invalid message structure detected: {msg}")
                    corruption_detected = True
            if len(valid_messages) != len(messages):
                st.session_state[KEY_MESSAGES] = valid_messages

    # Validate uploaded_files
    if KEY_UPLOADED_FILES in st.session_state:
        files = st.session_state[KEY_UPLOADED_FILES]
        if not isinstance(files, list):
            logger.warning(
                f"Session state corruption: {KEY_UPLOADED_FILES} is not a list, resetting"
            )
            st.session_state[KEY_UPLOADED_FILES] = []
            corruption_detected = True

    # Validate loaded_data
    if KEY_LOADED_DATA in st.session_state:
        data = st.session_state[KEY_LOADED_DATA]
        if not isinstance(data, list):
            logger.warning(
                f"Session state corruption: {KEY_LOADED_DATA} is not a list, resetting"
            )
            st.session_state[KEY_LOADED_DATA] = []
            corruption_detected = True

    # Validate prev_uploaded_files (used by sidebar)
    prev_files_key = "prev_uploaded_files"
    if prev_files_key in st.session_state:
        prev_files = st.session_state[prev_files_key]
        if not isinstance(prev_files, list):
            logger.warning(
                f"Session state corruption: {prev_files_key} is not a list, resetting"
            )
            st.session_state[prev_files_key] = []
            corruption_detected = True

    # Validate API key
    if KEY_API_KEY in st.session_state:
        api_key = st.session_state[KEY_API_KEY]
        if not isinstance(api_key, str):
            logger.warning(
                f"Session state corruption: {KEY_API_KEY} is not a string, resetting"
            )
            st.session_state[KEY_API_KEY] = ""
            corruption_detected = True

    # Validate model
    if KEY_MODEL in st.session_state:
        model = st.session_state[KEY_MODEL]
        if not isinstance(model, str):
            logger.warning(
                f"Session state corruption: {KEY_MODEL} is not a string, resetting"
            )
            st.session_state[KEY_MODEL] = "deepseek-chat"
            corruption_detected = True

    if corruption_detected:
        logger.warning("Session state corruption detected and fixed")
    else:
        logger.debug("Session state validation passed")

    return not corruption_detected
