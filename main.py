# ======================================================
# INSTALL (Run Once If Needed)
# ======================================================
# !pip install airtable-python-wrapper python-dotenv pandas google-api-python-client google-auth-oauthlib google-auth-httplib2

# ======================================================
# IMPORTS
# ======================================================
from datetime import datetime, timezone
from airtable import Airtable
import os
import sqlite3
import time
import pandas as pd
from dotenv import load_dotenv
from IPython.display import clear_output

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

# ======================================================
# LOAD ENV VARIABLES
# ======================================================
load_dotenv(override=True)

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("BASE_ID")
TABLE_NAME = "Lead Contacts"

# ======================================================
# CONNECT TO AIRTABLE
# ======================================================
airtable = Airtable(BASE_ID, TABLE_NAME, api_key=AIRTABLE_API_KEY)

# ======================================================
# SETUP SQLITE DATABASE
# ======================================================
conn = sqlite3.connect("db.sql", timeout=30, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("PRAGMA journal_mode=WAL;")

cursor.execute("""
CREATE TABLE IF NOT EXISTS leads (
    id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT,
    qualified INTEGER DEFAULT 0,
    emailed INTEGER DEFAULT 0
)
""")

conn.commit()

# ======================================================
# GMAIL SETUP
# ======================================================
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
creds = Credentials.from_authorized_user_file('/content/token.json', SCOPES)
service = build('gmail', 'v1', credentials=creds)

def send_email(recipient, subject, body):
    message = MIMEText(body)
    message['to'] = recipient
    message['from'] = 'me'
    message['subject'] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        sent = service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()
        return True
    except Exception as e:
        print("Email Error:", e)
        return False

# ======================================================
# QUALIFICATION LOGIC (EDIT THIS)
# ======================================================
def is_qualified(fields):
    """
    Customize your qualification logic here.
    Example: Must have email + company field.
    """
    if fields.get("Email") and fields.get("Company"):
        return True
    return False

# ======================================================
# MAIN LOOP
# ======================================================
print("System running...")

while True:
    try:
        records = airtable.get_all()
        new_count = 0
        email_count = 0

        for record in records:
            record_id = record["id"]
            fields = record["fields"]

            first = fields.get("First Name") or ""
            last = fields.get("Last Name") or ""
            name = (first + " " + last).strip() or "Kid Has No Name Apparently"
            email = fields.get("Email")

            qualified = 1 if is_qualified(fields) else 0

            # Insert if new
            cursor.execute(
                """
                INSERT OR IGNORE INTO leads (id, name, email, qualified)
                VALUES (?, ?, ?, ?)
                """,
                (record_id, name, email, qualified)
            )

            if cursor.rowcount > 0:
                new_count += 1

            # Check if needs email
            cursor.execute(
                "SELECT qualified, emailed FROM leads WHERE id = ?",
                (record_id,)
            )
            row = cursor.fetchone()
            company = fields.get("Company")
            if row and row[0] == 1 and row[1] == 0 and email:
                success = send_email(
                    recipient=email,
                    subject=f"{name}, let's talk about your goals🎉",
                    body=f"Hi {name},\n\nYou're qualified! We got your request for help with {company} and I'd love to discuss your goals soon. We'll be in touch shortly.\n\nBest,\nTeam"
                )

                if success:
                    cursor.execute(
                        "UPDATE leads SET emailed = 1 WHERE id = ?",
                        (record_id,)
                    )
                    email_count += 1

                    today = datetime.utcnow().strftime('%Y-%m-%d')

                    airtable.update(
                        record_id,
                        {
                            "Contacted On": today,
                        })

        conn.commit()

        # Refresh UI
        clear_output(wait=True)
        df = pd.read_sql_query(
            "SELECT name, email, qualified, emailed FROM leads ORDER BY rowid DESC",
            conn
        )

        print(f"Last Sync | New Leads: {new_count} | Emails Sent: {email_count}")
        display(df)

        time.sleep(10)

    except Exception as e:
        clear_output(wait=True)
        print("Error:", e)
        time.sleep(5)
