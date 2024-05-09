import json

link = 'youtube'

list = [link]

json_object = json.dumps(list, indent=1)
with open("sample.json", "w") as outfile:
    outfile.write(json_object)