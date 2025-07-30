"""
Currently does nothing, because Luis' code was looking for a JSON file, and
the subnetworks directory has no JSON file
"""
import requests
import base64
import json
import sys

from ..misc import yamlref


def constructURL(user = "404",repo_name= "404",path_to_file= "404",url= "404"):
  url = url.replace("{user}",user)
  url = url.replace("{repo_name}",repo_name)
  url = url.replace("{path_to_file}",path_to_file)
  return url

json_url ='https://gitlab.com/resif/smm/obsinfo/-/tree/master/src/obsinfo/_examples/subnetwork_files'

#json_url = constructURL(user,repo_name,path_to_file,json_url) #forms the correct URL
def test_github():
    try:
        r = requests.get(json_url) #get data from json file located at specified URL
    except Exception as e:
        # Could not connect to the URL
        print(e)
    else:
        if r.status_code == requests.codes.ok:
            print(r.text)
            try:
                jsonResponse = r.json()  # the response is a JSON
                #the JSON is encoded in base 64, hence decode it
                content = base64.b64decode(jsonResponse['content'])
                #convert the byte stream to string
                jsonString = content.decode('utf-8')
                print(jsonString)
                finalJson = yamlref.loads(jsonString, base_uri = json_url)
            except Exception as e:
                print('Found no JSON file')
        else:
            print(f'Content not found at {json_url=}.')
            raise ValueError(f'Content not found at {json_url=}.')


#for key, value in finalJson.items():
    #print("The key and value are ({}) = ({})".format(key, value))