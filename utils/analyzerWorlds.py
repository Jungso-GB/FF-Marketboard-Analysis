import requests

#Go in each world
def analyzer(worldsToAnalyze, pricePerWorld, item, itemName, universalisAPI):
    for worldID, worldName in worldsToAnalyze.items():
        #proxy = next(proxy_pool) #Prendre un nouveau proxy à chaque test, pour augmenter la rapidité
        tempItemData = []

        #Have data item in the world
        #Here there is a lot of requests, we need to optimize it
        try:
            tempItemData = requests.get(universalisAPI + str(worldID) + "/" + str(item)).json()#proxies={"http": proxy, "https": proxy}
        
        #Manage all exceptions
        except requests.exceptions.Timeout:
            print("Timeout - itemID:" + itemName + " World: " + worldName)
            continue
        except requests.exceptions.TooManyRedirects:
            print("TooManyRedirects - itemID:" + itemName + " World: " + worldName)
            continue
        except requests.exceptions.RequestException as e:
            print("RequestException ERROR - itemID:" + itemName + " World: " + worldName)
            continue
        try:
            price = tempItemData['listings'][0]["pricePerUnit"] #Price of last sell in the world
        except IndexError: #If object has never been sold
            price = 'null'
            continue

        #Price in dictionnary, where all prices of all worlds will be save
        pricePerWorld[worldName] = price