# expense_tracker.py
"""
Advanced Expense Tracker (CLI)
Features:
- Add expense (amount, category, date, note)
- View all expenses, filter by category/date range
- Totals and summary by category/date range
- Edit and delete expenses
- Save/load from JSON (auto-save after each write)
- Simple search and CSV export
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

DATA_FILE = Path("expenses.json")


def parse_date(text: str) -> datetime:
    text = text.strip()
    if not text or text.lower() in ("today", "t"):
        return datetime.today()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    # last resort: try iso parse
    try:
        return datetime.fromisoformat(text)
    except Exception:
        raise ValueError("Date format not recognized. Use YYYY-MM-DD or DD-MM-YYYY or leave empty for today.")


class ExpenseTracker:
    def __init__(self, path: Path = DATA_FILE):
        self.path = path
        self.expenses = []
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.expenses = json.load(f)
                # ensure proper types
                for e in self.expenses:
                    e["amount"] = float(e["amount"])
                    e["date"] = e["date"]  # stored as string
            except Exception as exc:
                print("Warning: could not load file:", exc)
                self.expenses = []
        else:
            self.expenses = []

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, indent=2, ensure_ascii=False)

    def _next_id(self) -> int:
        if not self.expenses:
            return 1
        return max(int(e["id"]) for e in self.expenses) + 1

    def add_expense(self, amount: float, category: str, date: datetime, note: str = "") -> Dict:
        expense = {
            "id": str(self._next_id()),
            "amount": float(amount),
            "category": category.strip(),
            "date": date.strftime("%Y-%m-%d"),
            "note": note.strip()
        }
        self.expenses.append(expense)
        self._save()
        return expense

    def list_expenses(self, limit: Optional[int] = None) -> List[Dict]:
        sorted_list = sorted(self.expenses, key=lambda x: x["date"], reverse=True)
        return sorted_list[:limit] if limit else sorted_list

    def find_by_id(self, id_str: str) -> Optional[Dict]:
        for e in self.expenses:
            if e["id"] == id_str:
                return e
        return None

    def delete_expense(self, id_str: str) -> bool:
        e = self.find_by_id(id_str)
        if not e:
            return False
        self.expenses.remove(e)
        self._save()
        return True

    def edit_expense(self, id_str: str, amount: Optional[float] = None,
                     category: Optional[str] = None, date: Optional[datetime] = None,
                     note: Optional[str] = None) -> bool:
        e = self.find_by_id(id_str)
        if not e:
            return False
        if amount is not None:
            e["amount"] = float(amount)
        if category is not None:
            e["category"] = category
        if date is not None:
            e["date"] = date.strftime("%Y-%m-%d")
        if note is not None:
            e["note"] = note
        self._save()
        return True

    def filter_expenses(self, category: Optional[str] = None, start: Optional[datetime] = None,
                        end: Optional[datetime] = None) -> List[Dict]:
        res = []
        for e in self.expenses:
            ed = datetime.strptime(e["date"], "%Y-%m-%d")
            if category and e["category"].lower() != category.lower():
                continue
            if start and ed < start:
                continue
            if end and ed > end:
                continue
            res.append(e)
        return sorted(res, key=lambda x: x["date"], reverse=True)

    def total(self, category: Optional[str] = None, start: Optional[datetime] = None,
              end: Optional[datetime] = None) -> float:
        selected = self.filter_expenses(category, start, end)
        return sum(float(e["amount"]) for e in selected)

    def summary_by_category(self, start: Optional[datetime] = None, end: Optional[datetime] = None) -> Dict[str, float]:
        selected = self.filter_expenses(None, start, end)
        summary = {}
        for e in selected:
            summary[e["category"]] = summary.get(e["category"], 0.0) + float(e["amount"])
        return summary

    def search(self, term: str) -> List[Dict]:
        t = term.lower()
        return [e for e in self.expenses if t in e.get("note", "").lower() or t in e.get("category", "").lower()]

    def export_csv(self, filename: str = "expenses_export.csv"):
        keys = ["id", "date", "category", "amount", "note"]
        with open(filename, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            for e in self.list_expenses():
                writer.writerow({k: e.get(k, "") for k in keys})
        return filename

    def import_from_json(self, filename: str):
        p = Path(filename)
        if not p.exists():
            raise FileNotFoundError(filename)
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        # append with new ids
        for e in data:
            try:
                self.add_expense(float(e["amount"]), e.get("category", "uncategorized"),
                                 parse_date(e.get("date", "")), e.get("note", ""))
            except Exception:
                continue


def pretty_print_list(expenses: List[Dict]):
    if not expenses:
        print("No expenses found.")
        return
    print(f"{'ID':<4} {'DATE':<12} {'CATEGORY':<15} {'AMOUNT':>8}  NOTE")
    print("-" * 60)
    for e in expenses:
        print(f"{e['id']:<4} {e['date']:<12} {e['category']:<15} {float(e['amount']):>8.2f}  {e.get('note','')}")


def cli():
    t = ExpenseTracker()
    print("Welcome — Advanced Expense Tracker")
    while True:
        print("\nChoose an option:")
        print("1) Add expense")
        print("2) View expenses (all)")
        print("3) View by category")
        print("4) View by date range")
        print("5) Total / Summary")
        print("6) Edit expense")
        print("7) Delete expense")
        print("8) Search notes/category")
        print("9) Export CSV")
        print("10) Import JSON file")
        print("0) Quit")
        choice = input("Enter number: ").strip()

        if choice == "1":
            try:
                amt = float(input("Amount (e.g. 250.50): ").strip())
                cat = input("Category (food, transport, bills, etc): ").strip() or "uncategorized"
                date_in = input("Date (YYYY-MM-DD) [leave empty = today]: ").strip()
                d = parse_date(date_in)
                note = input("Note (optional): ").strip()
                e = t.add_expense(amt, cat, d, note)
                print("Added:", e)
            except Exception as exc:
                print("Error:", exc)

        elif choice == "2":
            pretty_print_list(t.list_expenses())

        elif choice == "3":
            cat = input("Category: ").strip()
            pretty_print_list(t.filter_expenses(category=cat))

        elif choice == "4":
            start = input("Start date (YYYY-MM-DD) [empty = no start]: ").strip()
            end = input("End date (YYYY-MM-DD) [empty = no end]: ").strip()
            try:
                s = parse_date(start) if start else None
                e = parse_date(end) if end else None
                pretty_print_list(t.filter_expenses(start=s, end=e))
            except Exception as exc:
                print("Error:", exc)

        elif choice == "5":
            start = input("Start date (YYYY-MM-DD) [empty = no start]: ").strip()
            end = input("End date (YYYY-MM-DD) [empty = no end]: ").strip()
            try:
                s = parse_date(start) if start else None
                e = parse_date(end) if end else None
                total_all = t.total(None, s, e)
                print(f"Total: {total_all:.2f}")
                print("\nSummary by category:")
                for cat, amount in t.summary_by_category(s, e).items():
                    print(f"  {cat}: {amount:.2f}")
            except Exception as exc:
                print("Error:", exc)

        elif choice == "6":
            id_str = input("Expense ID to edit: ").strip()
            e = t.find_by_id(id_str)
            if not e:
                print("Not found.")
                continue
            print("Current:", e)
            new_amt = input(f"Amount [{e['amount']}]: ").strip()
            new_cat = input(f"Category [{e['category']}]: ").strip()
            new_date = input(f"Date [{e['date']}]: ").strip()
            new_note = input(f"Note [{e.get('note','')}]: ").strip()
            try:
                amt_val = float(new_amt) if new_amt else None
                date_val = parse_date(new_date) if new_date else None
                ok = t.edit_expense(id_str, amount=amt_val, category=new_cat or None, date=date_val, note=new_note or None)
                print("Updated." if ok else "Failed to update.")
            except Exception as exc:
                print("Error:", exc)

        elif choice == "7":
            id_str = input("Expense ID to delete: ").strip()
            ok = t.delete_expense(id_str)
            print("Deleted." if ok else "Not found.")

        elif choice == "8":
            term = input("Search term: ").strip()
            pretty_print_list(t.search(term))

        elif choice == "9":
            fn = input("File name (default expenses_export.csv): ").strip() or "expenses_export.csv"
            out = t.export_csv(fn)
            print("Exported to", out)

        elif choice == "10":
            fn = input("Path to JSON file to import: ").strip()
            try:
                t.import_from_json(fn)
                print("Imported.")
            except Exception as exc:
                print("Import error:", exc)

        elif choice == "0":
            print("Bye — data saved.")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    cli()