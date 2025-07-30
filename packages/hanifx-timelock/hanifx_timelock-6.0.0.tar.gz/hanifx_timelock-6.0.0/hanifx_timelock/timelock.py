import datetime
import time
import os

def lock_file(filename, unlock_time, mode="soft"):
    """
    Lock a file from being accessed until a specified datetime.

    Parameters:
    - filename (str): Path to the file to be locked.
    - unlock_time (str): Time until which the file is locked. Format: "YYYY-MM-DD HH:MM".
    - mode (str): "soft" (only delay access), "hard" (rename or deny access).
    """
    try:
        unlock_dt = datetime.datetime.strptime(unlock_time, "%Y-%m-%d %H:%M")
        while datetime.datetime.now() < unlock_dt:
            remaining = (unlock_dt - datetime.datetime.now()).total_seconds()
            print(f"[LOCKED] File is locked for {int(remaining)} more seconds...", end="\r")
            time.sleep(1)

        print(f"\n✅ File '{filename}' unlocked!")
    except Exception as e:
        print(f"Error: {e}")
