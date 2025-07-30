# hanifx-timelock

`hanifx-timelock` is a powerful Python module designed to protect your scripts with:

- ⏳ **Time Lock**: Prevent your script from running before a specific date and time  
- 🔒 **License Key Protection**: Require a valid license key to unlock the script  
- 🧬 **File Integrity Check**: Block execution if the script file has been copied or modified  

---

## 🚀 Installation

```bash
pip install hanifx-timelock

from hanifx_timelock import run_timelock

run_timelock()

# Your actual script code here
print("Script unlocked and running...")

🔑 Please enter your license key: HX-1234-ABCD
✅ File unlocked. Running script...

🚫 Invalid license key.

[LOCKED] File locked. Please try again in 5 days, 3:20:10.
