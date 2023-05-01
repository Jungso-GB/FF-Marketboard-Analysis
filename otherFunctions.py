import os
import shutil
import pip
import Marketplace_FF14_Analysis as mainscript

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
		dataItem = pip._vendor.requests.get(mainscript.universalisAPI + str(mainscript.usWorldID) + "/" + str(itemToData)).json() #proxies={"http": proxy, "https": proxy}
	#Different Except possible
	except pip._vendor.requests.exceptions.Timeout:
		print("Timeout - itemID:" + str(itemToData) + " World: " + str(mainscript.usWorldName))
	except pip._vendor.requests.exceptions.TooManyRedirects:
		print("TooManyRedirects - itemID:" + str(itemToData) + " World: " + str(mainscript.usWorldName))
	except pip._vendor.requests.exceptions.RequestException as e:
		print("RequestException ERROR - itemID:" + str(itemToData) + " World: " + str(mainscript.usWorldName))
	return dataItem