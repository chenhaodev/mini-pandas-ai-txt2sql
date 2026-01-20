# PandasAI TXT2SQL with DeepSeek

A conversational data analysis application that allows you to query Excel and CSV files using natural language. Built with PandasAI, DeepSeek API, and Streamlit.

## App Preview

![App Demo](img.jpg)

## Features

- **Natural Language Queries**: Ask questions about your data in plain English or Chinese
- **Multi-File Support**: Upload and query across multiple Excel and CSV files at once
- **Auto Insights**: One-click automated exploratory data analysis (EDA) with statistics, histograms, and correlations
- **Dynamic Visualizations**: Generate charts (bar, line, pie, histogram, scatter) with automatic detection and PNG download
- **Chinese Character Support**: Auto-detects system fonts for Chinese text in charts
- **DeepSeek Integration**: Uses DeepSeek API for powerful LLM capabilities
- **Chat Interface**: Streamlit-based chat with message history and preserved charts

## Installation

### Prerequisites

- Python 3.9 or higher
- DeepSeek API key (get one at https://platform.deepseek.com/)

### Quick Start

```bash
# Clone and install
git clone <repository-url>
cd mini-pandas-ai-txt2sql
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your DEEPSEEK_API_KEY

# Run application
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

## Usage

1. **Upload Data Files**: Use sidebar to upload `.xlsx`, `.xls`, or `.csv` files
2. **Configure API** (optional): Enter DeepSeek API key in sidebar or use `.env` file
3. **Quick Start**: Click "🔍 Generate Auto Insights" for automatic EDA with statistics and visualizations
4. **Ask Questions**: Type natural language queries like:
   - "How many rows are in the data?"
   - "Show me top 5 products by sales"
   - "What is average sales by region?"
   - "Create a bar chart of sales by product"
   - "Plot a pie chart showing regional distribution"

## Supported Formats

**Files**: `.xlsx`, `.xls`, `.csv`

**Charts**: Bar charts, line charts, scatter plots, histograms, pie charts, box plots, violin plots (matplotlib, seaborn, plotly)

## Chinese Language Support

The application supports Chinese characters in charts with automatic font detection:

- **macOS**: PingFang SC, Songti SC, STHeiti
- **Windows**: Microsoft YaHei, SimHei, SimSun
- **Linux**: Noto Sans CJK, WenQuanYi

If Chinese characters don't display correctly, install Chinese fonts for your operating system.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | Your DeepSeek API key | Required |
| `DEEPSEEK_MODEL` | Model to use (`deepseek-chat` or `deepseek-reasoner`) | `deepseek-chat` |
| `DEEPSEEK_BASE_URL` | DeepSeek API URL | `https://api.deepseek.com` |
| `APP_TITLE` | Application title | `PandasAI TXT2SQL` |
| `APP_LOG_LEVEL` | Logging level | `INFO` |

## Development

```bash
# Run tests
pytest tests/ -v

# Linting
ruff check src/ --fix

# Type checking
mypy src/
```

## Dependencies

- **pandasai**: Natural language data analysis
- **streamlit**: Web UI framework
- **openai**: OpenAI SDK (DeepSeek compatibility)
- **pandas**: Data manipulation
- **openpyxl**: Excel file support
- **pydantic**: Data validation
- **matplotlib**: Static plotting
- **seaborn**: Statistical visualization
- **plotly**: Interactive charts
- **kaleido**: Plotly export

## Project Structure

```
mini-pandas-ai-txt2sql/
├── app.py                      # Main Streamlit application
├── src/
│   ├── config.py               # Configuration management
│   ├── llm_client.py           # DeepSeek LLM wrapper
│   ├── data_loader.py          # Excel/CSV file loading
│   ├── chat_agent.py           # PandasAI Agent wrapper
│   ├── auto_insights.py        # Automated EDA features
│   ├── ui/
│   │   ├── sidebar.py          # Sidebar component
│   │   └── chat.py             # Chat interface
│   └── utils/
│       ├── session.py          # Session state management
│       └── font_config.py     # Chinese font detection
├── tests/                      # Unit tests
├── pyproject.toml              # Project configuration
├── requirements.txt            # Pip requirements
└── .env.example                # Environment variables template
```
