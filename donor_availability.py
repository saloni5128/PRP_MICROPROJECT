import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from theme import BG_COLOR, TEXT_COLOR
from utils import days_since_last_donation, is_eligible_to_donate, rare_blood_text


def show_donor_availability(parent):
    for widget in parent.winfo_children():
        widget.destroy()

    parent.configure(bg=BG_COLOR)

    tk.Label(
        parent,
        text="Donor Availability Status",
        font=("Segoe UI", 22, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(anchor="w", padx=20, pady=20)

    # 🔥 FRAME FOR TABLE + SCROLLBAR
    table_frame = tk.Frame(parent, bg=BG_COLOR)
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = ("ID", "Name", "Blood", "Phone", "City", "Area", "Available", "Days Since Donation", "Eligibility", "Type")

    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")

    # 🔥 VERTICAL SCROLLBAR
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    tree.tag_configure("rare", background="#ffe5e5")
    tree.tag_configure("normal", background="#f9fafb")

    def load_data():
        try:
            for item in tree.get_children():
                tree.delete(item)

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT donor_id, full_name, blood_group, phone, city, area, is_available, last_donation_date
                FROM donors
                ORDER BY donor_id DESC
            """)
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                donor_id, name, blood_group, phone, city, area, is_available, last_donation = row

                days = days_since_last_donation(last_donation) if last_donation else None
                days_text = "No previous donation" if days is None else str(days)

                eligibility = "Eligible" if is_eligible_to_donate(last_donation) else "Not Eligible"
                donor_type = rare_blood_text(blood_group)

                available_text = "Yes" if is_available == 1 else "No"
                tag = "rare" if donor_type == "Rare Blood Group" else "normal"

                tree.insert(
                    "",
                    tk.END,
                    values=(donor_id, name, blood_group, phone, city, area, available_text, days_text, eligibility, donor_type),
                    tags=(tag,)
                )

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_status(status):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a donor.")
            return

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to update availability?")
        if not confirm:
            return

        donor_id = tree.item(selected[0])["values"][0]

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE donors SET is_available = ? WHERE donor_id = ?", (status, donor_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Availability updated.")
            load_data()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    btn_frame = tk.Frame(parent, bg=BG_COLOR)
    btn_frame.pack(pady=10)

    ttk.Button(btn_frame, text="Refresh", command=load_data).pack(side="left", padx=10)
    ttk.Button(btn_frame, text="Mark Available", command=lambda: update_status(1)).pack(side="left", padx=10)
    ttk.Button(btn_frame, text="Mark Unavailable", command=lambda: update_status(0)).pack(side="left", padx=10)

    load_data()
