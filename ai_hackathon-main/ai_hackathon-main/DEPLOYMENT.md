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

## Cloud Platform Notes
- **Render/Railway**: You can deploy using the `Dockerfile`.
- **Warning**: These platforms often have "ephemeral filesystems". Files uploaded to `uploads/` will be **deleted** when the app restarts unless you configure a "Persistent Volume" (available on Railway/Render Paid plans).
