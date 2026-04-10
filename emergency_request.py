import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import get_connection
from theme import BG_COLOR, CARD_COLOR, TEXT_COLOR, MUTED_TEXT
from utils import request_priority


def show_emergency_request(parent):
    for widget in parent.winfo_children():
        widget.destroy()

    parent.configure(bg=BG_COLOR)

    tk.Label(
        parent,
        text="Emergency Request Module",
        font=("Segoe UI", 22, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(anchor="w", padx=20, pady=20)

    form = tk.Frame(parent, bg=CARD_COLOR, padx=20, pady=20)
    form.pack(fill="x", padx=20, pady=10)

    labels = [
        "Patient Name", "Blood Group", "Units Required", "Hospital Name",
        "City", "Area", "Contact Name", "Contact Phone", "Required Date (YYYY-MM-DD)"
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

        if label == "Blood Group":
            widget = ttk.Combobox(form, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], state="readonly", width=30)
            widget.current(0)
        else:
            widget = ttk.Entry(form, width=33)

        widget.grid(row=i, column=1, padx=10, pady=8, sticky="w")
        entries[label] = widget

    priority_label = tk.Label(
        form,
        text="Priority: ",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 11, "bold")
    )
    priority_label.grid(row=9, column=0, columnspan=2, sticky="w", padx=10, pady=8)

    def clear_form():
        for widget in entries.values():
            try:
                widget.delete(0, tk.END)
            except:
                widget.set("")
        priority_label.config(text="Priority: ")

    def preview_priority(*args):
        blood_group = entries["Blood Group"].get().strip()
        units_text = entries["Units Required"].get().strip()

        try:
            units = int(units_text) if units_text else 0
        except:
            units = 0

        if blood_group and units > 0:
            priority = request_priority(blood_group, units)
            priority_label.config(text=f"Priority: {priority}")

    entries["Blood Group"].bind("<<ComboboxSelected>>", preview_priority)
    entries["Units Required"].bind("<KeyRelease>", preview_priority)

    def save_request():
        patient_name = entries["Patient Name"].get().strip()
        blood_group = entries["Blood Group"].get().strip()
        units_required = entries["Units Required"].get().strip()
        hospital_name = entries["Hospital Name"].get().strip()
        city = entries["City"].get().strip()
        area = entries["Area"].get().strip()
        contact_name = entries["Contact Name"].get().strip()
        contact_phone = entries["Contact Phone"].get().strip()
        required_date = entries["Required Date (YYYY-MM-DD)"].get().strip()

        if not all([patient_name, blood_group, units_required, hospital_name, city, area, contact_name, contact_phone, required_date]):
            messagebox.showerror("Error", "Please fill all fields.")
            return

        # Phone validation
        if not contact_phone.isdigit() or len(contact_phone) != 10:
            messagebox.showerror("Error", "Phone must be 10 digits.")
            return

        try:
            units_required_int = int(units_required)
            if units_required_int <= 0:
                messagebox.showerror("Error", "Units must be greater than 0.")
                return

            req_date = datetime.strptime(required_date, "%Y-%m-%d")

            if req_date.date() < datetime.today().date():
                messagebox.showerror("Error", "Required date cannot be in the past.")
                return

        except ValueError:
            messagebox.showerror("Error", "Enter valid units and valid date.")
            return

        priority = request_priority(blood_group, units_required_int)

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO blood_requests
                (patient_name, blood_group, units_required, hospital_name, city, area, contact_name, contact_phone, required_date, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (patient_name, blood_group, units_required_int, hospital_name, city, area, contact_name, contact_phone, required_date, priority))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Emergency request submitted.\nPriority: {priority}")
            clear_form()

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    btn_frame = tk.Frame(parent, bg=BG_COLOR)
    btn_frame.pack(anchor="w", padx=20, pady=15)

    ttk.Button(btn_frame, text="Submit Request", command=save_request).pack(side="left", padx=10)
    ttk.Button(btn_frame, text="Clear", command=clear_form).pack(side="left", padx=10)
