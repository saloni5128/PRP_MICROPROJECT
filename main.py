import tkinter as tk
from tkinter import ttk, messagebox

from database import create_tables
from theme import BG_COLOR, SIDEBAR_COLOR, PRIMARY_COLOR, TEXT_COLOR
from dashboard import show_dashboard
from donor_registration import show_donor_registration
from blood_search import show_blood_search
from location_search import show_location_search
from emergency_request import show_emergency_request
from donor_availability import show_donor_availability
from donation_history import show_donation_history
from admin_module import show_admin_module


def main():
    try:
        create_tables()
    except Exception as e:
        messagebox.showerror("Startup Error", f"Database error:\n{e}")
        return

    root = tk.Tk()
    root.title("LifeLink - Blood Donor Finder System")
    root.geometry("1450x800")
    root.minsize(1100, 650)
    root.configure(bg=BG_COLOR)

    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
    style.configure("TEntry", padding=6)
    style.configure("TCombobox", padding=4)
    style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    header = tk.Frame(root, bg=PRIMARY_COLOR, height=60)
    header.pack(fill="x")

    tk.Label(
        header,
        text="LifeLink - Blood Donor Finder System",
        bg=PRIMARY_COLOR,
        fg="white",
        font=("Segoe UI", 20, "bold")
    ).pack(side="left", padx=20, pady=10)

    body = tk.Frame(root, bg=BG_COLOR)
    body.pack(fill="both", expand=True)

    sidebar = tk.Frame(body, bg=SIDEBAR_COLOR, width=260)
    sidebar.pack(side="left", fill="y")

    content = tk.Frame(body, bg=BG_COLOR)
    content.pack(side="right", fill="both", expand=True)

    active_btn = {"btn": None}

    def add_nav_button(text, command):
        btn = tk.Button(
            sidebar,
            text=text,
            command=lambda: switch_module(btn, command),
            bg=SIDEBAR_COLOR,
            fg=TEXT_COLOR,
            activebackground=PRIMARY_COLOR,
            activeforeground="white",
            relief="flat",
            anchor="w",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=12
        )
        btn.pack(fill="x", pady=2)
        return btn

    def switch_module(button, command):
        if active_btn["btn"]:
            active_btn["btn"].configure(bg=SIDEBAR_COLOR)

        button.configure(bg=PRIMARY_COLOR)
        active_btn["btn"] = button

        try:
            command()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Label(
        sidebar,
        text="Modules",
        bg=SIDEBAR_COLOR,
        fg="white",
        font=("Segoe UI", 14, "bold")
    ).pack(anchor="w", padx=20, pady=(20, 10))

    btn_dashboard = add_nav_button("Dashboard", lambda: show_dashboard(content))
    add_nav_button("Donor Registration", lambda: show_donor_registration(content))
    add_nav_button("Blood Group Search", lambda: show_blood_search(content))
    add_nav_button("Location Search", lambda: show_location_search(content))
    add_nav_button("Emergency Request", lambda: show_emergency_request(content))
    add_nav_button("Donor Availability", lambda: show_donor_availability(content))
    add_nav_button("Donation History", lambda: show_donation_history(content))
    add_nav_button("Admin Module", lambda: show_admin_module(content))

    # Default load
    switch_module(btn_dashboard, lambda: show_dashboard(content))

    root.mainloop()


if __name__ == "__main__":
    main()
