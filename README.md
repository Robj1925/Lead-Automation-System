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
```

### 4️⃣ Email Sending

Uses the Gmail API to send personalized emails.

**Subject:**

```
{Name}, let's talk about your goals 🎉
```

**Body:**

```
Hi {Name},

We got your request for help with {Company} and I'd love to discuss your goals soon.

Best,
Team
```

### 5️⃣ Airtable Update

Once email is successfully sent:

- `emailed = 1` in SQLite
- `Contacted On` date field updated in Airtable (`YYYY-MM-DD`)

---

## 🛠 Tech Stack

- Python
- Airtable API
- Gmail API
- SQLite
- Pandas (for display in Colab)

---

## ⚙️ Setup

### 1. Install Dependencies

```bash
pip install airtable-python-wrapper python-dotenv pandas google-api-python-client google-auth-oauthlib google-auth-httplib2
```

### 2. Environment Variables

Create a `.env` file:

```
AIRTABLE_API_KEY=your_key_here
BASE_ID=your_base_id_here
```

> ⚠️ Do NOT commit `.env`, `token.json`, or `db.sql` to GitHub.

Add to `.gitignore`:

```
.env
token.json
db.sql
```

### 3. Gmail API Setup

- Create a Google Cloud project
- Enable Gmail API
- Download OAuth credentials
- Generate `token.json` and place it in your working directory

---

## 🔁 Runtime

The script:

- Polls Airtable every 10 seconds
- Inserts new leads
- Sends emails if qualified
- Updates Airtable
- Displays status in console

---

## 📌 Notes

- Built for Google Colab but works locally
- Uses polling (not webhooks)
- Designed as a simple automation demo
- Can be extended into a full CRM automation system

---

## 🔒 Security

Never expose:

- Airtable API key
- Gmail `token.json`
- `.env` file

---
