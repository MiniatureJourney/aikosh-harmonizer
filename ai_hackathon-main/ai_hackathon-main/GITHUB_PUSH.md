# GitHub Push & Render Deployment Guide

Follow these steps to push your changes to GitHub. Once pushed, Render will automatically start a new deployment.

## 1. Push Changes to GitHub

Run these commands in your terminal (ensure you are in the project root):

### Stage your changes
Add all modified and new files to the staging area:
```powershell
git add .
```

### Commit your changes
Record your changes with a descriptive message:
```powershell
git commit -m "Your descriptive commit message here"
```

### Push to GitHub
Upload your changes to the remote repository. 
*Note: If your branch is not `main`, replace `main` with your branch name.*
```powershell
git push origin main
```

---

## 2. Render Deployment

### Automatic Deployment
By default, Render is configured to **Auto-Deploy**. As soon as you run `git push`, Render will:
1. Detect the new commit on your branch.
2. Trigger a new build.
3. Start the deployment process.

### Monitor Progress
You can monitor the build logs and deployment status at:
- [Render Dashboard](https://dashboard.render.com/)
- Select your **Web Service** (e.g., `aikosh-harmonizer`).
- View the **Events** or **Logs** tab.

### Manual Redeploy (If needed)
If you want to restart the deployment without making code changes:
1. Go to your service on the **Render Dashboard**.
2. Click the **Manual Deploy** button (top right).
3. Select **Clear Build Cache & Deploy** for a fresh start.

---

## Quick Reference (One-liner)
If you just want to push everything quickly:
```powershell
git add . 
git commit -m "Update" 
git push origin main
```
