# import the imports file
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
classes_dir = os.path.join(current_dir, '..', 'classes')
sys.path.insert(0, classes_dir)
from imports import *
import threading
import socket
import traceback
import json
import paramiko

private_key_file = 'rsa_private_key'
HOST_KEY = paramiko.RSAKey(filename=private_key_file)

logger = aws_logger("honeypot_ssh_stream")

original_directory = os.getcwd()
SSH_path = os.path.join(original_directory, 'SSH')

with open('instructions.txt', 'r') as instructions_file:
    instructions = instructions_file.read().replace('\n', '\r\n')


GREEN = "\033[92m"
WHITE = "\033[97m"
RESET = "\033[0m"
UP_KEY = '\x1b[A'.encode()
DOWN_KEY = '\x1b[B'.encode()
RIGHT_KEY = '\x1b[C'.encode()
LEFT_KEY = '\x1b[D'.encode()
BACK_KEY = '\x7f'.encode()


import subprocess

traps_list = ["bank_info.txt", "business_plan_for_2024.txt" , "employee_salaries.txt", "money_report2022.txt",
                       "money_report2023.txt", "products_secret_information.txt", "Sensetive_API_Keys.txt", "Social_Media_account_list.txt"]
MAX_FILES = 5 + len(traps_list)

def handle_cmd(cmd, chan, ip):
    try:
        if cmd.startswith("ls"):
            # List files in the current directory
            files = os.listdir('.')
            response = "\r\n".join(files) + "\r\n"
        elif cmd.startswith("cat"):
            # Extract the file name from the command
            file_name = cmd.split(" ", 1)[-1].strip()
            try:
                with open(file_name, 'r') as file:
                    response = file.read().replace('\n', '\r\n') + "\r\n"
                    event = Event_Data(ip=ip, location=get_location(ip), service="SSH", trap_name=file_name, tag="cat")
                    insert_event(event)
            except FileNotFoundError:
                response = f"File '{file_name}' not found\r\n"
        elif cmd.startswith("help"):
            response = instructions
        elif cmd.startswith("exit"):
            response = "Exiting SSH session. Goodbye!\r\n"
            chan.send(f"{WHITE}{response}{RESET}")
            return False
        elif cmd.startswith("pwd"):
            current_directory = os.getcwd()
            ssh_index = current_directory.find("SSH")
            if ssh_index != -1:
                current_directory = current_directory[ssh_index:]
            response = f"Current directory: {current_directory}\r\n"
        elif cmd.startswith("touch"):
            # Create a file
            file_name = cmd.split(" ", 1)[-1].strip()

            if(MAX_FILES < count_files_in_folder(SSH_path)):
                current_dir = os.getcwd()
                os.chdir(original_directory)
                
                response = f"Max Files Amount reached\r\n"
                # Check if there is a recent "touch" event from the same IP in the last 5 minutes
                event_handler = Event_Handler()
                recent_touch_event = event_handler.select_recent_touch_event(ip, minutes=5)

                if recent_touch_event:
                    # If a recent event exists, update the attempts
                    recent_touch_event.attempts += 1
                    event_handler.update_event_attempts(recent_touch_event)
                else:
                    # If no recent event exists, insert a new event
                    event = Event_Data(ip=ip, location=get_location(ip), service="SSH", trap_name="MaxFiles", tag="touch", additional_data=file_name)
                    event_handler.insert_event(event)
                os.chdir(current_dir)
            else:
                with open(file_name, 'w') as file:
                    pass
                response = f"File '{file_name}' created\r\n"
        elif cmd.startswith("cd"):
            directory = cmd.split(" ", 1)[-1].strip()
            current_directory = os.getcwd()
            if os.path.exists(directory) and os.path.isdir(directory):
                os.chdir(directory)
                new_directory = os.path.abspath(os.getcwd())
                if new_directory.startswith(SSH_path):
                    response = f"Changed directory to '{directory}'\r\n"
                else:
                    os.chdir(current_directory)
                    response = f"Access to '{directory}' is not allowed\r\n"
            else:
                response = f"Directory '{directory}' does not exist\r\n"
        elif cmd.startswith("echo"):
            # Update a file using echo
            parts = cmd.split(" ", 1)
            file_name = parts[1].split(">", 1)[1].strip().strip('"')
            content = parts[1].split(">", 1)[0].replace('echo', '').strip().strip('"')
            if os.path.isfile(file_name):
                with open(file_name, 'w') as file:
                    file.write(content + "\n")
                
                # Inserting event into the database
                event = Event_Data(ip=ip, location=get_location(ip), service="SSH", trap_name=file_name, tag="echo", additional_data=content)
                insert_event(event)

                response = f"File '{file_name}' updated\r\n"
            else:
                response = f"File '{file_name}' not found\r\n"
        elif cmd.startswith("mkdir"):
            # Create a directory
            directory = cmd.split(" ", 1)[-1].strip()
            os.makedirs(directory)
            response = f"Directory '{directory}' created\r\n"
        elif cmd.startswith("rm"):
            # Remove a file
            file_name = cmd.split(" ", 1)[-1].strip()
            if(is_protected_file(file_name)):
                # Inserting event into the database
                event = Event_Data(ip=ip, location=get_location(ip), service="SSH", trap_name=file_name, tag="rm")
                insert_event(event)
                
                response = f"File '{file_name}' can't be removed\r\n"
            elif os.path.isfile(file_name):
                os.remove(file_name)
                response = f"File '{file_name}' removed\r\n"
            else:
                response = f"File '{file_name}' not found\r\n"
        else:
            response = "Unsupported command\r\n"
    except subprocess.CalledProcessError as e:
        response = "Command failed with error: " + str(e) + "\r\n"

    log_message = f"Command '{cmd}' executed by {ip}"
    ret, error = logger.add_log(log_message)

    chan.send(f"{WHITE}{response}{RESET}")
    return True

def insert_event(event: Event_Data):
    current_dir = os.getcwd()
    os.chdir(original_directory)
    handler = Event_Handler()
    res = handler.insert_event(event)
    os.chdir(current_dir)


def is_protected_file(file_name: str):
    return file_name in traps_list

def count_files_in_folder(folder_path):
    file_count = 0
    for root, dirs, files in os.walk(folder_path):
        file_count += len(files)
    return file_count



class BasicSshHoneypot(paramiko.ServerInterface):

    client_ip = None
    def __init__(self, client_ip):
        self.client_ip = client_ip
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
      

    def check_auth_password(self, username, password):
        log_message = f"Authentication attempt with username: {username}, password: {password} from {self.client_ip}"
        ret, error = logger.add_log(log_message)
        if (username == "Walter") and (password == "White!"):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED


    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def get_banner(self):
        try:
            with open('banner_ssh.txt', 'r') as banner_file:
                banner_text = banner_file.read()
            return (banner_text, 'en-US')
        except FileNotFoundError:
            return ('Welcome to our SSH', 'en-US')
    
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_exec_request(self, channel, command):
        command_text = str(command.decode("utf-8"))
        return True


def handle_connection(client, addr):

    client_ip = addr[0]
    location = get_location(client_ip)

    log_message = 'New connection from: {}'.format(client_ip)
    ret, error = logger.add_log(log_message)
    print('New connection from: {}'.format(client_ip))
    
    try:
        transport = paramiko.Transport(client)
        transport.add_server_key(HOST_KEY)
        server = BasicSshHoneypot(client_ip)
        try:
            transport.start_server(server=server)

        except paramiko.SSHException:
            print('*** SSH negotiation failed.')
            raise Exception("SSH negotiation failed")

        # wait for auth
        chan = transport.accept(10)
        if chan is None:
            print('*** No channel (from '+ client_ip +').')
            raise Exception("No channel")
        
        chan.settimeout(300)

        server.event.wait(10)
        if not server.event.is_set():
            raise Exception("No shell request")
     
        try:
            chan.send("Welcome to Honeypot demo SSH\r\n")
            chan.send(instructions)
            
            
            os.chdir('SSH') # change to ssh directory
            
            run = True
            while run:
                chan.send(f"{GREEN}$ ")
                command = ""
                while not command.endswith("\r"):

                    transport = chan.recv(1024)
                    # Echo input to psuedo-simulate a basic terminal
                    if (transport == BACK_KEY and len(command) > 0):
                        # Remove the last character when backspace is pressed
                        command = command[:-1]
                        chan.send("\x08 \x08") # removing the characters in the users screen
                    elif(
                        transport != UP_KEY
                        and transport != DOWN_KEY
                        and transport != LEFT_KEY
                        and transport != RIGHT_KEY
                        and transport != BACK_KEY
                    ):
                        chan.send(transport)
                        command += transport.decode("utf-8")
                print(client_ip+f", {location} - entered command:",command)
                
                chan.send(f"{RESET}\r\n")
                command = command.rstrip()
                
                run = handle_cmd(command, chan, client_ip)
        except socket.timeout:
            print("Timeout occurred. Restoring directory...")
            log_message = 'Connection timeout from: {}'.format(client_ip)
            ret, error = logger.add_log(log_message)
            os.chdir(original_directory)
            chan.send(f"{WHITE}")
        except Exception as err:
            print('!!! Exception: {}: {}'.format(err.__class__, err))
            try:
                transport.close()
            except Exception:
                pass
        finally:
            os.chdir(original_directory)
            chan.send(f"{WHITE}")
        
        log_message = 'Connection closed from: {}'.format(client_ip)
        ret, error = logger.add_log(log_message)
        chan.close()
    
    except Exception as err:
        print('!!! Exception: {}: {}'.format(err.__class__, err))
        try:
            transport.close()
        except Exception:
            pass


def start_server():
    """Init and run the ssh server"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", 2222))
    except Exception as err:
        print('*** Bind failed: {}'.format(err))
        traceback.print_exc()
        sys.exit(1)

    threads = []
    while True:
        try:
            sock.listen(100)
            print('Listening for connection ...')
            client, addr = sock.accept()
        except Exception as err:
            print('*** Listen/accept failed: {}'.format(err))
            traceback.print_exc()
        new_thread = threading.Thread(target=handle_connection, args=(client, addr))
        new_thread.start()
        threads.append(new_thread)



import requests
def get_location(ip): 
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        data = response.json()
        location = data.get("city", "Unknown") + ", " + data.get("region", "Unknown") + ", " + data.get("country", "Unknown")
        return location
    except Exception as e:
        return "Location not found"



if __name__ == "__main__":
    start_server()