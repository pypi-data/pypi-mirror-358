import csv
import time
import random
import smtplib
from email.message import EmailMessage
import msvcrt
import random
import string
import webbrowser
import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


def home():
    print("="*60)
    print("🔐  Welcome to ViswamAuth - User Authentication System")
    print("="*60)
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
    print("="*60)

def passcodes():
    characters = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    passcode1=''.join(random.choices(characters, k=12))
    passcode2=''.join(random.choices(characters, k=12))
    passcode3=''.join(random.choices(characters, k=12))
    passcode4=''.join(random.choices(characters, k=12))
    pass_code_txt=open("Passcodes.txt",'w')
    pass_code_txt.write(passcode1+'\n')
    pass_code_txt.write(passcode2+'\n')
    pass_code_txt.write(passcode3+'\n')
    pass_code_txt.write(passcode4+'\n')
    pass_code_txt.close()
    print('Passcode file generated')

def sign_acc():
    global name
    global username
    global email
    name=input('\nEnter your name : ')
    username=input("Enter your username : ")
    email=input("Enter Email [should end with @gmail.com] : ")
    import msvcrt

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

    pwd = windows_password_input("Enter password: ")

    acc_list=[name,username,email,pwd]
    acc_f=open('acc.csv','a',newline='')
    acc_obj=csv.writer(acc_f)
    acc_obj.writerow(acc_list)
    time.sleep(2)
    print("\nAccount created successfully !\n")
    print("\nCreating passcode file :")
    passcodes()
    acc_f.close()

def passcode_verification():
    try:
        veri_passcode=open('Passcodes.txt','r')
        codes_data=veri_passcode.readlines()
        veri_code_entry=input("Enter any (i.e from 4 passcodes provided) PASSCODE for verification : ")
        for i in codes_data:
            if veri_code_entry in i:
                print("Passcode verified successfully")
                break
        else:
            print("No passcodes found")
                
    except FileNotFoundError:
        print("No access to your passcode file")
    finally:
        veri_passcode.close()

def pass_forgot(email,app_pass):
    global validation
    global authorisation
    authorisation=True
    validation==True
    f=open('acc.csv','r',newline='')
    acc_data=csv.reader(f)
    username_veri=input("Enter your username : ")
    for i in acc_data:
        if i[1]==username_veri:
            name_=i[0]
            user_=i[1]
            email_=i[2]
            pass_=i[3]
            email_veri_user=input(f"Confirm your email : {email_} [y/n] : ")
            print("\n Please wait for some moment ....\n")
            if email_veri_user.lower() in ['y', 'yes']:
                y=random.randint(100000,200000)
                msg = EmailMessage()
                msg['Subject'] = 'Email Verification Code For Password'
                msg['From'] = email
                msg['To'] = email_
                msg.set_content(f""" 

                This email is sent in order to determine your password. Your verification code is :
                                
                                                    {y}

                -Please do not share your verification code to anyone. Thank you.

                """)
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(email, app_pass)
                    smtp.send_message(msg)

                print("\nVerification code sent to your Email ID, please check : ")
                ver_code=int(input("\nEnter verification code : "))
                if y==ver_code:
                    print(f""" 

                    Successfully verified your account! Here, your account details : 
                            Name : {name_}
                            Username : {user_}
                            Email : {email_}
                            Password : {pass_}
                        
                    - Becareful with your password, do not reveal and remember it for furthur usage
                        
                        Thank You.

                """)
                break
            elif email_veri_user.lower() in ['n', 'no']:
                print("Email not verified")
            else:
                print("\nInvalid Input\n")
    f.close()

def help():
    print('''

        1) Purpose of the module
        2) How to create app password ?
        3) Documentation
        4) Any other

     ''')
    ch=int(input("Enter the number corresponding to your query : "))
    if ch==1:
        print("This module is developed by Viswam Groups and Technologies to provide: \na basic structure for sign in authorisation \nand also login for application build using python.")
    elif ch==3:
        print(""" 

            sign_acc : to sign in 
            log_acc : to log in 
            passcodes : to get passcodes for users
            passcode_verification : To verify passcodes
            pass_forgot(email,app_pass) : To retrieve back password [email and App password should be in '']

        """)
    elif ch==2:
        webbrowser.open('https://support.google.com/accounts/answer/185833?hl=en')
    elif ch==4:
        email=input("Your email id : ")
        pass_app=input('Enter your app password : ')
        query=input("Enter your query : ")
        msg = EmailMessage()
        msg['Subject'] = 'User Query - ViswamAuth'
        msg['From'] = email
        msg['To'] = 'viswamgroupstechnologies@gmail.com'
        msg.set_content(query)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email, pass_app)
            smtp.send_message(msg)
        print('Sent your query successfully .. Can expect reply within 2 days from Viswam |')
    else:
        print('Invalid Input')

def log_acc():
    acc_f_log = None 
    global validation
    validation = True  
    try:

        global username_log
        username_log = input("Enter your Username : ")
        acc_f_log = open('acc.csv', 'r', newline='')
        log_info = csv.reader(acc_f_log)
        for i in log_info:
            global name
            name = i[0]
            if username_log == i[1]:
                import msvcrt

                def windows_password_input(prompt='Enter password: '):
                    print(prompt, end='', flush=True)
                    password_ = ''
                    while True:
                        ch = msvcrt.getch()
                        if ch in {b'\r', b'\n'}:
                            print('')
                            break
                        elif ch == b'\x08':  # Backspace
                            if len(password_) > 0:
                                password_ = password_[:-1]
                                print('\b \b', end='', flush=True)
                        elif ch == b'\x03':  # Ctrl+C
                            raise KeyboardInterrupt
                        else:
                            password_ += ch.decode('utf-8')
                            print('*', end='', flush=True)
                    return password_

                password = windows_password_input("Enter password: ")
                if password == i[3]:
                    time.sleep(0.5)
                    print("\nLogged in successfully!")
                    break
        else:
            error_cause = input("Enter the cause of error during your log-in : 1) No Account  2)Forgot your password : ")
            if error_cause == '1':
                print("Please create an account : ")
                sign_acc()
            elif error_cause == '2':
                pass_forgot()
            else:
                print("\n|| INVALID INPUT ||\n ")
    except FileNotFoundError:
        print("\n|| Log file not authorised ||\n")
    finally:
        if acc_f_log is not None:
            acc_f_log.close()
