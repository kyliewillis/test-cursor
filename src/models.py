from datetime import datetime
from typing import List, Dict
from enum import Enum
import json
from dataclasses import dataclass, asdict
from pathlib import Path

class Category(Enum):
    GROCERIES = "Groceries"
    UTILITIES = "Utilities"
    RENT = "Rent"
    ENTERTAINMENT = "Entertainment"
    DINING = "Dining"
    TRANSPORT = "Transport"
    SHOPPING = "Shopping"
    SHARED = "Shared"  # For expenses that are shared between both people
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
            "date": self.date.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Expense':
        return cls(
            description=data["description"],
            amount=data["amount"],
            paid_by=data["paid_by"],
            category=Category(data["category"]),
            date=datetime.fromisoformat(data["date"])
        ) 