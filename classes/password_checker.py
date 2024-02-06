from password_json_handler import *
import json
import string
import admins_table
import users_reporting_table
import os
class Password_Checker:
    @staticmethod
    def check_password(password, user: str, service: str):
        error = ''
        password_config_file_path = 'password_config.json'
        with open(password_config_file_path, 'r') as config_file:
            config_data = json.load(config_file)

        password_length = config_data.get('passwordLength', 0)
        complex_password = config_data.get('complexPassword', False)
        password_history = config_data.get('passwordHistory', 0)
        prevent_dictionary_attack = config_data.get('preventDictionaryAttack', False)

        # Check password length
        if len(password) < password_length:
            error = f'Your password must be at least {password_length} characters long.'
            return False, error

        # Check for complex password
        if complex_password:
            count_arr = [0, 0, 0, 0]  # [digits, uppercase, lowercase, special characters]

            for c in password:
                if c.isdigit():
                    count_arr[0] = 1
                elif c.isupper():
                    count_arr[1] = 1
                elif c.islower():
                    count_arr[2] = 1
                elif c in string.punctuation:
                    count_arr[3] = 1

            if sum(count_arr) < 3:
                error = 'Your password must contain 3 of the 4 types of characters.'
                return False, error

        # Getting the password json of the user.
        if(service == "admin"): 
            passwords_json = admins_table.Admin_Handler().get_admin_by_user(user).password
        else:
            passwords_json = users_reporting_table.UsersReportingHandler().select_user_reporting_by_name(user).slt_hashed_pass

        # Check password history
        passwords_handler = PasswordJsonHandler(service=service, user=user, passwords_json=passwords_json)
        if passwords_handler.compare_new_password(password, password_history):
            error = 'Your password cannot be the same as your previous passwords.'
            return False, error

        # Prevent dictionary attacks (simulated with a list of common passwords)
        common_passwords_file_path = 'commonPasswords.txt'

        if prevent_dictionary_attack and Password_Checker.is_common_password(password, common_passwords_file_path):
            error = 'Common password. Please choose a different password.'
            return False, error

        return True, error
    
    @staticmethod
    def is_common_password(password, common_passwords_file_path='commonPasswords.txt'):
        try:
            with open(common_passwords_file_path, 'r') as file:
                common_passwords = file.read().splitlines()
                if password in common_passwords:
                    return True
        except FileNotFoundError:
            pass
        return False