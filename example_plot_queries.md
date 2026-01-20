# Plotting Feature Examples

This document provides example queries to test the dynamic plotting functionality.

## Basic Chart Types

### Bar Chart
```
Create a bar chart of sales by region
```
```
Plot a bar chart showing product categories and their counts
```

### Line Chart
```
Plot a line chart of sales over time
```
```
Show me a line chart of monthly revenue
```

### Histogram
```
Show me a histogram of customer ages
```
```
Create a histogram of price distribution
```

### Scatter Plot
```
Create a scatter plot of price vs quantity
```
```
Plot sales vs profit as a scatter chart
```

### Pie Chart
```
Show a pie chart of market share by region
```
```
Create a pie chart showing percentage distribution of categories
```

## Advanced Charts

### Multiple Series
```
Plot sales and profit over time on the same chart
```
```
Compare revenue across different regions as a grouped bar chart
```

### Aggregated Data
```
Show average sales by month as a line chart
```
```
Plot total revenue by category as a bar chart
```

## Supported Libraries

The application now supports:
- **Matplotlib**: Default plotting library for most charts
- **Seaborn**: Statistical visualizations with better styling
- **Plotly**: Interactive charts with hover tooltips and zoom

## Features

1. **Auto-detection**: The system automatically detects when a chart is generated
2. **Download buttons**: All charts include a download button to save as PNG
3. **Chat history**: Charts are preserved in chat history
4. **Multiple formats**: Supports various chart types and formats

## Usage Tips

1. **Be specific**: Include chart type in your query (bar chart, line chart, etc.)
2. **Specify columns**: Mention which columns to plot
3. **Add context**: Specify aggregations if needed (sum, average, count)
4. **Try variations**: If one query doesn't work, try rephrasing

## Examples with Sample Data

Assuming you have a DataFrame with columns: `Date`, `Product`, `Sales`, `Profit`, `Region`

```
"Create a bar chart showing total sales by product"
"Plot sales trends over time as a line chart"
"Show me a scatter plot of sales vs profit"
"Generate a pie chart of sales distribution by region"
"Create a histogram of profit values"
```
