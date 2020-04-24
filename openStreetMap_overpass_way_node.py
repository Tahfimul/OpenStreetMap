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

currQueryRelRef = 0

locationName = ""

def setLocationName(data):
    global locationName
    if 'alt_name' in data['elements'][0]['tags'].keys():
        locationName = data['elements'][0]['tags']['alt_name']
    else:
        locationName = data['elements'][0]['tags']['name']
    modifyLocation()

def processRelationMembers(data):
    global relations, relationsRetrieveCount, res, batch, queryCount
    dict = {}

    setLocationName(data)

    if not currQueryRelRef in existingLocationRefs:
        WaysToQuery = []
        for member in data['elements'][0]['members']:
            if 'way' in member['type']:
                WaysToQuery.append(member['ref'])

            if 'relation' in member['type']:
                relations.append(member['ref'])
        ways = queryWays(WaysToQuery)
        subDict = {'refId':currQueryRelRef, 'ways':ways}
        dict[locationName] = subDict
        output = open('/home/kptp/Documents/Coding/Reach4Help/Datasets/OSM/testCoordinates.json',"w+")
        output.write(str(dict))
        output.close()
        return
        if len(dict[locationName]) > 0:
            print(dict)
            res.append(dict)
            output = open('/home/kptp/Desktop/hellp.txt',"w+")
            output.write(str(res))
            output.close()
        print(f'Done Location: {locationName}\tQuery Count:\t{queryCount}', end="\n")
        if len(relations) > 0:
            if relationsRetrieveCount > 5:
                batch+=1
                print(batch, end="\n\n")
                relationsRetrieveCount = 0
            retrieveRelationsData()

def wayIsValid(data, ref):
    if 'tags' in data['elements'][0].keys():
        if 'admin_level' in data['elements'][0]['tags'].keys():
            if '5' in data['elements'][0]['tags']['admin_level']:
                return True
            else:
                print(f'admin_level 5 missing\t{ref}')
        else:
            print(f'no admin_level\t{ref}')
    else:
        print(f'no tags\t{ref}')

    return False

def processWayMembers(unordered_data, ref, ordered_data=0):
    # if wayIsValid(unordered_data, ref):
    nodes = []
    for node in unordered_data['elements'][0]['geometry']:
        nodes.append([float('%.6f'%node['lat']), float('%.6f'%node['lon'])])
    return nodes




def retrieveRelationsData():
    global relations, overpass_url,relationsRetrieveCount;
    relationRefId = relations.pop()
    overpass_query = stringifyQuery(relationRefId, 1)
    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    data = response.json()
    relationsRetrieveCount+=1
    processRelationMembers(data)

def calculateProgress(a, b):
    return float('%.2f'%((a/b)*100));


def queryWays(WaysToQuery):
    ways=[]
    for ref in WaysToQuery:
        overpass_query = stringifyQuery(ref, 2, False)
        response = requests.get(overpass_url,
                                    params={'data': overpass_query})
        unordered_data = response.json()

        # overpass_query = stringifyQuery(ref, 3, False)
        # response = requests.get(overpass_url,
        #                             params={'data': overpass_query})

        # ordered_data = response.json()
        way = processWayMembers(unordered_data, ref)
        if isinstance(way, list):
            print(f'ref: {ref}\tcurrQueryRelRef: {currQueryRelRef} progress:{calculateProgress(ref,WaysToQuery)}/100')
            ways.append(way)
    return ways

def initData(location, type, admin_level=0):
    global overpass_url;
    overpass_query = stringifyQuery(location, type, True,admin_level)

    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    print(response.url)
    data = response.json()
    return data

def stringifyQuery(data, type, isRel, admin_level=0):
    global queryCount, currQueryRelRef
    queryCount+=1
    res = """[out:json];"""

    if type == 0:
        res+= """(rel[name='""" + str(data) + """'][type=boundary];);out geom;"""

    if type == 1:
        if isRel:
            currQueryRelRef = data
        res+= """rel("""+str(data)+""");>;out;"""

    if type == 2:
        res+= """way("""+str(data)+""");out geom;"""

    if type == 3:
        res+= """way("""+str(data)+""");(._;>;);out body;"""
    if type == 4:
        res+= """node("""+str(data)+""");out;"""

    if type == 5:
        res+= """rel("""+str(data)+""");map_to_area;
        (
        relation
        ["boundary"="administrative"]
        ["admin_level"="""+str(admin_level)+"""]
        (area);
        >;
        );
        out; """


    return res

def modifyLocation():
    global locationName
    country = "US,"
    state = "NY,"
    subArea = locationName.upper().replace(' ','_')
    return country+state+subArea


locations = []
# with open('/home/kptp/Documents/Coding/Reach4Help/Dataset/OSM/data.json') as f:
#   locations = ast.literal_eval(f.read())
#
#   f.close()

for loc in locations:
    for name in loc.keys():
        if type(loc[name]) is dict:
            existingLocationRefs.append(loc[name]['refId'])

    res.append(loc)

# locs = [9691750, 9691916, 175905, 9691819, 9691948]
#
# for loc in locs:
#     processRelationMembers(initData(loc))
#     print("\n\n\n")
data = initData(2202162, 5, 4)

def turboSuggested(data):
    waysTotal=0
    waysCount=0
    nodes = {}
    waysList = []
    for member in data['elements']:
        if 'node' in member['type']:
            nodes[member['id']] = {'lat':float('%.6f'%member['lat']),'lng':float('%.6f'%member['lon'])}
    for member in data['elements']:
        if 'way' in member['type']:
            waysTotal+=1
    for member in data['elements']:
        if 'way' in member['type']:
            tempList = []
            for node in member['nodes']:
                if node in nodes.keys():
                   tempList.append(nodes[node])
            waysCount+=1
            waysList.append(tempList)

            print(f'{member["id"]} done | currProgress: {calculateProgress(waysCount,waysTotal)}')

    output = open('/home/kptp/Documents/Coding/Reach4Help/Datasets/OSM/testCoordinates.json',"w")
    output.write(str({'London':{'ways':waysList}}))
    output.close()

turboSuggested(data)
# processRelationMembers(data)
