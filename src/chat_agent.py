"""PandasAI Agent wrapper for data analysis."""

import logging
from typing import List, Dict, Any, Optional

import pandas as pd
from pandasai import Agent

from .llm_client import DeepSeekClient
from .data_loader import LoadedData

logger = logging.getLogger(__name__)


class QueryResponse:
    """Represents a response from a PandasAI query.

    Attributes:
        type: The type of response (text, dataframe, chart, error).
        content: The actual response content.
        success: Whether the query was successful.
        explanation: Optional explanation of the result.
    """

    def __init__(
        self,
        type_: str,
        content: Any,
        success: bool,
        explanation: Optional[str] = None,
    ):
        self.type = type_
        self.content = content
        self.success = success
        self.explanation = explanation

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the response.
        """
        return {
            "type": self.type,
            "content": self.content,
            "success": self.success,
            "explanation": self.explanation,
        }


class PandasAIAgent:
    """Wrapper for PandasAI Agent with DeepSeek LLM integration.

    This class provides a simplified interface for querying data using
    natural language, handling response parsing and error management.
    """

    def __init__(self, llm_client: DeepSeekClient, save_logs: bool = True):
        """Initialize the PandasAI agent.

        Args:
            llm_client: The DeepSeek client for LLM integration.
            save_logs: Whether to save PandasAI logs.
        """
        self.llm_client = llm_client
        self.save_logs = save_logs
        self.loaded_data: List[LoadedData] = []
        self.agent: Optional[Agent] = None

    def load_data(self, loaded_files: List[LoadedData]) -> None:
        """Load data into the PandasAI agent.

        Args:
            loaded_files: List of LoadedData objects with DataFrames.
        """
        self.loaded_data = loaded_files

        # Reason: Initialize Agent with all DataFrames for multi-file queries
        dataframes = [ld.data for ld in loaded_files]
        if dataframes:
            self.agent = Agent(
                *dataframes,
                config={
                    "llm": self.llm_client.get_client(),
                    "save_logs": self.save_logs,
                    "verbose": False,
                    "max_retries": 3,
                },
            )
            logger.info(
                f"Loaded {len(loaded_files)} DataFrames into PandasAI Agent"
            )
        else:
            self.agent = None
            logger.warning("No DataFrames loaded into Agent")

    def query(self, question: str) -> QueryResponse:
        """Execute a natural language query against loaded data.

        Args:
            question: The natural language question to ask.

        Returns:
            QueryResponse: The response with type, content, and success status.
        """
        if not self.agent:
            return QueryResponse(
                type_="error",
                content="No data loaded. Please upload Excel files first.",
                success=False,
            )

        try:
            logger.info(f"Query: {question}")
            # Reason: Call Agent.chat for natural language processing
            result = self.agent.chat(question)

            response = QueryResponse(
                type_=self._detect_response_type(result),
                content=result,
                success=True,
            )
            logger.info(f"Response type: {response.type}")
            return response

        except Exception as e:
            error_msg = f"Query failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return QueryResponse(
                type_="error",
                content=error_msg,
                success=False,
            )

    def _detect_response_type(self, result: Any) -> str:
        """Detect the type of response returned by PandasAI.

        Args:
            result: The result object returned by PandasAI.

        Returns:
            str: The response type (dataframe, chart, or text).
        """
        # Reason: Check for DataFrame (tabular data)
        if isinstance(result, pd.DataFrame):
            return "dataframe"

        # Reason: Check for matplotlib figure or chart object
        if hasattr(result, "figure") or hasattr(result, "plot"):
            return "chart"

        # Reason: Check for common chart library objects
        if hasattr(result, "show") and hasattr(result, "savefig"):
            return "chart"

        # Default to text
        return "text"

    def get_data_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all loaded data.

        Returns:
            List[Dict[str, Any]]: List of data summaries.
        """
        from .data_loader import get_dataframe_info

        return [get_dataframe_info(ld.data) for ld in self.loaded_data]

    def is_data_loaded(self) -> bool:
        """Check if data is loaded into the agent.

        Returns:
            bool: True if data is loaded, False otherwise.
        """
        return self.agent is not None and bool(self.loaded_data)
