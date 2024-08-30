import json
import re

## add type {key: string, value: number}[]

jsonType = {
  "key": "string",
  "value": "number"
}

with open('stats.json') as json_file:
    data: list[dict[str, int]] = json.load(json_file)

    # Calculate the total of all keystrokes
    total_keystrokes = sum(item['value'] for item in data)

    
    print("Total keystrokes:", total_keystrokes)


with open('README.md', 'r+') as readme:
    content = readme.read()

    stats = ''

    stats += 'keyboard events: \n'


    for key, value in data:
      print("key: ", key, "keyValues key:", value )
      if key == 'AmountOfClicks':
         continue
      percentage = (int(value)) / total_keystrokes) * 100
      bars = '█' * int(percentage / 5) + '░' * (20 - int(percentage / 5))
      stats += f'{key:<20} {value:<10} {bars} {percentage:.2f} % \n'
    new_content = re.sub('<!--START_SECTION:activity-->.*<!--END_SECTION:activity-->', f'<!--START_SECTION:activity-->\n```txt\n{stats}\n```\n<!--END_SECTION:activity-->', content, flags=re.DOTALL)
    readme.seek(0)
    readme.write(new_content)
    readme.truncate()