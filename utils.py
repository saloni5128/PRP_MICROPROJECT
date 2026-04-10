from datetime import datetime

RARE_BLOOD_GROUPS = {"AB-", "O-"}
DONATION_GAP_DAYS = 90


def parse_date(date_text):
    if not date_text:
        return None
    try:
        return datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        return None


def days_since_last_donation(last_donation_date):
    parsed = parse_date(last_donation_date)
    if not parsed:
        return None

    days = (datetime.today() - parsed).days
    return max(days, 0)  # Prevents future date issues


def is_eligible_to_donate(last_donation_date):
    days = days_since_last_donation(last_donation_date)
    return True if days is None else days >= DONATION_GAP_DAYS


def eligibility_text(last_donation_date):
    days = days_since_last_donation(last_donation_date)

    if days is None:
        return "Eligible"

    if days >= DONATION_GAP_DAYS:
        return "Eligible"
    else:
        remaining = DONATION_GAP_DAYS - days
        return f"Not Eligible ({remaining} days left)"


def rare_blood_text(blood_group):
    if not blood_group:
        return "Unknown"
    return "Rare Blood Group" if blood_group in RARE_BLOOD_GROUPS else "Common"


def request_priority(blood_group, units_required):
    try:
        units_required = int(units_required)
    except:
        units_required = 0

    if blood_group in RARE_BLOOD_GROUPS or units_required >= 3:
        return "High"
    return "Normal"
