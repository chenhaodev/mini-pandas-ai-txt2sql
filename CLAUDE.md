### Use-Case Specific Rules: PandasAI TXT2SQL

This document extends the main `CLAUDE.md` with use-case specific coding rules and guidelines.

## Project-Specific Patterns

### Configuration Management
- Always use `src.config.get_config()` to access configuration
- Never hardcode API keys, use environment variables via `.env` file
- Configuration is validated using pydantic - let validation errors bubble up

### LLM Integration
- Use `DeepSeekClient` wrapper for all DeepSeek API interactions
- LiteLLM is used for PandasAI compatibility
- The `DeepSeekClient.get_llm()` method returns the LiteLLM instance for PandasAI

### Data Loading
- Use `load_excel_files()` for all Excel file operations
- Files from Streamlit are file-like objects with `name` attribute
- Always handle `ValueError` for invalid files with user-friendly messages

### PandasAI Usage
- Use `PandasAIAgent` wrapper, not PandasAI classes directly
- Always call `load_data()` before querying
- Check `is_data_loaded()` before calling `query()`
- Response types are: `text`, `dataframe`, `chart`, `error`

### Session State Management
- Always call `init_session_state()` at the start of the app
- Use helper functions from `src.utils.session` for state operations
- Keys used: `messages`, `uploaded_files`, `api_key`, `model`

## File Size Limits

- No source file should exceed 500 lines
- Split large files into smaller modules with clear responsibilities
- If a module grows beyond 500 lines, refactor it

## Testing

- All new features must have unit tests
- Use fixtures from `conftest.py` for common test data
- Mock external API calls (DeepSeek, PandasAI)
- Test both happy paths and edge cases

## Error Handling

- Catch specific exceptions, not bare `except:`
- Provide user-friendly error messages
- Log errors with context using `logger.error(exc_info=True)`

## Type Hints

- All functions must have type hints
- Use `Optional[T]` for nullable parameters
- Use `List[T]` and `Dict[K, V]` for collections

## Docstring Style

- Use Google-style docstrings with Args, Returns, Raises sections
- Keep docstrings concise but informative
- Document public APIs thoroughly

## Code Style

- Follow PEP 8 formatting (enforced by ruff)
- Use `ruff check --fix` before committing
- Use type checking with `mypy`
- Keep functions focused and short (<50 lines when possible)
