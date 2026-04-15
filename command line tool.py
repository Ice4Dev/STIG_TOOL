import json
import subprocess
import sys

def get_reg_value(path, name):
    """
    Retrieve a registry value using PowerShell Get-ItemProperty command.
    """
    # Construct the PowerShell command to get the registry value
    cmd = f'powershell -Command "Get-ItemProperty -Path \'{path}\' -Name \'{name}\' | Select-Object -ExpandProperty {name}"'
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            # Silently fail for missing paths/values, just return None
            return None
    except subprocess.TimeoutExpired:
        print(f"Command timed out for {path}\\{name}")
        return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def main(json_file):
    """
    Load JSON file with checks, run each check, and report pass/fail.
    """
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"JSON file '{json_file}' not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return

    if 'checks' not in data:
        print("JSON must contain a 'checks' list.")
        return

    for check in data['checks']:
        path = check.get('path')
        name = check.get('name')
        expected = check.get('expected')
        stig = check.get('stig', 'N/A')

        if not all([path, name, expected is not None]):
            print(f"Invalid check: {check}")
            continue

        actual = get_reg_value(path, name)
        if actual is None:
            print(f"FAIL: {stig} - Could not retrieve value for {path}\\{name}")
            continue

        # Try to convert actual to the same type as expected for comparison
        try:
            if isinstance(expected, int):
                actual = int(actual)
            elif isinstance(expected, float):
                actual = float(actual)
            elif isinstance(expected, str):
                actual = str(actual)
            # For other types, keep as string
        except ValueError:
            # If conversion fails, compare as strings
            actual = str(actual)

        if actual == expected:
            print(f"PASS: {stig} - {path}\\{name} = {actual}")
        else:
            print(f"FAIL: {stig} - {path}\\{name} = {actual}, expected {expected}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python app.py <json_file>")
        sys.exit(1)
    main(sys.argv[1])
