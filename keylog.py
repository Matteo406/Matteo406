from pynput import keyboard, mouse
from datetime import datetime
from dotenv import load_dotenv
import git
import os
import schedule
import time

# Load the .env file
load_dotenv()

# Define the log file and the repo
log_file = os.getenv('PATH_TO_LOGFILE')
repo_dir = os.getenv('PATH_TO_REPO')

# Initialize counts
key_count = 0
click_count = 0

# Initialize last counts
last_key_count = 0
last_click_count = 0

def on_press(key):
    global key_count
    key_count += 1

def on_click(x, y, button, pressed):
    global click_count
    if pressed:
        click_count += 1

def save_counts():
    global last_key_count, last_click_count

    # Only save to file if the counts have changed
    if key_count != last_key_count or click_count != last_click_count:
        with open(log_file, 'w') as f:
            f.write(f'<!--START_SECTION:activity-->\n\n')
            f.write(f'```txt\n')
            f.write(f'From: {datetime.now().strftime("%d %B %Y")} - To: {datetime.now().strftime("%d %B %Y")}\n\n')
            f.write(f'Total Keystrokes: {key_count}\n')
            f.write(f'Total Mouse Clicks: {click_count}\n')
            f.write(f'```\n')
            f.write(f'\n<!--END_SECTION:activity-->\n')

        # Update last counts
        last_key_count = key_count
        last_click_count = click_count

def commit_and_push():
    # Commit and push
    repo = git.Repo(repo_dir)
    repo.git.add(log_file)
    repo.git.commit('-m', 'update log file')
    repo.git.push()

# Schedule the save_counts function to be called every 5 minutes
schedule.every(1).minutes.do(save_counts)

# Schedule the commit_and_push function to be called every hour
# schedule.every(1).hours.do(commit_and_push)
schedule.every(1).minutes.do(commit_and_push)

# Start the listeners
with keyboard.Listener(on_press=on_press) as k_listener, mouse.Listener(on_click=on_click) as m_listener:
    print('Listening...')
    while True:
        schedule.run_pending()
        time.sleep(1)