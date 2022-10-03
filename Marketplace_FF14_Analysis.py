
import pip._vendor.requests #Faire des requetes HTTP
worlds = [39,71,80,83,85,97,400,401,33,36,42,56,66,67,402,403] #Les mondes de Chaos jusqu'à 401 compris, puis Light.
itemmarketable = pip._vendor.requests.get("https://universalis.app/api/v2/marketable")


for item in itemmarketable: #Pour chaque item markettable
	for world in worlds:#On va dans chaque monde

	history = pip._vendor.requests.get("https://universalis.app/api/v2/history/" +  + "2")
	print(history.json())