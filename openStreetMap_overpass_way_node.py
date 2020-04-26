import requests
import json
import time
import ast

FILE_DEST = ""

overpass_url = "http://overpass-api.de/api/interpreter"

#Query options constants
#Refer to Overpass Turbo for Experimenting with Query types
REL_WITH_NAME_FOR_BOUNDARY = 0
REL_WITH_ID_FOR_WAYS_NODES = 1
WAYS_WITH_IDS_FOR_WAYS_WITH_NODES = 2
WAYS_WITH_IDS_FOR_WAYS_WITH_NODEIDS_AWAY = 3
WAY_WITH_ID_FOR_WAY_WITH_NODES = 4
WAY_WITH_ID_FOR_WAY_WITH_NODEIDS_AWAY = 5
NODE_WITH_ID_FOR_LAT_LNG = 6
REL_WITH_ID_AND_ADMIN_LEVEL = 7

res = []

existingLocationNames = []
existingLocationRefs = []


relations = []
relationsRetrieveCount = 0
batch = 0
queryCount = 0

currQueryRelName = ""
currQueryRelRef = 0

country=""
state=""
locationName = ""

def setLocationName(type, data=None, name=""):
    global locationName
    if type == REL_WITH_NAME_FOR_BOUNDARY:
        if 'alt_name' in data['elements'][0]['tags'].keys():
            locationName = data['elements'][0]['tags']['alt_name']
        else:
            locationName = data['elements'][0]['tags']['name']
    if type == REL_WITH_ID_AND_ADMIN_LEVEL:
        print(data.keys())
        for element in data['elements']:
            if 'relation' in element['type']:
                if 'alt_name' in element['tags'].keys():
                    locationName = element['tags']['alt_name']
                else:
                    locationName = element['tags']['name']

    if type == REL_WITH_ID_FOR_WAYS_NODES:
        locationName = name

    locationName = modifyLocation()

def processMembers(data, type, admin_level=0):
    if type == REL_WITH_NAME_FOR_BOUNDARY or type==REL_WITH_ID_FOR_WAYS_NODES or type==REL_WITH_ID_AND_ADMIN_LEVEL:
        if type == REL_WITH_ID_AND_ADMIN_LEVEL or type == REL_WITH_NAME_FOR_BOUNDARY:
            setLocationName(type, data=data)
        nodes = processNodes(data, type)
        processWays(data, type, nodes)
        if type==REL_WITH_ID_AND_ADMIN_LEVEL:
            processRelations(data, type,admin_level)
        else:
            processRelations(data, type)

    if type == WAY_WITH_ID_FOR_WAY_WITH_NODES or type == WAY_WITH_ID_FOR_WAY_WITH_NODEIDS_AWAY:
        nodes = processNodes(data)
        processWays(data, type, nodes)


def processRelations(data, type, admin_level=0):
    global relations, res, batch
    dict = {}
    if type == REL_WITH_NAME_FOR_BOUNDARY:
        for member in data["elements"][0]["members"]:
            if 'relation' in member['type']:
                relations.append({'type':type, 'ref':member['ref'], 'admin_level':0})
    if type == REL_WITH_ID_FOR_WAYS_NODES or type == REL_WITH_ID_AND_ADMIN_LEVEL:
        for member in data["elements"]:
            if 'relation' in member['type']:
                if type == REL_WITH_ID_AND_ADMIN_LEVEL:
                    relations.append({'type':type, 'ref':member['id'], 'admin_level':admin_level})
                else:
                    relations.append({'type':type, 'ref':member['ref'], 'admin_level':0})


    if len(relations) > 0 and batch < 20:
        for relationsRetrieveCount in range(0, len(relations)):
            if (relationsRetrieveCount%5)==0 :
                batch+=1
                print(batch, end="\n\n")
                time.sleep(120)
            relation = relations.pop(relationsRetrieveCount)
            members = None

            if relation['type'] == REL_WITH_ID_AND_ADMIN_LEVEL:
                members = query(relation['type'], id=relation['ref'], admin_level=relation['admin_level'])

            else:
                members = query(relation['type'], id=relation['ref'])

            processMembers(members, relation['type'])


# def wayIsValid(data, ref):
#     if 'tags' in data['elements'][0].keys():
#         if 'admin_level' in data['elements'][0]['tags'].keys():
#             if '5' in data['elements'][0]['tags']['admin_level']:
#                 return True
#             else:
#                 print(f'admin_level 5 missing\t{ref}')
#         else:
#             print(f'no admin_level\t{ref}')
#     else:
#         print(f'no tags\t{ref}')
#
#     return False

def processNodes(data, type):
    nodes = None
    if type == REL_WITH_NAME_FOR_BOUNDARY:
        nodes = []
        for member in data["elements"][0]["members"]:
            tempNodes = []
            if 'way' in member['type']:
                for node in member['geometry']:
                    tempNodes.append([node['lat'], node['lon']])
            nodes.append(tempNodes)

    if type == REL_WITH_ID_FOR_WAYS_NODES or type == REL_WITH_ID_AND_ADMIN_LEVEL:
        nodes={}
        for member in data["elements"]:
            if 'node' in member['type']:
                nodes[member['id']] = [member['lat'], member['lon']]

    return nodes

def processWays(data, type,nodes):
    global locationName, queryCount
    wayMembers = []

    if type == REL_WITH_NAME_FOR_BOUNDARY:
        wayIndex = 0
        for member in data["elements"][0]["members"]:
            if 'way' in member['type']:
                wayMembers.append(nodes[wayIndex])
                wayIndex+=1
    if type == REL_WITH_ID_FOR_WAYS_NODES or type == REL_WITH_ID_AND_ADMIN_LEVEL:

        for member in data["elements"]:
            if 'way' in member['type']:
                nodeList = []
                for node in member['nodes']:
                    if node in nodes.keys():
                       nodeList.append(nodes[node])
                wayMembers.append(nodeList)
    print(f'Done Location: {locationName}\tQuery Count:\t{queryCount}', end="\n")

    writeToFile(wayMembers)

def writeToFile(wayMembers):
    global res, currQueryRelRef
    subDict = {'refId':currQueryRelRef, 'ways':wayMembers}
    dict = {locationName:subDict}
    res.append(dict)

    for r in res:
        print(r,end="\n\n\n\n\n")
    # output = open(FILE_DEST,"w+")
    # output.write(str(res))
    # output.close()

def calculateProgress(a, b):
    return float('%.2f'%((a/b)*100));

def query(type, id=0, locationName=0, admin_level=0, WaysToQuery=0):

    if type == REL_WITH_NAME_FOR_BOUNDARY:
        if not currQueryRelName in existingLocationNames:
            return queryRelation(type, location=locationName)
    if type == REL_WITH_ID_FOR_WAYS_NODES:
        if not currQueryRelRef in existingLocationRefs:
            return queryRelation(type, id=id)
    if type == WAYS_WITH_IDS_FOR_WAYS_WITH_NODES or type == WAYS_WITH_IDS_FOR_WAYS_WITH_NODEIDS_AWAY:
        ways=[]
        for wayId in WaysToQuery:
            ways.append(queryWay(type,id=id))
        return ways
    if type == WAY_WITH_ID_FOR_WAY_WITH_NODES or type == WAY_WITH_ID_FOR_WAY_WITH_NODEIDS_AWAY:
        return queryWay(type,id=id)
    if type == NODE_WITH_ID_FOR_LAT_LNG:
        return queryNode(type,id=id)
    if type == REL_WITH_ID_AND_ADMIN_LEVEL:
        return queryRelation(type,id=id,admin_level=admin_level)

def queryRelation(type, id=0, location=0, admin_level=0):
    global overpass_url;

    overpass_query = ""

    if type == REL_WITH_NAME_FOR_BOUNDARY:
        currQueryRelName = location
        existingLocationNames.append(currQueryRelName)
        overpass_query = stringifyQuery(type, locationName=location)
    if type == REL_WITH_ID_FOR_WAYS_NODES:
        currQueryRelRef = id
        existingLocationRefs.append(currQueryRelRef)
        overpass_query = stringifyQuery(type,id=id)
    if type == REL_WITH_ID_AND_ADMIN_LEVEL:
        currQueryRelRef = id
        existingLocationRefs.append(currQueryRelRef)
        overpass_query = stringifyQuery(type,id=id,admin_level=admin_level)

    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    relation = response.json()
    return relation


def queryWay(type, id):
    global overpass_url;

    overpass_query = stringifyQuery(type,id)
    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    way = response.json()
    return way

def queryNode(type, id):
    global overpass_url;

    overpass_query = stringifyQuery(type,id)
    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    node = response.json()
    return node


def stringifyQuery(type, id=0, locationName=0, admin_level=0):

    global queryCount, currQueryRelRef
    queryCount+=1
    res = """[out:json];"""

    if type == REL_WITH_NAME_FOR_BOUNDARY:
        #Not useful when querying a specific region's border
        #Ex. name = "New York" will query data for New York State as well as New York County
        res+= """(rel[name='""" + str(locationName) + """'][type=boundary];);out geom;"""

    if type == REL_WITH_ID_FOR_WAYS_NODES:
        #Returns: [Node: id, lat, lon], Ways[Way ID : [Node id]]
        res+= """rel("""+str(id)+""");>;out;"""

    if type == WAY_WITH_ID_FOR_WAY_WITH_NODES:
        #Returns: Way w/ ID : [Node: id, lat, lon]
        res+= """way("""+str(id)+""");out geom;"""

    if type == WAY_WITH_ID_FOR_WAY_WITH_NODEIDS_AWAY:
        #Returns: [Node: id, lat, lon], Ways[Way ID : [Node id]]
        res+= """way("""+str(id)+""");(._;>;);out;"""

    if type == NODE_WITH_ID_FOR_LAT_LNG:
        #Returns: Node: id, lat, lon
        res+= """node("""+str(id)+""");out;"""

    if type == REL_WITH_ID_AND_ADMIN_LEVEL:
        #Returns all boundaries for given Relation Id with and given admin_level
        #Follows similar structure to type REL_WITH_ID_FOR_WAYS_NODES
        #Very expensive in terms of data size returned
        res+= """rel("""+str(id)+""");map_to_area;
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
    global country, state, locationName
    country = country.upper().replace(' ','_')+","
    state = state..upper().replace(' ','_')+","
    subArea = locationName.upper().replace(' ','_')

    if len(state) == 1:
       return country+subArea

    return country+state+subArea

def readFromFile():
    global existingLocationRefs, existingLocationNames, res
    locations = []
    with open(FILE_DEST) as f:
      locations = ast.literal_eval(f.read())
      f.close()

    for loc in locations:
        for name in loc.keys():
            if type(loc[name]) is dict:
                existingLocationRefs.append(loc[name]['refId'])
                existingLocationNames.append(name)

        res.append(loc)

# locs = [9691750, 9691916, 175905, 9691819, 9691948]
#
# for loc in locs:
#     processRelationMembers(queryRelation(loc))
#     print("\n\n\n")

def printInstructions():
    global FILE_DEST, country, state
    FILE_DEST = input("Enter file distination ")
    TYPE = int(input("Enter query type "))
    ID = int(input("Enter relation id "))
    NAME = input("Enter location name ")
    ADMIN_LEVEL = int(input("Enter admin_level "))
    country = input("Enter country name: ")
    state = input("Enter state name: ")
    readFromFile()

    if TYPE == REL_WITH_ID_FOR_WAYS_NODES:
        setLocationName(TYPE, name=NAME)
    data = query(TYPE, id=ID, locationName=NAME, admin_level=ADMIN_LEVEL)
    processMembers(data, TYPE)

printInstructions()


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

    output = open(FILE_DEST,"w")
    output.write(str({'London':{'ways':waysList}}))
    output.close()

# turboSuggested(data)
# processRelationMembers(data)
