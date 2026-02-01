# AIKosh Harmonizer

**Make Government Data AI-Ready, Instantly.**

The **AIKosh Harmonizer** is a tool that takes messy government files (PDFs, CSVs, Excel) and automatically organizes them. It extracts important details (metadata) like **Title**, **Ministry**, **Time Period**, and **Location** and formats them into a standard, computer-friendly structure (JSON).

Simply put: **Drag in a file, get clean data out.**

---

## ⚡ Quick Start (For Beginners)

You don't need to be a coder to use this. Follow these 3 steps:

### 1. Download & Install
1.  **Download** this folder to your computer.
2.  Open the folder.
3.  Double-click **`start_app.bat`** (or `run_server.bat`).
    *   *Note: A black window (terminal) will open. Keep it open! This is the engine running in the background.*

### 2. Open the App
1.  Open your web browser (Chrome, Edge, etc.).
2.  Go to this address: **[http://localhost:8000](http://localhost:8000)**

### 3. Use It
1.  **Drag and Drop** your files (PDF, CSV, or Excel) into the box on the screen.
2.  Wait for the status to say **"Ready"**.
3.  Click on the file name to see the extracted details.
4.  Click **"Download JSON"** to save the clean data.

---

## 🔑 Features at a Glance

*   **Works with Everything**: Handles scanned PDFs, digital PDFs, Excel sheets, and CSVs.
*   **Smart Filling**: If a file says "Hingoli" but misses the State, our AI fills in "Maharashtra" automatically.
*   **Standardized**: All output follows the strict **IDMO (India Data Management Office)** standards.
*   **Readiness Score**: Tells you how "clean" your file is (from 0 to 100%).

---

## 👨‍💻 For Developers (Technical Setup)

If you want to modify the code or contribute:

1.  **Clone the Repo**:
    ```bash
    git clone https://github.com/your-username/ai-hackathon.git
    cd ai-hackathon-main
    ```

2.  **Install Requirements**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set API Key**:
    *   Create a `.env` file.
    *   Add: `GEMINI_API_KEY=your_key_here`

4.  **Run Server**:
    ```bash
    uvicorn api:app --reload
    ```

---

## 📄 License
This project is open-source under the **MIT License**.
