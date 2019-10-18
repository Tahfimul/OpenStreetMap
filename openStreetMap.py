import requests
import json
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json];
area["ISO3166-1"="DE"][admin_level=2];
(node["amenity"="biergarten"](area);
 way["amenity"="biergarten"](area);
 rel["amenity"="biergarten"](area);
);
out center;
"""
response = requests.get(overpass_url,
                        params={'data': overpass_query})
data = response.json()

f = open("locations.csv", "a")
f.write("Latitude\t\t\t\tLongitude\n")

for node in data["elements"]:
    f.write(str(node["lat"])+"\t\t\t\t"+str(node["lon"])+"\n")
    print("lat %s, lon %s", node["lat"], node["lon"])

f.close()
