from typing import List, Dict, Optional
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from .models import Expense, Category

class ExpenseTracker:
    def __init__(self, person1: str, person2: str, sheet_url: str, save_dir: str = "data"):
        self.person1 = person1
        self.person2 = person2
        self.shared = "Shared"  # Third person for shared expenses
        self.expenses: List[Expense] = []
        self.sheet_url = sheet_url
        
        # Ensure data directory exists
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        self.save_path = self.save_dir / "expenses.json"
        
        self.load_expenses()

    def load_from_sheets(self) -> None:
        """Load expenses directly from Google Sheet."""
        try:
            # Convert Google Sheet URL to export URL
            sheet_id = self.sheet_url.split('/d/')[1].split('/')[0]
            export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            
            # Read the Google Sheet directly using pandas
            df = pd.read_csv(export_url)
            
            # Parse dates with a specific format
            def parse_date(date_str):
                try:
                    current_year = datetime.now().year
                    
                    # If the date string only has month/day (e.g., "3/28")
                    if '/' in date_str and len(date_str.split('/')) == 2:
                        month, day = map(int, date_str.split('/'))
                        return datetime(current_year, month, day)
                    
                    # Try formats with year
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%Y/%m/%d']:
                        try:
                            date = datetime.strptime(date_str, fmt)
                            # If the year is 1900 (pandas default), use current year
                            if date.year == 1900:
                                date = date.replace(year=current_year)
                            return date
                        except ValueError:
                            continue
                    
                    # Try formats without year
                    for fmt in ['%m-%d']:
                        try:
                            date = datetime.strptime(date_str, fmt)
                            return date.replace(year=current_year)
                        except ValueError:
                            continue
                            
                    # If no format works, try default parsing
                    date = pd.to_datetime(date_str).to_pydatetime()
                    # If the year is 1900 (pandas default), use current year
                    if date.year == 1900:
                        date = date.replace(year=current_year)
                    return date
                except Exception as e:
                    print(f"Warning: Could not parse date '{date_str}': {e}")
                    return None
            
            # Convert dates to datetime objects
            df['date'] = df['date'].apply(parse_date)
            df = df.dropna(subset=['date'])  # Remove rows with invalid dates
            
            # Clear existing expenses before loading new ones
            self.expenses = []
            
            for _, row in df.iterrows():
                expense = Expense(
                    description=row['description'],
                    amount=float(row['amount']),
                    paid_by=row['paid_by'],
                    category=Category(row['category']),
                    date=row['date']
                )
                self.expenses.append(expense)
            
            # Save to JSON for caching
            self.save_expenses()
            print(f"Successfully loaded {len(self.expenses)} expenses from Google Sheet")
            
        except Exception as e:
            print(f"Error loading from Google Sheet: {e}")

    def save_expenses(self) -> None:
        """Cache expenses in local JSON file for faster loading."""
        data = {
            "person1": self.person1,
            "person2": self.person2,
            "shared": self.shared,
            "expenses": [expense.to_dict() for expense in self.expenses]
        }
        with open(self.save_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_expenses(self) -> None:
        """Load expenses from Google Sheet, using cached JSON only if Sheet is unavailable."""
        try:
            self.load_from_sheets()
        except Exception as e:
            print(f"Warning: Could not load from Google Sheet: {e}")
            if self.save_path.exists():
                try:
                    with open(self.save_path, 'r') as f:
                        data = json.load(f)
                        self.expenses = [Expense.from_dict(exp) for exp in data["expenses"]]
                    print(f"Loaded {len(self.expenses)} expenses from cache")
                except json.JSONDecodeError:
                    print(f"Error: Could not load expenses from cache")
                    self.expenses = []
            else:
                print("No cached data available")
                self.expenses = []

    def _filter_expenses(self, start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> List[Expense]:
        """Filter expenses by date range."""
        expenses = self.expenses
        if start_date:
            expenses = [e for e in expenses if e.date >= start_date]
        if end_date:
            expenses = [e for e in expenses if e.date <= end_date]
        return expenses

    def get_spending_insights(self, start_date: Optional[datetime] = None, 
                            end_date: Optional[datetime] = None) -> Dict:
        filtered_expenses = self._filter_expenses(start_date, end_date)
        if not filtered_expenses:
            current_date = datetime.now()
            return {
                "total_spending": 0,
                "spending_by_person": {},
                "spending_by_category": {},
                "monthly_trends": {},
                "top_expenses": [],
                "expenses": [],  # Add empty expenses list
                "spending_patterns": {
                    "average_monthly_spend": 0,
                    "most_expensive_category": ("", 0),
                    "highest_spending_month": (current_date, 0),
                    "spending_by_day_of_week": {},
                    "spending_by_category_percentage": {},
                    "average_expense_amount": 0,
                    "shared_vs_individual_ratio": 0,
                    "spending_velocity": 0,
                    "category_trends": {},
                    "person_spending_ratio": {},
                    "budget_insights": {}
                }
            }

        # Ensure all dates use the current year
        current_year = datetime.now().year
        df = pd.DataFrame([{
            **exp.to_dict(),
            'date': exp.date.replace(year=current_year)  # Use current year for all dates
        } for exp in filtered_expenses])
        
        # Calculate total spending
        total_spending = df['amount'].sum()
        
        # Spending by person (including shared)
        spending_by_person = df.groupby('paid_by')['amount'].sum().to_dict()
        
        # Spending by category
        spending_by_category = df.groupby('category')['amount'].sum().to_dict()
        
        # Monthly trends (using 'ME' instead of 'M' for month-end frequency)
        monthly_trends = df.set_index('date').resample('ME')['amount'].sum().to_dict()
        
        # Top 5 largest expenses
        top_expenses = df.nlargest(5, 'amount')[['description', 'amount', 'category', 'date']].to_dict('records')
        
        # Format dates in top expenses
        for expense in top_expenses:
            expense['date'] = expense['date'].strftime('%Y-%m-%d')
        
        # Enhanced spending patterns
        spending_patterns = {
            "average_monthly_spend": df.groupby(df['date'].dt.strftime('%Y-%m'))['amount'].sum().mean(),
            "most_expensive_category": max(spending_by_category.items(), key=lambda x: x[1]),
            "highest_spending_month": max(monthly_trends.items(), key=lambda x: x[1]),
            "spending_by_day_of_week": df.groupby(df['date'].dt.day_name())['amount'].sum().to_dict(),
            "spending_by_category_percentage": {
                category: (amount / total_spending) * 100 
                for category, amount in spending_by_category.items()
            },
            # New insights
            "average_expense_amount": df['amount'].mean(),
            "shared_vs_individual_ratio": {
                "shared": spending_by_person.get(self.shared, 0) / total_spending * 100,
                "individual": (total_spending - spending_by_person.get(self.shared, 0)) / total_spending * 100
            },
            "spending_velocity": {
                "daily": df.groupby(df['date'].dt.date)['amount'].sum().mean(),
                "weekly": df.groupby(df['date'].dt.isocalendar().week)['amount'].sum().mean(),
                "monthly": df.groupby(df['date'].dt.month)['amount'].sum().mean()
            },
            "category_trends": {
                category: {
                    "total": amount,
                    "percentage": (amount / total_spending) * 100,
                    "average": df[df['category'] == category]['amount'].mean(),
                    "count": len(df[df['category'] == category])
                }
                for category, amount in spending_by_category.items()
            },
            "person_spending_ratio": {
                person: {
                    "total": amount,
                    "percentage": (amount / total_spending) * 100,
                    "average": df[df['paid_by'] == person]['amount'].mean(),
                    "count": len(df[df['paid_by'] == person])
                }
                for person, amount in spending_by_person.items()
            },
            "budget_insights": {
                "highest_single_expense": df['amount'].max(),
                "lowest_single_expense": df['amount'].min(),
                "expense_range": df['amount'].max() - df['amount'].min(),
                "expense_std_dev": df['amount'].std(),
                "most_common_category": df['category'].mode().iloc[0] if not df['category'].empty else "",
                "most_common_day": df['date'].dt.day_name().mode().iloc[0] if not df['date'].empty else "",
                "expense_distribution": {
                    "under_50": len(df[df['amount'] < 50]),
                    "50_to_100": len(df[(df['amount'] >= 50) & (df['amount'] < 100)]),
                    "100_to_200": len(df[(df['amount'] >= 100) & (df['amount'] < 200)]),
                    "200_to_500": len(df[(df['amount'] >= 200) & (df['amount'] < 500)]),
                    "over_500": len(df[df['amount'] >= 500])
                }
            }
        }

        return {
            "total_spending": total_spending,
            "spending_by_person": spending_by_person,
            "spending_by_category": spending_by_category,
            "monthly_trends": {k.strftime('%Y-%m'): v for k, v in monthly_trends.items()},
            "top_expenses": top_expenses,
            "expenses": [exp.to_dict() for exp in filtered_expenses],  # Add raw expenses
            "spending_patterns": spending_patterns
        } 