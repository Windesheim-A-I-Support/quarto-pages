import os
import pandas as pd
import win32com.client as win32

# ✅ CONFIGURATION
CSV_PATH = "data/cleaned_master.csv"
REPORTS_FOLDER = "reports"
TEST_MODE = True
TEST_EMAIL = "cg.verhoef@windesheim.nl"  # <- Change this to your address

def safe_filename(name):
    return "".join(c if c.isalnum() else "_" for c in str(name))

def send_emails():
    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.lower().str.strip()

    required_cols = {"company_name", "email_address", "name"}
    if not required_cols.issubset(df.columns):
        print(f"❌ Missing one or more required columns: {required_cols}")
        return

    outlook = win32.Dispatch("Outlook.Application")
    sent_count = 0

    for _, row in df.iterrows():
        company = str(row["company_name"])
        email = row["email_address"]
        name = row.get("name", "there")

        if pd.isna(email) or "@" not in email:
            print(f"⚠️ Skipping {company} — invalid email")
            continue

        report_filename = safe_filename(company) + ".pdf"
        attachment_path = os.path.join(REPORTS_FOLDER, report_filename)

        if not os.path.exists(attachment_path):
            print(f"❌ Report not found for {company}: {attachment_path}")
            continue

        if TEST_MODE:
            print(f"🧪 TEST MODE: Would send to {email} for {company}")
            real_email = email
            email = TEST_EMAIL
        else:
            print(f"📨 Sending to {email} for {company}")

        mail = outlook.CreateItem(0)
        mail.To = email
        mail.Subject = f"Your Resilience Scan Report – {company}"

        body = (
            f"Dear {name},\n\n"
            f"Please find attached your resilience scan report for {company}.\n\n"
            "If you have any questions, feel free to reach out.\n\n"
            "Best regards,\n\n"
            "Christiaan Verhoef\n"
            "Windesheim | Value Chain Hackers"
        )

        if TEST_MODE:
            body = (
                f"[TEST MODE]\nThis email was originally intended for: {real_email}\n\n"
                + body
            )

        mail.Body = body
        mail.Attachments.Add(os.path.abspath(attachment_path))
        mail.Send()
        sent_count += 1

    print(f"\n📬 Finished sending {sent_count} {'test' if TEST_MODE else 'live'} emails.")

if __name__ == "__main__":
    send_emails()
