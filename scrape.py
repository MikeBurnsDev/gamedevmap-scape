import sys
from urllib.request import urlopen
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
import csv
import time
import re

def getBs(url):
	try:
		user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17'
		req = urllib.request.Request(url, None, {'User-Agent' : user_agent})
		html = urllib.request.urlopen(req)
		
		#req = urllib.request.Request(url, data, headers)
		#with urllib.request.urlopen(req) as response:
		#   html = response.read()
	except Exception as e:
		print(e)
		return None
	else:
		if html is None:
			print("URL is not found")
			return None
	
	bsObj = BeautifulSoup(html, "html.parser");
	return bsObj

table = getBs("https://www.gamedevmap.com/index.php?location=&country=United%20States&state=&city=&query=&type=Developer&start=101&count=10000").find('table', attrs={'cellpadding':'6'})

entries = []
prev = ''

for row in table.find_all('tr'):
	try:
		rowClass = row['class']
	except KeyError as e:
		pass
	else:
		if (rowClass == ['row2'] or rowClass == ['row1']) and row.a.string != prev:
			prev = row.a.string
			entries.append([row.a.string,
			row.a.get('href'),
			row.find_all('td')[2].string,
			row.find_all('td')[3].string,
			row.find_all('td')[4].string])

def writeCsv():
	with open('entries.csv', 'w', newline="\n", encoding="utf-8") as csvfile:
		writer = csv.writer(csvfile, delimiter='|', quotechar='', escapechar='\\', quoting=csv.QUOTE_NONE)
		
		rowIndex = 0
		for entry in entries:
			writer.writerow(entry)

def containsJob(bs):
	jobs = bs.find(text = re.compile('Jobs', re.IGNORECASE))
	career = bs.find(text = re.compile('Career', re.IGNORECASE))
	prog = bs.find(text = re.compile('Programmer', re.IGNORECASE))
	dev = bs.find(text = re.compile('Engineer', re.IGNORECASE))
	eng = bs.find(text = re.compile('Developer', re.IGNORECASE))
	unity = bs.find_all(text = re.compile('Unity', re.IGNORECASE))
	
	clearUnity = True
	
	for u in unity:
		unityPattern1 = re.compile("community", re.IGNORECASE)
		unityPattern2 = re.compile("opportunity", re.IGNORECASE)
		if unityPattern1.search(str(unity)) is None and unityPattern2.search(str(unity)) is None:
			clearUnity = False
			break
	
	if clearUnity:
		unity = None
	
	return [jobs is not None,career is not None,prog is not None,dev is not None,eng is not None,unity is not None]
	
	#print(str(title.string).decode('utf8'))

def appendSearchResults(useUrl=True):
	for entry in entries:
		searchString = 'https://duckduckgo.com/html/?q=careers+'
		if useUrl:
			searchString += entry[0].replace('-','+').replace(' ','+')
		else:
			searchString += entry[1]
		
		bs = getBs(searchString)
		attemps = 0
		while bs is None:
			print(searchString + " retry")
			time.sleep(2)
			bs = getBs(searchString)
			attemps += 1
			if(attemps >= 30):
				break
		
		if bs is None:
			print(searchString + " failed. continue")
			continue
		
		resultLink = bs.find('div', attrs={'class':'result results_links results_links_deep web-result '}).div.h2.a.get('href')
		
		bs = getBs(resultLink)
		if bs is None:
			print("resultLink Error on: " + resultLink)
			continue
		
		contains = containsJob(bs)
		
		for c in contains:
			entry.append(c)
		
		entry.append(resultLink)
		
		print("Searched: " + entry[0])
		
appendSearchResults()
appendSearchResults(False)
writeCsv()
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	