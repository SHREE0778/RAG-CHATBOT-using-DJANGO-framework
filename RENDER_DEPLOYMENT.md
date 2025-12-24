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

## Step 4: Set up Free PostgreSQL (Recommended)

Since the free tier web service has ephemeral storage (data is lost on restart), you should use a separate database.

1.  Go back to the [Render Dashboard](https://dashboard.render.com/).
2.  Click **New +** -> **PostgreSQL**.
3.  **Name**: `rag-chatbot-db`
4.  **Instance Type**: **Free**
5.  Click **Create Database**.
6.  Wait for it to become "Available".
7.  Copy the **Internal DB URL** (it looks like `postgres://rag_chatbot_user:password@hostname/rag_chatbot`).
8.  Go back to your **Web Service** -> **Environment**.
9.  Add a new variable:
    *   **Key**: `DATABASE_URL`
    *   **Value**: *(Paste the Internal DB URL)*

## Step 5: Deploy

1.  Click **Create Web Service** (or **Manual Deploy** if you already created it).
2.  Watch the logs. It will install dependencies, collect static files, and migrate the database.
3.  Once it says "Live", click the URL at the top (e.g., `https://rag-chatbot-xxxx.onrender.com`).

## ⚠️ Important Notes for Free Tier

1.  **Spin Down**: Free web services verify spin down after 15 minutes of inactivity. The first request after that will take significantly longer (30s+).
2.  **Ephemeral Files**: Any uploaded files (PDFs) will still be lost on restart because we are saving them to the local filesystem.
    *   **Workaround**: Upload files again if they are missing, or upgrade to a plan that supports persistent disks (or use AWS S3).
    *   **Database Data**: Chat history and user accounts **WILL** be saved now that you are using Postgres.

## Troubleshooting

*   **Build Fails**: Check the logs. Common issues are missing dependencies in `requirements.txt`.
*   **Application Error**: Check the "Logs" tab.
    *   If you see "DisallowedHost", ensure `ALLOWED_HOSTS` in `settings.py` includes your Render URL (we set it to `['*']` so this shouldn't happen).
