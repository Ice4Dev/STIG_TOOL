import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import ctypes
import sys
from unittest import result

# ---------------- ADMIN CHECK ----------------
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

if not is_admin():
    relaunch_as_admin()

# ---------------- REGISTRY FUNCTIONS ----------------
def get_reg_value(path, name):
    cmd = f'powershell -Command "if (Test-Path \'{path}\') {{ Get-ItemProperty -Path \'{path}\' -Name \'{name}\' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty {name} }} else {{ Write-Output \'__MISSING_PATH__\' }}"'

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)

        output = result.stdout.strip()

        if output == "__MISSING_PATH__":
            return "__MISSING_PATH__"

        elif result.returncode == 0 and output != "":
            return output

        return None

    except:
        return None

def set_reg_value(path, name, value):
    try:
        if isinstance(value, int):
            ps_value = value
        else:
            ps_value = f'"{value}"'

        cmd = f'powershell -Command "Set-ItemProperty -Path \'{path}\' -Name \'{name}\' -Value {ps_value}"'

        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.returncode == 0
    except:
        return False

# ---------------- CHECK LOGIC ----------------
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

    for row in tree.get_children():
        tree.delete(row)

    total = passed = failed = 0

    for check in data['checks']:
        path = check.get('path')
        name = check.get('name')
        expected = check.get('expected')
        stig = check.get('stig', 'None')

        if not all([path, name, expected is not None]):
            continue

        total += 1
        actual = get_reg_value(path, name)
        if actual == "__MISSING_PATH__":
            status = "FAIL"
            failed += 1
            actual_display = "PATH NOT FOUND"
        elif actual is None:
            status = "FAIL"
            failed += 1
            actual_display = "None"
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

        tree.insert(
            "", "end",
            values=("☐", stig, status, actual_display, expected, path, name),
            tags=(status,)
        )

    compliance = (passed / total * 100) if total else 0
    summary_label.config(
        text=f"Total: {total}   Passed: {passed}   Failed: {failed}   Compliance: {compliance:.2f}%"
    )

# ---------------- UI ACTIONS ----------------
def browse_file(entry):
    file_path = filedialog.askopenfilename(
        title="Select JSON File",
        filetypes=[("JSON Files", "*.json")]
    )
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

def start_scan(entry, tree, summary_label):
    json_file = entry.get()
    if not json_file:
        messagebox.showwarning("Warning", "Please select a JSON file.")
        return
    run_checks(json_file, tree, summary_label)

def toggle_checkbox(event):
    region = tree.identify_region(event.x, event.y)
    column = tree.identify_column(event.x)
    item = tree.identify_row(event.y)

    # If header clicked
    if region == "heading" and column == "#1":
        toggle_select_all()
        return

    # If cell clicked
    if column == "#1" and item:
        current = tree.set(item, "Select")
        tree.set(item, "Select", "☑" if current == "☐" else "☐")


def select_all(tree):
    for item in tree.get_children():
        tree.set(item, "Select", "☑")

def select_failed(tree):
    for item in tree.get_children():
        status = tree.set(item, "Status")
        if status == "FAIL":
            tree.set(item, "Select", "☑")
        else:
            tree.set(item, "Select", "☐")

def clear_selection(tree):
    for item in tree.get_children():
        tree.set(item, "Select", "☐")

def remediate_selected(tree, entry, summary_label):
    confirm = messagebox.askyesno(
        "Confirm Remediation",
        "Apply fixes to selected registry keys?"
    )
    if not confirm:
        return

    success = 0
    failed = 0

    for item in tree.get_children():
        selected = tree.set(item, "Select")
        status = tree.set(item, "Status")

        if selected != "☑" or status != "FAIL":
            continue

        path = tree.set(item, "Path")
        name = tree.set(item, "Name")
        expected = tree.set(item, "Expected")

        # Detect missing path BEFORE attempting fix
        check_path = get_reg_value(path, name)
        if check_path == "__MISSING_PATH__":
            failed += 1
            messagebox.showwarning(
                "Path Not Found",
                f"Registry path not found:\n{path}\n\nSoftware may not be installed or configured correctly.\n\nManual remediation required."
            )
            continue
        try:
            if expected.isdigit():
                expected = int(expected)
        except:
            pass

        result = set_reg_value(path, name, expected)

        if result == True:
            success += 1

        elif result == False:
            failed += 1
            messagebox.showwarning(
                "Write Failed",
                f"{name} could not be applied (value missing after write)."
            )

        else:
            failed += 1

    messagebox.showinfo(
        "Remediation Complete",
        f"Successful: {success}\nFailed: {failed}"
    )

    start_scan(entry, tree, summary_label)

def toggle_select_all():
    items = tree.get_children()

    # Check if any are selected
    any_selected = any(tree.set(item, "Select") == "☑" for item in items)

    # If any selected → clear all, else select all
    new_value = "☐" if any_selected else "☑"

    for item in items:
        tree.set(item, "Select", new_value)

# ---------------- GUI SETUP ----------------
root = tk.Tk()
root.title("SII STIG Checker (Windows)")
root.geometry("1000x650")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("default")

style.configure("TFrame", background="#1e1e1e")
style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Segoe UI", 15, "bold"))
style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"))
style.configure("TButton", font=("Segoe UI", 10), padding=6)
style.configure("TEntry", fieldbackground="#2b2b2b", foreground="white")

style.configure("Treeview",
                background="#2b2b2b",
                foreground="white",
                rowheight=25,
                fieldbackground="#2b2b2b")

style.map("Treeview", background=[("selected", "#3a3a3a")])

# ---------------- HEADER ----------------
header = ttk.Label(root, text="SII STIG Checker (Windows)", style="Header.TLabel")
header.pack(pady=10)

# ---------------- FILE INPUT ----------------
file_frame = ttk.Frame(root)
file_frame.pack(pady=10, padx=10, fill="x")

entry = ttk.Entry(file_frame)
entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

browse_btn = ttk.Button(file_frame, text="Browse", command=lambda: browse_file(entry))
browse_btn.pack(side="left")

# ---------------- BUTTONS ----------------
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

run_btn = ttk.Button(button_frame, text="Run Scan",
                     command=lambda: start_scan(entry, tree, summary_label))
run_btn.pack(side="left", padx=5)

remediate_btn = ttk.Button(button_frame, text="Remediate Selected",
                           command=lambda: remediate_selected(tree, entry, summary_label))
remediate_btn.pack(side="left", padx=5)


select_failed_btn = ttk.Button(button_frame, text="Select Failed",
                               command=lambda: select_failed(tree))
select_failed_btn.pack(side="left", padx=5)


# ---------------- TABLE FRAME ----------------
table_frame = ttk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=10, pady=10)

scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")

tree = ttk.Treeview(
    table_frame,
    columns=("Select", "STIG", "Status", "Actual", "Expected", "Path", "Name"),
    show="headings",
    yscrollcommand=scroll_y.set,
    xscrollcommand=scroll_x.set
)

scroll_y.config(command=tree.yview)
scroll_x.config(command=tree.xview)

scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")
tree.pack(fill="both", expand=True)

# ---------------- COLUMN SETUP ----------------
tree.heading("Select", text="✔")
tree.column("Select", width=50, anchor="center", stretch=False)

tree.heading("STIG", text="STIG")
tree.column("STIG", width=120, anchor="center")

tree.heading("Status", text="Status")
tree.column("Status", width=80, anchor="center")

tree.heading("Actual", text="Actual")
tree.column("Actual", width=120, anchor="center")

tree.heading("Expected", text="Expected")
tree.column("Expected", width=150, anchor="center")

tree.heading("Path", text="Registry Path")
tree.column("Path", width=400, anchor="w", stretch=True)

tree.heading("Name", text="Key Name")
tree.column("Name", width=200, anchor="w", stretch=True)

# ---------------- TAG COLORS ----------------
tree.tag_configure("PASS", foreground="#00ff88")
tree.tag_configure("FAIL", foreground="#ff4d4d")

tree.bind("<Button-1>", toggle_checkbox)

# ---------------- SUMMARY ----------------
summary_label = ttk.Label(root, text="No scan run yet.")
summary_label.pack(pady=10)

root.mainloop()
