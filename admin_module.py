import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from theme import BG_COLOR, CARD_COLOR, TEXT_COLOR
from utils import days_since_last_donation, is_eligible_to_donate, rare_blood_text


def show_admin_module(parent):
    for widget in parent.winfo_children():
        widget.destroy()

    parent.configure(bg=BG_COLOR)

    # ===== MAIN TITLE =====
    tk.Label(
        parent,
        text="Admin Panel",
        font=("Segoe UI", 20, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(anchor="w", padx=20, pady=15)

    # ===== DONOR SECTION TITLE =====
    tk.Label(
        parent,
        text="Donor Records",
        font=("Segoe UI", 14, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(anchor="w", padx=20)

    # ===== DONOR TABLE FRAME WITH SCROLL =====
    donor_frame = tk.Frame(parent, bg=CARD_COLOR)
    donor_frame.pack(fill="both", expand=True, padx=20, pady=5)

    donor_scroll = ttk.Scrollbar(donor_frame)
    donor_scroll.pack(side="right", fill="y")

    donor_columns = ("ID", "Name", "Blood", "Phone", "City", "Area", "Available", "Days", "Eligibility", "Type")
    donor_tree = ttk.Treeview(
        donor_frame,
        columns=donor_columns,
        show="headings",
        yscrollcommand=donor_scroll.set,
        height=8
    )

    donor_scroll.config(command=donor_tree.yview)

    for col in donor_columns:
        donor_tree.heading(col, text=col)
        donor_tree.column(col, width=120, anchor="center")

    donor_tree.pack(fill="both", expand=True)

    donor_tree.tag_configure("rare", background="#ffe5e5")
    donor_tree.tag_configure("normal", background="#f9fafb")

    # ===== REQUEST SECTION TITLE =====
    tk.Label(
        parent,
        text="Blood Requests",
        font=("Segoe UI", 14, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(anchor="w", padx=20, pady=(10, 0))

    # ===== REQUEST TABLE FRAME WITH SCROLL =====
    request_frame = tk.Frame(parent, bg=CARD_COLOR)
    request_frame.pack(fill="both", expand=True, padx=20, pady=5)

    request_scroll = ttk.Scrollbar(request_frame)
    request_scroll.pack(side="right", fill="y")

    request_columns = ("Request ID", "Patient", "Blood", "Units", "Hospital", "City", "Priority", "Status")
    request_tree = ttk.Treeview(
        request_frame,
        columns=request_columns,
        show="headings",
        yscrollcommand=request_scroll.set,
        height=6
    )

    request_scroll.config(command=request_tree.yview)

    for col in request_columns:
        request_tree.heading(col, text=col)
        request_tree.column(col, width=130, anchor="center")

    request_tree.pack(fill="both", expand=True)

    request_tree.tag_configure("high", background="#ffe5e5")
    request_tree.tag_configure("normal", background="#f9fafb")

    # ===== FUNCTIONS =====
    def load_data():
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # LOAD DONORS
            for item in donor_tree.get_children():
                donor_tree.delete(item)

            cursor.execute("""
                SELECT donor_id, full_name, blood_group, phone, city, area, is_available, last_donation_date
                FROM donors
                ORDER BY donor_id DESC
            """)
            donor_rows = cursor.fetchall()

            for row in donor_rows:
                donor_id, name, blood_group, phone, city, area, is_available, last_donation = row

                days = days_since_last_donation(last_donation) if last_donation else None
                days_text = "No previous donation" if days is None else str(days)

                eligibility = "Eligible" if is_eligible_to_donate(last_donation) else "Not Eligible"
                donor_type = rare_blood_text(blood_group)

                available_text = "Yes" if is_available == 1 else "No"
                tag = "rare" if donor_type == "Rare Blood Group" else "normal"

                donor_tree.insert(
                    "",
                    tk.END,
                    values=(donor_id, name, blood_group, phone, city, area,
                            available_text, days_text, eligibility, donor_type),
                    tags=(tag,)
                )

            # LOAD REQUESTS
            for item in request_tree.get_children():
                request_tree.delete(item)

            cursor.execute("""
                SELECT request_id, patient_name, blood_group, units_required,
                       hospital_name, city, priority, status
                FROM blood_requests
                ORDER BY request_id DESC
            """)
            request_rows = cursor.fetchall()
            conn.close()

            for row in request_rows:
                tag = "high" if row[6] == "High" else "normal"
                request_tree.insert("", tk.END, values=row, tags=(tag,))

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def delete_selected_donor():
        selected = donor_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a donor.")
            return

        donor_id = donor_tree.item(selected[0])["values"][0]

        if not messagebox.askyesno("Confirm", "Delete this donor?"):
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM donations WHERE donor_id = ?", (donor_id,))
            cursor.execute("DELETE FROM donors WHERE donor_id = ?", (donor_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Donor deleted.")
            load_data()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mark_request_completed():
        selected = request_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a request.")
            return

        request_id = request_tree.item(selected[0])["values"][0]

        if not messagebox.askyesno("Confirm", "Mark as completed?"):
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE blood_requests SET status = 'Completed' WHERE request_id = ?",
                (request_id,)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Request updated.")
            load_data()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ===== BUTTONS (ALWAYS VISIBLE) =====
    btn_frame = tk.Frame(parent, bg=BG_COLOR)
    btn_frame.pack(pady=10)

    ttk.Button(btn_frame, text="Refresh", command=load_data).pack(side="left", padx=10)
    ttk.Button(btn_frame, text="Delete Donor", command=delete_selected_donor).pack(side="left", padx=10)
    ttk.Button(btn_frame, text="Complete Request", command=mark_request_completed).pack(side="left", padx=10)

    load_data()
