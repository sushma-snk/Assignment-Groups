# AI Project Group Formation App

A simple Streamlit application for forming 4-member ID/PD student groups.

## Features
- Group name registration
- Exactly 4 members per group
- Name, registration number and ID/PD programme
- 10 suggested project applications
- Prevents duplicate group names
- Prevents duplicate student registration numbers/names
- Faculty/admin dashboard
- Group/student summary
- CSV download
- Delete group functionality
- SQLite database for persistent storage

## Run locally

1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

4. Open the URL shown by Streamlit.

## Default admin password

`admin123`

### Change it before sharing the app.

For Streamlit Cloud, create:

`.streamlit/secrets.toml`

with:

```toml
ADMIN_PASSWORD = "your-new-password"
```

Do not commit the secrets file to a public GitHub repository.

## Important note about deployment

The SQLite database works well for a single local machine. If you deploy the app on a hosting platform where the filesystem is not persistent, use Google Sheets, Supabase, or another hosted database instead of SQLite.

## Suggested classroom setup

1. Deploy the app.
2. Give students the app link.
3. Assign each group a unique application.
4. Students submit their four members.
5. Faculty opens Admin Dashboard.
6. Download the CSV after all groups are registered.
