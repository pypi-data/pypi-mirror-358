# hanifx-timelock

A lightweight Python utility to lock any file until a specific date and time.

## Installation

```bash
pip install hanifx-timelock

from hanifx_timelock import lock_file

lock_file("hello.py", "2025-08-01 10:00", mode="soft")
