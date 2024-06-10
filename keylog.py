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
import sys


# Load the .env file
load_dotenv()

# Define the log file and the repo
repo_dir = os.getenv('PATH_TO_REPO')
lockFile = 'script.lock'
#timepattern
timePattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}"

# Configure logging
logging.basicConfig(filename=repo_dir + 'taskLog2.log', level=logging.INFO, format='%(asctime)s %(message)s')


EventArray = []
   


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

        if event_key == patternPartOne:
            print('works')
        else:
            print('shit')

        # # check for first pattern part
        # if not event['key'] == patternPartOne:
        #     print('skip')
        #     continue
        
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
    # print('list',eventArray_p )
    print('analyse')

    pressEvents = list(filter(lambda event: isEventOfType(event, 'Press'), eventArray_p))
    clickEvents = list(filter(lambda event: isEventOfType(event, 'Click'), eventArray_p))

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

    if os.path.exists('stats.json'):
        with open('stats.json', 'r') as f:
            existing_data = json.load(f)
        for key, value in data.items():
            if key in existing_data:
                existing_data[key] += value
            else:
                existing_data[key] = value
        data = existing_data

    with open('stats.json', 'w') as f:
        json.dump(data, f, indent=4)



    
    


def updateEventArray(eventType:str, pressedKey: str = None, y: int = None, x: int = None, buttonPressed: bool = None ):
    #create json object
    eventJSON = {'Event': eventType, 'key': pressedKey or "", "buttonPressed": buttonPressed or "", "y": y or '', "x": x or ''}

    #add to array
    EventArray.append(eventJSON)

    # print('length', len(EventArray))

    if len(EventArray) > 10:
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




def eventListener():
    with keyboard.Listener(on_press=onPressEventHandler) as k_listener, mouse.Listener(on_click=onClickEventHandler) as m_listener:
        while True:
            time.sleep(1)


def getTimeFromLockFile() -> datetime:
    with open(lockFile, 'r') as lockfile:
        lines = lockfile.readlines()
        for line in lines:
            match = re.search(timePattern, line)
            if match:
                return datetime.strptime(match.group(),"%Y-%m-%d %H:%M:%S.%f")


def writeLockFile():
    with open(lockFile, 'w') as file:
                file.write(str(datetime.now()))
                file.write('/n')
                file.write("Lock file for script instance management.")


def continueScriptCheck() -> bool: 
    if not os.path.exists(repo_dir + lockFile):
                writeLockFile()
                return True
    
    lastStartDateTime = getTimeFromLockFile()

    if lastStartDateTime.date() != datetime.now().date():
        print('started not today')
        os.remove(lockFile)
        writeLockFile()
        return True 
    else:
        print('started today')
        sys.exit()
        return False


if __name__ == "__main__":
    print('start')

    try:
        if not continueScriptCheck():
            sys.exit()

        eventListener()

        
    except Exception as e:
        print('error', e)

    finally:
        os.remove(lockFile)

