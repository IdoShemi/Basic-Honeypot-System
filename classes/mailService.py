import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import mail_table
import os  
from tokens_table import *
from admins_table import *
from users_reporting_table import *
from datetime import datetime

class Message:
    def __init__(self, subject, text, additional_files=[]):
        self.subject = subject
        self.text = text
        self.additional_files = additional_files
        
    

class MailService:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        mail_handler = mail_table.Mail_Handler()
        self.sender_email = mail_handler.get_all_mail()[0].user
        self.sender_password = mail_handler.get_all_mail()[0].password

    def send_mail(self, message, recipient_email):
        try:
            # Create a message container
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = message.subject

            # Attach the message text
            msg.attach(MIMEText(message.text, 'plain'))

            # Attach additional files
            for file_path in message.additional_files:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File {file_path} does not exist. The mail was not sent.")
                file_name = f"Reporting_{os.path.basename(file_path)}"
                with open(file_path, "rb") as file:
                    
                    attachment = MIMEApplication(file.read(), _subtype="pdf")  # Adjust subtype as needed
                    attachment.add_header('Content-Disposition', f'attachment; filename="{str(datetime.today().strftime("%Y-%m-%d"))}"')
                    msg.attach(attachment)

            # Connect to the SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Use TLS encryption
                server.login(self.sender_email, self.sender_password)

                # Send the email
                server.sendmail(self.sender_email, recipient_email, msg.as_string())

            print("Email sent successfully.")
        except Exception as e:
            print(f"Error sending email: {str(e)}")

    def send_verify_mail(self, username_reporting="", username_admin=""):
        print("username_reporting = " +username_reporting)
        print("username_admin =" + username_admin)

        token_handler=TokenHandler()
        token=(token_handler.select_token_by_username(username_reporting=username_reporting, username_admin=username_admin))
        message = Message(
        subject="Verification Code",
        text="the code is : "+ token["token"] ,
        additional_files=[] 
        )
        if username_admin:
            Admin_handler = Admin_Handler()
            retrieved_admin = Admin_handler.get_admin_by_user(username_admin)
            self.send_mail(message,retrieved_admin.admin_mail)

        else :
                reporting_handler = UsersReportingHandler()
                retrieved_reporting = reporting_handler.select_user_reporting_by_name(username_reporting)
                self.send_mail(message,retrieved_reporting.mail)

        
        

                


                

                

            
        
        
        
    

