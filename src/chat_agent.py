"""PandasAI Agent wrapper for data analysis."""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd
from pandasai import Agent
from pandasai.exceptions import NoCodeFoundError, NoResultFoundError

from .auto_insights import AutoInsight
from .data_loader import LoadedData
from .deep_insights import DeepInsightGenerator
from .llm_client import DeepSeekClient

logger = logging.getLogger(__name__)

# Keywords that indicate user is asking for general insights
INSIGHT_KEYWORDS = [
    # English
    "insight",
    "insights",
    "summary",
    "summarize",
    "overview",
    "describe",
    "tell me about",
    "analyze",
    "analysis",
    "what can you tell",
    "explore",
    # Chinese
    "分析",
    "洞察",
    "概述",
    "总结",
    "概览",
    "描述",
]


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
                    "llm": self.llm_client.get_llm(),
                    "save_logs": self.save_logs,
                    "verbose": False,
                    "max_retries": 3,
                    "enable_cache": True,
                    "save_charts": True,
                    "save_charts_path": "exports/charts",
                    "open_charts": False,
                },
            )
            logger.info(f"Loaded {len(loaded_files)} DataFrames into PandasAI Agent")
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

            # Reason: PandasAI catches exceptions internally and returns error strings
            # We need to detect these and handle them appropriately
            if self._is_pandasai_error(result):
                logger.warning(f"PandasAI returned error for query: {question}")
                return self._handle_pandasai_error(question, result)

            response = QueryResponse(
                type_=self._detect_response_type(result),
                content=result,
                success=True,
            )
            logger.info(f"Response type: {response.type}")
            return response

        except (NoCodeFoundError, NoResultFoundError) as e:
            # Reason: Handle exceptions if they somehow propagate
            logger.warning(f"Code generation/execution failed for query: {question} - {e}")
            return self._handle_pandasai_error(question, str(e))

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
        import matplotlib.figure

        # Reason: Check for DataFrame (tabular data)
        if isinstance(result, pd.DataFrame):
            return "dataframe"

        # Reason: Check for matplotlib Figure object
        if isinstance(result, matplotlib.figure.Figure):
            return "chart"

        # Reason: Check for matplotlib Axes object
        if hasattr(result, "figure"):
            return "chart"

        # Reason: Check for plotly figures
        try:
            import plotly.graph_objs as go

            if isinstance(result, (go.Figure, go.Scatter, go.Bar)):
                return "chart"
        except ImportError:
            pass

        # Reason: Check for seaborn objects (returns matplotlib axes)
        if hasattr(result, "get_figure"):
            return "chart"

        # Reason: Check if result is a file path to a saved chart
        if isinstance(result, str) and any(
            result.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".svg", ".pdf"]
        ):
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

    def _is_insight_question(self, question: str) -> bool:
        """Check if the question is asking for general data insights.

        Args:
            question: The user's question.

        Returns:
            bool: True if the question is asking for insights.
        """
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in INSIGHT_KEYWORDS)

    def _is_pandasai_error(self, result: Any) -> bool:
        """Check if the result is a PandasAI error string.

        PandasAI catches exceptions internally and returns error strings
        instead of raising them.

        Args:
            result: The result from Agent.chat().

        Returns:
            bool: True if the result is an error string.
        """
        if not isinstance(result, str):
            return False

        error_patterns = [
            "Unfortunately, I was not able to get your answer",
            "No code found in the response",
            "No result returned",
        ]
        return any(pattern in result for pattern in error_patterns)

    def _handle_pandasai_error(self, question: str, error_msg: str) -> QueryResponse:
        """Handle PandasAI error by falling back to deep insights if appropriate.

        Args:
            question: The original user question.
            error_msg: The error message from PandasAI.

        Returns:
            QueryResponse: Either deep insights or a helpful hint message.
        """
        # Reason: Fall back to deep insights for insight-related questions
        if self._is_insight_question(question):
            logger.info("Falling back to deep insights for insight question")
            return self.generate_deep_insights()

        hint_msg = (
            "I couldn't complete the analysis for that question. "
            "Try asking more specific questions like:\n"
            "- What is the average of [column]?\n"
            "- Show me the top 10 rows by [column]\n"
            "- Plot a histogram of [column]\n"
            "- What are the unique values in [column]?"
        )
        return QueryResponse(
            type_="text",
            content=hint_msg,
            success=True,
        )

    def generate_deep_insights(self) -> QueryResponse:
        """Generate deep insights by testing hypotheses about the data.

        This method acts as a "deep researcher" that:
        1. Analyzes data structure
        2. Generates 3-5 hypotheses based on the data
        3. Tests each hypothesis with specific queries
        4. Returns findings

        Returns:
            QueryResponse: Response containing deep insights.
        """
        if not self.loaded_data:
            return QueryResponse(
                type_="error",
                content="No data loaded. Please upload files first.",
                success=False,
            )

        try:
            dataframes = [ld.data for ld in self.loaded_data]
            names = [ld.filename for ld in self.loaded_data]

            generator = DeepInsightGenerator(dataframes, names)
            report = generator.generate_deep_insights()

            logger.info(
                f"Generated deep insights: {report['successful_count']}/"
                f"{report['hypothesis_count']} hypotheses tested successfully"
            )

            return QueryResponse(
                type_="deep_insights",
                content={
                    "text": report["insights_text"],
                    "hypotheses_results": report["hypotheses_results"],
                    "hypothesis_count": report["hypothesis_count"],
                    "successful_count": report["successful_count"],
                },
                success=True,
            )

        except Exception as e:
            error_msg = f"Failed to generate deep insights: {str(e)}"
            logger.error(error_msg, exc_info=True)
            # Fall back to auto-insights if deep insights fail
            logger.info("Falling back to auto-insights")
            return self.generate_auto_insights()

    def generate_auto_insights(self) -> QueryResponse:
        """Generate automatic insights for loaded data using AutoInsight.

        Returns:
            QueryResponse: Response containing insights text and visualizations.
        """
        if not self.loaded_data:
            return QueryResponse(
                type_="error",
                content="No data loaded. Please upload files first.",
                success=False,
            )

        try:
            dataframes = [ld.data for ld in self.loaded_data]
            names = [ld.filename for ld in self.loaded_data]

            auto_insight = AutoInsight(dataframes, names)
            report = auto_insight.generate_full_report()

            # Return insights text as the primary content
            # Visualizations can be accessed separately if needed
            logger.info("Generated auto-insights successfully")
            return QueryResponse(
                type_="auto_insights",
                content={
                    "text": report["insights_text"],
                    "visualizations": report["visualizations"],
                    "summaries": report["summaries"],
                },
                success=True,
            )

        except Exception as e:
            error_msg = f"Failed to generate insights: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return QueryResponse(
                type_="error",
                content=error_msg,
                success=False,
            )
