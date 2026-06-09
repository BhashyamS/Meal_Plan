# 🐻 Pooh Bear Yum Yum Tracker

A dynamic Streamlit + Google Sheets client meal plan tracker.

The client can:
- Pick meal options for each day
- See calories, protein, carbs, fats, and cost update dynamically
- Generate a grocery list from selected meals
- Track weekly budget against a goal
- Save meal plans to Google Sheets
- Review 30 days of saved history

## Files

```text
app.py
requirements.txt
.streamlit/secrets.toml.example
README.md
```

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app will run without Google Sheets, but data will not persist.

## Google Sheets Setup

### 1. Create a Google Cloud Project

Go to Google Cloud Console and create a project.

### 2. Enable APIs

Enable:
- Google Sheets API
- Google Drive API

### 3. Create a Service Account

Create a service account and generate a JSON key.

### 4. Create a Google Sheet

Create a sheet named:

```text
Pooh Bear Yum Yum Tracker
```

### 5. Share the Sheet

Share the Google Sheet with the service account email.

The email looks like:

```text
something@your-project.iam.gserviceaccount.com
```

Give it Editor access.

### 6. Add Secrets to Streamlit

In Streamlit Community Cloud:

```text
App > Settings > Secrets
```

Paste the contents from:

```text
.streamlit/secrets.toml.example
```

Then replace the placeholder values with the values from your service account JSON.

## Important

Do not upload your real secrets file to GitHub.

Only upload:

```text
secrets.toml.example
```

## Deploy to Streamlit Cloud

1. Push this folder to GitHub.
2. Go to Streamlit Community Cloud.
3. Create a new app.
4. Select your repo.
5. Main file path: `app.py`.
6. Add secrets.
7. Deploy.

## Suggested Repo Name

```text
pooh-bear-yum-yum-tracker
```