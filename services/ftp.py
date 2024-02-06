from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
classes_dir = os.path.join(current_dir, '..', 'classes')
sys.path.insert(0, classes_dir)
from imports import *

logger = aws_logger("honeypot_ftp_stream")
original_directory = os.getcwd()
FTP_path = os.path.join(original_directory, 'FTP')


traps_list = ["all_orders.html", "all_products.xlsx" , "Customer_Credit_Cards.csv", "past_products.docx",
                       "past_products.docx", "upcoming_products.docx"]
MAX_FILES = 10 + len(traps_list)
MAX_FILE_SIZE=30

class MyFTPHandler(FTPHandler):
    def on_connect(self):
        print("connected")
        log_message =f"client connected"
        ret, error = logger.add_log(log_message)
        pass

    def on_disconnect(self):
        log_message =f"client disconnected"
        ret, error = logger.add_log(log_message)
        pass
        
    def ftp_MLSD(self, path):
        path_cut=path[len(FTP_path):]
        print(f"ftp_MLSD command executed for path: {path_cut}")
        log_message =f"ftp_MLSD command executed for path: {path_cut}"
        ret, error = logger.add_log(log_message)
        super().ftp_MLSD(path)    

    def ftp_CWD(self, path):
        path_cut=path[len(FTP_path)-1:]
        print(f"CWD command executed. Changing working directory to: {path_cut}")
        log_message =f"CWD command executed. Changing working directory to: {path_cut}"
        ret, error = logger.add_log(log_message)
        super().ftp_CWD(path)
        
    def ftp_RETR(self, file):
        file_cut=os.path.relpath(file,FTP_path)        
        if is_protected_file(file_cut):   
            print(f"RETR command executed on a trap . file: {file_cut}")
            log_message =f"RETR command executed on a trap . file: {file_cut}"
            ret, error = logger.add_log(log_message)
            event = Event_Data(ip=self.remote_ip, location=get_location(self.remote_ip), service="FTP", trap_name=file_cut.split('\\')[-1], tag="RETR")
            insert_event(event)
            
        else:
            print(f"RETR command executed. file: {file_cut}")
            log_message =f"RETR command executed. file: {file_cut}"
            ret, error = logger.add_log(log_message)
        super().ftp_RETR(file)
        
              
        
        
    def ftp_STOR(self, file):
        file_cut=os.path.relpath(file,FTP_path)    
        file_amount=count_files_in_folder(FTP_path)            
        if(MAX_FILES>file_amount):           
            print(f"STOR command executed. file: {file_cut}")
            log_message =f"STOR command executed. file: {file_cut}"
            ret, error = logger.add_log(log_message)
            super().ftp_STOR(file)
        else:
            print(f"Rejected STOR command executed. file: {file_cut}  : max file amout reached" )
            log_message =f"Rejected STOR command executed. file: {file_cut}"
            ret, error = logger.add_log(log_message)
            return None
        
        
    def ftp_DELE(self, file):
        
        file_cut=os.path.relpath(file,FTP_path)        
        if is_protected_file(file_cut):   
            print(f"DELE command executed on a trap . file: {file_cut}")
            log_message =f"DELE command executed on a trap . file: {file_cut}"
            ret, error = logger.add_log(log_message)
            event = Event_Data(ip=self.remote_ip, location=get_location(self.remote_ip), service="FTP", trap_name=file_cut.split('\\')[-1], tag="DELE")
            insert_event(event)
            
        else:
            print(f"DELE command executed. file: {file_cut}")
            log_message =f"DELE command executed. file: {file_cut}"
            ret, error = logger.add_log(log_message)
            super().ftp_DELE(file) 

        
    def ftp_RNTO(self, file):
        src=self._rnfr
        file_cut=os.path.relpath(file,FTP_path)   
        src_file_cut=os.path.relpath(src,FTP_path)     
        if is_protected_file(src_file_cut):   
            print(f"RNTO command executed on a trap . file: {src_file_cut}")
            log_message =f"RNTO command executed on a trap . file: {src_file_cut}"
            ret, error = logger.add_log(log_message)
            event = Event_Data(ip=self.remote_ip, location=get_location(self.remote_ip), service="FTP", trap_name=src_file_cut.split('\\')[-1], tag="RNTO")
            insert_event(event)
            self.respond("550 Permission denied.")
            return 
            
        else:
            print(f"RNTO command executed. file: {src_file_cut} renamed to : {file_cut }")
            log_message =f"RNTO command executed. file: {src_file_cut} renamed to : {file_cut }"
            ret, error = logger.add_log(log_message)
            super().ftp_RNTO(file)
        
    def pre_process_command(self, line, cmd, arg):
        print(cmd)
        super().pre_process_command(line, cmd , arg)
        
  
    
def count_files_in_folder(folder_path):
    file_count = 0
    for root, dirs, files in os.walk(folder_path):
        file_count += len(files)
    return file_count
def insert_event(event: Event_Data):
    current_dir = os.getcwd()
    os.chdir(original_directory)
    handler = Event_Handler()
    res = handler.insert_event(event)
    os.chdir(current_dir)


def is_protected_file(file_name: str):
    return file_name.split('\\')[-1] in traps_list

import requests
def get_location(ip): 
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        data = response.json()
        location = data.get("city", "Unknown") + ", " + data.get("region", "Unknown") + ", " + data.get("country", "Unknown")
        return location
    except Exception as e:
        return "Location not found"

# Create an authorizer and an FTP server
authorizer = DummyAuthorizer()
original_directory = os.getcwd()
SSH_path = os.path.join(original_directory, 'FTP')

authorizer.add_user("user", "1234", SSH_path, perm="elradfmw")

handler = MyFTPHandler
handler.authorizer = authorizer

server = FTPServer(("127.0.0.1", 21), handler)

# Start the FTP server
server.serve_forever()