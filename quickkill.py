import json
import psutil
import keyboard
import logging
from datetime import datetime

# --- Logging Setup ---
logging.basicConfig(
    filename='logs/quickkill.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- Load Config ---
def load_config():
    try:
        with open('config.json', 'r') as file:
            data = json.load(file)
            return data.get("apps", [])
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return []

# --- Kill Target Processes ---
def kill_apps(app_names):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] in app_names:
                proc.kill()
                logging.info(f"Killed: {proc.info['name']} (PID {proc.info['pid']})")
        except Exception as e:
            logging.error(f"Error killing process {proc.info.get('name', 'Unknown')} : {e}")

# --- Main Listener ---
def main():
    app_names = load_config()
    print("QuickKill running. Press Ctrl+Shift+Q to close apps.", flush=True)

    keyboard.add_hotkey('ctrl+shift+q', lambda: kill_apps(app_names))
    keyboard.wait('esc')  # Stops when Esc is pressed

if __name__ == "__main__":
    main()
