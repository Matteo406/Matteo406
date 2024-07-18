import json
import logging
import subprocess
from threading import Timer, Lock
from pynput import keyboard, mouse
from pynput.keyboard import Key
from typing import Dict, Union
from customeKeyNames import customeKeyNames

# Define the type for the event buffer
EventBufferType = Dict[Union[Key, str], int]

# Configuration
BUFFER_FLUSH_INTERVAL = 10  # seconds
BUFFER_SIZE_THRESHOLD = 100  # Max events before flush

PATH_TO_REPO = 'C:/Tim-Paris-Schule/OwnProjects/Matteo406'

start_marker = "<!--START_SECTION:activity-->"
end_marker = "<!--END_SECTION:activity-->"

# Basic configuration for diagnostic logging
logging.basicConfig(filename='keyEvent.log',
                    filemode='a',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')



# Globals
event_buffer: EventBufferType = {}  # To store events
buffer_lock = Lock()  # To prevent concurrent access issues
flush_timer = None


class eventWriter:
    def sort_event_keys(self, event_buffer: EventBufferType) -> EventBufferType:
        """
        Sorts the keys of the event buffer dictionary and returns a new dictionary with sorted keys.

        Parameters:
        - event_buffer (EventBufferType): The event buffer dictionary to sort.

        Returns:
        - EventBufferType: A new dictionary with keys sorted.
        """
        # Using sorted() to sort the keys and then creating a new dictionary with these sorted keys
        sorted_data = dict(sorted(event_buffer.items(), key=lambda item: item[1], reverse=True))
        return sorted_data
    

    def combine_event_buffers(self, buffer1: EventBufferType, buffer2: EventBufferType) -> EventBufferType:
        combined_buffer = buffer1.copy()

        for key, count in buffer2.items():
            # Convert key to string if it's not already a string
            key_str = str(key) if not isinstance(key, str) else key

            # Attempt to match and combine with an existing key in combined_buffer
            if key_str in combined_buffer:
                combined_buffer[key_str] += count
            else:
                # If no direct match, attempt to find a matching key by other means
                # This is a placeholder for logic that matches object keys to string keys
                matched_key = self.match_key(key_str, list(combined_buffer.keys()))
                if matched_key:
                    combined_buffer[matched_key] += count
                else:
                    combined_buffer[key_str] = count

        return combined_buffer
    


    def match_key(self, key_str: str, existing_keys: list) -> str:
        # Implement logic to match key_str to an existing key in existing_keys
        # This could involve stripping object details, comparing base names, etc.
        # Placeholder implementation:
        for existing_key in existing_keys:
            if key_str.split(':')[0] in existing_key:
                return existing_key
        return None
    

    def getNameEvents(self, event) -> str: # : Union[str, Key]
        if isinstance(event, Key):
            print('event: ', event, ' is instance: ', event.name)
            return event.name
        else:
            print('analysing event: ', event)
            #get type of event
            print('type: ', type(event))
            print('customeKeyNames.get(event, event)', customeKeyNames.get(event, event))
            return customeKeyNames.get(event, event)





    def writeJSON(self, event_buffer: EventBufferType, path: str):
        with open(path, 'w', encoding='utf-8') as json_file:
            json.dump(event_buffer, json_file, ensure_ascii=False, indent=4)

    def readJSON(self, path: str) -> EventBufferType:
        try:
            with open(path, 'r', encoding='utf-8') as json_file:
                data = json_file.read()
                # Check if the file is empty or contains only whitespace
                if not data.strip():
                    return {}  # Return an empty dictionary for empty files
                return json.loads(data)  # Parse and return the JSON data
        except FileNotFoundError:
            return {}  # Return an empty dictionary if the file does not exist
        except json.JSONDecodeError:
            print(f"Warning: Corrupted JSON file at {path}. Returning empty dictionary.")
            return {}  # Return an empty dictionary if the JSON is invalidn json.loads(data)  # Parse and return the JSON data
        except FileNotFoundError:
            return {}  # Return an empty dictionary if the file does not exist
        except json.JSONDecodeError:
            print(f"Warning: Corrupted JSON file at {path}. Returning empty dictionary.")
            return {}  # Return an empty dictionary if the JSON is invalid
    
    def updateJSON(self, event_buffer: EventBufferType, path: str):
        existing_data = self.readJSON(path)
        print("existing_data", existing_data)
        combined_data = self.combine_event_buffers(existing_data, event_buffer)
            
        allNamedEvents = {self.getNameEvents(event): count for event, count in combined_data.items()}


        print("allNamedEvents", allNamedEvents)
        self.writeJSON(allNamedEvents, path) 

def flush_buffer():
    global event_buffer, flush_timer
    with buffer_lock:
        if event_buffer:
            newEventWriter = eventWriter()

            # newEventWriter.updateREADME(event_buffer, PATH_TO_REPO + '/README.md')
            newEventWriter.updateJSON(event_buffer, PATH_TO_REPO + '/stats.json')


            # Process the buffered events here
            logging.info(f"Flushing {len(event_buffer)} events")
            event_buffer.clear()  # Clear the buffer after processing
        flush_timer = Timer(BUFFER_FLUSH_INTERVAL, flush_buffer)
        flush_timer.start()


def commitChanges():
    try:
        # Add all changes to staging
        subprocess.run(["git", "add", "."], check=True)
        
        # Commit the changes
        commit_message = "Automated commit message"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Push the changes
        subprocess.run(["git", "push"], check=True)
        
        print("Changes have been successfully committed and pushed to the repository.")
        logging.info("Changes have been successfully committed and pushed to the repository.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to commit and push changes: {e}")
        logging.error(f"An error occurred while trying to commit and push changes: {e}")



def add_event_to_buffer(event):
    global event_buffer
    with buffer_lock:
        print(event)
        event_buffer[event] = event_buffer.get(event, 0) + 1

       
                
def onPressEventHandler(key):
    add_event_to_buffer(key)

def onClickEventHandler(x, y, button, pressed):
    if not pressed:
        add_event_to_buffer((button))

def eventListener():
    logging.info('Starting event listeners.')
    with keyboard.Listener(on_press=onPressEventHandler) as k_listener, \
         mouse.Listener(on_click=onClickEventHandler) as m_listener:
        k_listener.join()
        m_listener.join()


def start_flush_timer():
    global flush_timer
    flush_timer = Timer(BUFFER_FLUSH_INTERVAL, flush_buffer)
    flush_timer.start()

def stop_flush_timer():
    global flush_timer
    if flush_timer:
        flush_timer.cancel()

if __name__ == "__main__":
    logging.info('Start of the keylogger')
    start_flush_timer()
    try:
        eventListener()
    finally:
        logging.info('End of the keylogger')
        stop_flush_timer()
        flush_buffer()  # Ensure buffer is flushed on exit
        commitChanges()