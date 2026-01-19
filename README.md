# PandasAI TXT2SQL with DeepSeek

A conversational data analysis application that allows you to query Excel and CSV files using natural language. Built with PandasAI, DeepSeek API, and Streamlit.

## Features

- **Natural Language Queries**: Ask questions about your data in plain English
- **Multi-File Support**: Upload and query across multiple Excel and CSV files
- **Visualizations**: Generate charts and graphs on demand
- **DeepSeek Integration**: Uses DeepSeek API for LLM capabilities
- **Chat Interface**: Streamlit-based chat with message history
- **Data Exploration**: Get insights without writing SQL or Python code

## Installation

### Prerequisites

- Python 3.9 or higher
- DeepSeek API key (get one at https://platform.deepseek.com/)

### Setup

1. Clone and navigate to the project:
```bash
git clone <repository-url>
cd mini-pandas-ai-txt2sql
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt

# Or install as a package with dev dependencies:
pip install -e ".[dev]"
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your DEEPSEEK_API_KEY
```

## Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

### Using the Application

1. **Upload Data Files**:
   - Use the sidebar file uploader to upload `.xlsx`, `.xls`, or `.csv` files
   - Multiple files can be uploaded at once

2. **Configure API** (optional):
   - Enter your DeepSeek API key in the sidebar
   - Or set it via the `.env` file
   - Choose between `deepseek-chat` (standard) or `deepseek-reasoner` (thinking mode)

3. **Ask Questions**:
   - Type questions in the chat box
   - Examples:
     - "How many rows are in the data?"
     - "Show me the top 5 products by sales"
     - "What is the average sales by region?"
     - "Create a bar chart of sales by product"
     - "Plot a pie chart showing regional distribution"

### Example Queries

**Simple Queries:**
- "How many rows are in the data?"
- "What are the column names?"
- "Show me the top 5 rows"

**Aggregation Queries:**
- "What is the total sales?"
- "Show me the average of [column] grouped by [column]"
- "Count the occurrences of [column]"

**Visualization Requests:**
- "Create a bar chart of [column] vs [column]"
- "Plot a pie chart showing [column] distribution"
- "Create a histogram of [column]"
- "Generate a scatter plot of [column] and [column]"

## Project Structure

```
mini-pandas-ai-txt2sql/
├── app.py                      # Main Streamlit application
├── src/
│   ├── config.py               # Configuration management
│   ├── llm_client.py           # DeepSeek LLM wrapper
│   ├── data_loader.py          # Excel/CSV file loading
│   ├── chat_agent.py           # PandasAI Agent wrapper
│   ├── ui/
│   │   ├── sidebar.py          # Sidebar component
│   │   └── chat.py             # Chat interface
│   └── utils/
│       └── session.py          # Session state management
├── tests/                      # Unit tests
├── pyproject.toml              # Project configuration
├── requirements.txt            # Pip requirements
└── .env.example                # Environment variables template
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Linting
ruff check src/ --fix

# Type checking
mypy src/
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | Your DeepSeek API key | Required |
| `DEEPSEEK_MODEL` | Model to use | `deepseek-chat` |
| `DEEPSEEK_BASE_URL` | DeepSeek API URL | `https://api.deepseek.com` |
| `APP_TITLE` | Application title | `PandasAI TXT2SQL` |
| `APP_LOG_LEVEL` | Logging level | `INFO` |

## Supported File Formats

- Excel: `.xlsx`, `.xls`
- CSV: `.csv`

## Dependencies

- **pandasai**: Natural language data analysis
- **streamlit**: Web UI framework
- **openai**: OpenAI SDK (used for DeepSeek compatibility)
- **pandas**: Data manipulation
- **openpyxl**: Excel file support
- **pydantic**: Data validation
- **python-dotenv**: Environment variable management
