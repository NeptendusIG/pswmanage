import json
from utility import File
r = File.JsonFile.get_value_jsondict('main_settings.json', 'source_path')

print(r)