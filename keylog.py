from pynput import keyboard, mouse
from datetime import datetime
from dotenv import load_dotenv
import git
import os

# Load the .env file
load_dotenv()

# Define the log file and the repo
log_file = os.getenv('PATH_TO_LOGFILE')
repo_dir = os.getenv('PATH_TO_REPO')

# Initialize counts
key_count = 0
click_count = 0

def on_press(key):
    global key_count
    key_count += 1
    save_counts()

def on_click(x, y, button, pressed):
    global click_count
    if pressed:
        click_count += 1
        save_counts()

def save_counts():
    # Check if repo_dir is set
    if repo_dir is None:
        print('Please set the repo_dir variable in the .env file')
        return

    # Check if log_file var is set
    if log_file is None:
        print('Please set the log_file variable in the .env file')
        return

    with open(log_file, 'w') as f:
        f.write(f'<!--START_SECTION:activity-->\n\n')
        f.write(f'From: {datetime.now().strftime("%d %B %Y")} - To: {datetime.now().strftime("%d %B %Y")}\n\n')
        f.write(f'Total Keystrokes: {key_count}\n')
        f.write(f'Total Mouse Clicks: {click_count}\n')
        f.write(f'\n<!--END_SECTION:activity-->\n')

    # Commit and push
    repo = git.Repo(repo_dir)
    repo.git.add(log_file)
    repo.git.commit('-m', 'update log file')
    repo.git.push()

# Start the listeners
with keyboard.Listener(on_press=on_press) as k_listener, mouse.Listener(on_click=on_click) as m_listener:
    k_listener.join()
    m_listener.join()