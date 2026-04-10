import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import get_connection
from theme import BG_COLOR, CARD_COLOR, TEXT_COLOR, MUTED_TEXT
from utils import is_eligible_to_donate, eligibility_text, rare_blood_text


def show_donor_registration(parent):
    for widget in parent.winfo_children():
        widget.destroy()

    parent.configure(bg=BG_COLOR)

    tk.Label(
        parent,
        text="Donor Registration",
        font=("Segoe UI", 22, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(anchor="w", padx=20, pady=20)

    form = tk.Frame(parent, bg=CARD_COLOR, padx=20, pady=20)
    form.pack(fill="x", padx=20, pady=10)

    labels = [
        "Full Name", "Age", "Gender", "Blood Group", "Phone",
        "City", "Area", "Address", "Last Donation Date (YYYY-MM-DD)"
    ]

    entries = {}

    for i, label in enumerate(labels):
        tk.Label(
            form,
            text=label,
            bg=CARD_COLOR,
            fg=MUTED_TEXT,
            font=("Segoe UI", 11, "bold")
        ).grid(row=i, column=0, sticky="w", padx=10, pady=8)

        if label == "Gender":
            widget = ttk.Combobox(form, values=["Male", "Female", "Other"], state="readonly", width=30)
            widget.current(0)
        elif label == "Blood Group":
            widget = ttk.Combobox(form, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], state="readonly", width=30)
            widget.current(0)
        else:
            widget = ttk.Entry(form, width=33)

        widget.grid(row=i, column=1, padx=10, pady=8, sticky="w")
        entries[label] = widget

    available_var = tk.IntVar(value=1)

    tk.Label(form, text="Available", bg=CARD_COLOR, fg=MUTED_TEXT, font=("Segoe UI", 11, "bold")).grid(row=9, column=0, sticky="w", padx=10, pady=8)
    ttk.Checkbutton(form, variable=available_var).grid(row=9, column=1, sticky="w", padx=10, pady=8)

    status_label = tk.Label(form, text="Eligibility Status: ", bg=CARD_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 11, "bold"))
    status_label.grid(row=10, column=0, columnspan=2, sticky="w", padx=10, pady=8)

    rare_label = tk.Label(form, text="Blood Type Category: ", bg=CARD_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 11, "bold"))
    rare_label.grid(row=11, column=0, columnspan=2, sticky="w", padx=10, pady=8)

    def clear_form():
        for widget in entries.values():
            try:
                widget.delete(0, tk.END)
            except:
                widget.set("")
        available_var.set(1)
        status_label.config(text="Eligibility Status: ")
        rare_label.config(text="Blood Type Category: ")

    def preview_status(*args):
        last_donation = entries["Last Donation Date (YYYY-MM-DD)"].get().strip()
        blood_group = entries["Blood Group"].get().strip()

        status_label.config(text=f"Eligibility Status: {eligibility_text(last_donation)}")

        if blood_group:
            rare_label.config(text=f"Blood Type Category: {rare_blood_text(blood_group)}")

    entries["Last Donation Date (YYYY-MM-DD)"].bind("<KeyRelease>", preview_status)
    entries["Blood Group"].bind("<<ComboboxSelected>>", preview_status)

    def save_donor():
        name = entries["Full Name"].get().strip()
        age = entries["Age"].get().strip()
        gender = entries["Gender"].get().strip()
        blood_group = entries["Blood Group"].get().strip()
        phone = entries["Phone"].get().strip()
        city = entries["City"].get().strip()
        area = entries["Area"].get().strip()
        address = entries["Address"].get().strip()
        last_donation = entries["Last Donation Date (YYYY-MM-DD)"].get().strip()
        available = available_var.get()

        if not all([name, age, gender, blood_group, phone, city, area]):
            messagebox.showerror("Error", "Please fill all required fields.")
            return

        # Phone validation
        if not phone.isdigit() or len(phone) != 10:
            messagebox.showerror("Error", "Phone must be 10 digits.")
            return

        try:
            age = int(age)
            if age < 18 or age > 65:
                messagebox.showerror("Error", "Age must be between 18 and 65.")
                return
        except ValueError:
            messagebox.showerror("Error", "Age must be numeric.")
            return

        if last_donation:
            try:
                datetime.strptime(last_donation, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Date must be in YYYY-MM-DD format.")
                return

            if not is_eligible_to_donate(last_donation):
                messagebox.showerror("Error", "Donor is not eligible yet. Minimum 90-day gap is required.")
                return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO donors
                (full_name, age, gender, blood_group, phone, city, area, address, is_available, last_donation_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, age, gender, blood_group, phone, city, area, address, available, last_donation))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Donor registered successfully.")
            clear_form()

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    btn_frame = tk.Frame(parent, bg=BG_COLOR)
    btn_frame.pack(anchor="w", padx=20, pady=15)

    ttk.Button(btn_frame, text="Register Donor", command=save_donor).pack(side="left", padx=10)
    ttk.Button(btn_frame, text="Clear", command=clear_form).pack(side="left", padx=10)
