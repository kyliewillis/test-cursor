import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import seaborn as sns
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from calendar import month_name

class ExpenseVisualizer:
    def __init__(self, insights: Dict, output_dir: str = "out"):
        self.insights = insights
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Set style for all plots
        plt.style.use('seaborn-v0_8')
        sns.set_theme()
        
    def filter_insights_by_month(self, month: int, year: int) -> Dict:
        """Filter insights data for a specific month and year."""
        filtered_insights = {
            'total_spending': 0.0,
            'spending_by_category': {},
            'spending_by_person': {},
            'monthly_trends': {},
            'spending_patterns': {
                'average_monthly_spend': 0.0,
                'average_expense_amount': 0.0,
                'spending_by_category_percentage': {},
                'person_spending_ratio': {},
                'budget_insights': {
                    'highest_single_expense': 0.0,
                    'lowest_single_expense': float('inf'),
                    'expense_range': 0.0,
                    'expense_std_dev': 0.0,
                    'expense_distribution': {
                        'under_10': 0,
                        '10_to_50': 0,
                        '50_to_100': 0,
                        '100_to_200': 0,
                        'over_200': 0
                    },
                    'most_common_category': '',
                    'most_common_day': ''
                }
            }
        }
        
        # Get expenses from the insights dictionary
        expenses = self.insights.get('expenses', [])
        if not expenses:
            return filtered_insights
            
        # Filter expenses for the specified month
        month_expenses = []
        for exp in expenses:
            # Convert date string to datetime object
            date = datetime.strptime(exp['date'], '%Y-%m-%d')
            if date.month == month and date.year == year:
                month_expenses.append(exp)
        
        if not month_expenses:
            return filtered_insights
            
        # Calculate filtered insights
        amounts = [exp['amount'] for exp in month_expenses]
        filtered_insights['total_spending'] = sum(amounts)
        filtered_insights['spending_patterns']['average_expense_amount'] = sum(amounts) / len(amounts)
        
        # Calculate spending by category
        for exp in month_expenses:
            cat = exp['category']
            amt = exp['amount']
            filtered_insights['spending_by_category'][cat] = filtered_insights['spending_by_category'].get(cat, 0) + amt
            
            # Update person spending
            person = exp['paid_by']
            filtered_insights['spending_by_person'][person] = filtered_insights['spending_by_person'].get(person, 0) + amt
            
            # Update budget insights
            if amt > filtered_insights['spending_patterns']['budget_insights']['highest_single_expense']:
                filtered_insights['spending_patterns']['budget_insights']['highest_single_expense'] = amt
            if amt < filtered_insights['spending_patterns']['budget_insights']['lowest_single_expense']:
                filtered_insights['spending_patterns']['budget_insights']['lowest_single_expense'] = amt
                
            # Update expense distribution
            if amt < 10:
                filtered_insights['spending_patterns']['budget_insights']['expense_distribution']['under_10'] += 1
            elif amt < 50:
                filtered_insights['spending_patterns']['budget_insights']['expense_distribution']['10_to_50'] += 1
            elif amt < 100:
                filtered_insights['spending_patterns']['budget_insights']['expense_distribution']['50_to_100'] += 1
            elif amt < 200:
                filtered_insights['spending_patterns']['budget_insights']['expense_distribution']['100_to_200'] += 1
            else:
                filtered_insights['spending_patterns']['budget_insights']['expense_distribution']['over_200'] += 1
        
        # Calculate expense range
        filtered_insights['spending_patterns']['budget_insights']['expense_range'] = (
            filtered_insights['spending_patterns']['budget_insights']['highest_single_expense'] -
            filtered_insights['spending_patterns']['budget_insights']['lowest_single_expense']
        )
        
        # Calculate standard deviation
        if len(amounts) > 1:
            filtered_insights['spending_patterns']['budget_insights']['expense_std_dev'] = pd.Series(amounts).std()
        
        # Calculate percentages
        total = filtered_insights['total_spending']
        for cat, amt in filtered_insights['spending_by_category'].items():
            filtered_insights['spending_patterns']['spending_by_category_percentage'][cat] = (amt / total) * 100
            
        for person, amt in filtered_insights['spending_by_person'].items():
            filtered_insights['spending_patterns']['person_spending_ratio'][person] = {
                'total': amt,
                'percentage': (amt / total) * 100
            }
        
        # Find most common category and day
        if month_expenses:
            categories = [exp['category'] for exp in month_expenses]
            days = [datetime.strptime(exp['date'], '%Y-%m-%d').strftime('%A') for exp in month_expenses]
            filtered_insights['spending_patterns']['budget_insights']['most_common_category'] = max(set(categories), key=categories.count)
            filtered_insights['spending_patterns']['budget_insights']['most_common_day'] = max(set(days), key=days.count)
        
        return filtered_insights
    
    def create_spending_by_category_pie(self, month_insights: Dict) -> str:
        """Create a pie chart of spending by category."""
        plt.figure(figsize=(10, 6))
        categories = list(month_insights['spending_by_category'].keys())
        amounts = list(month_insights['spending_by_category'].values())
        
        plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
        plt.title('Spending by Category')
        
        # Save the plot
        output_path = self.output_dir / 'spending_by_category.png'
        plt.savefig(output_path)
        plt.close()
        return str(output_path)
    
    def create_spending_by_person_bar(self, month_insights: Dict) -> str:
        """Create a bar chart of spending by person."""
        plt.figure(figsize=(10, 6))
        people = list(month_insights['spending_by_person'].keys())
        amounts = list(month_insights['spending_by_person'].values())
        
        plt.bar(people, amounts)
        plt.title('Spending by Person')
        plt.ylabel('Amount ($)')
        
        # Add value labels on top of bars
        for i, v in enumerate(amounts):
            plt.text(i, v, f'${v:.2f}', ha='center', va='bottom')
        
        # Save the plot
        output_path = self.output_dir / 'spending_by_person.png'
        plt.savefig(output_path)
        plt.close()
        return str(output_path)
    
    def create_expense_distribution(self, month_insights: Dict) -> str:
        """Create a bar chart of expense distribution."""
        plt.figure(figsize=(10, 6))
        distribution = month_insights['spending_patterns']['budget_insights']['expense_distribution']
        
        ranges = list(distribution.keys())
        counts = list(distribution.values())
        
        plt.bar(ranges, counts)
        plt.title('Expense Distribution')
        plt.ylabel('Number of Transactions')
        plt.xticks(rotation=45)
        
        # Add value labels on top of bars
        for i, v in enumerate(counts):
            plt.text(i, v, str(v), ha='center', va='bottom')
        
        # Save the plot
        output_path = self.output_dir / 'expense_distribution.png'
        plt.savefig(output_path)
        plt.close()
        return str(output_path)
    
    def generate_monthly_report(self, month: int, year: int) -> str:
        """Generate a comprehensive PDF report for a specific month."""
        # Filter insights for the specified month
        month_insights = self.filter_insights_by_month(month, year)
        
        # Create all visualizations
        category_pie = self.create_spending_by_category_pie(month_insights)
        person_bar = self.create_spending_by_person_bar(month_insights)
        distribution = self.create_expense_distribution(month_insights)
        
        # Create PDF document
        report_path = self.output_dir / f'expense_report_{year}_{month:02d}.pdf'
        doc = SimpleDocTemplate(str(report_path), pagesize=letter)
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Create custom style for tables
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        
        # Build the PDF content
        story = []
        
        # Title
        story.append(Paragraph(f"Expense Report - {month_name[month]} {year}", title_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        story.append(Spacer(1, 20))
        
        # Summary
        story.append(Paragraph("Summary", heading_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Total Spending: ${month_insights['total_spending']:.2f}", normal_style))
        story.append(Paragraph(f"Average Expense Amount: ${month_insights['spending_patterns']['average_expense_amount']:.2f}", normal_style))
        story.append(Spacer(1, 20))
        
        # Spending by Category
        story.append(Paragraph("Spending by Category", heading_style))
        story.append(Spacer(1, 12))
        story.append(Image(category_pie, width=400, height=300))
        story.append(Spacer(1, 12))
        
        # Category table
        category_data = [['Category', 'Amount', 'Percentage']]
        for cat, amt in month_insights['spending_by_category'].items():
            percentage = month_insights['spending_patterns']['spending_by_category_percentage'][cat]
            category_data.append([cat, f"${amt:.2f}", f"{percentage:.1f}%"])
        
        category_table = Table(category_data)
        category_table.setStyle(table_style)
        story.append(category_table)
        story.append(Spacer(1, 20))
        
        # Spending by Person
        story.append(Paragraph("Spending by Person", heading_style))
        story.append(Spacer(1, 12))
        story.append(Image(person_bar, width=400, height=300))
        story.append(Spacer(1, 12))
        
        # Person table
        person_data = [['Person', 'Amount', 'Percentage']]
        for person, stats in month_insights['spending_patterns']['person_spending_ratio'].items():
            person_data.append([person, f"${stats['total']:.2f}", f"{stats['percentage']:.1f}%"])
        
        person_table = Table(person_data)
        person_table.setStyle(table_style)
        story.append(person_table)
        story.append(Spacer(1, 20))
        
        # Expense Distribution
        story.append(Paragraph("Expense Distribution", heading_style))
        story.append(Spacer(1, 12))
        story.append(Image(distribution, width=400, height=300))
        story.append(Spacer(1, 12))
        
        # Distribution table
        dist_data = [['Range', 'Count']]
        for range_name, count in month_insights['spending_patterns']['budget_insights']['expense_distribution'].items():
            dist_data.append([range_name.replace('_', ' ').title(), str(count)])
        
        dist_table = Table(dist_data)
        dist_table.setStyle(table_style)
        story.append(dist_table)
        story.append(Spacer(1, 20))
        
        # Budget Insights
        story.append(Paragraph("Budget Insights", heading_style))
        story.append(Spacer(1, 12))
        
        budget = month_insights['spending_patterns']['budget_insights']
        budget_data = [
            ['Metric', 'Value'],
            ['Highest Single Expense', f"${budget['highest_single_expense']:.2f}"],
            ['Lowest Single Expense', f"${budget['lowest_single_expense']:.2f}"],
            ['Expense Range', f"${budget['expense_range']:.2f}"],
            ['Standard Deviation', f"${budget['expense_std_dev']:.2f}"],
            ['Most Common Category', budget['most_common_category']],
            ['Most Common Day', budget['most_common_day']]
        ]
        
        budget_table = Table(budget_data)
        budget_table.setStyle(table_style)
        story.append(budget_table)
        
        # Build the PDF
        doc.build(story)
        return str(report_path)
    
    def generate_all_monthly_reports(self) -> List[str]:
        """Generate monthly reports for all months in the dataset."""
        # Get unique months and years from expenses
        dates = [exp['date'] for exp in self.insights['expenses']]
        unique_months = set((date.month, date.year) for date in dates)
        
        report_paths = []
        for month, year in unique_months:
            report_path = self.generate_monthly_report(month, year)
            report_paths.append(report_path)
        
        return report_paths 