# IMPORTS
import json
import time
import calendar
import sys
import pip._vendor.requests #Faire des requetes HTTP
from datetime import datetime
#COUNTER
start = time.time()

# JSON Item ID with name on different languages, par TeamCraft
itemsID = pip._vendor.requests.get("https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/master/apps/client/src/assets/data/items.json").json()
# Timestamp actuel
nowTime = datetime.now()
print(nowTime.strftime("%H:%M:%S"))
print(str(nowTime))

# WORLDS
worldsList = [39,71,80,83,85,97,400,401,33,36,42,56,66,67,402,403]
# CHAOS:
# 39: Omega
# 71: Moogle
# 80: Cerberus
# 83: Louisoix
# 85: Spriggan
# 97: Ragnarok
# 400: Sagittarius
# 401: Phantom

# LIGHT:
# 33: Twintania
# 36: Lich
# 42: Zordiak
# 56: Phoenix
# 66: Odin
# 67: Shiva
# 402: Alpha
# 403: Raiden
worldsName = ["Omega", "Moogle", "Cerberus", "Louisoix", "Spriggan", "Ragnarok", "Sagittarius", "Phantom", "Twintania", "Lich", "Zordiak", "Phoenix", "Odin", "Shiva", "Alpha", "Raiden"]

universalisAPI = "https://universalis.app/api/v2/"
itemMarketable = pip._vendor.requests.get(universalisAPI + "marketable").json()

# INPUT VARIABLES
usWorld = 97 #(Ragnarok)
coefMargin = 2 #(Coeff de marge souhaité)
minimumSellPrice = 30000

# PROCESSUS
#Retirer notre monde, des mondes à analyser
#worldsList.pop(usWorld)

print("Objets interressant:")
for item in itemMarketable: #Pour chaque item markettable
	#Je crée le dictionnaire qui va stocker tous les prix de l'item
	pricePerWorld = {}
 
	#Je récupère l'historique d'achat de l'item dans le monde 
	serverItemData = pip._vendor.requests.get(universalisAPI + str(usWorld) + "/" + str(item)).json()
	
	#Je prends le timestamp
	try:
		lastSell = serverItemData['recentHistory'][0]["timestamp"]
	except IndexError:
			lastSell = 'null' #Si l'article na jamais été vendu
			continue #Passe à l'item suivant
	
	#Conversion du timestamp
	lastSell = datetime.fromtimestamp(lastSell)
	
	#Je récupère le prix du serveur souhaité
	try:
		goalPrice = serverItemData['recentHistory'][0]["pricePerUnit"] / coefMargin #Je détermine mon prix objectif
	except IndexError: #Si l'item n'a jamais eu de prix défini
		goalPrice = 'null'
		continue #On passe à l'item suivant
	if goalPrice * coefMargin <= minimumSellPrice: #Si le prix de vente n'est pas au minimum celui souhaité
		continue #On passe à l'item suivant

	#On va dans chaque monde
	for world in worldsList:
		tempItemData = pip._vendor.requests.get(universalisAPI + str(world) + "/" + str(item)).json() #Je récupère l'historique d'achat de l'item dans le monde
		try:
			price = tempItemData['recentHistory'][0]["pricePerUnit"] #Prix de la dernière vente
		except IndexError: #Si y'a jamais eu de vente, et donc le prix de la dernière vente n'existe pas.
			price = 'null'
			continue

		#Je la stocke dans un dictionnaire, où chaque prix de chaque monde sera indiqué.
		pricePerWorld[world] = price

	print (pricePerWorld)
 #Pour chaque serveur, et donc chaque prix
	print("Vérification de valeur sur les mondes..")
	for world, price in pricePerWorld.items():
		if (price <= goalPrice): #Si on a bien le coeff de marg
			print(str(item))
			itemName = itemsID[str(item)]["fr"]
			print("Item: " + str(itemName) + " Valeur: " + str(price) + "g Monde: " + str(world) + " Valeur dans notre monde:" + str(goalPrice * coefMargin))

	#history = pip._vendor.requests.get("https://universalis.app/api/v2/history/" +  + "2")
	#print(history.json())
 
 #End of the script
end = time.time()
print(end - start)