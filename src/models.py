from datetime import datetime
from typing import List, Dict
from enum import Enum
from dataclasses import dataclass

class Category(Enum):
    GROCERIES = "Groceries"
    UTILITIES = "Utilities"
    RENT = "Rent"
    ENTERTAINMENT = "Entertainment"
    DINING = "Dining"
    TRANSPORT = "Transport"
    SHARED = "Shared"  # For expenses that are shared between both people
    SHOPPING = "Shopping"  # For shopping expenses
    OTHER = "Other"

    @classmethod
    def list_categories(cls) -> List[str]:
        return [category.value for category in cls]

@dataclass
class Expense:
    description: str
    amount: float
    paid_by: str
    category: Category
    date: datetime

    def to_dict(self) -> Dict:
        return {
            "description": self.description,
            "amount": self.amount,
            "paid_by": self.paid_by,
            "category": self.category.value,
            "date": self.date.strftime("%Y-%m-%d")  # Format date as YYYY-MM-DD
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Expense':
        # Handle both ISO format and YYYY-MM-DD format
        date_str = data["date"]
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            # Try parsing ISO format by taking just the date part
            date = datetime.fromisoformat(date_str).replace(hour=0, minute=0, second=0, microsecond=0)
        
        return cls(
            description=data["description"],
            amount=data["amount"],
            paid_by=data["paid_by"],
            category=Category(data["category"]),
            date=date
        ) 