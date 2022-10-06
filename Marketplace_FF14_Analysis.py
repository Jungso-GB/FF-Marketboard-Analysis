# IMPORTS
import json
import time
import calendar
import os
import shutil
import sys
import pip._vendor.requests #Faire des requetes HTTP
from datetime import datetime, timedelta
#COUNTER
start = time.time()

# JSON Item ID with name on different languages, par TeamCraft
itemsID = pip._vendor.requests.get("https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/master/apps/client/src/assets/data/items.json", verify=True).json()

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
coefMargin = 1.4 #(Coeff de marge souhaité)
minimumSellPrice = 30000
dayDelta = 3

# PROCESSUS
#Retirer notre monde, des mondes à analyser
#worldsList.pop(usWorld)


#Si le dossier 'items' existe pas, on le créer. Puis on va dedans.
filepath = './items/'
if os.path.exists(filepath) == False:
	os.makedirs(filepath, mode = 511, exist_ok= False)
else:
	shutil.rmtree(filepath)
	os.makedirs(filepath, mode = 511, exist_ok= False)

os.chdir(filepath)

print("Objets interressants:")
for item in itemMarketable: #Pour chaque item markettable
	#Je crée le dictionnaire qui va stocker tous les prix de l'item
	pricePerWorld = {}
	priceGoalSuccess = {}

	#Je récupère l'historique d'achat de l'item dans le monde 
	serverItemData = pip._vendor.requests.get(universalisAPI + str(usWorld) + "/" + str(item)).json()
	
	#Je prends le timestamp de la dernière vente
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
	itemName = itemsID[str(item)]["fr"]
	priceGoalSuccess["Name"] = itemName

	#Je stocke le prix de notre monde au tout début de l'itemID.json
	priceGoalSuccess[usWorld] = goalPrice * coefMargin 

	#On va dans chaque monde
	for world in worldsList:
		tempItemData = pip._vendor.requests.get(universalisAPI + str(world) + "/" + str(item)).json() #Je récupère l'historique d'achat de l'item dans le monde
		try:
			price = tempItemData['recentHistory'][0]["pricePerUnit"] #Prix de la dernière vente, /! IL FAUT PRENDRE LA VALEUR PLUS BASSE DU LISTING
		except IndexError: #Si y'a jamais eu de vente, et donc le prix de la dernière vente n'existe pas.
			price = 'null'
			continue

		#Je la stocke dans un dictionnaire, où chaque prix de chaque monde sera indiqué.
		pricePerWorld[world] = price

 #Pour chaque serveur, et donc chaque prix
	print("Vérification de valeur sur les mondes..")
	for world, price in pricePerWorld.items():
		if (price <= goalPrice): #Si on a bien le coeff de marg
			#Stocker dans un JSON
			priceGoalSuccess[world] = price
			
			#print("Item: " + str(itemName) + " Valeur: " + str(price) + "g Monde: " + str(world) + " Valeur dans notre monde:" + str(goalPrice * coefMargin))

#Je crée le fichier itemID.json où je stocke les prix interressants avec leur mondes
	with open(str(item) +'.json', 'a') as file:
		file.write(json.dumps(priceGoalSuccess, indent=4))

 #End of the script
end = time.time()
print(end - start)