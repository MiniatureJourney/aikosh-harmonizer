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

This is where the magic happens.

1.  Go to your **Render Dashboard**.
2.  Click **"New +"** (top right) -> Select **"Web Service"**.
3.  You should see your `aikosh-harmonizer` repository in the list. Click **"Connect"**.
4.  **Configure the settings**:
    *   **Name**: `aikosh-harmonizer` (or whatever you want your site to be called).
    *   **Region**: Choose the one closest to your customers (e.g., Singapore or Frankfurt).
    *   **Branch**: `master` (or `main`).
    *   **Runtime**: Select **"Docker"** (This is VERY important).
5.  **Environment Variables**:
    *   Scroll down to "Environment Variables".
    *   Click "Add Environment Variable".
    *   **Key**: `GEMINI_API_KEY`
    *   **Value**: *Target your actual API Key here* (e.g., `AIzaSy...`).
6.  Click **"Create Web Service"**.

Render will now build your Commercial Website. It might take 5-10 minutes the first time. Watch the logs!

---

## Phase 5: Connect a Custom Domain (Optional)

To make it truly "Commercial" (like `www.yourcompany.com` instead of `onrender.com`):

1.  Buy a domain from Namecheap, GoDaddy, or Cloudflare.
2.  In Render dashboard: Go to **Settings** -> **Custom Domains**.
3.  Click **"Add Custom Domain"**.
4.  Enter your domain (e.g., `www.my-aikosh-tool.com`).
5.  Render will verify it and give you DNS records to add to your domain provider.

---

## Troubleshooting

- **"Build Failed"**: Check the logs. Did you forget to add the API Key?
- **"Application Error"**: This usually means the app started but crashed. Check the "Logs" tab in Render for Python errors.
