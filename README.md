# Lead Automation System (Airtable + Gmail + Python)

A simple Python-based lead automation system that:

- Pulls leads from Airtable  
- Qualifies them using custom logic  
- Sends personalized emails via Gmail API  
- Prevents duplicate emails using SQLite  
- Updates Airtable with a “Contacted On” date  

No Zapier or Make required. Fully controlled in Python.

---

## 🚀 How It Works

### 1️⃣ Lead Source
Leads are pulled from an Airtable table (`Lead Contacts`).

### 2️⃣ Local Database
A local SQLite database (`db.sql`) stores:

- Lead ID  
- Name  
- Email  
- Qualification status  
- Email sent status  

This prevents duplicate emails.

### 3️⃣ Qualification Logic
Custom logic determines whether a lead should receive an email.

Example:

```python
def is_qualified(fields):
    if fields.get("Email") and fields.get("Company"):
        return True
    return False
