import os
import webbrowser
from tkinter import messagebox

from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor


def safe_text(text):
    return "".join(c for c in text if c.isalnum() or c in (" ", "_")).strip()


def build_certificate_number(donation_id, donation_date):
    try:
        year = donation_date.split("-")[0]
    except:
        year = "0000"
    return f"CERT-{year}-{int(donation_id):03d}"


def generate_certificate(donation_id, donor_name, donation_date, hospital_name, remarks=""):
    try:
        # ✅ SAFE FOLDER CREATION
        os.makedirs("certificates", exist_ok=True)

        safe_name = safe_text(donor_name).replace(" ", "_")
        safe_date = donation_date.replace("-", "_")

        # ✅ UNIQUE FILE NAME
        file_path = os.path.join(
            "certificates",
            f"certificate_{safe_name}_{safe_date}_{donation_id}.pdf"
        )

        certificate_number = build_certificate_number(donation_id, donation_date)

        c = canvas.Canvas(file_path, pagesize=landscape(A4))
        width, height = landscape(A4)

        # Background
        c.setFillColor(HexColor("#fffdf7"))
        c.rect(0, 0, width, height, fill=1, stroke=0)

        # Borders
        c.setStrokeColor(HexColor("#c9a227"))
        c.setLineWidth(10)
        c.rect(20, 20, width - 40, height - 40)

        c.setStrokeColor(HexColor("#b91c1c"))
        c.setLineWidth(3)
        c.rect(40, 40, width - 80, height - 80)

        # Header
        c.setFillColor(HexColor("#1d4ed8"))
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, height - 80, "LifeLink")

        c.setFillColor(HexColor("#7c2d12"))
        c.setFont("Helvetica", 16)
        c.drawCentredString(width / 2, height - 105, "Blood Donor Finder System")

        # Certificate number
        c.setFillColor(HexColor("#444444"))
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(width - 70, height - 70, f"Certificate No: {certificate_number}")

        # Title
        c.setFillColor(HexColor("#5b3a0f"))
        c.setFont("Helvetica-BoldOblique", 30)
        c.drawCentredString(width / 2, height - 155, "Certificate of Appreciation")

        # Ribbon
        c.setFillColor(HexColor("#b91c1c"))
        c.roundRect(width / 2 - 170, height - 205, 340, 30, 6, fill=1, stroke=0)
        c.setFillColor(HexColor("#ffffff"))
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, height - 195, "HONORING A LIFE-SAVING DONATION")

        # Presented text
        c.setFillColor(HexColor("#333333"))
        c.setFont("Helvetica", 18)
        c.drawCentredString(width / 2, height - 250, "This certificate is proudly presented to")

        # Donor name
        c.setFillColor(HexColor("#3f2a14"))
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(width / 2, height - 295, donor_name)

        # Underline
        c.setStrokeColor(HexColor("#c9a227"))
        c.setLineWidth(1.5)
        c.line(width / 2 - 170, height - 308, width / 2 + 170, height - 308)

        # Message
        c.setFillColor(HexColor("#2f2f2f"))
        c.setFont("Helvetica", 16)
        c.drawCentredString(width / 2, height - 360, "In deep gratitude for your valuable blood donation contribution.")
        c.drawCentredString(width / 2, height - 385, "Your selfless act can save lives and inspire others to help those in need.")

        # Details
        c.setFillColor(HexColor("#222222"))
        c.setFont("Helvetica-Bold", 15)
        c.drawString(100, height - 455, f"Donation Date: {donation_date}")
        c.drawString(width - 330, height - 455, f"Hospital Name: {hospital_name}")

        # Remarks
        c.setFont("Helvetica", 14)
        remarks_text = remarks if remarks else "N/A"
        if len(remarks_text) > 80:
            remarks_text = remarks_text[:77] + "..."
        c.drawCentredString(width / 2, height - 500, f"Remarks: {remarks_text}")

        # Seal
        c.setFillColor(HexColor("#b91c1c"))
        c.circle(width / 2, height - 555, 38, fill=1, stroke=0)
        c.setFillColor(HexColor("#facc15"))
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(width / 2, height - 550, "LIFELINK")

        # Signatures
        c.setStrokeColor(HexColor("#444444"))
        c.line(120, 90, 300, 90)
        c.line(width - 300, 90, width - 120, 90)

        c.setFillColor(HexColor("#222222"))
        c.setFont("Helvetica", 13)
        c.drawCentredString(210, 72, "Authorized Signature")
        c.drawCentredString(width - 210, 72, "Project Coordinator")

        c.save()
        return file_path

    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate certificate: {e}")
        return None


def open_existing_certificate(donor_name, donation_date, donation_id):
    safe_name = safe_text(donor_name).replace(" ", "_")
    safe_date = donation_date.replace("-", "_")

    file_path = os.path.join(
        "certificates",
        f"certificate_{safe_name}_{safe_date}_{donation_id}.pdf"
    )

    if os.path.exists(file_path):
        webbrowser.open(f"file://{os.path.abspath(file_path)}")
    else:
        messagebox.showerror("Error", "Certificate not found.")
