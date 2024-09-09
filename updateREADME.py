import json
import re
import sys


def clean_key(key):
    # create a match patter that replaces certain kesy with a more readable format
    match key:
        case "'\\x03'":
            return "Copy"
        case "'\\x16'":
            return "Paste"
        case "'\\x01'":
            return "Cut"
        case "'\\x18'":
            return "Select All"
        case _:
            # return the items.key as is but without the single quotes and \ character
            return key.replace("'", "").replace("\\", "")
   

def calculate_total_values(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            json_data = file.read()

        # Parse the JSON data
        data = json.loads(json_data)
        
        # Calculate the total items.value
        total_value = sum(item['value'] for item in data)
        
        return total_value, data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None, []

def update_readme(readme_file_path, stats_data, total_value):
    try:
        with open(readme_file_path, 'r', encoding="utf-8") as file:
            readme_content = file.read()



        stats = ''
        

        for items in stats_data:
            key = items['key']
            value = items['value']
            percentage = (value / total_value) * 100

            #skip items with percentage less than 1
            if percentage < 1:
                continue
            bars = '█' * int(percentage / 5) + '░' * (20 - int(percentage / 5))
            # stats += f'{key:<20} {value:<10} {bars} {percentage:.2f} % \n'
            stats += f'{key:<20} {value:<10} {bars} {percentage:.2f} % \n'

        print("Stats: ", stats)


        # Replace the content between the markers
        updated_content = re.sub(
            r'<!--START_SECTION:activity-->(.*?)<!--END_SECTION:activity-->',
            f'<!--START_SECTION:activity-->\n```txt\n{stats}\n```\n<!--END_SECTION:activity-->',
            readme_content,
            flags=re.DOTALL
        )
        print("new Content: ", updated_content)


        with open(readme_file_path, 'w', encoding="utf-8") as file:
            file.write(updated_content)
        
        print("README.md updated successfully.")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main(json_file_path, readme_file_path):
    try:
        
        total_value, stats_data = calculate_total_values(json_file_path)
        print(f"Total items.value combined: {total_value}")

        # sort the stats_data by items.value in descending order
        stats_data = sorted(stats_data, key=lambda x: x['value'], reverse=True)

        #map over the stats_data and clean the keys
        stats_data = [{"key": clean_key(item['key']), "value": item['value']} for item in stats_data]
        
        update_readme(readme_file_path, stats_data, total_value)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    
    #read commandline input
    if len(sys.argv) != 3:
        print("Usage: python updateREADME.py <path_to_stats.json> <path_to_README.md>")
        sys.exit(1)
    json_file_path = sys.argv[1]
    readme_file_path = sys.argv[2]


    json_file_path = './stats.json'  # Replace with the actual path to your JSON file
    readme_file_path = './README.md'  # Replace with the actual path to your README.md file
    main(json_file_path, readme_file_path)