# How to Share Your App (Quick Guide)

You can share your local Metadata Extractor with anyone on the internet using a free tool called **ngrok**.

## Steps

1.  **Download ngrok**:
    -   Go to [ngrok.com/download](https://ngrok.com/download).
    -   Download the version for **Windows**.
    -   Unzip it (extract `ngrok.exe`).

2.  **Start your Server**:
    -   Make sure your AIKosh app is running (`run_server.bat` or `uvicorn api:app`).
    -   It should be on `http://localhost:8000`.

3.  **Run ngrok**:
    -   **Easier Method**: Copy `ngrok.exe` into this project folder and double-click `share_app.bat`.
    -   **Manual Method**: Open a terminal in the folder where `ngrok.exe` is and run:
        ```cmd
        ngrok http 8000
        ```

4.  **Get the URL**:
    -   ngrok will show a screen like this:
        ```
        Forwarding                    https://a1b2-c3d4.ngrok-free.app -> http://localhost:8000
        ```
    -   Copy the `https://...` URL.

5.  **Share**:
    -   Send that URL to your colleague or friend.
    -   They can open it on their phone or laptop and use the app just like you do!

> [!NOTE]
> The link will stop working when you close the ngrok terminal.
