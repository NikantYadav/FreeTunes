from fastapi import FastAPI
import json


app = FastAPI()


@app.get("/items/{item_id}")

async def read_link(item_id):
	global link 
	link = item_id
	list_json = [link]
	json_object = json.dumps(list_json, indent=1)
	with open("sample.json", "w") as outfile:
		outfile.write(json_object)
	return link
