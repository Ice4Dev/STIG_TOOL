# STIG_TOOL

# App_Main.py / SII_STIG_Checker.exe
This Python program is a Windows-based STIG compliance checker and remediation tool with a graphical interface. It first ensures the program is running with administrator privileges so it can access and modify Windows Registry settings. The user then selects a JSON file that contains a list of security checks, where each check includes a registry path, key name, expected secure value, and a STIG ID. The program scans each registry entry using PowerShell commands and compares the actual system value against the expected value. The results are displayed in a table showing whether each check passed or failed, along with the actual and expected values.
Unlike a basic checker, this version also includes remediation capabilities, allowing the user to select failed checks and automatically attempt to fix them by writing the correct values back into the registry. It includes safety checks to detect missing registry paths or group policy–controlled settings, and it warns the user when manual intervention is required. The GUI also allows users to select failed items, toggle selections, and run scans again after remediation. Overall, this tool not only audits system security settings but can also help automatically correct misconfigurations to bring a system closer to STIG compliance.

# command line tool.py
This Python script is a command-line Windows STIG compliance checker. It reads a JSON file that contains a list of security checks, where each check specifies a Windows Registry path, a registry key name, and an expected secure value. For each check, the script uses a PowerShell command (run through Python’s subprocess module) to retrieve the actual value from the Windows Registry. It then compares the retrieved value with the expected value from the JSON file.
If the values match, the script prints a “PASS” message showing the STIG ID and the registry setting. If the values do not match or cannot be retrieved, it prints a “FAIL” message with details about what was expected versus what was found. The script also includes error handling for missing files, invalid JSON formatting, timeouts, and conversion issues when comparing different data types. Overall, it provides a simple automated way to verify whether a Windows system is compliant with STIG security requirements directly from the terminal.

# test.json
This JSON file is a STIG compliance checklist used by the Python script to automatically verify Windows security settings. It contains a list of registry-based checks, where each entry defines a specific security configuration that the system should follow. Every check includes a registry path, the name of the registry value to inspect, the expected secure value, and a STIG identifier that references the official security rule being enforced.
When the script runs, it reads each item in this file and compares the actual Windows Registry value on the system against the expected value defined in the checklist. If the values match, the system is considered compliant for that rule; if they do not match or the value cannot be found, it is marked as non-compliant. Overall, this file serves as a baseline of required security configurations to ensure the system meets STIG hardening standards.

# SII STIG Checker (Windows)

A Windows GUI tool for validating and remediating registry settings against predefined STIG-style compliance checks.

This application is distributed as a standalone `.exe` and does not require Python or additional dependencies.

---

## Overview

SII STIG Checker reads a JSON configuration file containing registry compliance checks, compares the expected values against the current Windows Registry state, and displays results in a structured interface. It also provides optional remediation capabilities for failed checks.

---

## Features

- Scan Windows Registry using predefined checks
- Compare actual values against expected values
- Display results in a table-based GUI
- Highlight PASS and FAIL results
- Select individual or failed entries for remediation
- Automatically apply registry fixes for selected items
- Display compliance summary (total, passed, failed, percentage)
- Automatic administrator elevation on launch

---

## Getting Started

### Files Included

- SII STIG Checker.exe
- test.json (sample configuration file)

---

## Running the Application

1. Double-click `SII STIG Checker.exe`
2. If prompted, approve administrator elevation  
   (Administrator privileges are required for registry access and modification)

---

## Using the Application

### Step 1: Load a Configuration File

- Click the Browse button
- Select `test.json` or a custom JSON file following the same structure

---

### Step 2: Run a Scan

- Click Run Scan
- The application will evaluate all registry checks in the file
- Results will populate in the table view

---

### Step 3: Review Results

Each row represents a registry check.

Status values:

- PASS: Registry value matches expected value
- FAIL: Registry value does not match expected value or is missing

Special conditions:

- PATH NOT FOUND: The registry path does not exist
- None: Value could not be read or is missing

---

## Table Columns

| Column   | Description |
|----------|-------------|
| Select   | Checkbox for selecting entries |
| STIG     | Reference ID or identifier |
| Status   | PASS or FAIL result |
| Actual   | Current registry value |
| Expected | Expected value defined in JSON |
| Path     | Registry key path |
| Name     | Registry value name |

---

## Selection Controls

- Click a row checkbox to select an individual item
- Click the Select column header to toggle select all or clear all
- Click Select Failed to automatically select only failed entries

---

## Remediation

The tool supports automatic remediation of failed registry settings.

### Steps:

1. Select one or more failed entries
2. Click Remediate Selected
3. Confirm the action when prompted

### Behavior:

- The tool attempts to write the expected value to the registry
- After completion, the system is automatically re-scanned
- Results are updated in the interface

### Warnings:

- Registry paths that do not exist will not be created
- Some values may fail due to system restrictions or missing permissions
- Certain configurations may require manual remediation

---

## JSON Configuration Format

The application requires a JSON file containing a top-level `checks` array.

### Example

The JSON structure should look like this:

{
  "checks": [
    {
      "path": "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\Example",
      "name": "ExampleSetting",
      "expected": 1,
      "stig": "V-12345"
    }
  ]
}

---

## JSON Field Definitions

| Field     | Description |
|----------|-------------|
| path     | Full Windows Registry path |
| name     | Registry value name |
| expected | Expected value (string, integer, or float) |
| stig     | Optional STIG or reference identifier |

---

## Compliance Summary

After each scan, the application displays:

- Total checks evaluated
- Number of passed checks
- Number of failed checks
- Overall compliance percentage

---

## Example Workflow

1. Launch the application
2. Load `test.json`
3. Click Run Scan
4. Review failed checks
5. Use Select Failed to filter non-compliant entries
6. Click Remediate Selected
7. Run a new scan to verify changes

---

## Technical Notes

- Built with Python Tkinter (packaged as executable)
- Uses PowerShell commands for registry access
- Requires administrative privileges for full functionality
- Registry reads are performed using Get-ItemProperty
- Registry writes are performed using Set-ItemProperty
- Administrator elevation is handled automatically at startup

---

## Important Notes

- Administrative privileges are required
- Improper registry changes may affect system stability
- Always validate JSON files before use
- Use `test.json` to verify correct installation and functionality
- Missing registry paths are not automatically created

---

Specify license information here (e.g., MIT License, proprietary, etc.)
