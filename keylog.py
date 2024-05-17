from pynput import keyboard, mouse
from datetime import datetime
from dotenv import load_dotenv
import logging
import git
import os
import schedule
import time




# Load the .env file
load_dotenv()

# Define the log file and the repo
log_file = os.getenv('PATH_TO_LOGFILE')
repo_dir = os.getenv('PATH_TO_REPO')


# Configure logging
logging.basicConfig(filename=repo_dir + 'taskLog.log', level=logging.INFO, format='%(asctime)s %(message)s')


# Log script start
logging.info('Script started')

# Initialize counts
key_count = 0
click_count = 0

# Initialize last counts
last_key_count = 0
last_click_count = 0


def getLastcount() -> tuple[int, int]:
    global key_count, click_count
    with open(log_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if 'Total Keystrokes' in line:
                last_key_count = int(line.split(':')[-1].strip())
                print("Last Key Count: ", last_key_count)
            if 'Total Mouse Clicks' in line:
                last_click_count = int(line.split(':')[-1].strip())
                print("Last Click Count: ", last_click_count)

    return last_key_count, last_click_count


def on_press(key):
    global key_count
    key_count += 1
    logging.info('Key press detected')

def on_click(x, y, button, pressed):
    global click_count
    if pressed:
        click_count += 1
        logging.info('Mouse click detected')

def save_counts():
    with open(log_file, 'w') as f:
        f.write(f'<!--START_SECTION:activity-->\n\n')
        f.write(f'```txt\n')
        f.write(f'From: {datetime.now().strftime("%d %B %Y")} - To: {datetime.now().strftime("%d %B %Y")}\n\n')
        f.write(f'Total Keystrokes: {key_count}\n')
        f.write(f'Total Mouse Clicks: {click_count}\n')
        f.write(f'```\n')
        f.write(f'\n<!--END_SECTION:activity-->\n')
    # Log script save
        logging.info('Script saved counts')

def commit_and_push():
    # Commit and push
    repo = git.Repo(repo_dir)
    repo.git.add(log_file)
    repo.git.commit('-m', 'update log file')
    repo.git.push()
    # Log script finish
    logging.info('Script git pushed')

# Schedule the save_counts function to be called every 5 minutes
schedule.every(5).minutes.do(save_counts)

# Schedule the commit_and_push function to be called every hour
# schedule.every(1).hours.do(commit_and_push)
schedule.every(1).minutes.do(commit_and_push)

# Start the listeners
with keyboard.Listener(on_press=on_press) as k_listener, mouse.Listener(on_click=on_click) as m_listener:
    print('Listening...')
    key_count, click_count = getLastcount()
    print("Key Count: ", key_count, "Click Count: ", click_count)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
            logging.info('Script finished sleeping (:')
    except Exception as e:
        logging.error('Script stopped due to error: %s', e)
        raise
    finally:
        logging.info('Script ended')