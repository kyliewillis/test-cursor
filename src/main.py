import os
from datetime import datetime
from typing import List, Dict
from .expense_tracker import ExpenseTracker, Category
from .visualization import ExpenseVisualizer

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    print("\n=== Expense Tracker ===")
    print("=====================\n")

def print_menu():
    """Print the main menu options."""
    print("1. Add Expense")
    print("2. View All Expenses")
    print("3. Generate Monthly Report")
    print("4. Generate All Monthly Reports")
    print("5. Exit")
    print("\n=====================\n")

def get_valid_amount() -> float:
    """Get a valid amount from the user."""
    while True:
        try:
            amount = float(input("Enter amount: $"))
            if amount <= 0:
                print("Amount must be greater than 0")
                continue
            return amount
        except ValueError:
            print("Please enter a valid number")

def get_valid_date() -> datetime:
    """Get a valid date from the user."""
    while True:
        try:
            date_str = input("Enter date (YYYY-MM-DD): ")
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("Please enter a valid date in YYYY-MM-DD format")

def get_valid_category() -> Category:
    """Get a valid category from the user."""
    print("\nAvailable categories:")
    for i, category in enumerate(Category, 1):
        print(f"{i}. {category.value}")
    
    while True:
        try:
            choice = int(input("\nEnter category number: "))
            if 1 <= choice <= len(Category):
                return list(Category)[choice - 1]
            print("Invalid category number")
        except ValueError:
            print("Please enter a valid number")

def get_valid_person() -> str:
    """Get a valid person from the user."""
    while True:
        person = input("Enter person (Kylie/Jeff): ").strip()
        if person in ["Kylie", "Jeff"]:
            return person
        print("Please enter either 'Kylie' or 'Jeff'")

def add_expense(tracker: ExpenseTracker):
    """Add a new expense."""
    print("\n=== Add New Expense ===\n")
    
    amount = get_valid_amount()
    date = get_valid_date()
    category = get_valid_category()
    person = get_valid_person()
    description = input("Enter description: ").strip()
    
    tracker.add_expense(amount, date, category, person, description)
    print("\nExpense added successfully!")

def view_expenses(tracker: ExpenseTracker):
    """View all expenses."""
    print("\n=== All Expenses ===\n")
    expenses = tracker.get_all_expenses()
    
    if not expenses:
        print("No expenses found.")
        return
    
    for expense in expenses:
        print(f"Date: {expense['date'].strftime('%Y-%m-%d')}")
        print(f"Amount: ${expense['amount']:.2f}")
        print(f"Category: {expense['category']}")
        print(f"Person: {expense['person']}")
        print(f"Description: {expense['description']}")
        print("-" * 30)

def generate_monthly_report(tracker: ExpenseTracker):
    """Generate a report for a specific month."""
    print("\n=== Generate Monthly Report ===\n")
    
    try:
        year = int(input("Enter year (YYYY): "))
        month = int(input("Enter month (1-12): "))
        
        if not (1 <= month <= 12):
            print("Invalid month. Please enter a number between 1 and 12.")
            return
            
        visualizer = ExpenseVisualizer(tracker.get_spending_insights())
        report_path = visualizer.generate_monthly_report(month, year)
        print(f"\nMonthly report generated successfully!")
        print(f"Report saved to: {report_path}")
        
    except ValueError:
        print("Please enter valid numbers for year and month.")

def generate_all_monthly_reports(tracker: ExpenseTracker):
    """Generate reports for all months in the dataset."""
    print("\n=== Generating All Monthly Reports ===\n")
    
    visualizer = ExpenseVisualizer(tracker.get_spending_insights())
    report_paths = visualizer.generate_all_monthly_reports()
    
    print(f"\nGenerated {len(report_paths)} monthly reports:")
    for path in report_paths:
        print(f"- {path}")

def main():
    """Main application loop."""
    # Initialize the expense tracker with Google Sheet URL
    sheet_url = "https://docs.google.com/spreadsheets/d/1rkVBCRISztia33SBiH1UFy8AeXvq9CN0HtwZ9CWZCME/edit?usp=sharing"
    tracker = ExpenseTracker("Kylie", "Jeff", sheet_url)
    
    # Load latest data from Google Sheet
    tracker.load_from_sheets()
    
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            add_expense(tracker)
        elif choice == "2":
            view_expenses(tracker)
        elif choice == "3":
            generate_monthly_report(tracker)
        elif choice == "4":
            generate_all_monthly_reports(tracker)
        elif choice == "5":
            print("\nThank you for using Expense Tracker!")
            break
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 