# utils.py

def category_summary(expenses):
    """
    Returns category-wise total expense
    Time Complexity: O(n)
    """
    summary = {}

    for expense in expenses:
        category = expense["category"]
        amount = expense["amount"]

        if category not in summary:
            summary[category] = 0

        summary[category] += amount

    return summary


def monthly_summary(expenses, month):
    """
    Returns total expense for a given month (YYYY-MM)
    Time Complexity: O(n)
    """
    total = 0

    for expense in expenses:
        if expense["date"].startswith(month):
            total += expense["amount"]

    return total


def sort_by_amount_desc(expenses):
    """
    Sorts expenses by amount (descending)
    Time Complexity: O(n log n)
    """
    return sorted(expenses, key=lambda x: x["amount"], reverse=True)
