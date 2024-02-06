from imports import *
from datetime import datetime
def create_user_admin_table(admin_data: Admin_Data):
    # part 1 - create user with empty password
    admin = Admin_Data(admin_data.admin_name, "", admin_data.admin_mail, datetime.now())
    handler = Admin_Handler()
    res = handler.insert_admin(admin)
    
    # part 2 - create salt for the user
    salt_handler = Salt_Handler()
    salt = Salt_Data(username_admin=admin_data.admin_name)
    insert_res1 = salt_handler.insert_salt(salt)

    # part 3 - updating password with Password Json Handler
    json_handler = PasswordJsonHandler(service="admin", user=admin_data.admin_name)
    json_handler.insert_password(admin_data.password)
    password_json = json_handler.build_json()
    admin_data.password = password_json
    handler.update_admin(admin_data.admin_name, admin_data)
    
    
def create_user_reporting_table(admin_data: UsersReportingData):
    # part 1 - create user with empty password
    admin = UsersReportingData(admin_data.admin_name, "", admin_data.mail, datetime.now())
    handler = UsersReportingHandler()
    res = handler.insert_user_reporting(admin)
    
    # part 2 - create salt for the user
    salt_handler = Salt_Handler()
    salt = Salt_Data(username_reporting=admin_data.admin_name)
    insert_res1 = salt_handler.insert_salt(salt)

    # part 3 - updating password with Password Json Handler
    json_handler = PasswordJsonHandler(service="reporting", user=admin_data.admin_name)
    json_handler.insert_password(admin_data.slt_hashed_pass)
    password_json = json_handler.build_json()
    admin_data.slt_hashed_pass = password_json
    handler.update_user_reporting(admin_data.admin_name, admin_data)
    
     