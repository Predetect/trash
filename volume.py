import requests
import re
import json
from bs4 import BeautifulSoup

def get(id):
	page = requests.get("http://services.runescape.com/m=itemdb_oldschool/Iron_pickaxe/viewitem?obj=%s#180" % id)
	soup = BeautifulSoup(page.content, 'html.parser')
	data = soup.find_all('script')[1]
	text = data.get_text()
	regex = r"trade180\.push\(\[new Date\('\d+/\d+/\d+'\), (\d+)"
	volumes = re.findall(regex, text)
	return(volumes)
	
def all(filename):
	with open(filename) as f:
		items = json.load(f)
	
	volumes = {}
	
	for item in items:
		v = get(item)
		volumes[item] = v 

	with open('volumes'+filename, 'w') as f:
		json.dump(volumes, f)


