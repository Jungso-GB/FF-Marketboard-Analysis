# IMPORTS
import importlib
import json
import time
import calendar
import os
import shutil
import csv
import sys
import pip._vendor.requests #Faire des requetes HTTP
import pandas as pd
from datetime import datetime, timedelta

#Import for Proxies Cycle; 
#pip3 install lxml
from lxml.html import fromstring #A FINIR
from itertools import cycle
import traceback

#Counter Scan Research
start = time.time()

# The modify variables
usWorldID = 97 #(Ragnarok)
coefMargin = 1.3 #(Coeff de marge souhaité)
minimumSellPrice = 6000
dayDelta = 1
language = "fr"
categoryWanted = "furniture"


#Get proxy list to speed up the scan. (8 requests simulatenous / IP)
def get_proxies():
	urlProxies = 'https://free-proxy-list.net/'
	response = pip._vendor.requests.get(urlProxies)
	parser = fromstring(response.text) #Script HTML de la page complet
	proxies = set()
	for i in parser.xpath('//tbody/tr')[:20]:
		if i.xpath('.//td[7][contains(text(),"yes")]'): #If HTTPS is "yes"
		#Grabbing IP and corresponding PORT
			proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
			proxies.add(proxy)
	return proxies

#Initialisation Proxy
proxies = get_proxies()
proxy_pool = cycle(proxies)

# JSON Item ID with name on different languages, par TeamCraft
itemsID = pip._vendor.requests.get("https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/master/apps/client/src/assets/data/items.json", verify=True).json()

# WORLDS
# EU
worldsList = {
	"39" : "Omega", # CHAOS
	"71" : "Moogle",# CHAOS
	"80" : "Cerberus",# CHAOS
	"83" : "Louisoix",# CHAOS
	"85" : "Spriggan",# CHAOS
	"97" : "Ragnarok",# CHAOS
	"400" : "Sagittarius",# CHAOS
	"401" : "Phantom",# CHAOS
	"33" : "Twintania",# LIGHT
	"36" : "Lich",# LIGHT
	"42" : "Zordiak",# LIGHT
	"56" : "Phoenix",# LIGHT
	"66" : "Odin",# LIGHT
	"67" : "Shiva",# LIGHT
	"402" : "Alpha",# LIGHT
	"403" : "Raiden",# LIGHT
}

#API
universalisAPI = "https://universalis.app/api/v2/"
allItemsMarketable = pip._vendor.requests.get(universalisAPI + "marketable").json()

#Convert usWorldID to usWorldName
usWorldName = ""
for worldID, worldName in worldsList.items():
	if worldID == str(usWorldID):
		usWorldName = str(worldName)
		break

#If the folder 'items' doesn't exist, we create it, and go in
def itemsFolderVerification():
	filepathItems = './items/'
	if os.path.exists(filepathItems) == False:
		os.makedirs(filepathItems, mode = 511, exist_ok= False)
	else:
		shutil.rmtree(filepathItems)
		os.makedirs(filepathItems, mode = 511, exist_ok= False)
	os.chdir(filepathItems)

def getServerItemData(itemToData):
	
	dataItem = []
	try:
		dataItem = pip._vendor.requests.get(universalisAPI + str(usWorldID) + "/" + str(itemToData)).json() #proxies={"http": proxy, "https": proxy}
	#Different Except possible
	except pip._vendor.requests.exceptions.Timeout:
		print("Timeout - itemID:" + str(itemToData) + " World: " + str(usWorldName))
	except pip._vendor.requests.exceptions.TooManyRedirects:
		print("TooManyRedirects - itemID:" + str(itemToData) + " World: " + str(usWorldName))
	except pip._vendor.requests.exceptions.RequestException as e:
		print("RequestException ERROR - itemID:" + str(itemToData) + " World: " + str(usWorldName))
	return dataItem


#Function To Analyze items, with WorldList
def analyzeItems(itemsToAnalyze, worldsToAnalyze):
	#For each item
	for item in itemsToAnalyze:
		#(TESTING) Juste pour analyser le début des items marketable
		if item > 3000:
			break

		#Create dictionnary to stock all prices of items
		pricePerWorld = {}
		priceGoalSuccess = {}

		#Take a new proxy for each world, to speed up the scan
		proxy = next(proxy_pool)
		#Take history of the item in each world
		serverItemData = getServerItemData(item)
		#Take last timestamp in us world
		try:
			lastSell = serverItemData['recentHistory'][0]["timestamp"]
		except IndexError:
			lastSell = 'null' #If item has never been sell
			continue #Next Item
		
		#If the item is sell before X days..
		if datetime.fromtimestamp(lastSell) < (datetime.now() - timedelta(days=dayDelta)):
			continue #Next Item

		#Convert timestamp
		lastSell = datetime.fromtimestamp(lastSell) #FORMAT 2022-10-05 05:25:18
		
		#Take price of item in world want
		try:
			goalPrice = serverItemData['recentHistory'][0]["pricePerUnit"] / coefMargin #Je détermine mon prix objectif
		except IndexError: #Si l'item n'a jamais eu de prix défini
			goalPrice = 'null'
			continue #Next Item
		if goalPrice * coefMargin <= minimumSellPrice: #Si le prix de vente n'est pas au minimum celui souhaité
			continue #Next Item

		#SO, if the item has been already sell, in a delay of - X days and that the price's verification is good, SO...

		#Take name of the item and put it in l'itemID.json
		itemName = itemsID[str(item)][language]
		priceGoalSuccess["Name"] = itemName

		#Put price of us world'item in l'itemID.json at first
		priceGoalSuccess[usWorldName] = round(goalPrice * coefMargin)

		#On va dans chaque monde
		print("Vérification dans chaque monde...")
		for worldID, worldName in worldsToAnalyze.items():
			proxy = next(proxy_pool) #Prendre un nouveau proxy à chaque test, pour augmenter la rapidité
			tempItemData = []

			#On essaye d'avoir les données entière de l'item dans le monde, via un PROXY
			try:
				tempItemData = pip._vendor.requests.get(universalisAPI + str(worldID) + "/" + str(item)).json()#proxies={"http": proxy, "https": proxy}
			#On y gère tous les Excepts générales
			except pip._vendor.requests.exceptions.Timeout:
				print("Timeout - itemID:" + itemName + " World: " + worldName)
				continue
			except pip._vendor.requests.exceptions.TooManyRedirects:
				print("TooManyRedirects - itemID:" + itemName + " World: " + worldName)
				continue
			except pip._vendor.requests.exceptions.RequestException as e:
				print("RequestException ERROR - itemID:" + itemName + " World: " + worldName)
				continue
			try:
				price = tempItemData['listings'][0]["pricePerUnit"] #Prix de la dernière vente,
			except IndexError: #Si y'a jamais eu de vente, et donc le prix de la dernière vente n'existe pas.
				price = 'null'
				continue

			#Je la stocke dans un dictionnaire, où chaque prix de chaque monde sera indiqué.
			pricePerWorld[worldName] = price

	#Once price of each world in pricePerWorld[X], we verify if we have the margin
		for world, price in pricePerWorld.items():
			if (price <= goalPrice):
				#Put in a JSON
				priceGoalSuccess[world] = price
				
	#Create the itemID.json where put the name, usWorld's price and the multiple world where the name and price associated
		with open(str(item) +'.json', 'a', encoding='UTF-8') as file:
			file.write(json.dumps(priceGoalSuccess, indent=4, ensure_ascii=False))

def getItemMarketable(category):
	itemsCategory = {}
	#Convert CSV with all item of the category in JSON
	url = 'https://github.com/xivapi/ffxiv-datamining/blob/master/csv/FurnitureCatalogItemList.csv'
	fields = ["1"]
	itemsCategory = pd.read_csv(url, header=None, names=fields, on_bad_lines='skip')

	#Compare JSON's file with allItemsMarketable and itemsCategory
	with open(itemsCategory) as csvFile:
		csvReader = csv.DictReader(csvFile)
		for rows in csvReader:
			id = rows['id']
			print(str(id))
			itemsCategory[id] = rows
			print(itemsCategory)
	#return itemMarketable

#MAIN SCRIPT
def main():
	itemsFolderVerification()
	itemsMarketableToAnalyze = getItemMarketable(categoryWanted)
	analyzeItems(itemsMarketableToAnalyze, worldsList)
main()

#Après que chaque item est été regardé 
 #End of the script
end = time.time()
print("Durée du scan: " + str(round(end - start)) + "s")