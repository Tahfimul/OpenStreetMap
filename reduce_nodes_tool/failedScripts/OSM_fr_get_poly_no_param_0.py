import requests
import json
testUrl = 'https://nominatim.openstreetmap.org/reverse?format=json&osm_id=2202162&osm_type=R&polygon_geojson=.1'
testRes = requests.get(testUrl)
testData = json.loads(testRes.text)

url = 'http://polygons.openstreetmap.fr/get_geojson.py?id=2202162'
res = requests.get(url)
originalData = json.loads(res.text)

shortDataUrl = 'http://polygons.openstreetmap.fr/get_poly.py?id=2202162&params=0'
shortData  = requests.get(shortDataUrl, stream=True)

originalDataset = []

testDataset = []

# for ways in originalData['geometries'][0]['coordinates']:
#     for way in ways:
#         for node in way:
#             dict = {'lat':float('%.6f'%float(node[1])), 'lng':float('%.6f'%float(node[0]))}
#             originalDataset.append(dict)

for ways in testData['geojson']['coordinates']:
    for way in ways:
        for node in way:
            dict = {'lat':float('%.6f'%float(node[1])), 'lng':float('%.6f'%float(node[0]))}
            testDataset.append(dict)


count=0
shortenedDataset = []
for line in shortData.iter_lines():
    # if not (('3' in line.decode() or '2' in line.decode() or '1' in line.decode() or 'END' in line.decode() or 'polygon' in line.decode()) and '.' in line.decode()) :
    if '.' in line.decode():
        count+=1
        print(count)
        shortenedDataset.append(line[2:].decode().replace('\t', ',').split(','))
i = 0

print(len(originalDataset))
print(len(shortenedDataset))

# for coordinate in shortenedDataset:
#     if len(coordinate) > 1:
#         dict = {'lat':float('%.6f'%float(coordinate[1])), 'lng':float('%.6f'%float(coordinate[0]))*-1}
#         if dict in originalDataset:
#            shortenedDataset[i] = dict
#
#     i+=1



# def clean(count=0):
#     for coordinate in shortenedDataset:
#         if type(coordinate) is type(shortenedDataset):
#             shortenedDataset.remove(coordinate)
#     for coordinate in shortenedDataset:
#         if type(coordinate) is type(shortenedDataset):
#             count+=1
#             return clean(count)
#
# clean(0)
print(len(shortenedDataset))
output = open('/home/kptp/Documents/Coding/Reach4Help/Datasets/OSM/testCoordinates.json',"w+")
output.write(str(testDataset))
output.close()
