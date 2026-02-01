# Deployment Guide

This guide covers how to deploy the AI Hackathon Metadata Harmonizer project.

## Prerequisites
- **Git**
- **Docker** (Recommended) or **Python 3.10+**
- **Google Gemini API Key**

---

## Option 1: Docker (Recommended)
Containerization is the easiest way to run the application without worrying about system dependencies (like Ghostscript or OpenCV drivers).

### 1. Build the Image
Run this command in the project root:
```bash
docker build -t aikosh-harmonizer .
```

### 2. Run the Container
Replace `YOUR_API_KEY` with your actual key. We map the `uploads` and `outputs` directories so your data persists even if the container restarts.

```bash
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY="YOUR_API_KEY_HERE" \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  --name harmonizer \
  aikosh-harmonizer
```

- Access the app at `http://localhost:8000`

---

## Option 2: Cloud VM (Ubuntu/DigitalOcean/AWS)
If you prefer running directly on a server (e.g., an EC2 instance).

### 1. Install System Dependencies
The project relies on `ghostscript` for table extraction and OpenGl libraries for OCR.
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv libgl1-mesa-glx libglib2.0-0 ghostscript
```

### 2. Clone & Setup
```bash
git clone <repository-url>
cd ai_hackathon-main

# Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install Python Libs
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file:
```bash
nano .env
# Add: GEMINI_API_KEY=your_key_here
```

### 4. Run with Systemd (Production)
Don't use `uvicorn` directly in production. Use a systemd service to keep it alive.

Create file `/etc/systemd/system/harmonizer.service`:
```ini
[Unit]
Description=AIKosh Harmonizer API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/ai_hackathon-main
ExecStart=/home/ubuntu/ai_hackathon-main/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable harmonizer
sudo systemctl start harmonizer
```

---

## Option 3: Render + GitHub
Deploy from a GitHub repo so Render builds and runs the app automatically.

### 1. Connect GitHub
- Go to [Render](https://render.com) → New → Web Service.
- Connect your GitHub account and select the repository (e.g. `ai_hackathon-main`).
- Root directory: set to the app folder if the repo has nested structure (e.g. `ai_hackathon-main/ai_hackathon-main`).

### 2. Build & Run
- **Build Command:** `pip install -r requirements.txt` (or use Docker: set Dockerfile path).
- **Start Command:** `uvicorn api:app --host 0.0.0.0 --port $PORT`
- **Environment:** Add variables in Render dashboard (see below).

### 3. Environment Variables (Render)
| Variable | Required | Notes |
|---------|----------|--------|
| `GEMINI_API_KEY` | Yes | From Google AI Studio |
| `MAX_UPLOAD_MB` | No | Default 25. Render free tier allows ~25MB request body; set lower if you see 413. |
| `DATABASE_URL` | No | Postgres connection string (Render Postgres). If unset, uses local JSON cache. |
| `REDIS_URL` | No | For Celery async workers. If unset, uses in-process BackgroundTasks. |
| `USE_CELERY` | No | Set `true` to use Celery (requires Redis). |

### 4. Avoiding 413 (Payload Too Large)
- Render limits request body size. Default app limit is **25MB** (`MAX_UPLOAD_MB=25`).
- If PDFs still return 413, set `MAX_UPLOAD_MB=20` or lower to stay under platform limits.
- The UI shows the current limit from `/health` (max_upload_mb).

---

## Cloud Platform Notes
- **Render/Railway**: You can deploy using the `Dockerfile` or native Python (see Option 3).
- **Warning**: Ephemeral filesystems: files in `uploads/` and `outputs/` are lost on restart unless you use a Persistent Disk (Render paid) or external storage (S3 + `USE_S3=true`).
