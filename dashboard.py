import tkinter as tk
from tkinter import messagebox
from database import get_connection
from theme import BG_COLOR, CARD_COLOR, SECONDARY_COLOR, TEXT_COLOR, MUTED_TEXT


def create_stat_card(parent, title, value, row, col):
    card = tk.Frame(parent, bg=CARD_COLOR, padx=20, pady=20)
    card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

    tk.Label(
        card,
        text=title,
        bg=CARD_COLOR,
        fg=MUTED_TEXT,
        font=("Segoe UI", 12, "bold")
    ).pack(anchor="w")

    tk.Label(
        card,
        text=str(value),
        bg=CARD_COLOR,
        fg=SECONDARY_COLOR,
        font=("Segoe UI", 24, "bold")
    ).pack(anchor="w", pady=(10, 0))


def show_dashboard(parent):
    for widget in parent.winfo_children():
        widget.destroy()

    parent.configure(bg=BG_COLOR)

    tk.Label(
        parent,
        text="LifeLink Dashboard",
        font=("Segoe UI", 24, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(anchor="w", padx=20, pady=(20, 10))

    tk.Label(
        parent,
        text="Blood Donor Finder and Management System",
        font=("Segoe UI", 12),
        bg=BG_COLOR,
        fg=MUTED_TEXT
    ).pack(anchor="w", padx=20, pady=(0, 20))

    content = tk.Frame(parent, bg=BG_COLOR)
    content.pack(fill="both", expand=True, padx=10, pady=10)

    for i in range(2):
        content.grid_columnconfigure(i, weight=1)
        content.grid_rowconfigure(i, weight=1)  # FIX

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM donors")
        total_donors = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM donors WHERE is_available = 1")
        available_donors = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM blood_requests")
        total_requests = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM blood_requests WHERE status = 'Pending'")
        pending_requests = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM blood_requests WHERE priority = 'High'")
        high_priority_requests = cursor.fetchone()[0]

        conn.close()

    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return

    create_stat_card(content, "Total Donors", total_donors, 0, 0)
    create_stat_card(content, "Available Donors", available_donors, 0, 1)
    create_stat_card(content, "Blood Requests", total_requests, 1, 0)
    create_stat_card(content, "Pending Requests", pending_requests, 1, 1)

    extra = tk.Frame(parent, bg=CARD_COLOR, padx=20, pady=20)
    extra.pack(fill="x", padx=20, pady=10)

    tk.Label(
        extra,
        text=f"High Priority Requests: {high_priority_requests}",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 13, "bold")
    ).pack(anchor="w")

    tk.Label(
        extra,
        text="Modules: Registration, Smart Search, Emergency Request, Availability, Donation History, Admin",
        bg=CARD_COLOR,
        fg=MUTED_TEXT,
        font=("Segoe UI", 11)
    ).pack(anchor="w", pady=(10, 0))
