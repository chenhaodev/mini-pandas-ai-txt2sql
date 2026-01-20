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
