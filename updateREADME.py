import json
import re

with open('stats.json') as json_file:
    data = json.load(json_file)
totalPressEvents = data['AmountOfPress']
totalAmountClicks = data['AmountOfClicks']

with open('README.md', 'r+') as readme:
    content = readme.read()

    stats = ''

    stats += 'keyboard events: \n'


    for key, value in data.items():
      if key == 'AmountOfClicks':
         continue
      percentage = (value / totalPressEvents) * 100
      bars = '█' * int(percentage / 5) + '░' * (20 - int(percentage / 5))
      stats += f'{key:<20} {value:<10} {bars} {percentage:.2f} % \n'
    new_content = re.sub('<!--START_SECTION:activity-->.*<!--END_SECTION:activity-->', f'<!--START_SECTION:activity-->\n```txt\n{stats}\n```\n<!--END_SECTION:activity-->', content, flags=re.DOTALL)
    readme.seek(0)
    readme.write(new_content)
    readme.truncate()