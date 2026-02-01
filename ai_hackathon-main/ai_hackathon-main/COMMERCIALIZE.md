# Commercialization Guide: From Code to Website

This document is your **Master Plan** to take this project and turn it into a live, commercial website accessible to anyone on the internet.

We will use **Render** for hosting because it is the **Easiest** and **Fastest** way to deploy this specific project. It handles all the complex installation (like Ghostscript and OpenCV) automatically using the files I just added to your project.

---

## Phase 1: Preparation (Already Done!)

I have already added the necessary "wiring" files to your project folders:
1.  **`Dockerfile`**: Tells the server how to install your app.
2.  **`.dockerignore`**: Keeps your deployment fast and secure.
3.  **`docker-compose.yml`**: Allows you to test it locally if you ever install Docker.

**You do NOT need to write any code.**

---

## Phase 2: Sign Up (5 Minutes)

1.  **GitHub Account**
    *   Go to [github.com](https://github.com/) and Sign Up.
    *   *Why?* Render pulls your code directly from GitHub.

2.  **Render Account**
    *   Go to [dashboard.render.com/register](https://dashboard.render.com/register).
    *   **Crucial**: Sign up using the **"Continue with GitHub"** button. This links them automatically.

---

## Phase 3: Push Your Code (5 Minutes)

You need to get your code from your computer to GitHub.

1.  Open your terminal/command prompt in the `ai_hackathon-main` folder.
2.  Run these commands one by one:

```bash
# 1. Initialize Git (if not already done)
git init

# 2. Add all your files
git add .
git commit -m "Commercial release ready"

# 3. Create a repo on GitHub website (Click 'New Repository' -> Name it 'aikosh-harmonizer')
# 4. Connect it (Copy the commands GitHub gives you, they look like this):
git remote add origin https://github.com/YOUR_USERNAME/aikosh-harmonizer.git
git push -u origin master
```

---

## Phase 4: Go Live! (3 Minutes)

# Commercial Deployment Guide

This guide details how to deploy **AIKosh Enterprise** to a commercial environment like **Render**.

## 1. Prerequisites
Ensure your project is compliant with the following structure (already configured):
- `Dockerfile`: Defines the system environment (Python 3.11).
- `.dockerignore`: Excludes unnecessary files.
- `requirements.txt`: Lists all Python dependencies.

## 2. Deployment Steps (Render)

### Step 1: Create Web Service
1.  Log in to [Render.com](https://render.com).
2.  Click **New +** -> **Web Service**.
3.  Connect your GitHub repository: `aikosh-harmonizer`.
4.  Give it a name (e.g., `aikosh-app`).

### Step 2: Configure Environment
In the setup screen, ensure these settings are correct:

| Setting | Value |
| :--- | :--- |
| **Runtime** | `Docker` |
| **Region** | `Singapore` (or nearest to you) |
| **Branch** | `main` |
| **Root Directory** | `ai_hackathon-main/ai_hackathon-main` |

### Step 3: Environment Variables
You **MUST** set the following environment variable for the AI to work:

1.  Click **"Advanced"** or **"Environment Variables"**.
2.  Add Key: `GEMINI_API_KEY`
3.  Add Value: `(Your Google Gemini API Key)`

Click **Create Web Service**. Render will build and deploy your app.

---

## 3. Enterprise Scaling (Optional)
The application handles scaling automatically if you provide the following optional configuration variables. **You do not need to change the code.**

### Phase A: Persistent Storage (AWS S3)
*Prevents data loss when the server restarts.*
- `USE_S3`: `true`
- `S3_BUCKET_NAME`: `your-bucket-name`
- `AWS_ACCESS_KEY_ID`: `...`
- `AWS_SECRET_ACCESS_KEY`: `...`
- `AWS_REGION`: `us-east-1`

### Phase B: Production Database (PostgreSQL)
*Enables robust data management and querying.*
- `DATABASE_URL`: (Render automatically provides this if you add a Postgres database).

### Phase C: High-Performance Workers (Celery)
*Handles heavy traffic without freezing the app.*
- `USE_CELERY`: `true`
- `REDIS_URL`: (Render automatically provides this if you add a Redis instance).

---

## 4. Troubleshooting
- **502 Bad Gateway**: Usually means the application crashed. Check the **Logs** tab.
- **ModuleNotFoundError**: A dependency is missing from `requirements.txt`.
- **Memory Error**: The free tier has 512MB RAM. We have optimized the code to fit, but extremely large PDF processing might still spike memory.
