from flask import Flask, render_template, redirect, url_for, request, session, flash, send_from_directory, abort, make_response
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
classes_dir = os.path.join(current_dir, '..', 'classes')
sys.path.insert(0, classes_dir)
from imports import *
from mailService import *
from datetime import timedelta, datetime
import pandas as pd
from xhtml2pdf import pisa
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import json
from pandas import Timestamp
from io import BytesIO
import base64
import ast
import numpy as np
from matplotlib import pyplot as plt
import shutil


logger = aws_logger("reporting_website_stream")
app = Flask(__name__)
app.secret_key = "stam_key"
app.permanent_session_lifetime = timedelta(minutes=5)

    
@app.route("/")
def home():
    user=session.get("user")
    if not user or user is None:          
        return (redirect(url_for("login_route")))
    return render_template("reportings.html")


@app.route('/login', methods=['GET', 'POST'])
def login_route(error_message=""):
    authenticated = False
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        res, error_message = user_validation.User_Validation.TryLogin(service="reporting", password=password, username=username, mail=username)
        if res:
            user1 = UsersReportingHandler().select_user_reporting_by_mail(username)
            user2 = UsersReportingHandler().select_user_reporting_by_name(username)
            user = user1 if user1 else user2
            # Authentication successful
            authenticated = True
            session["user"] = user.admin_name
            session["mail"] = user.mail
            log_message =f"client connected"
            ret, error = logger.add_log(log_message)
            return redirect(url_for('reportings'))
        else:
            log_message =f"failed client connection"
            ret, error = logger.add_log(log_message)
            return render_template('login.html', error_message = error_message)
    return render_template('login.html', error_message = error_message)


@app.route('/logout')
def logout():
    session["user"] = None
    log_message =f"client logged out"
    ret, error = logger.add_log(log_message)  
    
    return redirect(url_for('home'))


@app.route('/reportings', methods=['GET', 'POST']) 
def reportings():
    user=session.get("user")
    if not user or user is None:            
        return (redirect(url_for("login_route")))
    
    if request.method=='POST':
        if "button" in request.form:
            if request.form["button"]=="back":
                return redirect(url_for("reportings"))
            elif request.form["button"]=="Export to mail":
                raw_data = request.form.get('raw_data')
                if raw_data:
                    filepath = create_pdf_raw(raw_data)
                    send_mail(filepath)
                    os.remove(filepath)
                    flash("Reporting was sent to mail.")
                    return render_template('reporting_pandas.html', table_html=eval(raw_data)) 
                return 
        
        
        event_id = request.form.get('event_id') or None 
        service = request.form.get('service') if request.form.get('service')!='ALL' else None
        start_date = request.form.get('start_date') if request.form.get('start_date') else '2000-01-01'
        end_date = request.form.get('end_date') if request.form.get('end_date') else str(datetime.today().strftime('%Y-%m-%d'))
        ip = request.form.get('ip') or None
        location = request.form.get('location') or None
        trap_name = request.form.get('trap_name') or None
        event_handler = Event_Handler()     
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        data_type = request.form.get('data_type') or None
        if event_id:
            event = event_handler.select_event(event_id)        
            df = pd.DataFrame([event.__dict__])
            table_html = df.to_dict(orient='records') 
            return render_template('reporting_pandas.html', table_html=table_html)
        
        events = event_handler.filter_events(start_date=start_date, end_date=end_date, ip=ip, location=location, trap_name=trap_name, service=service)        
        df = pd.DataFrame([event.__dict__ for event in events])
        if data_type=="raw_data":
            table_html = df.to_dict(orient='records') 
            return render_template('reporting_pandas.html', table_html=table_html)
        else:
            plots = get_plots(df)
            chart_paths=[]
            dir_path = os.path.join('Reporting_Website', 'static', 'images', user)
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                except OSError as e:
                    print(f"Error: {dir_path} : {e.strerror}")
                
            dir_path = os.path.join('Reporting_Website', 'static', 'images', user)
            os.makedirs(dir_path)
            for i, plot in enumerate(plots): 
                path = os.path.join('Reporting_Website', 'static', 'images',user, f'{i}.png')
                chart_path = os.path.join('images',user, f'{i}.png').replace("\\", "/")
                chart_paths.append(chart_path)
                plot.savefig(path)
            return redirect(url_for("reporting_analyzed"))
            
    
    
    
    return render_template('reportings.html')

    




def create_pdf_raw(raw_data):
    path = os.path.join(app.root_path, 'reporting_files')
    pdf_file_name = f'{count_files_in_folder(path) + 1}.pdf'
    data_list = eval(raw_data)
    
    pdf_file_path = os.path.join(app.root_path, 'reporting_files', pdf_file_name)

    doc = SimpleDocTemplate(pdf_file_path, pagesize=letter, title="Reporting")
    
    styles = getSampleStyleSheet()
    normalStyle = styles['Normal']
    normalStyle.wordWrap = 'CJK'
    headerStyle = styles['Normal'].clone('HeaderStyle')  
    headerStyle.backColor = colors.royalblue
    headerStyle.textColor = colors.white
    elements = []

    data = []
    column_names = ['Event ID', 'Timestamp', 'IP', 'Location', 'Service', 'Tag', 'Attempts', 'Additional Data', 'Trap Name']
    data.append([Paragraph(str(val), headerStyle) for val in column_names])
    
    for item in data_list:
        data.append([Paragraph(str(val), normalStyle) for val in item.values()])

    t = Table(data, colWidths=[doc.width * 1.2 / len(column_names) for _ in column_names])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), headerStyle.backColor),  
                           ('TEXTCOLOR', (0, 0), (-1, 0), headerStyle.textColor),
                           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                           ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                           ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                           ('BACKGROUND', (0, 1), (-1, -1), colors.white),  
                           ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),                           
                           ('GRID', (0, 0), (-1, -1), 1, colors.black),
                           ('WORDWRAP', (0, 0), (-1, -1), 'CJK')]))
    
    elements.append(t)
    doc.build(elements)

    return pdf_file_path
         
def send_mail(file_path):
    recipient_email = session.get("mail")
    
    message = Message (
        subject="Reporting pdf summary.",
        text="The reporting is attached to this message.",
        additional_files=[file_path] ) 
      

    mail_service = MailService()
    mail_service.send_mail(message, recipient_email)

     
def generate_table(data_list):
    html_rows = ""
    for row in data_list:
        html_row = "<tr>"
        for key, value in row.items():
            html_row += f"<td>{value}</td>"
        html_row += "</tr>"
        html_rows += html_row

    # Construct complete HTML table with CSS styling
    html_table = f"""
    <style>
        table {{
            border-collapse: collapse;
            width: 100%; /* Set the width of the table */
        }}
        th, td {{
            border: 1px solid black;
            -pdf-word-wrap: CJK;
            padding: 5px;
            text-align: left;
            word-wrap: break-word; /* Use word-wrap for word break */
        }}
        th {{
            background-color: #f2f2f2;
        }}
    </style>
    <table style="width: 100%">
        <thead>
            <tr>
                <th style="width: 10%;">Event ID</th> <!-- Adjust column widths as needed -->
                <th style="width: 15%">Timestamp</th>
                <th style="width: 12%">IP</th>
                <th style='width:10%'>Location</th>
                <th style='width:8%'>Service</th>
                <th style='width:10%;'>Tag</th>
                <th style='width:9%'>Attempts</th>
                <th style='width:16%'>Additional Data</th>
                <th style="width: 10%">Trap Name</th>
            </tr>
        </thead>
        <tbody>
            {html_rows}
        </tbody>
    </table>
    """
    return html_table

  
  
@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password_route():
    error_message = ""
    if request.method == 'POST':
        username = request.form.get('username')
        mail = request.form.get('mail')
        
        res = user_validation.User_Validation.FogetPassword(service="reporting", username=username, mail=mail)
        if res: 
            session["user_to_recover"] = username
            log_message =f"client {username} requested to change password, code sent to mail"
            ret, error = logger.add_log(log_message)
            return redirect(url_for('verify_code'))
        error_message = "Credentials incorrect"
        log_message = f"failed client password modification request"
        ret, error = logger.add_log(log_message)
    return render_template('forget_password.html', error_message = error_message)


@app.route('/verify_code', methods=['GET', 'POST'])
def verify_code(error_message=""):
    if(not session.get("user_to_recover")):
        return redirect(url_for("forget_password_route"))
    
    if request.method == 'POST':
        token = request.form.get('token')
        res, error_message = user_validation.User_Validation.VerifyPassword(token,  username_reporting=str(session["user_to_recover"]))
        if not res: 
            if error_message == "Verification code is not correct.":
                log_message =f"client {str(session['user_to_recover'])} entered wrong verification code."
                ret, error = logger.add_log(log_message)
                return render_template('verify_code.html', error_message=error_message)
            else: # expired
                return render_template('forget_password.html', error_message = error_message)
        session["Token"] = token
        return redirect(url_for("change_pass"))
    return render_template('verify_code.html', error_message=error_message)


@app.route('/change_pass', methods=['GET', 'POST'])
def change_pass(error_message=""):
    if(not session.get("Token")):
        return redirect(url_for("forget_password_route"))   
    token_handler = TokenHandler()
    username = token_handler.select_username_from_token(str(session["Token"]))
    if username:
        if request.method == 'POST':
            password = request.form.get('password')
            password_verified = request.form.get('password_verified')
            if (password == password_verified):
                log_message =f"client {username} changed password."
                ret, error = logger.add_log(log_message)
                err_message = user_validation.User_Validation.ChangePassword(password, str(session["Token"]), service="reporting")
                if err_message == True:
                    return redirect(url_for('password_changed'))
                return render_template('change_pass.html', error_message = err_message)
            else:
                return render_template('change_pass.html', error_message ="passwords are not the same")
        return render_template('change_pass.html', error_message = error_message)
    else: # expired
        return redirect(url_for("forget_password_route"))



@app.route('/password_changed', methods=['GET'])
def password_changed():
    session.clear()
    return render_template('password_changed.html')

def count_files_in_folder(folder_path):
    file_count = 0
    for root, dirs, files in os.walk(folder_path):
        file_count += len(files)
    return file_count


@app.route('/delete_images', methods=['POST'])
def delete_images():
    # chart_paths = request.form.getlist('chart_paths')
    # chart_paths= ast.literal_eval(chart_paths[0])
    # for chart_path in chart_paths:
    #     chart_path = os.path.join(app.root_path,'static', chart_path)
    #     if os.path.exists(chart_path):
    #         os.remove(chart_path)
    user=session.get("user")
    if not user or user is None:            
        return (redirect(url_for("login_route")))
    
    dir_path = os.path.join('Reporting_Website', 'static', 'images', user)
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
        except OSError as e:
            print(f"Error: {dir_path} : {e.strerror}")
    return 'Images deleted successfully', 200



def get_plots(df: pd.DataFrame):
    df['Timestamp'] = pd.to_datetime(df['timestamp'])
    
    fig_list = []

    fig_traps = plt.figure(figsize=(8, 6))  
    top5_traps = df['trap_name'].value_counts().head(5)
    top5_traps.plot(kind='bar', color='skyblue')
    plt.title('Top 5 Traps')
    plt.xlabel('Trap Name')
    plt.ylabel('Frequency')
    plt.tight_layout()  
    fig_list.append(fig_traps)

    fig_users = plt.figure(figsize=(8, 6)) 
    top5_users = df['ip'].value_counts().head(5)
    top5_users.plot(kind='bar', color='salmon')
    plt.title('Top 5 Users')
    plt.xlabel('IP Address')
    plt.ylabel('Frequency')
    plt.tight_layout()  
    fig_list.append(fig_users)

    fig_days = plt.figure(figsize=(8, 6))  
    df['Date'] = df['Timestamp'].dt.date
    top5_days = df['Date'].value_counts().head(5)
    top5_days.plot(kind='bar', color='lightgreen')
    plt.title('Top 5 Days')
    plt.xlabel('Date')
    plt.ylabel('Frequency')
    plt.tight_layout()  
    fig_list.append(fig_days)

    if 'service' in df.columns and 'tag' in df.columns:
        unique_services = df['service'].unique()
        for service in unique_services:
            fig_tag = plt.figure(figsize=(8, 6))  
            top_tag = df[df['service'] == service]['tag'].value_counts().head(1)
            if not top_tag.empty:
                top_tag.plot(kind='bar', color='lightcoral')
                plt.title(f'Top Tag for {service}')
                plt.xlabel('Tag')
                plt.ylabel('Frequency')
                plt.tight_layout() 
                fig_list.append(fig_tag)

    return fig_list



@app.route('/reporting_analyzed', methods=['GET', 'POST'])
def reporting_analyzed():   
    user=session.get("user")
    if not user or user is None:            
        return (redirect(url_for("login_route")))
    dir_path = os.path.join('Reporting_Website', 'static', 'images', user)
    if request.method == 'POST':
        pdf = BytesIO()
        html = f'<style>img {{ display: block; margin-bottom: 10px; height:450px;}}</style>'  # CSS for spacing between images
        html += f'<center><h1>Analyzed Report, Date: {datetime.today().strftime("%d.%m.%Y")}</h1></center>'

        for filename in os.listdir(dir_path):
            img_path = os.path.join(dir_path, filename)
            
            with open(img_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
                html += f'<img src="data:image/png;base64,{img_data}" />'


        pisa.CreatePDF(html, dest=pdf)

        # Save PDF to file
        pdf_path = os.path.join('Reporting_Website', 'static', 'pdf', 'reporting.pdf')
        with open(pdf_path, 'wb') as f:
            f.write(pdf.getvalue())
            
        pdf_path_without_root = os.path.join('static', 'pdf', 'reporting.pdf')
        pdf_file_path = os.path.join(app.root_path, pdf_path_without_root)
        send_mail(pdf_file_path)
        os.remove(pdf_file_path)
        flash("Reporting was sent to mail.")    
    
    chart_paths = []
    for filename in os.listdir(dir_path):
        img_path = os.path.join('images',user, filename).replace("\\", "/")
        chart_paths.append(img_path)
    return render_template('reporting_analyzed.html', chart_paths=chart_paths)


if __name__ == "__main__":
    app.run()