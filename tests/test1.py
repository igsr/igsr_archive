import requests
import xmltodict

r = requests.get('https://www.ebi.ac.uk/ena/browser/api/xml/ERR4968409')

my_dict = xmltodict.parse(r.content)

for k, v in my_dict.items():
    for k1, v1 in my_dict[k].items():
        for k2, v2 in my_dict[k][k1].items():
            print(f"Key:{k2} Value:{v2}")