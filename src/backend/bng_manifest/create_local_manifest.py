'''
Code from https://destinydevs.github.io/BungieNetPlatform/docs/Manifest
'''

# All of these imports used, if the code is broken down into several sections like it is on the wiki,
# might not make sense to include all of them at the beginning, but will save time for new devs

import requests, zipfile, os, json, sqlite3

PATH = "/Users/ruts/Projects/RedKnightM/d2_manifest/"

def create_manifest():
    manifest_url = 'http://www.bungie.net/Platform/Destiny2/Manifest/'

    #get the manifest location from the json
    r = requests.get(manifest_url, headers={'X-API-KEY': "6250b4fbc6044931b45897c8109d692e"})
    manifest = r.json()
    mani_url = 'http://www.bungie.net' + manifest['Response']['mobileWorldContentPaths']['en']

    #Download the file, write it to 'MANZIP'
    r = requests.get(mani_url)
    with open(f"{PATH}MANZIP", "wb") as zip:
        zip.write(r.content)
    print("Download Complete!")

    #Extract the file contents, and rename the extracted file
    # to 'Manifest.content'
    with zipfile.ZipFile(f"{PATH}MANZIP") as zip:
        name = zip.namelist()
        zip.extractall()
    os.rename(name[0], f'{PATH}Manifest.content')
    print('Unzipped!')

def build_dict(hash_dict):
    #connect to the manifest
    con = sqlite3.connect(f'{PATH}manifest.content')
    print('Connected')
    #create a cursor object
    cur = con.cursor()

    all_data = {}
    #for every table name in the dictionary
    for table_name in hash_dict.keys():
        #get a list of all the jsons from the table
        cur.execute('SELECT json from '+table_name)
        print('Generating '+table_name+' dictionary....')

        #this returns a list of tuples: the first item in each tuple is our json
        items = cur.fetchall()

        #create a list of jsons
        item_jsons = [json.loads(item[0]) for item in items]

        #create a dictionary with the hashes as keys
        #and the jsons as values
        item_dict = {}
        hash = hash_dict[table_name]
        for item in item_jsons:
            item_dict[item[hash]] = item

        #add that dictionary to our all_data using the name of the table
        #as a key.
        all_data[table_name] = item_dict

    print('Dictionary Generated!')
    return all_data

