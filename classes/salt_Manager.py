from salts_table import *
import random
import string
import psycopg2
import uuid
import hashlib
from DatabaseConfig import DatabaseConfig

class Salt_Manager:
 def GetSaltedHashPassword(self,password,username_reporting=None, username_admin=None):
    salt_handler=Salt_Handler()
    # Encode the password as bytes
    salt = salt_handler.select_salt_by_username_and_service(username_reporting,username_admin)
    password_bytes = password.encode('utf-8')
    if salt is None:
            return None
    # Ensure the salt is bytes (if it's not already)
    
    salt = salt.encode('utf-8')
    # Combine the salt and password
    salted_password = salt + password_bytes

    # Create a SHA-256 hash object
    sha256 = hashlib.sha256()

    # Update the hash object with the salted password
    sha256.update(salted_password)

    # Get the hexadecimal representation of the hash
    sha256_hash = sha256.hexdigest()

    return sha256_hash

