# hanifx

**hanifx** is a Python security and utility module built by Hanif. It includes tools like **time-locking Python scripts**, code protection, and more upcoming advanced security features.

---

## 🔐 Features

- `lock_file()`: Inject a time-lock in any Python script so it cannot be executed before a specific time.
- Modes:
  - `hard`: blocks execution completely before time
  - `warn`: shows warning but allows execution
- Easy to use with one function
- Lightweight and zero dependencies

---

## 🚀 Installation

```bash
pip install hanifx

from hanifx import lock_file

# Lock script until July 1, 2025 at 14:30 UTC
lock_file("my_script.py", "2025-07-01 14:30", mode="hard")

⛔ This script is time-locked until 2025-07-01 14:30 UTC.
