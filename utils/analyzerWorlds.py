import requests
import asyncio #Simulateous requests
import aiohttp

#Do each request
async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()
    
#Function to make asynchronous multi-requests
async def fetch_all(session, urls):
    results = await asyncio.gather(*[fetch(session, url) for url in urls])
    return results


#To get data of worlds
async def analyze_world(session, worldID, item, universalisAPI):
    url = f"{universalisAPI}{worldID}/{item}"
    result = await fetch(session, url)
    try:
        price = result['listings'][0]["pricePerUnit"]
    except IndexError:
        price = 'null'
    except requests.exceptions.Timeout:
      print("Timeout - itemID:" + item + " WorldID: " + worldID)
    except requests.exceptions.TooManyRedirects:
        print("TooManyRedirects - itemID:" + item + " WorldID: " + worldID)
    except requests.exceptions.RequestException as e:
        print("RequestException ERROR - itemID:" + item + " WorldID: " + worldID)
    return price

#Go in each world
async def analyzer(worldsToAnalyze, item, universalisAPI):
    
    #Define all URL to requests
    urls = [f"{universalisAPI}{worldID}/{item}" for worldID in worldsToAnalyze.keys()]
    
    async with aiohttp.ClientSession() as session: 
        # Send requests asynchronous
        responses = await fetch_all(session, urls)
        # Manage responses
        pricePerWorld = {}
        for i in range(len(worldsToAnalyze)):
            worldName = list(worldsToAnalyze.values())[i]
            try:
                price = responses[i]['listings'][0]["pricePerUnit"]
            except IndexError:
                price = 'null' or '0' or ''
                continue #Next world
            pricePerWorld[worldName] = price
        return pricePerWorld
    
    #OLD SYSTEM / REQUESTS NON-ASYNCHRONOUS
    
 #   for worldID, worldName in worldsToAnalyze.items():
        #proxy = next(proxy_pool) #Prendre un nouveau proxy à chaque test, pour augmenter la rapidité
  #      tempItemData = []

        #Have data item in the world
        #Here there is a lot of requests, we need to optimize it
   #     try:
    #        tempItemData = requests.get(universalisAPI + str(worldID) + "/" + str(item)).json()#proxies={"http": proxy, "https": proxy}
        
        #Manage all exceptions
     #   except requests.exceptions.Timeout:
      #      print("Timeout - itemID:" + itemName + " World: " + worldName)
       #     continue
        #except requests.exceptions.TooManyRedirects:
         #   print("TooManyRedirects - itemID:" + itemName + " World: " + worldName)
          #  continue
        #except requests.exceptions.RequestException as e:
         #   print("RequestException ERROR - itemID:" + itemName + " World: " + worldName)
          #  continue
        #try:
         #   price = tempItemData['listings'][0]["pricePerUnit"] #Price of last sell in the world
        #except IndexError: #If object has never been sold
         #   price = 'null'
         #   continue

        #Price in dictionnary, where all prices of all worlds will be save
        #pricePerWorld[worldName] = price