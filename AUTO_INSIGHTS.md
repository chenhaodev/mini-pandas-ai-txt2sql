# Auto Insights Feature

## Overview

The Auto Insights feature provides **one-click automated exploratory data analysis (EDA)** for your uploaded datasets. It automatically generates comprehensive statistics, visualizations, and natural language summaries without requiring any manual queries.

## How to Use

1. **Upload your data files** using the sidebar file uploader
2. Click the **"🔍 Generate Auto Insights"** button in the sidebar (Actions section)
3. Wait a few seconds while insights are generated
4. View the results in the chat interface

## What Gets Generated

### 1. Summary Statistics

For each uploaded dataset:

- **Shape**: Number of rows and columns
- **Data Types**: Type of each column (numeric, categorical, etc.)
- **Missing Values**: Columns with null values and their counts/percentages
- **Numeric Summary**: Descriptive statistics (mean, std, min, max, quartiles)
- **Categorical Summary**: Unique value counts and most frequent values

### 2. Automatic Visualizations

#### Distribution Histograms
- Automatically generated for **up to 6 numeric columns**
- Shows frequency distribution
- Helps identify:
  - Data distribution patterns (normal, skewed, bimodal)
  - Outliers and anomalies
  - Data range and spread

#### Categorical Bar Charts
- Generated for **up to 3 categorical columns**
- Only for columns with ≤20 unique values
- Shows top 10 most frequent values
- Helps identify:
  - Most common categories
  - Category imbalances
  - Dominant values

#### Correlation Heatmap
- Generated when there are **2+ numeric columns**
- Shows relationships between numeric variables
- Uses color coding:
  - Red/warm colors: Positive correlation
  - Blue/cool colors: Negative correlation
  - White/neutral: No correlation
- Limited to first 10 numeric columns for readability

### 3. Natural Language Summary

Markdown-formatted text report including:
- Dataset overview (name, shape)
- Column type breakdown
- Missing value warnings
- List of numeric and categorical columns
- Key observations about data quality

## Example Output

### Sample Dataset: Sales Data

**Input**: `sales_2023.xlsx` with columns: `Date`, `Product`, `Region`, `Sales`, `Profit`

**Generated Insights**:

```markdown
# 📊 Auto-Generated Data Insights

## sales_2023.xlsx

**Shape**: 1,000 rows × 5 columns

**📈 Numeric Columns (2):**
`Sales`, `Profit`

**📋 Categorical Columns:**
- `Product`: 15 unique values
  - Most frequent: `Widget A` (120 times)
- `Region`: 4 unique values
  - Most frequent: `North` (350 times)

---
```

**Generated Visualizations**:
1. Histogram: Distribution of Sales
2. Histogram: Distribution of Profit
3. Bar Chart: Top 10 Products
4. Bar Chart: Top Values in Region
5. Correlation Heatmap: Sales vs Profit

## Technical Details

### Limits and Constraints

To ensure performance and readability:

| Feature | Limit | Reason |
|---------|-------|--------|
| Numeric histograms | First 6 columns | Avoid chart overload |
| Categorical bar charts | First 3 columns | Screen space limitation |
| Categorical cardinality | ≤20 unique values | Skip high-cardinality columns |
| Correlation heatmap | First 10 columns | Readability of heatmap |
| Categorical summary | First 5 columns | Summary text length |

### Processing Time

Typical generation time:
- Small datasets (<1,000 rows): 2-5 seconds
- Medium datasets (1,000-10,000 rows): 5-15 seconds
- Large datasets (>10,000 rows): 15-30 seconds

Time depends on:
- Number of rows and columns
- Number of unique categorical values
- Complexity of correlation calculations

### Memory Usage

Auto insights creates matplotlib figures in memory:
- Each visualization: ~1-2 MB
- Typical report (5-10 charts): 10-20 MB
- All figures are displayed and stored in chat history

## Use Cases

### 1. Initial Data Exploration
**When**: First time loading a new dataset
**Why**: Get a quick overview of data structure, types, and quality

### 2. Data Quality Check
**When**: Before starting analysis
**Why**: Identify missing values, outliers, and data issues early

### 3. Feature Understanding
**When**: Working with unfamiliar datasets
**Why**: Understand distributions and relationships between variables

### 4. Quick Reports
**When**: Need fast insights for stakeholders
**Why**: Generate presentation-ready charts without manual work

### 5. Baseline for Further Analysis
**When**: Planning deeper analysis
**Why**: Identify which columns/relationships deserve closer investigation

## Best Practices

### ✅ Do's

1. **Run auto insights first** before asking specific questions
2. **Review missing values** highlighted in the summary
3. **Check distributions** for unexpected patterns or outliers
4. **Use correlation heatmap** to identify relationships worth exploring
5. **Download charts** for reports using the download buttons

### ❌ Don'ts

1. **Don't run on very wide datasets** (>50 columns) - too many charts
2. **Don't expect insights on text columns** - only works on numeric/categorical
3. **Don't use for time-series analysis** - use specific queries instead
4. **Don't ignore warnings** about high-cardinality columns

## Limitations

1. **No time-series detection**: Auto insights treats dates as categorical
2. **No custom binning**: Histogram bins are automatically determined
3. **No statistical tests**: Only descriptive statistics, no hypothesis testing
4. **Limited text analysis**: Long text fields are not analyzed
5. **Fixed chart types**: Cannot customize chart styles via auto insights

## Integration with Chat

Auto insights results appear in the chat as:
1. One text message with markdown-formatted summary
2. Multiple chart messages, one per visualization

These messages:
- ✅ Are preserved in chat history
- ✅ Can be downloaded individually
- ✅ Scroll with other chat messages
- ❌ Cannot be regenerated (click button again for fresh insights)

## Implementation Details

### Code Architecture

**Module**: `src/auto_insights.py`

**Main Class**: `AutoInsight`

**Key Methods**:
- `generate_summary_statistics()` - Computes descriptive stats
- `generate_visualizations()` - Creates matplotlib figures
- `generate_insights_text()` - Formats markdown report
- `generate_full_report()` - Orchestrates all generation

### Libraries Used

- **pandas**: Data manipulation and statistics
- **matplotlib**: Chart generation
- **seaborn**: Enhanced heatmaps
- **numpy**: Numerical computations

### Chart Generation

All charts are created as matplotlib Figure objects:
- Resolution: 100 DPI
- Format: PNG when downloaded
- Style: Default matplotlib with seaborn for heatmaps

## Troubleshooting

### Issue: Button is Disabled
**Cause**: No data files uploaded
**Solution**: Upload at least one `.xlsx`, `.xls`, or `.csv` file

### Issue: No Charts Generated
**Cause**: Dataset has no numeric or categorical columns
**Solution**: Check that your data has appropriate column types

### Issue: Missing Columns in Charts
**Cause**: Limits on number of charts (see table above)
**Solution**: Use specific queries for other columns

### Issue: Chinese Characters Show as Squares
**Cause**: Font configuration issue (should be automatic)
**Solution**: See Chinese Language Support section in main README

### Issue: Generation Takes Too Long
**Cause**: Very large dataset with many columns
**Solution**: Consider reducing columns or using specific queries

## Future Enhancements

Potential improvements (not yet implemented):

- **Time-series detection**: Automatically identify and plot trends
- **Outlier highlighting**: Mark suspicious data points
- **Statistical tests**: Add hypothesis testing results
- **Custom chart options**: Allow users to configure chart types
- **Export to PDF**: Generate downloadable reports
- **Scheduled insights**: Automatically run on new data uploads

## Feedback

If you have suggestions for improving auto insights:
- Add feature requests to GitHub Issues
- Share example datasets that don't work well
- Suggest additional statistics or visualizations

---

**Related Documentation**:
- [Main README](README.md) - General usage
- [Plotting Features](PLOTTING_FEATURES.md) - Chart capabilities
- [Example Queries](example_plot_queries.md) - Manual query examples
