"""Unit tests for chat agent module."""

from unittest.mock import MagicMock, patch

import pandas as pd

from src.chat_agent import PandasAIAgent, QueryResponse
from src.data_loader import LoadedData


class TestQueryResponse:
    """Tests for QueryResponse class."""

    def test_initialization(self):
        """Test QueryResponse initialization."""
        response = QueryResponse(
            type_="text",
            content="Test response",
            success=True,
        )

        assert response.type == "text"
        assert response.content == "Test response"
        assert response.success is True
        assert response.explanation is None

    def test_initialization_with_explanation(self):
        """Test QueryResponse with explanation."""
        response = QueryResponse(
            type_="dataframe",
            content=pd.DataFrame({"a": [1, 2]}),
            success=True,
            explanation="This is a summary",
        )

        assert response.type == "dataframe"
        assert response.explanation == "This is a summary"

    def test_to_dict(self):
        """Test converting response to dictionary."""
        response = QueryResponse(
            type_="text",
            content="Test",
            success=True,
            explanation="Explanation",
        )

        result = response.to_dict()

        assert result["type"] == "text"
        assert result["content"] == "Test"
        assert result["success"] is True
        assert result["explanation"] == "Explanation"


class TestPandasAIAgent:
    """Tests for PandasAIAgent class."""

    def test_initialization(self, mock_llm_client):
        """Test agent initialization."""
        agent = PandasAIAgent(llm_client=mock_llm_client)

        assert agent.llm_client == mock_llm_client
        assert agent.save_logs is True
        assert agent.loaded_data == []
        assert agent.agent is None

    def test_load_data(self, mock_llm_client, sample_dataframe):
        """Test loading data into agent."""

        with patch("src.chat_agent.Agent") as mock_agent_class:
            mock_agent_instance = MagicMock()
            mock_agent_class.return_value = mock_agent_instance

            agent = PandasAIAgent(llm_client=mock_llm_client)

            loaded_data = LoadedData(
                data=sample_dataframe,
                filename="test.xlsx",
                sheet_name="Sheet1",
            )

            agent.load_data([loaded_data])

            assert len(agent.loaded_data) == 1
            assert agent.agent is not None
            mock_agent_class.assert_called_once()

    def test_load_data_with_multiple_files(self, mock_llm_client, sample_dataframe):
        """Test loading multiple DataFrames."""
        with patch("src.chat_agent.Agent") as mock_agent_class:
            mock_agent_instance = MagicMock()
            mock_agent_class.return_value = mock_agent_instance

            agent = PandasAIAgent(llm_client=mock_llm_client)

            df1 = sample_dataframe
            df2 = pd.DataFrame({"X": [1, 2], "Y": [3, 4]})

            loaded_data = [
                LoadedData(data=df1, filename="file1.xlsx", sheet_name="Sheet1"),
                LoadedData(data=df2, filename="file2.xlsx", sheet_name="Sheet2"),
            ]

            agent.load_data(loaded_data)

            assert len(agent.loaded_data) == 2

    def test_load_data_with_empty_list(self, mock_llm_client):
        """Test loading empty list of files."""
        agent = PandasAIAgent(llm_client=mock_llm_client)

        agent.load_data([])

        assert agent.agent is None
        assert len(agent.loaded_data) == 0

    def test_query_without_data(self, mock_llm_client):
        """Test query when no data is loaded."""
        agent = PandasAIAgent(llm_client=mock_llm_client)

        response = agent.query("Show me data")

        assert response.success is False
        assert "No data loaded" in response.content
        assert response.type == "error"

    def test_query_with_dataframe_response(self, mock_llm_client, sample_dataframe):
        """Test query returning DataFrame."""
        with patch("src.chat_agent.Agent") as mock_agent_class:
            mock_agent_instance = MagicMock()
            mock_agent_instance.chat.return_value = sample_dataframe
            mock_agent_class.return_value = mock_agent_instance

            agent = PandasAIAgent(llm_client=mock_llm_client)
            agent.load_data(
                [
                    LoadedData(
                        data=sample_dataframe,
                        filename="test.xlsx",
                        sheet_name="Sheet1",
                    )
                ]
            )

            response = agent.query("What is the average sales?")

            assert response.success is True
            assert response.type == "dataframe"

    def test_query_with_text_response(self, mock_llm_client, sample_dataframe):
        """Test query returning text response."""
        with patch("src.chat_agent.Agent") as mock_agent_class:
            mock_agent_instance = MagicMock()
            mock_agent_instance.chat.return_value = "Average is 1233.33"
            mock_agent_class.return_value = mock_agent_instance

            agent = PandasAIAgent(llm_client=mock_llm_client)
            agent.load_data(
                [
                    LoadedData(
                        data=sample_dataframe,
                        filename="test.xlsx",
                        sheet_name="Sheet1",
                    )
                ]
            )

            response = agent.query("What is the average sales?")

            assert response.success is True
            assert response.type == "text"
            assert response.content == "Average is 1233.33"

    def test_query_with_error(self, mock_llm_client, sample_dataframe):
        """Test query with error."""
        with patch("src.chat_agent.Agent") as mock_agent_class:
            mock_agent_instance = MagicMock()
            mock_agent_instance.chat.side_effect = Exception("API error")
            mock_agent_class.return_value = mock_agent_instance

            agent = PandasAIAgent(llm_client=mock_llm_client)
            agent.load_data(
                [
                    LoadedData(
                        data=sample_dataframe,
                        filename="test.xlsx",
                        sheet_name="Sheet1",
                    )
                ]
            )

            response = agent.query("Invalid query")

            assert response.success is False
            assert response.type == "error"
            assert "Query failed" in response.content

    def test_query_with_no_code_error_non_insight(self, mock_llm_client, sample_dataframe):
        """Test query when LLM doesn't return code for non-insight questions."""
        from pandasai.exceptions import NoCodeFoundError

        with patch("src.chat_agent.Agent") as mock_agent_class:
            mock_agent_instance = MagicMock()
            mock_agent_instance.chat.side_effect = NoCodeFoundError(
                "No code found in the response"
            )
            mock_agent_class.return_value = mock_agent_instance

            agent = PandasAIAgent(llm_client=mock_llm_client)
            agent.load_data(
                [
                    LoadedData(
                        data=sample_dataframe,
                        filename="test.xlsx",
                        sheet_name="Sheet1",
                    )
                ]
            )

            # Non-insight question should return hint message
            response = agent.query("Do something random with the data")

            assert response.success is True
            assert response.type == "text"
            assert "couldn't complete the analysis" in response.content
            assert "specific questions" in response.content

    def test_query_with_no_code_error_insight_fallback(
        self, mock_llm_client, sample_dataframe
    ):
        """Test that insight questions fall back to deep-insights."""
        from pandasai.exceptions import NoCodeFoundError

        with patch("src.chat_agent.Agent") as mock_agent_class:
            mock_agent_instance = MagicMock()
            mock_agent_instance.chat.side_effect = NoCodeFoundError(
                "No code found in the response"
            )
            mock_agent_class.return_value = mock_agent_instance

            agent = PandasAIAgent(llm_client=mock_llm_client)
            agent.load_data(
                [
                    LoadedData(
                        data=sample_dataframe,
                        filename="test.xlsx",
                        sheet_name="Sheet1",
                    )
                ]
            )

            # Insight question should trigger deep-insights
            response = agent.query("Any potential insights of this data?")

            assert response.success is True
            assert response.type == "deep_insights"
            assert "text" in response.content
            assert "hypotheses_results" in response.content

    def test_query_with_no_result_error(self, mock_llm_client, sample_dataframe):
        """Test query when code executes but doesn't return a result."""
        from pandasai.exceptions import NoResultFoundError

        with patch("src.chat_agent.Agent") as mock_agent_class:
            mock_agent_instance = MagicMock()
            mock_agent_instance.chat.side_effect = NoResultFoundError(
                "No result returned"
            )
            mock_agent_class.return_value = mock_agent_instance

            agent = PandasAIAgent(llm_client=mock_llm_client)
            agent.load_data(
                [
                    LoadedData(
                        data=sample_dataframe,
                        filename="test.xlsx",
                        sheet_name="Sheet1",
                    )
                ]
            )

            # Insight question should trigger deep-insights fallback
            response = agent.query("Show me a summary of this data")

            assert response.success is True
            assert response.type == "deep_insights"

    def test_is_insight_question(self, mock_llm_client):
        """Test insight question detection."""
        agent = PandasAIAgent(llm_client=mock_llm_client)

        # Should be detected as insight questions
        assert agent._is_insight_question("Any potential insights?") is True
        assert agent._is_insight_question("Give me a summary") is True
        assert agent._is_insight_question("Analyze this data") is True
        assert agent._is_insight_question("Please summarize the data") is True
        assert agent._is_insight_question("数据分析") is True  # Chinese

        # Should NOT be detected as insight questions
        assert agent._is_insight_question("What is the average sales?") is False
        assert agent._is_insight_question("Show me top 10 rows") is False
        assert agent._is_insight_question("Plot a bar chart") is False

    def test_generate_auto_insights(self, mock_llm_client, sample_dataframe):
        """Test auto-insights generation."""
        agent = PandasAIAgent(llm_client=mock_llm_client)
        agent.loaded_data = [
            LoadedData(
                data=sample_dataframe,
                filename="test.xlsx",
                sheet_name="Sheet1",
            )
        ]

        response = agent.generate_auto_insights()

        assert response.success is True
        assert response.type == "auto_insights"
        assert "text" in response.content
        assert isinstance(response.content["text"], str)
        assert "visualizations" in response.content

    def test_generate_auto_insights_no_data(self, mock_llm_client):
        """Test auto-insights when no data is loaded."""
        agent = PandasAIAgent(llm_client=mock_llm_client)

        response = agent.generate_auto_insights()

        assert response.success is False
        assert response.type == "error"

    def test_generate_deep_insights(self, mock_llm_client, sample_dataframe):
        """Test deep insights generation with hypothesis testing."""
        agent = PandasAIAgent(llm_client=mock_llm_client)
        agent.loaded_data = [
            LoadedData(
                data=sample_dataframe,
                filename="test.xlsx",
                sheet_name="Sheet1",
            )
        ]

        response = agent.generate_deep_insights()

        assert response.success is True
        assert response.type == "deep_insights"
        assert "text" in response.content
        assert "hypotheses_results" in response.content
        assert "hypothesis_count" in response.content
        assert response.content["hypothesis_count"] > 0

    def test_generate_deep_insights_no_data(self, mock_llm_client):
        """Test deep insights when no data is loaded."""
        agent = PandasAIAgent(llm_client=mock_llm_client)

        response = agent.generate_deep_insights()

        assert response.success is False
        assert response.type == "error"

    def test_detect_response_type_dataframe(self, mock_llm_client):
        """Test response type detection for DataFrame."""
        agent = PandasAIAgent(llm_client=mock_llm_client)
        df = pd.DataFrame({"a": [1]})

        result = agent._detect_response_type(df)

        assert result == "dataframe"

    def test_detect_response_type_chart(self, mock_llm_client):
        """Test response type detection for chart."""
        agent = PandasAIAgent(llm_client=mock_llm_client)
        mock_chart = MagicMock()
        mock_chart.figure = "figure"

        result = agent._detect_response_type(mock_chart)

        assert result == "chart"

    def test_detect_response_type_matplotlib_figure(self, mock_llm_client):
        """Test response type detection for matplotlib Figure."""
        import matplotlib.pyplot as plt

        agent = PandasAIAgent(llm_client=mock_llm_client)
        fig = plt.figure()

        result = agent._detect_response_type(fig)

        assert result == "chart"
        plt.close(fig)

    def test_detect_response_type_chart_path(self, mock_llm_client):
        """Test response type detection for chart file path."""
        agent = PandasAIAgent(llm_client=mock_llm_client)

        result = agent._detect_response_type("exports/charts/plot.png")

        assert result == "chart"

    def test_detect_response_type_text(self, mock_llm_client):
        """Test response type detection for text."""
        agent = PandasAIAgent(llm_client=mock_llm_client)

        result = agent._detect_response_type("Some text")

        assert result == "text"

    def test_get_data_summary(self, mock_llm_client, sample_dataframe):
        """Test getting data summary."""
        agent = PandasAIAgent(llm_client=mock_llm_client)

        loaded_data = LoadedData(
            data=sample_dataframe,
            filename="test.xlsx",
            sheet_name="Sheet1",
        )

        agent.loaded_data = [loaded_data]

        summary = agent.get_data_summary()

        assert len(summary) == 1
        assert summary[0]["rows"] == 3
        assert summary[0]["columns"] == 3

    def test_is_data_loaded(self, mock_llm_client):
        """Test checking if data is loaded."""
        agent = PandasAIAgent(llm_client=mock_llm_client)

        assert agent.is_data_loaded() is False

        agent.loaded_data = [
            LoadedData(
                data=pd.DataFrame({"a": [1]}),
                filename="test.xlsx",
                sheet_name="Sheet1",
            )
        ]
        agent.agent = MagicMock()

        assert agent.is_data_loaded() is True

    def test_is_pandasai_error(self, mock_llm_client):
        """Test PandasAI error string detection."""
        agent = PandasAIAgent(llm_client=mock_llm_client)

        # Should be detected as errors
        assert agent._is_pandasai_error(
            "Unfortunately, I was not able to get your answers, "
            "because of the following error:\nNo code found"
        ) is True
        assert agent._is_pandasai_error("No code found in the response") is True
        assert agent._is_pandasai_error("No result returned") is True

        # Should NOT be detected as errors
        assert agent._is_pandasai_error("The average is 100") is False
        assert agent._is_pandasai_error(pd.DataFrame({"a": [1]})) is False
        assert agent._is_pandasai_error(123) is False

    def test_query_with_pandasai_error_string_insight(
        self, mock_llm_client, sample_dataframe
    ):
        """Test query when PandasAI returns error string for insight question."""
        with patch("src.chat_agent.Agent") as mock_agent_class:
            mock_agent_instance = MagicMock()
            # Simulate PandasAI returning error string instead of raising exception
            mock_agent_instance.chat.return_value = (
                "Unfortunately, I was not able to get your answers, "
                "because of the following error:\nNo code found in the response"
            )
            mock_agent_class.return_value = mock_agent_instance

            agent = PandasAIAgent(llm_client=mock_llm_client)
            agent.load_data(
                [
                    LoadedData(
                        data=sample_dataframe,
                        filename="test.xlsx",
                        sheet_name="Sheet1",
                    )
                ]
            )

            # Insight question should trigger deep-insights
            response = agent.query("Show me some insights about the data")

            assert response.success is True
            assert response.type == "deep_insights"

    def test_query_with_pandasai_error_string_non_insight(
        self, mock_llm_client, sample_dataframe
    ):
        """Test query when PandasAI returns error string for non-insight question."""
        with patch("src.chat_agent.Agent") as mock_agent_class:
            mock_agent_instance = MagicMock()
            mock_agent_instance.chat.return_value = (
                "Unfortunately, I was not able to get your answers, "
                "because of the following error:\nNo code found in the response"
            )
            mock_agent_class.return_value = mock_agent_instance

            agent = PandasAIAgent(llm_client=mock_llm_client)
            agent.load_data(
                [
                    LoadedData(
                        data=sample_dataframe,
                        filename="test.xlsx",
                        sheet_name="Sheet1",
                    )
                ]
            )

            # Non-insight question should return hint message
            response = agent.query("Do something weird")

            assert response.success is True
            assert response.type == "text"
            assert "couldn't complete the analysis" in response.content
