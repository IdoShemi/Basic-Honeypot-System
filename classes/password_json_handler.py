import json
import base64
import hashlib
from salts_table import *

class PasswordJsonHandler:
    def __init__(self,user: str ,service: str, passwords_json: str = ""):
        self.length = 10
        self.user = user
        self.service = service
        self.passwords = ["" for _ in range(self.length)]
        if passwords_json:
            self.read_from_json(passwords_json)

    def insert_password(self, new_password: str):
        for i in range(self.length - 1, 0, -1):
            self.passwords[i] = self.passwords[i - 1]
        self.passwords[0] = self.get_hashed_password(new_password)

    def read_from_json(self, passwords_json: str):
        data = json.loads(passwords_json)
        passwords_array = data.get("passwords", [])
        for i, password in enumerate(passwords_array):
            if i < self.length:
                self.passwords[i] = password

    def build_json(self):
        data = {"passwords": self.passwords}
        return json.dumps(data, indent=4)

    def print_password(self):
        for password in self.passwords:
            print(password if password else "null")

    def compare_new_password(self, password: str, history: int):
        salted_hashed_pass= self.get_hashed_password(password)
        return salted_hashed_pass in self.passwords[:history]

    def compare_current_password(self, password: str):
        return self.passwords[0] == self.get_hashed_password(password)

    def get_hashed_password(self, password: str):
        # Assuming this is your logic to retrieve salt
        if(self.service == "admin"): 
            salt = Salt_Handler().select_salt_by_username_and_service(username_admin=self.user)
        else:
            salt = Salt_Handler().select_salt_by_username_and_service(username_reporting=self.user)

        if salt:
            salt_bytes = base64.b64decode(salt)
            password_bytes = password.encode('utf-8')
            hashed_password = hashlib.sha256(password_bytes + salt_bytes).digest()
            return base64.b64encode(hashed_password).decode('utf-8')
        else:
            raise ValueError("Salt not found for the user.")

    def delete_first(self):
        for i in range(self.length - 1):
            self.passwords[i] = self.passwords[i + 1]
        self.passwords[self.length - 1] = ""