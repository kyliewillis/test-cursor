# Expense Tracking System Specifications

## Overview
The Expense Tracking System is a Python-based application designed to track and analyze shared expenses between two individuals and shared expenses. The system reads expense data from a Google Sheet and provides detailed insights, visualizations, and reports.

## Core Components

### 1. Data Models
#### Expense Class
- **Purpose**: Represents a single expense entry
- **Attributes**:
  - `description`: String describing the expense
  - `amount`: Float representing the cost
  - `paid_by`: String indicating who paid (person1, person2, or "Shared")
  - `category`: Enum value from Category class
  - `date`: DateTime object for the expense date

#### Category Enum
- **Purpose**: Defines expense categories
- **Values**:
  - GROCERIES
  - UTILITIES
  - ENTERTAINMENT
  - RENT
  - DINING
  - TRANSPORT
  - SHARED
  - SHOPPING
  - OTHER

### 2. ExpenseTracker Class
#### Core Functionality
- **Initialization**:
  - Takes person1, person2 names
  - Requires Google Sheet URL for data source
  - Creates data directory for caching if not exists

#### Data Management
- **Loading Data**:
  - Primary: Loads directly from Google Sheet
  - Fallback: Uses cached JSON file if Sheet is unavailable
  - Handles date parsing with multiple format support
  - Validates data integrity

- **Caching**:
  - Saves loaded data to local JSON file
  - Used as backup when Google Sheet is unavailable
  - Automatically updates when new data is loaded

### 3. Visualization System
#### ExpenseVisualizer Class
- **Output Directory**:
  - Creates and manages `/out` directory
  - Generates visualizations as PNG files
  - Creates comprehensive HTML report

#### Generated Visualizations
1. **Spending by Category**:
   - Pie chart showing category distribution
   - Includes percentage labels

2. **Spending by Person**:
   - Bar chart showing individual spending
   - Includes value labels

3. **Expense Distribution**:
   - Bar chart showing expense ranges
   - Includes transaction counts

4. **Monthly Trends**:
   - Line chart showing spending over time
   - Includes value labels at data points

#### HTML Report
- **Sections**:
  1. Summary statistics
  2. Spending by category with visualizations
  3. Spending by person with visualizations
  4. Monthly trends with visualizations
  5. Expense distribution with visualizations
  6. Budget insights
  7. Detailed tables for all metrics

### 4. Insights Generation
#### Spending Insights
- **Basic Metrics**:
  - Total spending
  - Spending by person
  - Spending by category
  - Monthly trends
  - Top 5 largest expenses

#### Enhanced Patterns
- **Averages**:
  - Monthly spend
  - Expense amount
  - Daily/Weekly/Monthly velocity

- **Ratios**:
  - Shared vs. Individual spending
  - Category percentages
  - Person spending ratios

#### Budget Insights
- **Statistics**:
  - Highest/Lowest expenses
  - Expense range
  - Standard deviation
  - Most common category
  - Most common day
  - Expense distribution

## Technical Requirements

### Dependencies
- Python 3.x
- Required packages:
  - pandas >= 2.0.0
  - matplotlib >= 3.8.0
  - seaborn >= 0.13.0
  - python-dateutil >= 2.8.2
  - pytest >= 7.4.0

### Data Source
- **Google Sheet**:
  - Must be publicly accessible
  - CSV export format supported
  - Required columns:
    - description (text)
    - amount (number)
    - paid_by (text: person1, person2, or "Shared")
    - category (text: must match Category enum values)
    - date (date: supports multiple formats)

### Local Storage
- **JSON Cache**:
  - Located in `/data` directory
  - Used as backup when Google Sheet is unavailable
  - Automatically updated when new data is loaded

### Output
- **Visualizations**: PNG files in `/out` directory
- **Report**: HTML file in `/out` directory
- **Console Output**: Formatted text with all insights

## Error Handling
- Validates expense data format
- Handles missing or invalid dates
- Provides fallback to cached data
- Graceful handling of missing data in insights generation

## Performance Considerations
- Efficient data loading from Google Sheets
- Local caching for faster subsequent runs
- Optimized visualization generation
- Memory-efficient processing of large datasets

## Future Enhancements
1. Support for additional data sources
2. Custom visualization options
3. Export to different report formats
4. Budget tracking and alerts
5. Multi-currency support
6. User authentication for Google Sheets
7. API endpoints for integration
8. Mobile-friendly report interface 