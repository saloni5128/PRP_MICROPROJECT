import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import time  # ✅ ADDED

from database import get_connection
from theme import BG_COLOR, CARD_COLOR, TEXT_COLOR, MUTED_TEXT
from utils import is_eligible_to_donate, days_since_last_donation
from certificate_utils import generate_certificate, open_existing_certificate


def show_donation_history(parent):
    for widget in parent.winfo_children():
        widget.destroy()

    parent.configure(bg=BG_COLOR)

    selected_edit_id = {"id": None}

    tk.Label(
        parent,
        text="Donation History",
        font=("Segoe UI", 22, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(anchor="w", padx=20, pady=20)

    form = tk.Frame(parent, bg=CARD_COLOR, padx=20, pady=20)
    form.pack(fill="x", padx=20, pady=10)

    tk.Label(form, text="Donor ID", bg=CARD_COLOR, fg=MUTED_TEXT, font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=10, pady=8)
    donor_id_entry = ttk.Entry(form, width=20)
    donor_id_entry.grid(row=0, column=1, padx=10, pady=8)

    tk.Label(form, text="Donation Date (YYYY-MM-DD)", bg=CARD_COLOR, fg=MUTED_TEXT, font=("Segoe UI", 11, "bold")).grid(row=0, column=2, padx=10, pady=8)
    donation_date_entry = ttk.Entry(form, width=20)
    donation_date_entry.grid(row=0, column=3, padx=10, pady=8)

    tk.Label(form, text="Hospital Name", bg=CARD_COLOR, fg=MUTED_TEXT, font=("Segoe UI", 11, "bold")).grid(row=1, column=0, padx=10, pady=8)
    hospital_entry = ttk.Entry(form, width=25)
    hospital_entry.grid(row=1, column=1, padx=10, pady=8)

    tk.Label(form, text="Remarks", bg=CARD_COLOR, fg=MUTED_TEXT, font=("Segoe UI", 11, "bold")).grid(row=1, column=2, padx=10, pady=8)
    remarks_entry = ttk.Entry(form, width=25)
    remarks_entry.grid(row=1, column=3, padx=10, pady=8)

    info_label = tk.Label(form, text="", bg=CARD_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 11, "bold"))
    info_label.grid(row=2, column=0, columnspan=4, sticky="w", padx=10, pady=8)

    # TABLE
    columns = ("Donation ID", "Donor ID", "Donor Name", "Date", "Hospital", "Remarks")
    tree_frame = tk.Frame(parent, bg=BG_COLOR)
    tree_frame.pack(fill="x", padx=20, pady=10)

    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=140, anchor="center")

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="x", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ---------------- FUNCTIONS ---------------- #

    def load_history():
        for item in tree.get_children():
            tree.delete(item)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT d.donation_id, d.donor_id, dn.full_name, d.donation_date, d.hospital_name, d.remarks
            FROM donations d
            JOIN donors dn ON d.donor_id = dn.donor_id
            ORDER BY d.donation_id DESC
        """)

        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

        conn.close()

    def clear_form():
        donor_id_entry.delete(0, tk.END)
        donation_date_entry.delete(0, tk.END)
        hospital_entry.delete(0, tk.END)
        remarks_entry.delete(0, tk.END)
        info_label.config(text="")
        selected_edit_id["id"] = None

    def add_or_update_record():
        donor_id = donor_id_entry.get().strip()
        donation_date = donation_date_entry.get().strip()
        hospital_name = hospital_entry.get().strip()
        remarks = remarks_entry.get().strip()

        if not all([donor_id, donation_date, hospital_name]):
            messagebox.showerror("Error", "Please fill required fields.")
            return

        try:
            donor_id = int(donor_id)
            datetime.strptime(donation_date, "%Y-%m-%d")
        except:
            messagebox.showerror("Error", "Invalid input.")
            return

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT full_name FROM donors WHERE donor_id=?", (donor_id,))
        donor = cursor.fetchone()

        if not donor:
            messagebox.showerror("Error", "Donor not found.")
            conn.close()
            return

        donor_name = donor[0]

        try:
            if selected_edit_id["id"]:
                # 🔥 UPDATE donation
                cursor.execute("""
                    UPDATE donations 
                    SET donor_id=?, donation_date=?, hospital_name=?, remarks=?
                    WHERE donation_id=?
                """, (donor_id, donation_date, hospital_name, remarks, selected_edit_id["id"]))

                # 🔥 ALSO UPDATE donor last donation date
                cursor.execute("""
                    UPDATE donors 
                    SET last_donation_date = ?
                    WHERE donor_id = ?
                """, (donation_date, donor_id))

                messagebox.showinfo("Success", "Record updated successfully")

            else:
                # 🔥 INSERT donation
                cursor.execute("""
                    INSERT INTO donations (donor_id, donation_date, hospital_name, remarks)
                    VALUES (?, ?, ?, ?)
                """, (donor_id, donation_date, hospital_name, remarks))

                donation_id = cursor.lastrowid

                # 🔥 UPDATE donor last donation date
                cursor.execute("""
                    UPDATE donors 
                    SET last_donation_date = ?
                    WHERE donor_id = ?
                """, (donation_date, donor_id))

                # 🔥 GENERATE CERTIFICATE
                generate_certificate(donation_id, donor_name, donation_date, hospital_name, remarks)

                messagebox.showinfo("Success", "Record added & certificate generated")

            conn.commit()
            conn.close()

            clear_form()
            load_history()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def edit_record():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a record first")
            return

        data = tree.item(selected[0])["values"]

        selected_edit_id["id"] = data[0]

        donor_id_entry.delete(0, tk.END)
        donor_id_entry.insert(0, data[1])

        donation_date_entry.delete(0, tk.END)
        donation_date_entry.insert(0, data[3])

        hospital_entry.delete(0, tk.END)
        hospital_entry.insert(0, data[4])

        remarks_entry.delete(0, tk.END)
        remarks_entry.insert(0, data[5])

    def delete_record():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a record first")
            return

        confirm = messagebox.askyesno("Confirm", "Delete this record?")
        if not confirm:
            return

        donation_id = tree.item(selected[0])["values"][0]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM donations WHERE donation_id=?", (donation_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Deleted", "Record deleted")
        load_history()

    def view_certificate():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record.")
            return

        data = tree.item(selected[0])["values"]
        open_existing_certificate(data[2].strip(), data[3].strip(), data[0])

    # ---------------- BUTTONS ---------------- #

    btn_frame = tk.Frame(parent, bg=BG_COLOR)
    btn_frame.pack(anchor="w", padx=20, pady=10)

    ttk.Button(btn_frame, text="Add / Update", command=add_or_update_record).pack(side="left", padx=8)
    ttk.Button(btn_frame, text="Edit", command=edit_record).pack(side="left", padx=8)
    ttk.Button(btn_frame, text="Delete", command=delete_record).pack(side="left", padx=8)
    ttk.Button(btn_frame, text="View Certificate", command=view_certificate).pack(side="left", padx=8)

    load_history()
