from imports import *
from mailService import *
import os
password_config_file_path = 'password_config.json'
with open(password_config_file_path, 'r') as config_file:
    config_data = json.load(config_file)
USER_LOGIN_ATTEMPTS = config_data.get('loginAttempts', 3)

BLOCKED_TIMEOUT_MINUTES = 1
from datetime import datetime
class User_Validation:
    @staticmethod
    def sendmail(mail, token):     
        message = Message(
            subject="Verification code - Futuristic Technologies",
            text=f"Your code is: {token}") 
        mail_service = MailService()
        mail_service.send_mail(message, mail)
    
    @staticmethod
    def FogetPassword(mail, username, service, errorMessage=""):
        """ This function checks the credentials and returns True if the username and the mail matches. 

        Args:
            mail (_type_): _description_
            username (_type_): _description_
            service (_type_): accepts 'reporting' and 'admin' other values lead to error
        """
        if service == "admin":
            admin_data =  Admin_Handler().get_admin_by_user(username)
            if admin_data != None and admin_data.admin_mail == mail:
                token = TokenData(username_admin=username)
                token_handler = TokenHandler()
                token_handler.delete_token_by_username(username_admin=username)
                insert_res = token_handler.insert_token(token)
                User_Validation.sendmail(admin_data.admin_mail, token.token)
                return True
            else:
                errorMessage = "Credentials are incorrect" 
                return False
        elif service == "reporting":
            reporting_data =  UsersReportingHandler().select_user_reporting_by_name(username)
            if reporting_data != None and reporting_data.mail == mail: 
                token_handler = TokenHandler()
                token_handler.delete_token_by_username(username_reporting=username)
                token = TokenData(username_reporting=username)
                insert_res = token_handler.insert_token(token)
                User_Validation.sendmail(reporting_data.mail, token.token)
                return True
            else:
                errorMessage = "Credentials are incorrect" 
                return False
        else:
            errorMessage = "Service Not Valid"
            return False
        
    @staticmethod   
    def VerifyPassword(inputed_token, errorMessage="", username_reporting="", username_admin= ""):
        token, expiration_date = TokenHandler().select_token_by_username(username_reporting=username_reporting, username_admin=username_admin)
        datetime_format = "%Y-%m-%d %H:%M:%S.%f"
        current_time = datetime.now()
        if current_time > expiration_date:
            errorMessage = "Verification code has expired."
            return False, errorMessage
        if token != inputed_token:
            errorMessage = "Verification code is not correct."
            return False, errorMessage
        return True, errorMessage
    
    
    @staticmethod  
    def ChangePassword(new_password, token, service):
        """This function getting the service and changing the password to a new one.

        Args:
            mail (_type_): _description_
            new_password (_type_): _description_
            service (_type_): accepts 'reporting' and 'admin' other values lead to error
        """
        user = TokenHandler().select_username_from_token(token)
        if service == "admin":
            user = Admin_Handler().get_admin_by_user(user)
            res, error = Password_Checker.check_password(new_password, user.admin_name, "admin")
            if not res:
                return error
            handler = PasswordJsonHandler(service=service, user=user.admin_name, passwords_json=user.password)
            handler.insert_password(new_password=new_password)
            json_str = handler.build_json()
            user.password= json_str
            Admin_Handler().update_admin(user.admin_name, user)
            TokenHandler().delete_token_by_username(username_admin=user.admin_name)
            return True
        elif service == "reporting":
            user = UsersReportingHandler().select_user_reporting_by_name(user)
            res, error = Password_Checker.check_password(new_password, user.admin_name, "reporting")
            if not res:
                return error
            handler = PasswordJsonHandler(service=service, user=user.admin_name, passwords_json=user.slt_hashed_pass)
            handler.insert_password(new_password=new_password)
            json_str = handler.build_json()
            user.slt_hashed_pass = json_str
            UsersReportingHandler().update_user_reporting(user.admin_name, user)
            TokenHandler().delete_token_by_username(username_reporting=user.admin_name)
            return True
        else:
            return "Service is not valid"
        return None
        
    @staticmethod 
    def TryLogin(service, password, mail = "", username=""):
        if service == "admin":
            admin1 = Admin_Handler().get_admin_by_mail(mail)
            admin2 = Admin_Handler().get_admin_by_user(username)
            admin = admin1 if admin1 else admin2
            if admin is None: 
                errorMessage = "credentials incorrect"
                return False, errorMessage
            
            pj = admin.password
            # check if blocked
            current_datetime = datetime.now()
            time_difference = (current_datetime - admin.LastLogin).total_seconds() / 60
            
            if(admin.Login_attempts >= USER_LOGIN_ATTEMPTS):
                if(time_difference < BLOCKED_TIMEOUT_MINUTES):
                    errorMessage = "user is blocked"
                    return False, errorMessage
                admin.Login_attempts = 0
                Admin_Handler().update_admin(admin.admin_name, admin)
                
            handler = PasswordJsonHandler(passwords_json=pj, user=admin.admin_name, service=service)
            if(handler.compare_current_password(password)):
                admin.Login_attempts = 0
                admin.LastLogin = datetime.now()
                Admin_Handler().update_admin(admin.admin_name, admin)
                return True , ""
            admin.Login_attempts = admin.Login_attempts + 1
            admin.LastLogin = datetime.now()
            Admin_Handler().update_admin(admin.admin_name, admin)
            errorMessage = "credentials incorrect"
            return False, errorMessage
        elif service == "reporting":
            admin1 = UsersReportingHandler().select_user_reporting_by_name(username)
            admin2 = UsersReportingHandler().select_user_reporting_by_mail(mail) 
            admin = admin1 if admin1 else admin2
            if admin is None: 
                errorMessage = "credentials incorrect"
                return False, errorMessage
            
            pj = admin.slt_hashed_pass
            # check if blocked
            current_datetime = datetime.now()
            time_difference = (current_datetime - admin.last_login).total_seconds() / 60
            if(admin.login_attempts >= USER_LOGIN_ATTEMPTS):
                if(time_difference < BLOCKED_TIMEOUT_MINUTES):
                    errorMessage = "user is blocked"
                    return False, errorMessage
                admin.login_attempts = 0
                UsersReportingHandler().update_user_reporting(admin.admin_name, admin)
            handler = PasswordJsonHandler(passwords_json=pj, user=admin.admin_name, service=service)
            if(handler.compare_current_password(password)):
                admin.login_attempts = 0
                admin.last_login = datetime.now()
                UsersReportingHandler().update_user_reporting(admin.admin_name, admin)
                return True, ""
            admin.login_attempts = admin.login_attempts + 1
            admin.last_login = datetime.now()
            UsersReportingHandler().update_user_reporting(admin.admin_name, admin)
            errorMessage = "credentials incorrect"
            return False, errorMessage
        else:
            return False, ""
        
        

    