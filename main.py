from db import fetch_all, fetch_one, execute_query
import datetime
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# CORE LOGIC FUNCTIONS
def core_add_expense(date, amount, category_id, description):
    query = """
        INSERT INTO expenses (date, amount, category_id, description, updated_at)
        VALUES (%s, %s, %s, %s, NOW())
    """
    return execute_query(query, (date, amount, category_id, description))


def core_get_categories():
    return fetch_all("SELECT id, name FROM categories ORDER BY name")


def core_add_category(name):
    existing = fetch_one("SELECT id FROM categories WHERE name = %s", (name,))
    if existing:
        return "exists"

    result = execute_query(
        "INSERT INTO categories (name, created_at) VALUES (%s, NOW())",
        (name,)
    )
    return "ok" if result else "error"


def core_view_expenses():
    return fetch_all("""
        SELECT e.id, e.date, e.amount, c.name, e.description
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        ORDER BY e.date DESC """)


def core_update_expense(expense_id, amount, description, date=None, category_id=None):
    """
    Extended version: if date and category_id are provided, update them too.
    If not, only amount & description are updated.
    """
    if date is not None and category_id is not None:
        return execute_query("""
            UPDATE expenses
            SET date = %s, amount = %s, category_id = %s, description = %s, updated_at = NOW()
            WHERE id = %s
        """, (date, amount, category_id, description, expense_id))

    else:
        return execute_query("""
            UPDATE expenses
            SET amount = %s, description = %s, updated_at = NOW()
            WHERE id = %s
        """, (amount, description, expense_id))



def core_delete_expense(expense_id):
    return execute_query("DELETE FROM expenses WHERE id = %s", (expense_id,))


def core_monthly_summary(year, month):
    return fetch_all("""
        SELECT c.name, SUM(e.amount)
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE YEAR(e.date) = %s AND MONTH(e.date) = %s
        GROUP BY c.name
    """, (year, month))


def core_set_budget(month, category_id, amount):
    # month is string 'YYYY-MM'
    return execute_query("""
        INSERT INTO budgets (month, category_id, amount)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE amount = VALUES(amount)
    """, (month, category_id, amount))


# CLI FUNCTIONS 
def cli_add_expense():
    print("\n--- Add Expense ---")

    date_str = input("Enter date (YYYY-MM-DD): ")
    try:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format.")
        return
    try:
        amount = float(input("Amount: "))
    except ValueError:
        print("Invalid amount.")
        return

    while True:
        categories = core_get_categories()
        if not categories:
            print("No categories found. You must add a category first.")
            new_cat_name = input("Enter new category name: ").strip()
            if not new_cat_name:
                print("Category name cannot be empty.")
                return
            status = core_add_category(new_cat_name)
            if status == "exists":
                print("Category already exists")
            elif status == "ok":
                print(f"Category '{new_cat_name}' added.")
            else:
                print("Error adding category.")
            continue
        else:
            break

    print("\nCategories:")
    for c in categories:
        print(f"{c[0]}. {c[1]}")
    print("0. Add new category")

    try:
        category_id = int(input("Choose category ID: "))
    except ValueError:
        print("Invalid category.")
        return

    description = input("Description: ")

    if core_add_expense(date, amount, category_id, description):
        print("Expense added successfully!")
    else:
        print("Error adding expense.")


def cli_view_expenses():
    print("\n--- All Expenses ---")
    rows = core_view_expenses()

    for r in rows:
        print(f"ID: {r[0]} | Date: {r[1]} | Amount: {r[2]} | Category: {r[3]} | {r[4]}")


def cli_update_expense():
    print("\n--- Update Expense ---")
    try:
        expense_id = int(input("Enter expense ID to update: "))
        amount = float(input("New amount: "))
    except ValueError:
        print("Invalid input.")
        return

    description = input("New description: ")

    if core_update_expense(expense_id, amount, description):
        print("Expense updated!")
    else:
        print("Update failed.")


def cli_delete_expense():
    print("\n--- Delete Expense ---")
    try:
        expense_id = int(input("Expense ID to delete: "))
    except ValueError:
        print("Invalid input.")
        return

    if core_delete_expense(expense_id):
        print("Expense deleted.")
    else:
        print("Error deleting expense.")


def cli_monthly_summary():
    print("\n--- Monthly Summary ---")
    try:
        year = int(input("Year (YYYY): "))
        month = int(input("Month (1-12): "))
    except ValueError:
        print("Invalid input.")
        return

    rows = core_monthly_summary(year, month)

    print("\nCategory | Total Spent")
    print("------------------------")
    for r in rows:
        print(f"{r[0]} | {r[1]}")


def cli_set_budget():
    print("\n--- Set Monthly Budget ---")

    month = input("Month (YYYY-MM): ")

    categories = core_get_categories()
    if not categories:
        print("No categories found.")
        return

    print("\nCategories:")
    for c in categories:
        print(f"{c[0]}. {c[1]}")

    try:
        category_id = int(input("Category ID: "))
        amount = float(input("Budget Amount: "))
    except ValueError:
        print("Invalid input.")
        return

    valid_category_ids = [c[0] for c in categories]
    if category_id not in valid_category_ids:
        print(f"Error: Category ID {category_id} does not exist.")
        return

    if core_set_budget(month, category_id, amount):
        print("Budget set successfully!")
    else:
        print("Failed to set budget.")


def cli_exit():
    print("Exiting...")
    sys.exit()


def cli_main_menu():
    while True:
        print("\n====== Expense Tracker CLI ======")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Update Expense")
        print("4. Delete Expense")
        print("5. Monthly Summary")
        print("6. Set Budget")
        print("7. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            cli_add_expense()
        elif choice == "2":
            cli_view_expenses()
        elif choice == "3":
            cli_update_expense()
        elif choice == "4":
            cli_delete_expense()
        elif choice == "5":
            cli_monthly_summary()
        elif choice == "6":
            cli_set_budget()
        elif choice == "7":
            cli_exit()
        else:
            print("Invalid option Try again.")


# GUI 

class ExpenseTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("1050x600")

        # category name -> id
        self.category_map = {}

        # Default month filter: current month in 'YYYY-MM'
        today = datetime.date.today()
        self.current_month_str = today.strftime("%Y-%m")

        self.remaining_amount = 0.0 

        # Root grid
        self.rowconfigure(0, weight=0)  # title
        self.rowconfigure(1, weight=0)  # remaining budget
        self.rowconfigure(2, weight=1)  # main content
        self.columnconfigure(0, weight=1)

        # ====== ROW 0: HEADING ======
        self.title_label = tk.Label(
            self,
            text="Expense Tracker",
            font=("Helvetica", 20, "bold")
        )
        self.title_label.grid(row=0, column=0, pady=(10, 0), sticky="n")

        # ====== ROW 1: REMAINING BUDGET ======
        self.remaining_budget_var = tk.StringVar(value="Remaining Budget: ₹0.00")
        self.remaining_label = tk.Label(
            self,
            textvariable=self.remaining_budget_var,
            font=("Helvetica", 14),
            fg="green"
        )
        self.remaining_label.grid(row=1, column=0, pady=(5, 5), sticky="n")

        # MAIN CONTENT (LEFT + RIGHT) 
        main_frame = tk.Frame(self, borderwidth=0)
        main_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # left
        main_frame.columnconfigure(1, weight=2)  # right

        # ---------- LEFT PANEL ----------
        left_panel = tk.Frame(main_frame, borderwidth=1, relief="groove")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)

        left_panel.rowconfigure(0, weight=0)
        left_panel.rowconfigure(1, weight=0)
        left_panel.rowconfigure(2, weight=0)
        left_panel.rowconfigure(3, weight=1)
        left_panel.columnconfigure(0, weight=1)

        expense_form_label = tk.Label(
            left_panel,
            text="Add / Update Expense",
            font=("Helvetica", 12, "bold")
        )
        expense_form_label.grid(row=0, column=0, pady=5, sticky="w")

        # Form frame
        form_frame = tk.Frame(left_panel)
        form_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        form_frame.columnconfigure(0, weight=0)
        form_frame.columnconfigure(1, weight=1)

        # Amount
        tk.Label(form_frame, text="Amount:").grid(row=0, column=0, sticky="w", pady=2)
        self.amount_entry = tk.Entry(form_frame)
        self.amount_entry.grid(row=0, column=1, sticky="ew", pady=2)

        # Category Combobox (user can type new)
        tk.Label(form_frame, text="Category:").grid(row=1, column=0, sticky="w", pady=2)
        self.category_combo = ttk.Combobox(form_frame, state="normal")
        self.category_combo.grid(row=1, column=1, sticky="ew", pady=2)

        # Date
        tk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", pady=2)
        self.date_entry = tk.Entry(form_frame)
        self.date_entry.grid(row=2, column=1, sticky="ew", pady=2)
        self.date_entry.insert(0, today.strftime("%Y-%m-%d"))

        # Description
        tk.Label(form_frame, text="Description:").grid(row=3, column=0, sticky="w", pady=2)
        self.description_entry = tk.Entry(form_frame)
        self.description_entry.grid(row=3, column=1, sticky="ew", pady=2)

        # Buttons
        btn_frame = tk.Frame(left_panel)
        btn_frame.grid(row=2, column=0, pady=10, sticky="ew")
        for i in range(3):
            btn_frame.columnconfigure(i, weight=1)

        add_btn = tk.Button(btn_frame, text="Add Expense", command=self.on_add_expense)
        add_btn.grid(row=0, column=0, padx=5, sticky="ew")

        update_btn = tk.Button(btn_frame, text="Update Selected", command=self.on_update_expense)
        update_btn.grid(row=0, column=1, padx=5, sticky="ew")

        delete_btn = tk.Button(btn_frame, text="Delete Selected", command=self.on_delete_expense)
        delete_btn.grid(row=0, column=2, padx=5, sticky="ew")

        # Filters + Budget
        filter_frame = tk.LabelFrame(left_panel, text="Filters, Summary & Budget")
        filter_frame.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="nsew")
        filter_frame.columnconfigure(0, weight=0)
        filter_frame.columnconfigure(1, weight=1)

        tk.Label(filter_frame, text="Month (YYYY-MM):").grid(row=0, column=0, sticky="w", pady=2)
        self.month_entry = tk.Entry(filter_frame, width=10)
        self.month_entry.grid(row=0, column=1, sticky="w", pady=2)
        self.month_entry.insert(0, self.current_month_str)

        tk.Label(filter_frame, text="Monthly Budget (₹, all categories):").grid(row=1, column=0, sticky="w", pady=2)
        self.budget_entry = tk.Entry(filter_frame, width=10)
        self.budget_entry.grid(row=1, column=1, sticky="w", pady=2)

        filter_btn = tk.Button(filter_frame, text="Filter by Month", command=self.on_filter_month)
        filter_btn.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 2))

        summary_btn = tk.Button(filter_frame, text="Show Monthly Summary", command=self.on_show_summary)
        summary_btn.grid(row=3, column=0, columnspan=2, sticky="ew", pady=2)

        set_budget_btn = tk.Button(filter_frame, text="Save Budget for Month", command=self.on_set_budget)
        set_budget_btn.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(2, 8))

        #  RIGHT PANEL
        right_panel = tk.Frame(main_frame, borderwidth=1, relief="groove")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=0)

        right_panel.rowconfigure(0, weight=0)
        right_panel.rowconfigure(1, weight=1)
        right_panel.rowconfigure(2, weight=0)
        right_panel.columnconfigure(0, weight=1)
        right_panel.columnconfigure(1, weight=0)

        table_label = tk.Label(right_panel, text="Expenses", font=("Helvetica", 12, "bold"))
        table_label.grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

        columns = ("date", "amount", "category", "description")
        self.expense_tree = ttk.Treeview(
            right_panel,
            columns=columns,
            show="headings"
        )
        self.expense_tree.heading("date", text="Date")
        self.expense_tree.heading("amount", text="Amount")
        self.expense_tree.heading("category", text="Category")
        self.expense_tree.heading("description", text="Description")

        self.expense_tree.column("date", width=100, anchor="w")
        self.expense_tree.column("amount", width=80, anchor="e")
        self.expense_tree.column("category", width=120, anchor="w")
        self.expense_tree.column("description", width=280, anchor="w")

        self.expense_tree.grid(row=1, column=0, sticky="nsew", padx=(5, 0), pady=5)

        scrollbar = ttk.Scrollbar(
            right_panel,
            orient="vertical",
            command=self.expense_tree.yview
        )
        scrollbar.grid(row=1, column=1, sticky="ns", pady=5)
        self.expense_tree.configure(yscrollcommand=scrollbar.set)

        bottom_frame = tk.Frame(right_panel)
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=0)

        self.monthly_total_var = tk.StringVar(value="Monthly Total: ₹0.00")
        monthly_total_label = tk.Label(bottom_frame, textvariable=self.monthly_total_var)
        monthly_total_label.grid(row=0, column=0, sticky="w")

        refresh_btn = tk.Button(bottom_frame, text="Refresh All", command=self.on_refresh_all)
        refresh_btn.grid(row=0, column=1, sticky="e")

        # Bind row selection to fill form
        self.expense_tree.bind("<<TreeviewSelect>>", self.on_row_select)

        # Initial data load
        self.load_categories()
        self.load_all_expenses()
        self.update_monthly_total()
        self.recalc_remaining_budget()

    # DB helpers for GUI 

    def reload_category_combo_values(self):
        self.category_combo["values"] = list(self.category_map.keys())

    def load_categories(self):
        rows = core_get_categories()
        self.category_map = {}
        for cat_id, name in rows:
            self.category_map[name] = cat_id
        self.reload_category_combo_values()

    def get_or_create_category_id(self, category_name: str):
        category_name = category_name.strip()
        if not category_name:
            return None

        if category_name in self.category_map:
            return self.category_map[category_name]

        status = core_add_category(category_name)
        if status == "error":
            return None

        # re-load categories
        self.load_categories()
        return self.category_map.get(category_name)

    def load_all_expenses(self):
        self.expense_tree.delete(*self.expense_tree.get_children())
        rows = core_view_expenses()
        for exp_id, dt, amount, cat_name, desc in rows:
            self.expense_tree.insert(
                "", "end", iid=str(exp_id),
                values=(dt, f"{float(amount):.2f}", cat_name, desc or "")
            )

    def load_expenses_for_month(self, month_str: str):
        self.expense_tree.delete(*self.expense_tree.get_children())
        rows = fetch_all(
            """
            SELECT e.id, e.date, e.amount, c.name, e.description
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE DATE_FORMAT(e.date, '%%Y-%%m') = %s
            ORDER BY e.date DESC
            """,
            (month_str,)
        )
        for exp_id, dt, amount, cat_name, desc in rows:
            self.expense_tree.insert(
                "", "end", iid=str(exp_id),
                values=(dt, f"{float(amount):.2f}", cat_name, desc or "")
            )

    def get_total_budget_for_month(self, month_str: str) -> float:
        row = fetch_one(
            "SELECT IFNULL(SUM(amount), 0) FROM budgets WHERE month = %s",
            (month_str,)
        )
        if row:
            return float(row[0])
        return 0.0

    def get_total_expenses_for_month(self, month_str: str) -> float:
        month_str = month_str.strip()
        
        row = fetch_one(
            "SELECT IFNULL(SUM(amount), 0) FROM expenses "
            "WHERE DATE_FORMAT(date, '%%Y-%%m') = %s",
            (month_str,)
        )
        if row:
            return float(row[0])
        return 0.0

    # Event handlers

    def clear_form(self):
        self.amount_entry.delete(0, tk.END)
        self.category_combo.set("")
        # keep date as is
        self.description_entry.delete(0, tk.END)

    def recalc_remaining_budget(self):
        total_budget = self.get_total_budget_for_month(self.current_month_str)
        total_expenses = self.get_total_expenses_for_month(self.current_month_str)
        self.remaining_amount = total_budget - total_expenses
        self.update_remaining_budget()
  

    def on_add_expense(self):
        amount_text = self.amount_entry.get().strip()
        category_name = self.category_combo.get().strip()
        date_text = self.date_entry.get().strip()
        description = self.description_entry.get().strip()

        if not amount_text or not category_name or not date_text:
            messagebox.showerror("Error", "Amount, Category and Date are required.")
            return

        try:
            amount = float(amount_text)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.")
            return

        # validate date
        try:
            _ = datetime.datetime.strptime(date_text, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format.")
            return

        cat_id = self.get_or_create_category_id(category_name)
        if cat_id is None:
            messagebox.showerror("Error", "Could not create/find category.")
            return

        if core_add_expense(date_text, amount, cat_id, description):
            messagebox.showinfo("Success", "Expense added successfully.")
            self.clear_form()
            self.load_all_expenses()
            self.update_monthly_total()

            expense_month = date_text[:7]
            if expense_month == self.current_month_str:
                self.remaining_amount -= amount

            self.update_remaining_budget()
        else:
            messagebox.showerror("Error", "Failed to add expense.")

    def on_update_expense(self):
        selected = self.expense_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an expense to update.")
            return

        expense_id = int(selected[0])

        old_dt, old_amount, _, _ = self.expense_tree.item(selected[0], "values")
        old_amount = float(old_amount)
        old_month = old_dt[:7]

        amount_text = self.amount_entry.get().strip()
        category_name = self.category_combo.get().strip()
        date_text = self.date_entry.get().strip()
        description = self.description_entry.get().strip()

        if not amount_text or not category_name or not date_text:
            messagebox.showerror("Error", "Amount, Category and Date are required.")
            return

        try:
            amount = float(amount_text)
            datetime.datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.")
            return

        try:
            _ = datetime.datetime.strptime(date_text, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format.")
            return

        cat_id = self.get_or_create_category_id(category_name)
        if cat_id is None:
            messagebox.showerror("Error", "Could not create/find category.")
            return

        if core_update_expense(expense_id, amount, description, date_text, cat_id):
            messagebox.showinfo("Success", "Expense updated successfully.")
            new_month = date_text[:7]
            #budget adjusment 
            if old_month == self.current_month_str:
                self.remaining_amount += old_amount
            if new_month == self.current_month_str:
                self.remaining_amount -= amount

            self.load_all_expenses()
            self.update_monthly_total()
            self.update_remaining_budget()
        else:
            messagebox.showerror("Error", "Failed to update expense.")

    def on_delete_expense(self):
        selected = self.expense_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an expense to delete.")
            return

        if not messagebox.askyesno("Confirm", "Are you sure you want to delete the selected expense(s)?"):
            return

        all_ok = True
        for iid in selected:
            dt, amount, _,_ = self.expense_tree.item(iid,"values")
            amount = float(amount)
            month = dt[:7]

            if month == self.current_month_str:
                self.remaining_amount += amount

            expense_id = int(iid)
            if not core_delete_expense(expense_id):
                all_ok = False

        if all_ok:
            messagebox.showinfo("Success", "Selected expense(s) deleted.")
        else:
            messagebox.showerror("Error", "Some deletes may have failed.")

        self.load_all_expenses()
        self.update_monthly_total()
        self.update_remaining_budget()

    def on_filter_month(self):
        month_str = self.month_entry.get().strip()
        if not month_str:
            messagebox.showerror("Error", "Please enter month in YYYY-MM format.")
            return

        try:
            datetime.datetime.strptime(month_str + "-01", "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid month format. Use YYYY-MM.")
            return

        self.current_month_str = month_str
        self.load_expenses_for_month(month_str)
        self.update_monthly_total()
        self.recalc_remaining_budget()

    def on_show_summary(self):
        # convert month string to year, month
        try:
            dt = datetime.datetime.strptime(self.current_month_str + "-01", "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Current month format is invalid.")
            return

        rows = core_monthly_summary(dt.year, dt.month)
        if not rows:
            messagebox.showinfo(
                "Monthly Summary",
                f"No expenses for {self.current_month_str}."
            )
            return

        lines = [f"Summary for {self.current_month_str}:", "", "Category | Total"]
        lines.append("-" * 25)
        for cat, total in rows:
            lines.append(f"{cat} | ₹{float(total):.2f}")

        messagebox.showinfo("Monthly Summary", "\n".join(lines))

    def on_set_budget(self):
        month_str = self.month_entry.get().strip()
        if not month_str:
            messagebox.showerror("Error", "Please enter month in YYYY-MM format.")
            return

        budget_text = self.budget_entry.get().strip()
        if not budget_text:
            messagebox.showerror("Error", "Please enter a budget amount.")
            return

        try:
            budget_amount = float(budget_text)
        except ValueError:
            messagebox.showerror("Error", "Budget amount must be a number.")
            return
        
        self.current_month_str = month_str
        self.recalc_remaining_budget()

        # messagebox.showinfo("Success", "Monthly budget set for this month.")

        categories = core_get_categories()
        if not categories:
            messagebox.showerror("Error", "No categories found. Add a category first.")
            return

        share = budget_amount / len(categories)
        all_ok = True
        for cat_id, _name in categories:
            if not core_set_budget(month_str, cat_id, share):
                all_ok = False

        if all_ok:
            messagebox.showinfo("Success", "Budget saved (divided equally across categories).")
            self.current_month_str = month_str
            self.update_remaining_budget()
        else:
            messagebox.showerror("Error", "Failed to save budget.")

    def on_refresh_all(self):
        # Reset month entry to current
        self.month_entry.delete(0, tk.END)
        self.month_entry.insert(0, self.current_month_str)

        self.load_all_expenses()
        self.update_monthly_total()
        self.recalc_remaining_budget()

    def on_row_select(self, event):
        selected = self.expense_tree.selection()
        if not selected:
            return
        iid = selected[0]
        dt, amount, category, desc = self.expense_tree.item(iid, "values")

        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, dt)

        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, amount)

        self.category_combo.set(category)

        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, desc)

    # Summary / budget display 

    def update_monthly_total(self):
        total = self.get_total_expenses_for_month(self.current_month_str)
        self.monthly_total_var.set(f"Monthly Total ({self.current_month_str}): ₹{total:.2f}")

    def update_remaining_budget(self):
        remaining = self.remaining_amount
        self.remaining_budget_var.set(
            f"Remaining Budget ({self.current_month_str}): ₹{remaining:.2f}"
        )
        self.remaining_label.config(fg="red" if remaining < 0 else "green")


if __name__ == "__main__":
    app = ExpenseTrackerApp()
    app.mainloop()

    # cli_main_menu()
