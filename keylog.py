from datetime import datetime
from pynput import keyboard, mouse
import logging
import os
import json
from dotenv import load_dotenv
import schedule
from typing import Optional
import time
from memory_profiler import profile
import re
import git
import sys


# Load the .env file
load_dotenv()

# Define the log file and the repo
repo_dir = os.getenv('PATH_TO_REPO')

lockFile = 'script.lock'
#timepattern
timePattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}"

# Configure logging
logging.basicConfig(filename=repo_dir + 'app.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def isEventOfType(currentEvent: object, eventType: str):
    if (currentEvent['Event'] == eventType):
        return True
    else:
        return False
    


def isPattern(eventArray_p: list[object],  patternPartOne: str = None, patternPartTwo: str = None, patternPartThree: str = None):
    PatternOccurrence = 0
    for index, event in enumerate(eventArray_p):
        print('i: ', index, ' e: ', event)

        # Remove the extra quotes from the event key
        event_key = event['key'].strip("'")

        
        #check for first pattern only first 
        if event_key == patternPartOne and patternPartTwo is None:
            # print('case 1')
            PatternOccurrence = PatternOccurrence + 1
            continue

        # check if eventArray is long enough
        if not len(eventArray_p) > index + 1:
            continue

        if event_key == patternPartOne and eventArray_p[index + 1]['key'] == patternPartTwo and patternPartThree is None:
            # print('case 2')
            PatternOccurrence = PatternOccurrence + 1
            continue

        # check if eventArray is long enough
        if not len(eventArray_p) > index + 2:
            continue

        # check for the first, secon and third pattern
        if event_key == patternPartOne and eventArray_p[index + 1]['key'] == patternPartTwo and eventArray_p[index + 2]['key'] == patternPartThree:
            # print('case 3')
            PatternOccurrence = PatternOccurrence + 1
            continue
    

    return PatternOccurrence









def analyseEvents(eventArray_p: list[object]):
    logging.info('Starting to analyse events.')

    pressEvents = list(filter(lambda event: isEventOfType(event, 'Press'), eventArray_p))
    clickEvents = list(filter(lambda event: isEventOfType(event, 'Click'), eventArray_p))

    logging.info(f'Found {len(pressEvents)} press events and {len(clickEvents)} click events.')

    data = {
        "AmountOfClicks": len(clickEvents),
        "AmountOfPress": len(pressEvents),
        "AmountOfCopy": isPattern(pressEvents, '\\x03'),
        "AmountOfPaste": isPattern(pressEvents, '\\x16'),
        "AmountOfSave": isPattern(pressEvents, '\\x13'),
        "AmountOfCut": isPattern(pressEvents, '\\x18'),
        "AmountOfUndo": isPattern(pressEvents, '\\x1a'),
        "AmountOfRedo": isPattern(pressEvents, '\\x19'),
        "AmountOfSelectAll": isPattern(pressEvents, '\\x01'),
        "AmountOfFind": isPattern(pressEvents, '\\x06'),
        "AmountOfReplace": isPattern(pressEvents, '\\x08'),
        "AmountOfPrint": isPattern(pressEvents, '\\x10')
    }

    logging.info('Generated data from events.')

    statsFilePath = repo_dir + 'stats.json'

    if not statsFilePath:
        logging.info('no stats file path found')
        statsFilePath = os.getcwd()

    if os.path.exists(statsFilePath):
        with open(statsFilePath, 'r') as f:
            existing_data = json.load(f)
        for key, value in data.items():
            if key in existing_data:
                existing_data[key] += value
            else:
                existing_data[key] = value
        data = existing_data

    logging.info('Updated existing data with new data.')

    with open(statsFilePath, 'w') as f:
        json.dump(data, f, indent=4)

    logging.info('Saved data to file. %s', statsFilePath)



    
    


def updateEventArray(eventType:str, pressedKey: str = None, y: int = None, x: int = None, buttonPressed: bool = None ):
    #create json object
    eventJSON = {'Event': eventType, 'key': pressedKey or "", "buttonPressed": buttonPressed or "", "y": y or '', "x": x or ''}

    #add to array
    EventArray.append(eventJSON)


    if len(EventArray) > 50:
        analyseEvents(EventArray)
        print('clear')
        EventArray.clear()





def onPressEventHandler(key):
    # print('key: '+ str(key))
    updateEventArray("Press", str(key))

def onClickEventHandler(x, y, button, pressed):
    # print('button: '+ str(button))
    # print('y: '+ str(y) + 'x: '+ str(x))
    # print('pressed: '+ str(pressed))
    updateEventArray("Click", "", y, x, pressed)


def commit_and_push():
    # Commit and push
    try: 
        repo = git.Repo(repo_dir)
        repo.git.add(repo_dir + 'stats.json')
        repo.git.commit('-m', 'update stats file')
        repo.git.push()
        logging.info('Script git pushed')
    except Exception as e:
        print(f'Failed to push to repo: {str(e)}')
        logging.error('Failed to push to repo', e)


# Schedule the commit_and_push function to be called every hour
schedule.every(1).hours.do(commit_and_push)


def eventListener():
    logging.info('Starting event listeners.')
    with keyboard.Listener(on_press=onPressEventHandler) as k_listener, mouse.Listener(on_click=onClickEventHandler) as m_listener:
        while True:
            schedule.run_pending()
            time.sleep(1)


def getTimeFromLockFile() -> datetime:
    with open(lockFile, 'r') as lockfile:
        lines = lockfile.readlines()
        for line in lines:
            match = re.search(timePattern, line)
            if match:
                return datetime.strptime(match.group(),"%Y-%m-%d %H:%M:%S.%f")
        logging.warning('No match found in lock file.')

def writeLockFile():
    with open(lockFile, 'w') as file:
        file.write(str(datetime.now()))
        file.write('/n')
        file.write("Lock file for script instance management.")
        logging.info('Lock file written.')


def continueScriptCheck() -> bool: 
    if not os.path.exists(repo_dir + lockFile):
        logging.info('Lock file does not exist. Writing lock file.')
        writeLockFile()
        return True

    lastStartDateTime = getTimeFromLockFile()

    if lastStartDateTime.date() != datetime.now().date():
        logging.info('Script not started today. Removing and writing lock file.')
        os.remove(lockFile)
        writeLockFile()
        return True 
    else:
        logging.info('Script started today. Exiting.')
        sys.exit()
        return False
    


if __name__ == "__main__":
    logging.info('Start')

    EventArray = []


    try:
        if not continueScriptCheck():
            logging.warning('Script check failed. Exiting.')
            sys.exit()

        if not repo_dir:
            logging.error("Error: repo_dir is empty")
            sys.exit("Error: repo_dir is empty")

        eventListener()

    except Exception as e:
        logging.error('Error occurred: %s', e)

    finally:
        commit_and_push()
        os.remove(lockFile)
        logging.info('Lock file removed.')

