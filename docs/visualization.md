# Visualization Module

The visualization module provides tools for generating visual reports of expense data using matplotlib and reportlab.

## Features

- Generate PDF reports with expense visualizations
- Create monthly expense reports
- Visualize spending patterns by category and person
- Display expense distribution analysis
- Show budget insights and statistics

## Usage

```python
from src.visualization import ExpenseVisualizer

# Create a visualizer instance
visualizer = ExpenseVisualizer(insights)

# Generate a report for a specific month
report_path = visualizer.generate_monthly_report(3, 2024)  # For March 2024

# Generate reports for all months in the dataset
report_paths = visualizer.generate_all_monthly_reports()
```

## Report Contents

Each monthly report includes:

1. **Summary Section**
   - Total spending for the month
   - Average expense amount

2. **Spending by Category**
   - Pie chart showing category distribution
   - Detailed table with amounts and percentages

3. **Spending by Person**
   - Bar chart showing spending by person
   - Table with individual spending amounts and percentages

4. **Expense Distribution**
   - Bar chart showing transaction size distribution
   - Table with transaction counts by range

5. **Budget Insights**
   - Highest and lowest single expenses
   - Expense range and standard deviation
   - Most common category and day

## Output Files

The module generates the following files in the specified output directory:

- `expense_report_YYYY_MM.pdf`: Monthly expense report (e.g., `expense_report_2024_03.pdf`)
- `spending_by_category.png`: Pie chart of category spending
- `spending_by_person.png`: Bar chart of person spending
- `expense_distribution.png`: Bar chart of expense distribution

## Dependencies

- matplotlib: For creating visualizations
- reportlab: For generating PDF reports
- pandas: For data manipulation and statistics
- seaborn: For enhanced visualization styling

## Notes

- Reports are generated in PDF format for easy sharing and printing
- Visualizations use a consistent style with the seaborn theme
- Monthly reports are automatically generated for all months in the dataset
- Empty months (no expenses) will still generate a report with zero values 