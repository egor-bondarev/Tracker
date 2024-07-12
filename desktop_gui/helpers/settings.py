''' Get settings from settings.json. '''

import json

SETTINGS_FILENAME = './desktop_gui/settings.json'

class Settings:
    ''' Get settings. '''

    def get_url(self):
        ''' Return url. '''

        with open(file=SETTINGS_FILENAME, encoding="utf-8", mode='r') as file:
            settings = json.load(file)

        return settings["url"]
