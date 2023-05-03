import requests
from lxml.html import fromstring

#Get proxy list to speed up the scan. (8 requests simulatenous / IP)
def get_proxies():
	urlProxies = 'https://free-proxy-list.net/'
	response = requests.get(urlProxies)
	parser = fromstring(response.text) #Script HTML de la page complet
	proxies = set()
	for i in parser.xpath('//tbody/tr')[:20]:
		if i.xpath('.//td[7][contains(text(),"yes")]'): #If HTTPS is "yes"
		#Grabbing IP and corresponding PORT
			proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
			proxies.add(proxy)
	return proxies