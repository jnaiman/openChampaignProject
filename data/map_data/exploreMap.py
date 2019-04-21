import json

saveFilejson = '/Users/jillnaiman1/openChampaignProject/data/map_data/City_Council_Districts_topojson.json'


with open(saveFilejson) as json_file:
    data = json.load(json_file)

t = data['transform']
