from flask import Flask, render_template, redirect, url_for, request, session, flash, send_from_directory, abort
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
classes_dir = os.path.join(current_dir, '..', 'classes')
sys.path.insert(0, classes_dir)
from imports import *

logger = aws_logger("honeypot_website_stream")
app = Flask(__name__)
app.secret_key = "stam_key"
app.permanent_session_lifetime = timedelta(minutes=5) 

traps_list = ["bank_info.txt", "business_plan_for_2024.txt" , "employee_salaries.txt", "money_report2022.txt",
                       "money_report2023.txt", "products_secret_information.txt", "Sensetive_API_Keys.txt", "Social_Media_account_list.txt"]

import requests
def get_location(ip): # it has problems because we are running it on local machine
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        data = response.json()
        location = data.get("city", "Unknown") + ", " + data.get("region", "Unknown") + ", " + data.get("country", "Unknown")
        return location
    except Exception as e:
        return "Location not found"


def insert_event(event: Event_Data):
    handler = Event_Handler()
    res = handler.insert_event(event)

 
    
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login_route():
    authenticated = False
    error_message = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        res, error_message = user_validation.User_Validation.TryLogin(service="admin", password=password, username=username, mail=username)
        if res:
            admin1 = Admin_Handler().get_admin_by_mail(username)
            admin2 = Admin_Handler().get_admin_by_user(username)
            admin = admin1 if admin1 else admin2
            # Authentication successful
            authenticated = True
            session["user"] = admin.admin_name
            log_message =f"client connected"
            ret, error = logger.add_log(log_message)
            event = Event_Data(ip=request.remote_addr, location=get_location(request.remote_addr), service="website", trap_name="Login", tag="")
            insert_event(event)
            return redirect(url_for('explore_folder'))
    if error_message=="user is blocked" :
        event = Event_Data(ip=request.remote_addr, location=get_location(request.remote_addr), service="website", trap_name="blocked connection to user", tag="MAX TRIES")
        insert_event(event)
    log_message =f"failed client connection"
    ret, error = logger.add_log(log_message)    
    return render_template('login.html', error_message = error_message)


@app.route('/logout')
def logout():
    session["user"] = None
    log_message =f"client logged out"
    ret, error = logger.add_log(log_message)  
    
    return redirect(url_for('home'))


def get_file_list(directory_path):
    file_list = []
    for item in os.scandir(directory_path):
        if item.is_file() or item.is_dir():
            file_list.append(item)
    return file_list

@app.route('/file_explorer/<path:folder_path>')
@app.route('/file_explorer/')
def explore_folder(folder_path=None):
    user=session.get("user")
    if not user or user is None:        
        event = Event_Data(ip=request.remote_addr, location=get_location(request.remote_addr), service="website", trap_name="view file explorer", tag="un-authenticated user")
        insert_event(event)     
        return (redirect(url_for("login_route")))
        

    if folder_path:
        directory_path = os.path.join(app.root_path, 'website_files', folder_path)
    else:
        directory_path = os.path.join(app.root_path, 'website_files')

    if not os.path.exists(directory_path):
        abort(404)  

    # Get a list of files and subfolders in the directory
    file_list = get_file_list(directory_path)

    # Determine the current folder for the back button
    current_folder = os.path.normpath(os.path.join(folder_path, '../')) if folder_path else None
    log_message =f"folder : {folder_path} opened"
    ret, error = logger.add_log(log_message) 
    return render_template('file_explorer.html', file_list=file_list, current_folder=current_folder, folder_path=folder_path)


@app.route('/view_file/<path:file_path>')
def view_file(file_path):
    directory_path = os.path.join(app.root_path, 'website_files', os.path.dirname(file_path))
    relevant_file_path=file_path.split("/")[-1]
    print(relevant_file_path)
    file_path = os.path.join(directory_path, os.path.basename(file_path))
    
    

    if relevant_file_path in traps_list :
        event = Event_Data(ip=request.remote_addr, location=get_location(request.remote_addr), service="website", trap_name=relevant_file_path, tag="file viewed")
        insert_event(event)
    log_message =f"file : {relevant_file_path} viewed"
    ret, error = logger.add_log(log_message)      
    return send_from_directory(directory_path, os.path.basename(file_path))


if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context=('cert.pem', 'key.pem'), port=30760)