from datetime import datetime
import sys

def lock_file(file_path, unlock_time, mode="hard"):
    """
    Inject time-lock code into a Python file.
    :param file_path: path to your .py file
    :param unlock_time: string in format "YYYY-MM-DD HH:MM"
    :param mode: "hard" or "warn"
    """
    try:
        unlock_dt = datetime.strptime(unlock_time, "%Y-%m-%d %H:%M")

        header_code = f"""# 🔒 hanifx time-lock
import datetime, sys
if datetime.datetime.utcnow() < datetime.datetime({unlock_dt.year}, {unlock_dt.month}, {unlock_dt.day}, {unlock_dt.hour}, {unlock_dt.minute}):
    print("⛔ This script is time-locked until {unlock_dt} UTC.")
"""
        if mode == "hard":
            header_code += "    sys.exit()\n"

        with open(file_path, "r", encoding='utf-8') as f:
            original_code = f.read()

        with open(file_path, "w", encoding='utf-8') as f:
            f.write(header_code + "\n" + original_code)

        print(f"✅ Time-lock added to {file_path}")

    except Exception as e:
        print(f"❌ Error: {e}")
