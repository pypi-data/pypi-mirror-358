# hanifx_timelock/timelock.py

import os
import hashlib
from datetime import datetime
import sys

# ========== SETTINGS ==========
UNLOCK_TIME = "2025-08-01 10:00"
VALID_LICENSE_KEYS = {"HX-1234-ABCD", "HX-5678-EFGH"}
ORIGINAL_HASH = "PUT_YOUR_FILE_HASH_HERE"
# ==============================

def get_file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def check_file_integrity():
    current_hash = get_file_hash(__file__)
    if ORIGINAL_HASH == "PUT_YOUR_FILE_HASH_HERE":
        print("[🔐] First time running. Copy and paste this hash in ORIGINAL_HASH:")
        print(f"[COPY THIS] {current_hash}")
        sys.exit(0)
    if current_hash != ORIGINAL_HASH:
        print("🚫 File has been modified or copied. Aborting.")
        sys.exit(1)

def check_unlock_time():
    unlock_dt = datetime.strptime(UNLOCK_TIME, "%Y-%m-%d %H:%M")
    now = datetime.now()
    if now < unlock_dt:
        remaining = unlock_dt - now
        print(f"[LOCKED] File locked. Try again in {remaining}.")
        sys.exit(1)

def ask_license_key():
    key = input("🔑 Enter your license key: ").strip()
    if key not in VALID_LICENSE_KEYS:
        print("🚫 Invalid license key.")
        sys.exit(1)

def run_timelock():
    check_file_integrity()
    check_unlock_time()
    ask_license_key()
    print("✅ File unlocked. Running...")

if __name__ == "__main__":
    run_timelock()
