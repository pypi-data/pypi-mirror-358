# ViswamAuth 🔐

**A simple Python-based user authentication system with email-based password recovery and secure login.**

ViswamAuth is a lightweight, console-driven authentication module for Windows. It provides essential features such as user registration, login, password masking, passcode generation, and recovery through email verification.

---

## ✨ Features

- ✅ Account creation with name, username, and email
- 🔐 Secure password input (console-masked)
- 🧾 Auto-generated passcodes stored locally
- 📧 Password recovery with email-based OTP
- 🆘 Help menu with Gmail App Password support
- 📂 Local file-based storage (`CSV` and `.txt`)

---

## 📦 Installation

```bash
pip install viswamauth


from viswamauth import sign_acc, log_acc, passcode_verification, pass_forgot, help

sign_acc()                 # Register a new user
log_acc()                  # Login using credentials
passcode_verification()    # Verify using one of 4 generated passcodes
pass_forgot(email, app_password)  # Recover password with Gmail
help()                     # Learn or get support
