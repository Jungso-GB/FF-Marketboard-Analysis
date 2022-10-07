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
from datetime import datetime, timedelta

#Import for Proxies Cycle; 
#pip3 install lxml
from lxml.html import fromstring
from itertools import cycle
import traceback


#Avoir une liste de proxy pour éviter le Ban IP (et pouvoir changer proxy/ip pour scrap + vite; dû limite 8r/IP)
def get_proxies():
	urlProxies = 'https://free-proxy-list.net/'
	response = pip._vendor.requests.get(urlProxies)
	parser = fromstring(response.text)
	proxies = set()
	for i in parser.xpath('//tbody/tr')[:10]:
		if i.xpath('.//td[7][contains(text(),"yes")]'):
		#Grabbing IP and corresponding PORT
			proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
	proxies.add(proxy)
	return proxies

proxies = get_proxies()
print(proxies)

#COUNTER
start = time.time()

# JSON Item ID with name on different languages, par TeamCraft
itemsID = pip._vendor.requests.get("https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/master/apps/client/src/assets/data/items.json", verify=True).json()

# WORLDS
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

universalisAPI = "https://universalis.app/api/v2/"
itemMarketable = pip._vendor.requests.get(universalisAPI + "marketable").json()

# INPUT VARIABLES
usWorldID = 97 #(Ragnarok)
coefMargin = 2.3 #(Coeff de marge souhaité)
minimumSellPrice = 6000
dayDelta = 1
language = "fr"

# PROCESSUS
#Retirer notre monde, des mondes à analyser
#worldsList.pop(usWorld)

#Conversion du usWorldID en usWorldName
usWorldName = ""
for worldID, worldName in worldsList.items():
	if worldID == str(usWorldID):
		usWorldName = str(worldName)
		break

#Si le dossier 'items' existe pas, on le créer. Puis on va dedans.
filepathItems = './items/'
if os.path.exists(filepathItems) == False:
	os.makedirs(filepathItems, mode = 511, exist_ok= False)
else:
	shutil.rmtree(filepathItems)
	os.makedirs(filepathItems, mode = 511, exist_ok= False)

os.chdir(filepathItems)

print("Objets interressants:")
for item in itemMarketable: #Pour chaque item markettable
	#(TESTING) Juste pour analyser le début des items marketable
	#if item > 1700:
		#break

	#Je crée le dictionnaire qui va stocker tous les prix de l'item
	pricePerWorld = {}
	priceGoalSuccess = {}

	#Je récupère l'historique d'achat de l'item dans notre monde 
	serverItemData = pip._vendor.requests.get(universalisAPI + str(usWorldID) + "/" + str(item)).json()
	
	#Je prends le timestamp de la dernière vente, dans notre monde
	try:
		lastSell = serverItemData['recentHistory'][0]["timestamp"]
	except IndexError:
		lastSell = 'null' #Si l'article na jamais été vendu
		continue #Passe à l'item suivant
	
	#print(datetime.fromtimestamp(lastSell)) -> Derniere vente
	#Si lastSell (converti à partir du timestamp) est plus vieux que maintenant - le delta en heure renseigné
	if datetime.fromtimestamp(lastSell) < (datetime.now() - timedelta(days=dayDelta)):
		#Décalage temps + de X jours
		continue #Item suivant

	#Conversion du timestamp
	lastSell = datetime.fromtimestamp(lastSell) #FORMAT 2022-10-05 05:25:18
	
	#Je récupère le prix du serveur souhaité
	try:
		goalPrice = serverItemData['recentHistory'][0]["pricePerUnit"] / coefMargin #Je détermine mon prix objectif
	except IndexError: #Si l'item n'a jamais eu de prix défini
		goalPrice = 'null'
		continue #On passe à l'item suivant
	if goalPrice * coefMargin <= minimumSellPrice: #Si le prix de vente n'est pas au minimum celui souhaité
		continue #On passe à l'item suivant


	#Donc si l'article a déjà été vendu, dans un délai de - de X jours,- et que le prix est Okay ALORS

	#Je prends le nom de l'item, et le stocke dans l'itemID.json
	itemName = itemsID[str(item)][language]
	#itemName = itemName.encode(encoding='UTF-8',errors='strict')
	priceGoalSuccess["Name"] = itemName

	#Je stocke le prix de notre monde au tout début de l'itemID.json
	priceGoalSuccess[usWorldName] = round(goalPrice * coefMargin)

	#On va dans chaque monde
	for worldID, worldName in worldsList.items():
		tempItemData = pip._vendor.requests.get(universalisAPI + str(worldID) + "/" + str(item)).json() #Je récupère l'historique d'achat de l'item dans le monde
		try:
			price = tempItemData['listings'][0]["pricePerUnit"] #Prix de la dernière vente,
		except IndexError: #Si y'a jamais eu de vente, et donc le prix de la dernière vente n'existe pas.
			price = 'null'
			continue

		#Je la stocke dans un dictionnaire, où chaque prix de chaque monde sera indiqué.
		pricePerWorld[worldName] = price

 #Pour chaque serveur, et donc chaque prix
	print("Vérification de valeur sur les mondes..")
	for world, price in pricePerWorld.items():
		if (price <= goalPrice): #Si on a bien le coeff de marg
			#Stocker dans un JSON
			priceGoalSuccess[world] = price
			
#Je crée le fichier itemID.json où je stocke les prix interressants avec leur mondes
	with open(str(item) +'.json', 'a', encoding='UTF-8') as file:
		file.write(json.dumps(priceGoalSuccess, indent=4, ensure_ascii=False))

#Après que chaque item est été regardé 
 #End of the script
end = time.time()
print("Durée du scan: " + str(round(end - start)) + "s")