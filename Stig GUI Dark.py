import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import ctypes
import sys

# Check for admin rights and relaunch if not
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def relaunch_as_admin():
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, None, 1
    )
    sys.exit()

# Check for admin rights at startup
if not is_admin():
    relaunch_as_admin()
    
# ---------------- Registry Function ----------------
def get_reg_value(path, name):
    cmd = f'powershell -Command "Get-ItemProperty -Path \'{path}\' -Name \'{name}\' | Select-Object -ExpandProperty {name}"'
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except:
        return None

# ---------------- Run Checks ----------------
def run_checks(json_file, tree, summary_label):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load JSON:\n{e}")
        return

    if 'checks' not in data:
        messagebox.showerror("Error", "JSON must contain a 'checks' list.")
        return

    # Clear table
    for row in tree.get_children():
        tree.delete(row)

    total = passed = failed = 0

    for check in data['checks']:
        path = check.get('path')
        name = check.get('name')
        expected = check.get('expected')
        stig = check.get('stig', 'N/A')

        if not all([path, name, expected is not None]):
            continue

        total += 1
        actual = get_reg_value(path, name)

        if actual is None:
            status = "FAIL"
            failed += 1
            actual_display = "N/A"
        else:
            try:
                if isinstance(expected, int):
                    actual = int(actual)
                elif isinstance(expected, float):
                    actual = float(actual)
                else:
                    actual = str(actual)
            except:
                actual = str(actual)

            if actual == expected:
                status = "PASS"
                passed += 1
            else:
                status = "FAIL"
                failed += 1

            actual_display = actual

        # Insert into table
        tree.insert("", "end", values=(stig, status, actual_display, expected),
                    tags=(status,))

    compliance = (passed / total * 100) if total else 0
    summary_label.config(
        text=f"Total: {total}   Passed: {passed}   Failed: {failed}   Compliance: {compliance:.2f}%"
    )

# ---------------- File Picker ----------------
def browse_file(entry):
    file_path = filedialog.askopenfilename(
        title="Select JSON File",
        filetypes=[("JSON Files", "*.json")]
    )
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

# ---------------- Start Scan ----------------
def start_scan(entry, tree, summary_label):
    json_file = entry.get()
    if not json_file:
        messagebox.showwarning("Warning", "Please select a JSON file.")
        return
    run_checks(json_file, tree, summary_label)

# ---------------- GUI Setup ----------------
root = tk.Tk()
root.title("Erudio STIG Checker (Windows)")
root.geometry("900x600")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("default")

# Dark theme styling
style.configure("TFrame", background="#1e1e1e")
style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Segoe UI", 10))
style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
style.configure("TButton", font=("Segoe UI", 10), padding=6)
style.configure("TEntry", fieldbackground="#2b2b2b", foreground="white")

style.configure("Treeview",
                background="#2b2b2b",
                foreground="white",
                rowheight=25,
                fieldbackground="#2b2b2b")

style.map("Treeview",
          background=[("selected", "#3a3a3a")])

# PASS/FAIL colors
style.configure("PASS.Treeview", foreground="#00ff88")
style.configure("FAIL.Treeview", foreground="#ff4d4d")

# ---------------- Layout ----------------

# Header
header = ttk.Label(root, text="Erudio STIG Checker (Windows)", style="Header.TLabel")
header.pack(pady=10)

# File selection frame
file_frame = ttk.Frame(root)
file_frame.pack(pady=10, padx=10, fill="x")

entry = ttk.Entry(file_frame)
entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

browse_btn = ttk.Button(file_frame, text="Browse", command=lambda: browse_file(entry))
browse_btn.pack(side="left")

run_btn = ttk.Button(root, text="Run Scan",
                     command=lambda: start_scan(entry, tree, summary_label))
run_btn.pack(pady=5)

# Table
columns = ("STIG", "Status", "Actual", "Expected")
tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center")

tree.pack(fill="both", expand=True, padx=10, pady=10)

# Tag colors
tree.tag_configure("PASS", foreground="#00ff88")
tree.tag_configure("FAIL", foreground="#ff4d4d")

# Summary
summary_label = ttk.Label(root, text="No scan run yet.")
summary_label.pack(pady=10)

root.mainloop()