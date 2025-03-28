from typing import List, Dict, Optional
import json
from pathlib import Path
import csv
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
from .models import Expense, Category

class ExpenseTracker:
    def __init__(self, person1: str, person2: str, save_dir: str = "data"):
        self.person1 = person1
        self.person2 = person2
        self.shared = "Shared"  # Third person for shared expenses
        self.expenses: List[Expense] = []
        
        # Ensure data directory exists
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        self.save_path = self.save_dir / "expenses.json"
        
        self.load_expenses()

    def add_expense(self, description: str, amount: float, paid_by: str, 
                   category: Category, date: datetime = None) -> None:
        if paid_by not in [self.person1, self.person2, self.shared]:
            raise ValueError(f"Paid by must be either {self.person1}, {self.person2}, or {self.shared}")
        
        if not isinstance(category, Category):
            raise ValueError(f"Category must be one of: {Category.list_categories()}")

        expense = Expense(
            description=description,
            amount=amount,
            paid_by=paid_by,
            category=category,
            date=date or datetime.now()
        )
        self.expenses.append(expense)
        self.save_expenses()

    def save_expenses(self) -> None:
        data = {
            "person1": self.person1,
            "person2": self.person2,
            "shared": self.shared,
            "expenses": [expense.to_dict() for expense in self.expenses]
        }
        with open(self.save_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_expenses(self) -> None:
        if not self.save_path.exists():
            return
        
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                self.expenses = [Expense.from_dict(exp) for exp in data["expenses"]]
        except json.JSONDecodeError:
            print(f"Warning: Could not load expenses from {self.save_path}")
            self.expenses = []

    def export_to_csv(self, filename: str = "expenses.csv") -> None:
        filepath = self.save_dir / filename
        df = pd.DataFrame([exp.to_dict() for exp in self.expenses])
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
        df.to_csv(filepath, index=False)
        print(f"Expenses exported to {filepath}")

    def get_spending_insights(self, start_date: Optional[datetime] = None, 
                            end_date: Optional[datetime] = None) -> Dict:
        filtered_expenses = self._filter_expenses(start_date, end_date)
        if not filtered_expenses:
            return {
                "total_spending": 0,
                "spending_by_person": {},
                "spending_by_category": {},
                "monthly_trends": {},
                "top_expenses": [],
                "spending_patterns": {}
            }

        df = pd.DataFrame([exp.to_dict() for exp in filtered_expenses])
        df['date'] = pd.to_datetime(df['date'])
        
        # Calculate total spending
        total_spending = df['amount'].sum()
        
        # Spending by person (including shared)
        spending_by_person = df.groupby('paid_by')['amount'].sum().to_dict()
        
        # Spending by category
        spending_by_category = df.groupby('category')['amount'].sum().to_dict()
        
        # Monthly trends
        monthly_trends = df.set_index('date').resample('M')['amount'].sum().to_dict()
        
        # Top 5 largest expenses
        top_expenses = df.nlargest(5, 'amount')[['description', 'amount', 'category', 'date']].to_dict('records')
        
        # Spending patterns
        spending_patterns = {
            "average_monthly_spend": df.groupby(df['date'].dt.strftime('%Y-%m'))['amount'].sum().mean(),
            "most_expensive_category": max(spending_by_category.items(), key=lambda x: x[1]),
            "highest_spending_month": max(monthly_trends.items(), key=lambda x: x[1]),
            "spending_by_day_of_week": df.groupby(df['date'].dt.day_name())['amount'].sum().to_dict(),
            "spending_by_category_percentage": {
                category: (amount / total_spending) * 100 
                for category, amount in spending_by_category.items()
            }
        }

        return {
            "total_spending": total_spending,
            "spending_by_person": spending_by_person,
            "spending_by_category": spending_by_category,
            "monthly_trends": {k.strftime('%Y-%m'): v for k, v in monthly_trends.items()},
            "top_expenses": top_expenses,
            "spending_patterns": spending_patterns
        }

    def _filter_expenses(self, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[Expense]:
        if not (start_date or end_date):
            return self.expenses
        
        return [
            exp for exp in self.expenses
            if (not start_date or exp.date >= start_date) and
               (not end_date or exp.date <= end_date)
        ] 