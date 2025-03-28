from .expense_tracker import ExpenseTracker
from .models import Category

def print_spending_insights(insights: dict, tracker: ExpenseTracker) -> None:
    print("\nSpending Insights")
    print("=" * 50)
    
    # Total Spending
    print(f"\nTotal Spending: ${insights['total_spending']:.2f}")
    
    # Spending by Person
    print("\nSpending by Person:")
    print("-" * 30)
    for person, amount in insights['spending_by_person'].items():
        print(f"{person}: ${amount:.2f}")
    
    # Spending by Category
    print("\nSpending by Category:")
    print("-" * 30)
    for category, amount in insights['spending_by_category'].items():
        percentage = insights['spending_patterns']['spending_by_category_percentage'][category]
        print(f"{category}: ${amount:.2f} ({percentage:.1f}%)")
    
    # Monthly Trends
    print("\nMonthly Spending Trends:")
    print("-" * 30)
    for month, amount in insights['monthly_trends'].items():
        print(f"{month}: ${amount:.2f}")
    
    # Top Expenses
    print("\nTop 5 Largest Expenses:")
    print("-" * 30)
    for expense in insights['top_expenses']:
        print(f"${expense['amount']:.2f} - {expense['description']} ({expense['category']})")
    
    # Spending Patterns
    patterns = insights['spending_patterns']
    print("\nSpending Patterns:")
    print("-" * 30)
    print(f"Average Monthly Spend: ${patterns['average_monthly_spend']:.2f}")
    
    highest_month, amount = patterns['highest_spending_month']
    print(f"Highest Spending Month: {highest_month.strftime('%Y-%m')} (${amount:.2f})")
    
    most_expensive_category, amount = patterns['most_expensive_category']
    print(f"Most Expensive Category: {most_expensive_category} (${amount:.2f})")
    
    print("\nSpending by Day of Week:")
    for day, amount in patterns['spending_by_day_of_week'].items():
        print(f"{day}: ${amount:.2f}")

def main():
    # Create an expense tracker for Alice and Bob
    tracker = ExpenseTracker("Alice", "Bob")
    
    # Add some sample expenses
    tracker.add_expense(
        "Weekly groceries",
        120.50,
        "Alice",
        Category.GROCERIES
    )
    tracker.add_expense(
        "Electric bill",
        200.00,
        "Bob",
        Category.UTILITIES
    )
    tracker.add_expense(
        "Movie night",
        30.00,
        "Alice",
        Category.ENTERTAINMENT
    )
    tracker.add_expense(
        "Monthly rent",
        2500.00,
        "Bob",
        Category.RENT
    )
    tracker.add_expense(
        "Dinner at restaurant",
        85.00,
        "Alice",
        Category.DINING
    )
    
    # Add some shared expenses
    tracker.add_expense(
        "Vacation fund",
        500.00,
        "Shared",
        Category.OTHER
    )
    tracker.add_expense(
        "Home improvement",
        1000.00,
        "Shared",
        Category.OTHER
    )
    
    # Get and print spending insights
    insights = tracker.get_spending_insights()
    print_spending_insights(insights, tracker)
    
    # Export to CSV
    tracker.export_to_csv()

if __name__ == "__main__":
    main() 