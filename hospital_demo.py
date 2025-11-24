import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import sqlite3
from datetime import datetime

# ------------------------------
# Helper Functions
# ------------------------------

def password_strength(pw: str) -> str:
    """Very simple password strength checker."""
    length_ok = len(pw) >= 8
    has_digit = any(c.isdigit() for c in pw)
    has_special = any(c in string.punctuation for c in pw)

    score = sum([length_ok, has_digit, has_special])
    if score == 3:
        return "Strong"
    elif score == 2:
        return "Medium"
    else:
        return "Weak"


# ------------------------------
# TAB 1: Login Security (Password Policy + MFA)
# ------------------------------

class LoginSecurityTab:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg="#e3f2fd")  # Light blue background

        # Title
        title = tk.Label(self.frame, text="Secure Login (Password Policy + MFA)",
                         font=("Arial", 14, "bold"), bg="#e3f2fd", fg="#0d47a1")
        title.grid(row=0, column=0, columnspan=3, pady=15)

        # Username
        tk.Label(self.frame, text="Username:", bg="#e3f2fd", fg="#0d47a1").grid(
            row=1, column=0, sticky="e", padx=10, pady=10)
        self.username_entry = tk.Entry(self.frame, width=30)
        self.username_entry.grid(row=1, column=1, padx=10, pady=10)

        # Password
        tk.Label(self.frame, text="Password:", bg="#e3f2fd", fg="#0d47a1").grid(
            row=2, column=0, sticky="e", padx=10, pady=10)
        self.password_entry = tk.Entry(self.frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, padx=10, pady=10)

        # Strength label
        self.strength_label = tk.Label(self.frame, text="Strength: -",
                                       bg="#e3f2fd", fg="black",
                                       font=("Arial", 10, "bold"))
        self.strength_label.grid(row=2, column=2, padx=10)

        self.password_entry.bind("<KeyRelease>", self.update_strength)

        # MFA Section
        tk.Label(self.frame, text="MFA Code:", bg="#e3f2fd", fg="#0d47a1").grid(
            row=3, column=0, sticky="e", padx=10, pady=10)
        self.mfa_entry = tk.Entry(self.frame, width=15)
        self.mfa_entry.grid(row=3, column=1, sticky="w", padx=10, pady=10)

        self.generated_code = None

        generate_btn = tk.Button(self.frame, text="Generate MFA",
                                 bg="#42a5f5", fg="white",
                                 command=self.generate_mfa)
        generate_btn.grid(row=3, column=2, padx=10, pady=10)

        # Login button
        login_btn = tk.Button(self.frame, text="Login",
                              bg="#1e88e5", fg="white",
                              command=self.login_demo)
        login_btn.grid(row=4, column=0, columnspan=3, pady=20)

        # Instructions
        info = tk.Label(self.frame,
                        text="Type different passwords to test strength.\n"
                             "- Weak password = blocked\n"
                             "- Strong password + MFA = success window opens",
                        bg="#e3f2fd", fg="#0d47a1", justify="left")
        info.grid(row=5, column=0, columnspan=3, pady=10)

    # ---------------------------
    # Update Strength Function
    # ---------------------------
    def update_strength(self, event=None):
        pw = self.password_entry.get()
        level = password_strength(pw)

        if level == "Weak":
            color = "#e53935"  # red
        elif level == "Medium":
            color = "#fb8c00"  # orange
        else:
            color = "#43a047"  # green

        self.strength_label.config(text=f"Strength: {level}", fg=color)

    # ---------------------------
    # MFA Code Generator
    # ---------------------------
    def generate_mfa(self):
        self.generated_code = "".join(random.choices(string.digits, k=6))
        messagebox.showinfo("MFA Code", f"Your MFA code is: {self.generated_code}")

    # ---------------------------
    # Login Attempt Handler
    # ---------------------------
    def login_demo(self):
        username = self.username_entry.get()
        pw = self.password_entry.get()
        mfa_code = self.mfa_entry.get()
        level = password_strength(pw)

        # Weak password blocked
        if level == "Weak":
            messagebox.showwarning("Weak Password",
                                   "This password does not meet the hospital's security policy.\n"
                                   "Please use a STRONG password.")
            return

        # No MFA code
        if not self.generated_code:
            messagebox.showwarning("Missing MFA",
                                   "Please generate an MFA code before logging in.")
            return

        if mfa_code != self.generated_code:
            messagebox.showerror("MFA Failed",
                                 "Invalid MFA code.\n"
                                 "Login denied for safety.")
            return

        # If everything correct → open success window
        self.open_success_window(username)

    # ---------------------------
    # Successful Login Window
    # ---------------------------
    def open_success_window(self, username):
        success_win = tk.Toplevel(self.frame)
        success_win.title("Login Successful")
        success_win.geometry("350x220")
        success_win.configure(bg="#e8f5e9")  # Light green success background

        tk.Label(success_win, text="✓ Login Successful",
                 font=("Arial", 16, "bold"),
                 bg="#e8f5e9", fg="#2e7d32").pack(pady=15)

        tk.Label(success_win,
                 text=f"Welcome, {username}!\nYour account passed:\n"
                      "✔ Password Policy\n✔ Multi-Factor Authentication",
                 bg="#e8f5e9", fg="#1b5e20", justify="center",
                 font=("Arial", 12)).pack(pady=10)

        tk.Button(success_win, text="Close",
                  bg="#43a047", fg="white",
                  command=success_win.destroy).pack(pady=15)

# ------------------------------
# TAB 2: Secure Database Access (SQL Injection Demo)
# ------------------------------
class SQLInjectionTab:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg="#e3f2fd")  # Light blue theme

        title = tk.Label(self.frame, text="SQL Injection Protection (Patient DB)",
                         font=("Arial", 14, "bold"), fg="#0d47a1", bg="#e3f2fd")
        title.grid(row=0, column=0, columnspan=3, pady=15)

        desc = tk.Label(self.frame,
                        text="This demo compares a vulnerable query vs a parameterized safe query.\n"
                             "Try entering:   ' OR '1'='1",
                        font=("Arial", 10), fg="#0d47a1", bg="#e3f2fd")
        desc.grid(row=1, column=0, columnspan=3, pady=5)

        # Input field
        tk.Label(self.frame, text="Search patient by name:", fg="#0d47a1", bg="#e3f2fd").grid(
            row=2, column=0, sticky="e", padx=10, pady=10)
        self.search_entry = tk.Entry(self.frame, width=40)
        self.search_entry.grid(row=2, column=1, padx=10, pady=10)

        # Buttons
        unsafe_btn = tk.Button(self.frame, text="Run UNSAFE Search",
                               bg="#e53935", fg="white", width=18,
                               command=self.unsafe_search)
        unsafe_btn.grid(row=3, column=0, pady=10)

        safe_btn = tk.Button(self.frame, text="Run SAFE Search",
                             bg="#43a047", fg="white", width=18,
                             command=self.safe_search)
        safe_btn.grid(row=3, column=1, pady=10)

        # Results box
        self.results_box = tk.Text(self.frame, width=75, height=14,
                                   bg="#ffffff", fg="#0d47a1", font=("Arial", 10))
        self.results_box.grid(row=4, column=0, columnspan=3, pady=10, padx=10)

        # Build DB
        self.conn = sqlite3.connect(":memory:")
        self.setup_db()

    def setup_db(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE patients(id INTEGER PRIMARY KEY, name TEXT, diagnosis TEXT)")
        data = [("Ali", "Flu"), ("Bala", "Diabetes"), ("Cindy", "Hypertension")]
        cur.executemany("INSERT INTO patients(name, diagnosis) VALUES (?, ?)", data)
        self.conn.commit()

    # UNSAFE VERSION (SQL Injection vulnerable)
    def unsafe_search(self):
        name = self.search_entry.get()
        cur = self.conn.cursor()

        query = f"SELECT id, name, diagnosis FROM patients WHERE name = '{name}'"

        self.results_box.delete("1.0", tk.END)
        self.results_box.insert(tk.END, "[ UNSAFE QUERY EXECUTED ]\n", "red")
        self.results_box.insert(tk.END, f"{query}\n\n", "red")

        try:
            rows = cur.execute(query).fetchall()
            if rows:
                for r in rows:
                    self.results_box.insert(tk.END, f"{r}\n")
            else:
                self.results_box.insert(tk.END, "No records found.\n")
        except Exception as e:
            self.results_box.insert(tk.END, f"Error: {e}")

    # SAFE VERSION (Parameterized)
    def safe_search(self):
        name = self.search_entry.get()
        cur = self.conn.cursor()

        query = "SELECT id, name, diagnosis FROM patients WHERE name = ?"

        self.results_box.delete("1.0", tk.END)
        self.results_box.insert(tk.END, "[ SAFE PARAMETERIZED QUERY ]\n", "green")
        self.results_box.insert(tk.END, f"{query}\nParams: ({name})\n\n", "green")

        rows = cur.execute(query, (name,)).fetchall()
        if rows:
            for r in rows:
                self.results_box.insert(tk.END, f"{r}\n")
        else:
            self.results_box.insert(tk.END, "No records found.\n")


# ------------------------------
# TAB 3: Transaction Monitoring & Logging (Billing System)
# ------------------------------
class TransactionMonitoringTab:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg="#e3f2fd")

        title = tk.Label(self.frame, text="Billing System – Fraud Monitoring",
                         font=("Arial", 14, "bold"),
                         fg="#0d47a1", bg="#e3f2fd")
        title.grid(row=0, column=0, columnspan=3, pady=15)

        desc = tk.Label(self.frame,
                        text="Transactions above RM5000 are flagged as suspicious.",
                        font=("Arial", 10),
                        fg="#0d47a1", bg="#e3f2fd")
        desc.grid(row=1, column=0, columnspan=3, pady=5)

        run_btn = tk.Button(self.frame, text="Run Monitoring",
                            bg="#1e88e5", fg="white",
                            command=self.run_monitoring)
        run_btn.grid(row=2, column=0, pady=10)

        self.log_box = tk.Text(self.frame, width=75, height=14,
                               bg="#ffffff", fg="#0d47a1", font=("Arial", 10))
        self.log_box.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        self.sample_data = [
            {"id": 1, "patient": "Ali",   "amount": 120.00},
            {"id": 2, "patient": "Bala",  "amount": 500.00},
            {"id": 3, "patient": "Cindy", "amount": 8700.00},   # suspicious
            {"id": 4, "patient": "David", "amount": 12500.00},  # suspicious
            {"id": 5, "patient": "Emily", "amount": 450.00}
        ]

    def run_monitoring(self):
        threshold = 5000
        self.log_box.delete("1.0", tk.END)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_box.insert(tk.END,
                            f"{now} – Running fraud detection...\n\n")

        for tx in self.sample_data:
            line = f"TX#{tx['id']} | Patient: {tx['patient']} | Amount: RM{tx['amount']:.2f}"

            if tx['amount'] > threshold:
                self.log_box.insert(tk.END, line + "  →  FLAGGED\n", "red")
            else:
                self.log_box.insert(tk.END, line + "  →  OK\n", "green")

        self.log_box.insert(tk.END,
                            "\nFlagged transactions require manual audit.\n")

# ------------------------------
# MAIN APP
# ------------------------------

def main():
    root = tk.Tk()
    root.title("Hospital Security Controls Demo")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    login_tab = LoginSecurityTab(notebook)
    sql_tab = SQLInjectionTab(notebook)
    tx_tab = TransactionMonitoringTab(notebook)

    notebook.add(login_tab.frame, text="Login Security")
    notebook.add(sql_tab.frame, text="SQL Protection")
    notebook.add(tx_tab.frame, text="Billing Monitoring")

    root.mainloop()


if __name__ == "__main__":
    main()
