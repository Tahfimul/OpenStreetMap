import requests
import ast
from bs4 import BeautifulSoup

url = 'http://polygons.openstreetmap.fr/'


def processQuery(nodes):
    shortenedData = []
    for line in nodes.iter_lines():
        if '.' in line.decode():
            shortenedData.append(line[1:].decode().replace('\t', ',').split(','))


    i = 0

    for coordinate in shortenedData:

        dict = {'lat':float('%.6f'%float(coordinate[1])), 'lng':float('%.6f'%float(coordinate[0]))}
        shortenedData[i] = dict
        print(shortenedData[i])
        i+=1

    output = open('/home/kptp/Documents/Coding/Reach4Help/Datasets/OSM/testCoordinates.json',"w+")
    output.write(str({'London':{'ways':shortenedData}}))
    output.close()

def getShortestURL(id):
    global url

    tempURL=url+"?id="+str(id)
    r = requests.get(tempURL, stream=True)
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table')
    trs = table.findChildren("tr" , recursive=False)

    lowestNodeCount = 0
    lowestNodeCountURL = ""
    i=0
    for tr in trs:
        tds = tr.findChildren("td" , recursive=False)
        if len(tds)>0:
            nodeCount = int(str(tds[2]).replace('<td>','').replace('</td>',''))
            if lowestNodeCount == 0:
                lowestNodeCount = nodeCount
                a = tds[6].find_all("a" , recursive=False)
                lowestNodeCountURL = a[0].attrs['href']

            elif nodeCount<lowestNodeCount:
                lowestNodeCount = nodeCount
                a = tds[6].find_all("a" , recursive=False)
                lowestNodeCountURL = a[0].attrs['href']
    lowestNodeCountURL = url+lowestNodeCountURL
    return lowestNodeCountURL

def queryNodes(url):
    r = requests.get(url, stream=True)
    return r

processQuery(queryNodes(getShortestURL(62428)))
