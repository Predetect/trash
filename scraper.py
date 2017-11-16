import datetime as datetime
import json
import requests
import traceback
import time
import os.path
import os
import csv
import psutil
import gc
import requests
import re
import json
import time
from bs4 import BeautifulSoup

def GetItemLists():
	
	"""
	Scrapes a item summary from rsbuddy
	Creates two seperate jsons (membs/nonmembs)
	for members/non-member items respectively,
	keys are item-ids
	"""

	r = requests.get('https://rsbuddy.com/exchange/summary.json')
	items_json = r.json()

	membs = {}
	nonmembs = {}

	for k, v in items_json.items():
		if v['members'] == True:
			membs[k] = {'id': v['id'], 
						   'name': v['name']}
		else:
			nonmembs[k] = {'id': v['id'], 
							  'name': v['name']}

	with open('nonmembs.json', 'w') as f:
		json.dump(nonmembs, f)
	with open('membs.json', 'w') as f:
		json.dump(membs, f)


def PriceUpdate(filename, flushinterval):

	"""
	input: filename of the json containing the items to be scraped
	flushinterval in seconds, flushes ram every interval
	e.g. ayye = PriceUpdate('nonmembs.json', 1800)
		autosaves the content it scrapes, stores errors in 'ayye'
	"""
	
	errors = {} #Storing failed api calls
	update = {} #New price data in RAM
	zeroes = 0	#counter: Api returned a dict with values 0
	j = 0		#counter: Api returned legit stuff 
	scrapestart = time.time() 
	
	with open(filename) as f:
		items = json.load(f)
		print('Loaded items...')
	
	try:
		while True:
			#Scrape and store in RAM untill full RAM/time limit
			while (psutil.virtual_memory().available > 1000000
				   and time.time()-scrapestart < flushinterval):

				for item in items:
					try:
						r = requests.get('https://api.rsbuddy.com/grandExchange?a=guidePrice&i=%s' % item)
						data = r.json()
					except Exception as error:
						errors[str(int(time.time()))] = str(error)
						continue
					
					#Some requests return this 0 bullshit
					#Probably due to the item not being traded for a while
					if (data != {"overall":0,"buying":0,"buyingQuantity":0
								,"selling":0,"sellingQuantity":0} and
							isinstance(data, dict)):

						data['name'] = items[item]['name']
						data['timestamp'] = time.time()

						if item in update:			  
							update[item].append(data)
						else:
							update[item] = []
							update[item].append(data)

						j += 1

					else:
						zeroes += 1

			#Write to disk upon full RAM/time limit

			else:
				for key in update:
					file_exists = os.path.isfile('%s.csv' % key)
					with open ('%s.csv' % key, 'a') as f:
						w = csv.writer(f)
						w.writerow(update[key])

				a = psutil.virtual_memory().available
				del update
				gc.collect()
				b = psutil.virtual_memory().available
				print (time.strftime('%Y/%m/%d %H:%M:%S'))
				print ('|Flushed', a-b, 'bytes,', b, 'bytes available')
				print ('|Finished run in', round(time.time() - scrapestart), 'seconds.')
				print ('|Fails:', len(errors), 'Successes:', j, 'Empties:', zeroes)

				zeroes = 0
				j = 0
				errors = {}
				update = {}
				scrapestart = time.time()

	except KeyboardInterrupt:
		with open('errors.json', 'w') as f:
			json.dump(errors, f)