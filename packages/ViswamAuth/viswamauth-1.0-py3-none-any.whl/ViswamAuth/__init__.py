import csv
import time
import random
import smtplib
import string
import webbrowser
import os
from email.message import EmailMessage
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import msvcrt

__all__ = [
    'home', 'sign_acc', 'log_acc', 'passcode_verification',
    'pass_forgot', 'help'
]


def home():
    print("=" * 60)
    print("🔐  Welcome to ViswamAuth - User Authentication System")
    print("=" * 60)
    print("Developed by: Viswam Groups and Technologies\n")
    print("Features:")
    print("1️⃣  Sign Up with secure passcodes")
    print("2️⃣  Login with masked password")
    print("3️⃣  Passcode verification")
    print("4️⃣  Password recovery via email (Gmail App Password needed)")
    print("5️⃣  Help & Email support\n")
    print("📌 Note:")
    print("- Works only on Windows (uses msvcrt for secure input)")
    print("- Internet required for email-based features")
    print("- Gmail App Password required for sending emails\n")
    print("📂 Files Used:")
    print(" - acc.csv         → Stores your credentials")
    print(" - Passcodes.txt   → Contains your generated passcodes\n")
    print("Start with: sign_acc(), log_acc(), help(), etc.\n")
    print("=" * 60)


def generate_passcodes():
    characters = string.ascii_letters + string.digits
    codes = [''.join(random.choices(characters, k=12)) for _ in range(4)]
    with open("Passcodes.txt", 'w') as f:
        f.writelines(code + '\n' for code in codes)
    print('Passcode file generated')


def windows_password_input(prompt='Enter password: '):
    print(prompt, end='', flush=True)
    password = ''
    while True:
        ch = msvcrt.getch()
        if ch in {b'\r', b'\n'}:
            print('')
            break
        elif ch == b'\x08':  # Backspace
            if len(password) > 0:
                password = password[:-1]
                print('\b \b', end='', flush=True)
        elif ch == b'\x03':  # Ctrl+C
            raise KeyboardInterrupt
        else:
            password += ch.decode('utf-8')
            print('*', end='', flush=True)
    return password


def sign_acc():
    name = input('\nEnter your name: ')
    username = input("Enter your username: ")
    email = input("Enter Email [should end with @gmail.com]: ")
    pwd = windows_password_input("Enter password: ")

    with open('acc.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([name, username, email, pwd])

    time.sleep(1)
    print("\nAccount created successfully!")
    print("Creating passcode file...")
    generate_passcodes()


def log_acc():
    username_input = input("Enter your Username: ")
    try:
        with open('acc.csv', 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                name, username, email, password = row
                if username_input == username:
                    input_password = windows_password_input("Enter password: ")
                    if input_password == password:
                        print("\nLogged in successfully!")
                        return
                    else:
                        print("Incorrect password.")
                        return
            print("Username not found.")
            choice = input("1) Create Account  2) Forgot Password : ")
            if choice == '1':
                sign_acc()
            elif choice == '2':
                email = input("Enter your Gmail ID: ")
                app_pass = input("Enter your Gmail App Password: ")
                pass_forgot(email, app_pass)
            else:
                print("Invalid input.")
    except FileNotFoundError:
        print("User database not found. Please create an account first.")


def passcode_verification():
    try:
        with open('Passcodes.txt', 'r') as f:
            codes = f.read().splitlines()
        code_input = input("Enter one of your 4 passcodes: ")
        if code_input in codes:
            print("Passcode verified successfully.")
        else:
            print("Invalid passcode.")
    except FileNotFoundError:
        print("No passcode file found.")


def pass_forgot(sender_email, app_password):
    username_input = input("Enter your username: ")
    try:
        with open('acc.csv', 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                name, username, email, password = row
                if username_input == username:
                    confirm = input(f"Confirm your email: {email} [y/n]: ")
                    if confirm.lower() in ['y', 'yes']:
                        verification_code = random.randint(100000, 999999)
                        msg = EmailMessage()
                        msg['Subject'] = 'Your Verification Code'
                        msg['From'] = sender_email
                        msg['To'] = email
                        msg.set_content(f"Your verification code is: {verification_code}")

                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                            smtp.login(sender_email, app_password)
                            smtp.send_message(msg)

                        user_input = int(input("Enter the verification code sent to your email: "))
                        if user_input == verification_code:
                            print(f"""
Account Verified ✅
Name     : {name}
Username : {username}
Email    : {email}
Password : {password}

Please keep your password safe and do not share it.
""")
                        else:
                            print("Incorrect verification code.")
                        return
                    else:
                        print("Email not verified.")
                        return
            print("Username not found.")
    except FileNotFoundError:
        print("Account file not found.")


def help():
    print("""
1) Purpose of the module
2) How to create app password?
3) Documentation
4) Send a Query
""")
    try:
        ch = int(input("Enter your choice (1–4): "))
    except ValueError:
        print("Invalid input.")
        return

    if ch == 1:
        print("ViswamAuth is a simple user authentication module with secure login and recovery features.")
    elif ch == 2:
        webbrowser.open('https://support.google.com/accounts/answer/185833?hl=en')
    elif ch == 3:
        print("""
Functions:
- sign_acc(): Sign up
- log_acc(): Login
- passcode_verification(): Verify passcode
- pass_forgot(email, app_password): Recover password
""")
    elif ch == 4:
        email = input("Your email: ")
        app_pass = input("Your Gmail App Password: ")
        query = input("Enter your query: ")

        msg = EmailMessage()
        msg['Subject'] = 'User Query - ViswamAuth'
        msg['From'] = email
        msg['To'] = 'viswamgroupstechnologies@gmail.com'
        msg.set_content(query)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email, app_pass)
            smtp.send_message(msg)
        print("Query sent successfully.")
    else:
        print("Invalid choice.")
