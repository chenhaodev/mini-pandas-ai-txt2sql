# Dynamic Plotting Feature Implementation

## Summary

Enhanced the PandasAI TXT2SQL application with comprehensive dynamic plotting capabilities. The system now automatically detects, displays, and enables downloading of charts generated through natural language queries.

## Changes Made

### 1. Dependencies Added

**requirements.txt** and **pyproject.toml**:
- `matplotlib>=3.7.0` - Core plotting library
- `seaborn>=0.12.0` - Statistical visualizations
- `plotly>=5.14.0` - Interactive charts
- `kaleido>=0.2.1` - Plotly export support

### 2. PandasAI Configuration (`src/chat_agent.py`)

Enhanced the PandasAI Agent initialization with plotting configuration:
```python
config={
    "llm": self.llm_client.get_llm(),
    "save_logs": self.save_logs,
    "verbose": False,
    "max_retries": 3,
    "enable_cache": True,
    "save_charts": True,                    # NEW
    "save_charts_path": "exports/charts",   # NEW
    "open_charts": False,                   # NEW
}
```

### 3. Enhanced Chart Detection (`src/chat_agent.py`)

Improved `_detect_response_type()` method to recognize:
- Matplotlib Figure objects
- Matplotlib Axes objects
- Plotly figures (Figure, Scatter, Bar)
- Seaborn objects (via `get_figure()`)
- Chart file paths (PNG, JPG, SVG, PDF)

### 4. Enhanced Chart Display (`src/ui/chat.py`)

Completely rewrote `_display_chart()` function with:
- **File path handling**: Display saved chart images
- **Matplotlib support**: Display Figure and Axes objects
- **Plotly support**: Display interactive charts
- **Seaborn support**: Extract and display underlying matplotlib figures
- **Download buttons**: PNG export for all chart types

### 5. Testing

Added comprehensive tests:
- `test_detect_response_type_matplotlib_figure()` - Matplotlib detection
- `test_detect_response_type_chart_path()` - File path detection
- Updated `test_display_plotly_figure()` - Real plotly object testing

All 93 tests pass successfully.

### 6. Documentation

Created/Updated:
- **example_plot_queries.md** - Comprehensive plotting examples and tips
- **README.md** - Updated features section and added plotting documentation
- **PLOTTING_FEATURES.md** - This implementation summary

### 7. Chinese Font Support (`src/utils/font_config.py`)

Added comprehensive Chinese font configuration:
```python
# Platform-specific font detection
def get_chinese_font() -> Optional[str]:
    # Detects macOS, Windows, Linux
    # Returns best available Chinese font
```

**Key Features**:
- Platform detection using `platform.system()`
- Priority-based font selection (Songti SC first on macOS)
- Case-insensitive font name matching
- Matplotlib rcParams configuration
- Font cache clearing for immediate effect
- Unicode minus sign fix
- No external dependencies

**Integration**:
- `src/utils/__init__.py` - Exported new functions
- `app.py` - Called `configure_matplotlib_fonts()` at startup
- Warning UI: Shows Streamlit warning if no Chinese font found

## Features Implemented

### Automatic Detection
- System automatically identifies when a chart is generated
- No manual configuration needed by users
- Works across matplotlib, seaborn, and plotly

### Download Capability
- Every displayed chart includes a download button
- Charts saved as high-quality PNG images
- Works for all supported chart types

### Chat History Preservation
- Charts are stored in session state
- Preserved when scrolling through chat history
- Survives page reloads (if session persists)

### Multiple Library Support
- **Matplotlib**: Bar, line, scatter, histogram, pie charts
- **Seaborn**: Statistical plots with enhanced styling
- **Plotly**: Interactive charts with zoom and hover

### Chinese Character Support
- **Automatic font detection**: Finds best Chinese font on system
- **Platform-specific priorities**:
  - macOS: Songti SC, PingFang SC, STHeiti (serif preferred)
  - Windows: SimHei, Microsoft YaHei, SimSun
  - Linux: WenQuanYi Micro Hei, Noto Sans CJK
- **Case-insensitive matching**: Works regardless of font name case
- **Graceful degradation**: Falls back to English-only fonts if needed
- **UI warnings**: Shows warning if no Chinese font is available
- **No bundled fonts**: Uses system fonts only (no project size increase)
- **Unicode support**: Proper minus sign rendering with `axes.unicode_minus=False`

## Usage Examples

Users can now ask queries like:

```
"Create a bar chart of sales by region"
"Plot sales trends over time as a line chart"
"Show me a scatter plot of price vs quantity"
"Generate a pie chart of market share by category"
"Create a histogram of customer ages"
```

The system will:
1. Generate the appropriate chart using PandasAI
2. Automatically detect it's a chart response
3. Display it inline in the chat
4. Provide a download button

## File Structure Changes

```
pandas-ai-txt2sql/
├── exports/
│   └── charts/              # NEW: Chart storage directory
├── example_plot_queries.md  # NEW: Plotting examples
├── PLOTTING_FEATURES.md     # NEW: This document
├── requirements.txt         # UPDATED: Added plotting libs
├── pyproject.toml           # UPDATED: Added plotting libs
├── README.md                # UPDATED: Plotting docs
└── src/
    ├── chat_agent.py        # UPDATED: Enhanced detection
    └── ui/
        └── chat.py          # UPDATED: Enhanced display
```

## Technical Details

### Chart Detection Flow
1. Query executed via `PandasAIAgent.query()`
2. Result passed to `_detect_response_type()`
3. Type detection checks (in order):
   - DataFrame → "dataframe"
   - Matplotlib Figure → "chart"
   - Matplotlib Axes → "chart"
   - Plotly objects → "chart"
   - Seaborn objects → "chart"
   - File paths (.png, .jpg, etc.) → "chart"
   - Default → "text"

### Chart Display Flow
1. `QueryResponse` with type="chart" created
2. `_display_chart()` called with chart object
3. Display logic branches by type:
   - File path → `st.image()`
   - Matplotlib → `st.pyplot()`
   - Plotly → `st.plotly_chart()`
   - Seaborn → Extract figure, then `st.pyplot()`
4. Download button added with PNG export

### Download Implementation
- Uses `io.BytesIO()` for in-memory buffer
- Matplotlib: `.savefig(buf, format="png")`
- Plotly: `.write_image(buf, format="png")`
- File paths: Direct file read

## Benefits

1. **User Experience**: No need to manually save or export charts
2. **Flexibility**: Works with multiple plotting libraries
3. **Convenience**: Download button for easy sharing
4. **Robustness**: Graceful fallbacks for unknown types
5. **Maintainability**: Clear separation of detection and display logic

## Future Enhancements

Potential improvements:
- Multiple format exports (SVG, PDF)
- Chart editing/customization UI
- Chart templates/presets
- Animation support
- 3D plotting support

## Testing Coverage

- 93 total tests passing
- Specific chart-related tests:
  - Chart type detection
  - Matplotlib figure handling
  - Plotly figure handling
  - File path recognition
  - Download button integration

## Installation Notes

To use the new features, users must:
```bash
pip install -r requirements.txt
```

Or with development dependencies:
```bash
pip install -e ".[dev]"
```

## Backward Compatibility

All changes are backward compatible:
- Existing text and DataFrame responses work unchanged
- No breaking changes to API
- Graceful fallbacks for unsupported chart types

---

## Chinese Font Support Implementation (Additional Feature)

### Summary

Added automatic Chinese font detection and configuration to support CJK characters in matplotlib charts. Solves the issue where Chinese province names displayed as empty squares in pie charts.

### Problem

When users queried in Chinese (e.g., "各自省份的用户，占比？画个饼状图"), generated charts showed:
- Empty squares instead of Chinese characters
- 80+ warnings: "Glyph XXXX missing from font(s) DejaVu Sans"
- Unusable visualizations for Chinese-language data

### Solution

Implemented platform-aware font detection with priority-based selection:
1. Detect operating system (macOS, Windows, Linux)
2. Query available system fonts via matplotlib
3. Match against priority list (best fonts first)
4. Configure matplotlib rcParams globally
5. Clear font cache for immediate effect
6. Show UI warning if no Chinese font found

### Files Added/Modified

| File | Change | Description |
|------|---------|-------------|
| `src/utils/font_config.py` | NEW | Font detection and configuration utility |
| `src/utils/__init__.py` | UPDATE | Export font configuration functions |
| `app.py` | UPDATE | Initialize fonts at startup, show warning |
| `tests/test_font_config.py` | NEW | Comprehensive unit tests |
| `README.md` | UPDATE | Chinese language support documentation |
| `PLOTTING_FEATURES.md` | UPDATE | Font implementation details |

### Test Results

- **Total tests**: 108 passing (93 original + 15 new font tests)
- **Platform coverage**: macOS, Windows, Linux with mocking
- **Edge cases**: Case-insensitive matching, fallbacks, cache clearing

### Font Priority Lists

**macOS** (Songti preferred as requested):
1. Songti SC (宋体-简) - serif, traditional
2. PingFang SC (苹方-简) - sans-serif, modern
3. Heiti SC (黑体-简) - bold, widely used
4. STHeiti (黑体) - system default Chinese font

**Windows**:
1. SimSun (宋体) - serif, default
2. SimHei (黑体) - bold, common
3. Microsoft YaHei (微软雅黑) - modern, clean
4. KaiTi (楷体) - calligraphy style

**Linux**:
1. WenQuanYi Micro Hei - open source
2. Noto Sans CJK SC - Google's font
3. Noto Sans CJK - fallback

### Usage

Users can now query in both languages:

**English**:
```
"Show me a pie chart of users by province"
```

**Chinese**:
```
"各自省份的用户，占比？画个饼状图"
```

Both will generate identical charts with proper character rendering.

### Technical Implementation

**Font Detection** (`get_chinese_font()`):
```python
# Platform-specific priority lists
font_priority = {
    "Darwin": ["Songti SC", "PingFang SC", "Heiti SC", "STHeiti"],
    "Windows": ["SimSun", "SimHei", "Microsoft YaHei", "KaiTi"],
    "Linux": ["WenQuanYi Micro Hei", "Noto Sans CJK SC"]
}

# Case-insensitive matching
available = [f.lower() for f in get_font_names()]
for font in font_priority:
    if font.lower() in available:
        return font
return None
```

**Matplotlib Configuration** (`configure_matplotlib_fonts()`):
```python
if chinese_font:
    matplotlib.rcParams["font.sans-serif"] = [
        chinese_font, "DejaVu Sans", "Arial"
    ]
    matplotlib.rcParams["axes.unicode_minus"] = False
    matplotlib.font_manager._load_fontmanager(try_read_cache=False)
```

**User Warning**:
```python
if not configured_font:
    st.warning("⚠️ Warning: Chinese characters may not display correctly...")
```

### Benefits

1. **Seamless**: Automatic detection, no user configuration needed
2. **Cross-platform**: Works on macOS, Windows, Linux
3. **Reliable**: Case-insensitive matching handles font name variations
4. **Graceful**: Falls back to English fonts if needed
5. **User-friendly**: Shows clear warning if Chinese fonts missing
6. **No dependencies**: Uses only matplotlib and built-in Python libs
7. **Lightweight**: No bundled fonts, uses system fonts only
