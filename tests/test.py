import requests
import xml.etree.ElementTree as ET
import pdb

r = requests.get('https://www.ebi.ac.uk/ena/browser/api/xml/ERR4968409')

print(r.content)

xmlDict = {}
root = ET.fromstring(r.content)
for child in root.iter('*'):
    print(child.tag)
for sitemap in root:
    children = sitemap.getchildren()
    xmlDict[children[0].text] = children[1].text
pdb.set_trace()
print (xmlDict)
