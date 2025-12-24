# 🚀 Deploying RAG Chatbot to Render

This guide will help you deploy your Django RAG Chatbot to Render's Free Tier.

## prerequisites

1.  **GitHub Account**
2.  **Render Account** (Connect with GitHub)
3.  **Groq API Key** (from [Groq Console](https://console.groq.com/))

## Step 1: Push Code to GitHub

Since you are already in a git repository, you need to commit your changes and push them to GitHub.

```bash
git add .
git commit -m "Prepare for Render deployment: cleanup Firebase, update settings"
git push origin main
```

*(If you haven't connected to a remote repo yet, follow GitHub's instructions to add a remote origin)*

## Step 2: Create Web Service on Render

1.  Go to [dashboard.render.com](https://dashboard.render.com/).
2.  Click **New +** -> **Web Service**.
3.  Select **Build and deploy from a Git repository**.
4.  Connect your GitHub repository.
5.  **Configuration**:
    *   **Name**: `rag-chatbot` (or your preferred name)
    *   **Region**: Closest to you (e.g., Oregon, Frankfurt)
    *   **Branch**: `main`
    *   **Runtime**: `Python 3`
    *   **Build Command**: `./build.sh`
    *   **Start Command**: `gunicorn config.wsgi:application`
    *   **Instance Type**: **Free**

## Step 3: Configure Environment Variables

Scroll down to the **Environment Variables** section and add the following:

| Key | Value |
| :--- | :--- |
| `PYTHON_VERSION` | `3.11.0` |
| `SECRET_KEY` | *(Generate a random string)* |
| `DEBUG` | `False` |
| `GROQ_API_KEY` | `your_actual_groq_api_key_here` |
| `Forb_Use_Sqlite` | `True` (Optional: If you want to use SQLite on disk, warning: data is ephemeral on free tier)* |

> **Note on Database**: Render Free Tier Web Services have **ephemeral files**. This means your SQLite database will reset every time the app restarts.
> For a persistent database, you should create a **Render PostgreSQL** database (also has a free tier) and copy the `Internal DB URL` to a `DATABASE_URL` environment variable.

## Step 4: Deploy

1.  Click **Create Web Service**.
2.  Watch the logs. It will install dependencies, collect static files, and migrate the database.
3.  Once it says "Live", click the URL at the top (e.g., `https://rag-chatbot-xxxx.onrender.com`).

## ⚠️ Important Notes for Free Tier

1.  **Spin Down**: Free web services verify spin down after 15 minutes of inactivity. The first request after that will take significantly longer (30s+).
2.  **Ephemeral Files**: Any uploaded files (PDFs) or SQLite database changes will be **lost** when the app restarts or spins down.
    *   **Solution**: Use a persistent Postgres DB for chat history.
    *   **Solution**: Since we removed Firebase Storage, file uploads effectively rely on the local disk. They will disappear on restart. For a production app, you would need AWS S3 or similar.

## Troubleshooting

*   **Build Fails**: Check the logs. Common issues are missing dependencies in `requirements.txt`.
*   **Application Error**: Check the "Logs" tab.
    *   If you see "DisallowedHost", ensure `ALLOWED_HOSTS` in `settings.py` includes your Render URL (we set it to `['*']` so this shouldn't happen).
