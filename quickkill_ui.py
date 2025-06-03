import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import json
import os

# --- Constants ---
CONFIG_FILE = "config.json"

# --- Function to get unique running app names ---
def get_running_apps():
    app_names = set()
    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info['name']
            if name and name.lower() != "system idle process":
                app_names.add(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return sorted(app_names)

# --- Function to save selected apps to config.json ---
def save_selected_apps():
    selected = [app for app, var in checkboxes.items() if var.get()]
    data = {"apps": selected}
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        messagebox.showinfo("Saved", "Selected apps have been saved successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save config: {e}")

# --- Function to kill selected apps ---
def kill_selected_apps():
    selected = [app for app, var in checkboxes.items() if var.get()]
    if not selected:
        messagebox.showwarning("No Selection", "Please select at least one app to kill.")
        return
    
    killed_apps = []
    failed_apps = []
    for proc in psutil.process_iter(['name', 'pid']):
        try:
            if proc.info['name'] in selected:
                proc.kill()
                killed_apps.append(proc.info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            failed_apps.append(proc.info['name'])
    
    msg = f"Killed apps: {', '.join(set(killed_apps))}" if killed_apps else "No apps were killed."
    if failed_apps:
        msg += f"\nFailed to kill: {', '.join(set(failed_apps))}"
    messagebox.showinfo("Kill Result", msg)

# --- Main UI setup ---
def create_app_grid(app_names):
    for i, app in enumerate(app_names):
        var = tk.BooleanVar()
        cb = ttk.Checkbutton(frame, text=app, variable=var)
        cb.grid(row=i // 3, column=i % 3, padx=10, pady=5, sticky='w')
        checkboxes[app] = var

# --- Load existing config to pre-check saved apps ---
def load_existing_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                saved_apps = data.get("apps", [])
                for app in saved_apps:
                    if app in checkboxes:
                        checkboxes[app].set(True)
        except Exception:
            pass

# --- GUI Initialization ---
root = tk.Tk()
root.title("QuickKill App Selector")
root.geometry("600x400")

main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(main_frame)
scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
frame = ttk.Frame(canvas)

frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# --- Checkbox Dictionary ---
checkboxes = {}

# --- Load apps into grid ---
app_list = get_running_apps()
create_app_grid(app_list)
load_existing_config()

# --- Buttons Frame ---
btn_frame = ttk.Frame(root)
btn_frame.pack(pady=10)

# --- Save Button ---
save_btn = ttk.Button(btn_frame, text="Save Selection", command=save_selected_apps)
save_btn.grid(row=0, column=0, padx=10)

# --- Kill Button ---
kill_btn = ttk.Button(btn_frame, text="Kill Selected Apps", command=kill_selected_apps)
kill_btn.grid(row=0, column=1, padx=10)

# --- Start GUI ---
root.mainloop()
