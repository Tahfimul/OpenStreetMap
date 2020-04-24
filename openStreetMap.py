import requests
import json
import time
import ast
overpass_url = "http://overpass-api.de/api/interpreter"

res = []

existingLocationRefs = []

relations = []
relationsRetrieveCount = 0
batch = 0
queryCount = 0

currQueryRefVal = 0

def processMembers(data):
    global relations, relationsRetrieveCount, res, batch, queryCount
    dict = {}

    location = ""
    if 'alt_name' in data['elements'][0]['tags'].keys():
        location = data['elements'][0]['tags']['alt_name']
    else:
        location = data['elements'][0]['tags']['name']
    location = modifyLocation(location)
    if not currQueryRefVal in existingLocationRefs:
        waysList = []
        for member in data['elements'][0]['members']:
            if 'way' in member['type']:
                nodes = []
                for coordinate in member['geometry']:
                    nodes.append([coordinate['lat'], coordinate['lon']])
                waysList.append(nodes)
            if 'relation' in member['type']:
                relations.append(member['ref'])
        subDict = {'refId':currQueryRefVal, 'ways':waysList}
        dict[location] = subDict
        if len(dict[location]) > 0:
            print(dict)
            res.append(dict)
            output = open('/home/kptp/Desktop/hellp.txt',"w+")
            output.write(str(res))
            output.close()
        print(f'Done Location: {location}\tQuery Count:\t{queryCount}', end="\n")
        if len(relations) > 0:
            if relationsRetrieveCount > 5:
                batch+=1
                print(batch, end="\n\n")
                relationsRetrieveCount = 0
            retrieveRelationsData()


def retrieveRelationsData():
    global relations, overpass_url,relationsRetrieveCount;
    relationRefId = relations.pop()
    overpass_query = stringifyQuery(relationRefId, 1)
    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    data = response.json()
    relationsRetrieveCount+=1
    processMembers(data)


def initData(location):
    global overpass_url;
    overpass_query = stringifyQuery(location, 1)

    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    data = response.json()
    return data

def stringifyQuery(data, type):
    global queryCount, currQueryRefVal
    queryCount+=1
    res = """[out:json];"""

    if type == 0:
        res+= """(rel[name='""" + data + """'][type=boundary];);out geom;"""

    else:
        currQueryRefVal = data
        res+= """rel("""+str(data)+""");out geom;"""

    return res

def modifyLocation(location):
    country = "US,"
    state = "NY,"
    subArea = location.upper().replace(' ','_')
    return country+state+subArea


locations = []
with open('/home/kptp/Documents/Coding/Reach4Help/Dataset/OSM/data.json') as f:
  locations = ast.literal_eval(f.read())

  f.close()

for loc in locations:
    for name in loc.keys():
        if type(loc[name]) is dict:
            existingLocationRefs.append(loc[name]['refId'])

    res.append(loc)

# locs = [9691750, 9691916, 175905, 9691819, 9691948]
#
# for loc in locs:
#     processMembers(initData(loc))
#     print("\n\n\n")

processMembers(initData(2202162))
