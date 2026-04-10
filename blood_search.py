import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from theme import BG_COLOR, CARD_COLOR, TEXT_COLOR, MUTED_TEXT
from utils import days_since_last_donation, is_eligible_to_donate, rare_blood_text


def show_blood_search(parent):
    for widget in parent.winfo_children():
        widget.destroy()

    parent.configure(bg=BG_COLOR)

    tk.Label(
        parent,
        text="Smart Blood Group Search",
        font=("Segoe UI", 22, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(anchor="w", padx=20, pady=20)

    top = tk.Frame(parent, bg=CARD_COLOR, padx=20, pady=20)
    top.pack(fill="x", padx=20, pady=10)

    tk.Label(top, text="Blood Group", bg=CARD_COLOR, fg=MUTED_TEXT, font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=10, pady=8)
    blood_combo = ttk.Combobox(top, values=["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], state="readonly", width=18)
    blood_combo.grid(row=0, column=1, padx=10, pady=8)
    blood_combo.current(0)

    tk.Label(top, text="City", bg=CARD_COLOR, fg=MUTED_TEXT, font=("Segoe UI", 11, "bold")).grid(row=0, column=2, padx=10, pady=8)
    city_entry = ttk.Entry(top, width=20)
    city_entry.grid(row=0, column=3, padx=10, pady=8)

    available_var = tk.IntVar(value=1)
    ttk.Checkbutton(top, text="Available Only", variable=available_var).grid(row=0, column=4, padx=10, pady=8)

    ttk.Button(top, text="Search", command=lambda: search()).grid(row=0, column=5, padx=10, pady=8)

    # 🔥 TABLE FRAME (for scrollbar)
    table_frame = tk.Frame(parent, bg=BG_COLOR)
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = ("ID", "Name", "Blood", "Phone", "City", "Area", "Available", "Days Since Donation", "Eligibility", "Type")

    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")

    # 🔥 SCROLLBAR
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    tree.tag_configure("rare", background="#ffe5e5")
    tree.tag_configure("normal", background="#f9fafb")

    def search():
        try:
            for item in tree.get_children():
                tree.delete(item)

            blood = blood_combo.get().strip()
            city = city_entry.get().strip()
            available_only = available_var.get()

            query = """
                SELECT donor_id, full_name, blood_group, phone, city, area, is_available, last_donation_date
                FROM donors
                WHERE 1=1
            """
            params = []

            if blood:
                query += " AND blood_group = ?"
                params.append(blood)

            if city:
                query += " AND city LIKE ?"
                params.append(f"%{city}%")

            if available_only:
                query += " AND is_available = 1"

            query += " ORDER BY is_available DESC, city ASC, donor_id DESC"

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                messagebox.showinfo("No Results", "No donors found.")
                return

            for row in rows:
                donor_id, name, blood_group, phone, city_val, area, is_available, last_donation = row

                days = days_since_last_donation(last_donation) if last_donation else None
                days_text = "No previous donation" if days is None else str(days)

                eligibility = "Eligible" if is_eligible_to_donate(last_donation) else "Not Eligible"
                donor_type = rare_blood_text(blood_group)

                available_text = "Yes" if is_available == 1 else "No"
                tag = "rare" if donor_type == "Rare Blood Group" else "normal"

                tree.insert(
                    "",
                    tk.END,
                    values=(donor_id, name, blood_group, phone, city_val, area, available_text, days_text, eligibility, donor_type),
                    tags=(tag,)
                )

        except Exception as e:
            messagebox.showerror("Error", str(e))
