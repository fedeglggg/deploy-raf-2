# type: ignore pylance drunk
import paramiko
import getpass
import sys
import os

# Git commands
checkout = 'git checkout'
fetch = 'git fetch'
pull = 'git pull'

# Clear the terminal screen
def clear_terminal():
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Linux and macOS
        os.system('clear')
clear_terminal()


# Directories
project_directory = ""
backend_folder = ""
frontend_folder = ""

print("What enviroment are you updating?")
print("1 -  (155)")
print("2 -  (165)")
serv = input()
clear_terminal()

# SSH server details
host = 
port = 
username = 
password = getpass.getpass('Password:')
clear_terminal()

############## Menu ##############

# Asking for what to update
print("What do you wanna update?")
print("1 - update everything")
print("2 - only backend")
print("3 - only frontend")
side = input()
clear_terminal()


# Asking for storybook
build_stories = False
if side == "1" or side == "3":
    print("Do you wanna build the storybook? y/n")
    if input() == "y":
        build_stories = True
    clear_terminal()

# Asking for the enviroment
print("Pick an enviroment to update:")
print("1 - dev (developing)")
print("2 - tst (testing)")
print("3 - stg (staging)")
env = input()
if env == "1":
    env = "dev"
elif env == "2":
    env = "tst"
elif env == "3":
    env = "stg"
else:
    sys.exit(0)

clear_terminal()

# Asking for git branch
checkout_branch = input("Do you wanna switch to a git branch ? if so write a branchname: ")
clear_terminal()

# Cds
cd_backend = f'cd {project_directory}/{env}/{backend_folder}'
cd_frontend = f'cd {project_directory}/{env}/{frontend_folder}'

# Terminal command to execute
yarn_build = 'yarn run build'
yarn_build_storybook = 'yarn run build-storybook'
activate_venv = f'source {project_directory}/{env}/{backend_folder}/env/bin/activate'
run_migrations = f'python manage.py migrate && echo {password} | sudo -S supervisorctl restart all'

# Functions
def is_tag(branchname):
    return '.' in branchname

def add_update_backend_to_comms(comms, checkout_branch):
    if checkout_branch != "":
        set_backend = f'{fetch} && {checkout} {checkout_branch}'
        if not is_tag(checkout_branch):
            set_backend = f'{set_backend} && {pull}'
    else:
        set_backend = pull
    
    command = {
            "exec":  f'{cd_backend} && {set_backend} && {activate_venv} && {run_migrations}',
            "error": "error during running migrations",
            "skip": False
        }
    comms.insert(0, command)
    return comms

def add_update_frontend_to_comms(comms, checkout_branch, build_stories):

    if build_stories:
        command = {
            "exec":  f'{cd_frontend} && {yarn_build_storybook}',
            "error": "error during building react app",
            "skip": True
        }
        comms.insert(0, command)

    if checkout_branch != "":
        set_frontend = f'{fetch} && {checkout} {checkout_branch}'
        if not is_tag(checkout_branch):
            set_frontend = f'{set_frontend} && {pull}'
    else:
        set_frontend = pull
    
    command = {
        "exec": f'{cd_frontend} && {set_frontend} && {yarn_build}',
        "error": "error during building react app",
        "skip": False
    }
    comms.insert(0, command)

    return comms

# building command list
commands = []
if side == "1":
    commands = add_update_backend_to_comms(commands, checkout_branch)
    commands = add_update_frontend_to_comms(commands, checkout_branch, build_stories)
elif side == "2":
    commands = add_update_backend_to_comms(commands, checkout_branch)
elif side == "3":
    commands = add_update_frontend_to_comms(commands, checkout_branch, build_stories)
else:
    sys.exit(0)

clear_terminal()

print(f'Running ssh {username}@{host} -p {port}')

# Create SSH client
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Connect to the SSH server
    ssh_client.connect(host, port, username, password)
    print("Connected to the server")

    for command in commands:
        print("Running", command["exec"])
        stdin, stdout, stderr = ssh_client.exec_command(command["exec"])

        if command["skip"] != True:
            exit_status = stdout.channel.recv_exit_status()
            print(stderr.read().decode())

            output = stdout.read().decode()
            print(output)

        if exit_status == 0:
            print("Finished running ", command["exec"])
        else:
            print("Error - ", command["error"])
        print("------------------------")


finally:
    ssh_client.close()
