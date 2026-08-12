# Bug Reporting Automation

Turns a Google Sheet into a bug intake queue. Fill in a row, run the app,
and it creates an OpenProject ticket, then a linked RT1 ticket that's
automatically resolved — no manual ticket entry in either system.

## How it works

You keep a Google Sheet with these columns:

| Column | Meaning |
|---|---|
| A: Title | Short bug summary |
| B: Steps | Steps to reproduce |
| C: Expected | Expected result |
| D: Actual | Actual result |
| E: Environment | Browser/env/account used |
| F: OpenProject Link | Filled in automatically |
| G: RT1 Ticket # | Filled in automatically |
| H: Status | Filled in automatically ("Done" or "Failed: ...") |

Any row where **Title** has text and **Status** is empty is picked up on the
next run. For each pending row, the app:

1. Creates a Bug work package in OpenProject, assigned to a fixed backlog
   version so it shows up on the team's Backlogs board
2. Creates an RT1 ticket referencing it (summary + link back to the full
   OpenProject details) and resolves it immediately
3. Writes the OpenProject link, RT1 ticket number, and status back to the row

## Setup

### 1. Clone and install

```bash
git clone <your-repo-url>
cd bug_reporting_automation
pip install -r requirements.txt
```

You'll also need Google Chrome installed, with a matching `chromedriver`
available on your PATH.

### 2. Create a Google service account

1. In [Google Cloud Console](https://console.cloud.google.com/), enable the
   **Google Sheets API** for a project.
2. Create a service account under **APIs & Services > Credentials**.
3. Generate a JSON key for it, rename the file to `service_account.json`,
   and place it in the project root.
4. Share your Google Sheet with the service account's `client_email`
   (Editor access).

### 3. Get an OpenProject API token

In OpenProject, go to **My Account > Access Tokens** and generate one.
You'll also need:
- Your project identifier (the slug in your project's URL)
- The numeric project ID
- The Bug type ID for your project — fetch it with:
  ```bash
  curl -u apikey:<your_token> "https://<your-instance>/api/v3/projects/<project-identifier>/types"
  ```
- The version ID you want new bugs assigned to (e.g. a "next sprint" backlog
  placeholder) — fetch it with:
  ```bash
  curl -u apikey:<your_token> "https://<your-instance>/api/v3/projects/<project-identifier>/versions"
  ```

Update the corresponding values in `config.py` to match your instance.

### 4. Configure environment variables

```bash
cp .env.example .env
```

```
OP_API_TOKEN=your_openproject_token
RT_USERNAME=your.name@yourcompany.com
RT_PASSWORD=your_password
GOOGLE_SHEET_ID=your_google_sheet_id
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
SHEET_TAB_NAME=Bug Reports
```

### 5. Run it

```bash
python app.py
```

Click **Run Now** to process all pending rows.

## Notes

- `.env` and `service_account.json` hold real credentials — excluded via
  `.gitignore`, never commit them.
- Failed rows are marked `Failed: <reason>` in Status instead of being
  retried silently. Clear the Status cell to make a row pending again.
- The RT1 custom field values (queue, touchpoint, issue type, etc.) live in
  `config.py` — adjust them if your RT instance differs.
