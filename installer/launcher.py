"""
MindSphere desktop launcher.
Runs the FastAPI server locally and opens the user's browser.
On first launch, prompts for Gemini API key via a small webview window.
"""
import os
import sys
import time
import socket
import threading
import webbrowser
from pathlib import Path

# Make sure backend/ is importable whether running from source or PyInstaller bundle
if getattr(sys, "frozen", False):
    # Running from PyInstaller bundle
    BASE = Path(sys._MEIPASS)
else:
    # Running from source
    BASE = Path(__file__).parent.parent

BACKEND_DIR = BASE / "backend"
FRONTEND_DIR = BASE / "frontend"
sys.path.insert(0, str(BACKEND_DIR))

from config import has_api_key, set_api_key  # noqa: E402


def find_free_port(start: int = 8000, end: int = 8050) -> int:
    """Find a free localhost port in the given range."""
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free port available in range")


def start_server(port: int):
    """Run uvicorn in this process (blocking)."""
    import uvicorn
    os.chdir(BACKEND_DIR)
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=port,
        log_level="warning",
    )


def wait_for_server(port: int, timeout: float = 15.0) -> bool:
    """Wait until server is responding, return True if ready."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(0.3)
    return False


def show_setup_window():
    """Tiny webview to capture Gemini API key on first run."""
    import webview

    html = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>MindSphere Setup</title>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
          font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
          background: #f5f1ea;
          color: #2c3530;
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 24px;
        }
        .card {
          background: #fbf8f3;
          border: 1px solid #e0d8c8;
          border-radius: 16px;
          padding: 32px;
          max-width: 460px;
          width: 100%;
          box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        }
        h1 {
          font-size: 22px;
          margin-bottom: 8px;
          background: linear-gradient(135deg, #5a7a58 0%, #a8b89b 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
        p { color: #6b7770; font-size: 14px; line-height: 1.55; margin-bottom: 20px; }
        a { color: #7a9b76; }
        label { display: block; font-size: 13px; color: #6b7770; margin-bottom: 6px; }
        input {
          width: 100%;
          padding: 12px 14px;
          font-size: 14px;
          font-family: monospace;
          background: #f5f1ea;
          border: 1px solid #e0d8c8;
          border-radius: 10px;
          color: #2c3530;
        }
        input:focus { outline: none; border-color: #7a9b76; }
        button {
          width: 100%;
          margin-top: 16px;
          padding: 12px;
          font-size: 15px;
          font-weight: 500;
          background: #7a9b76;
          color: #fbf8f3;
          border: none;
          border-radius: 10px;
          cursor: pointer;
          transition: background 0.15s;
        }
        button:hover { background: #5a7a58; }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        .err { color: #b56654; font-size: 13px; margin-top: 10px; min-height: 18px; }
        .note { font-size: 12px; color: #6b7770; margin-top: 14px; }
      </style>
    </head>
    <body>
      <div class="card">
        <h1>🧠 Welcome to MindSphere</h1>
        <p>To start, paste your Google Gemini API key below. It's free at <a href="https://aistudio.google.com/apikey" target="_blank">aistudio.google.com/apikey</a>.</p>
        <label>Gemini API Key</label>
        <input id="key" type="password" placeholder="AIza..." autofocus />
        <button id="save">Save & Continue</button>
        <div class="err" id="err"></div>
        <p class="note">Your key stays on this device. Stored in your app data folder, never sent anywhere except Google's Gemini API.</p>
      </div>
      <script>
        const btn = document.getElementById('save');
        const input = document.getElementById('key');
        const err = document.getElementById('err');

        async function submit() {
          const k = input.value.trim();
          if (!k.startsWith('AIza') || k.length < 30) {
            err.textContent = "That doesn't look like a valid Gemini key. It should start with 'AIza'.";
            return;
          }
          btn.disabled = true;
          btn.textContent = 'Saving...';
          await window.pywebview.api.save_key(k);
        }
        btn.addEventListener('click', submit);
        input.addEventListener('keydown', e => { if (e.key === 'Enter') submit(); });
      </script>
    </body>
    </html>
    """

    class Api:
        def save_key(self, key):
            set_api_key(key)
            window.destroy()

    window = webview.create_window(
        "MindSphere Setup",
        html=html,
        width=520,
        height=440,
        resizable=False,
        js_api=Api(),
    )
    webview.start()


def main():
    print("MindSphere starting...")

    # First-run: show setup window if no key
    if not has_api_key():
        print("No API key found, showing setup...")
        show_setup_window()
        if not has_api_key():
            print("Setup cancelled. Exiting.")
            sys.exit(0)

    # Find a free port
    port = find_free_port()
    url = f"http://127.0.0.1:{port}"
    print(f"Starting server on {url}")

    # Start server in background thread
    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()

    # Wait for server
    if not wait_for_server(port):
        print("Server failed to start.")
        sys.exit(1)

    # Open browser
    print(f"Opening browser at {url}")
    webbrowser.open(url)

    # Keep main thread alive (server is daemon)
    try:
        while server_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down.")
        sys.exit(0)


if __name__ == "__main__":
    main()