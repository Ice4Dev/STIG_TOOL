import json
import subprocess
import tkinter as tk
from tkinter import filedialog

def get_reg_value(path, name):
    cmd = f'powershell -Command "Get-ItemProperty -Path \'{path}\' -Name \'{name}\' | Select-Object -ExpandProperty {name}"'
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)
        return result.stdout.strip() if result.returncode == 0 else None
    except:
        return None

def run_scan():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not file_path:
        return

    output.delete("1.0", tk.END)

    try:
        with open(file_path) as f:
            data = json.load(f)
    except:
        output.insert(tk.END, "Error reading JSON file\n")
        return

    passed = 0
    failed = 0

    for check in data.get("checks", []):
        path = check.get("path")
        name = check.get("name")
        expected = check.get("expected")
        stig = check.get("stig", "N/A")

        actual = get_reg_value(path, name)

        if actual is None:
            output.insert(tk.END, f"FAIL: {stig} - Could not read {name}\n")
            failed += 1
            continue

        try:
            if isinstance(expected, int):
                actual = int(actual)
        except:
            pass

        if actual == expected:
            output.insert(tk.END, f"PASS: {stig} - {name} = {actual}\n")
            passed += 1
        else:
            output.insert(tk.END, f"FAIL: {stig} - {name} = {actual}, expected {expected}\n")
            failed += 1

    total = passed + failed
    compliance = (passed / total * 100) if total > 0 else 0

    output.insert(tk.END, "\n=== Summary ===\n")
    output.insert(tk.END, f"Total: {total}\n")
    output.insert(tk.END, f"Passed: {passed}\n")
    output.insert(tk.END, f"Failed: {failed}\n")
    output.insert(tk.END, f"Compliance: {compliance:.2f}%\n")
