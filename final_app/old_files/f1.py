# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 11:53:13 2019

@author: prateek.sethi
"""

from web_scrap_class import WebsiteParser 
from application import WebsiteQA
from flask import Flask, jsonify, render_template
from flask import request
from flask_cors import CORS
from urllib.parse import urlparse
import json

app = Flask(__name__)
CORS(app,resources={r"/*": {"origins": "*"}})
path = 0

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/data" , methods = ["POST"])
def getDetails():
    
    global path
    
    #print('HELLO', request.json)
    #content = json.loads(request.data.decode("utf-8"))
    content = request.get_json()
    print(content)
    id = 0
    resp = {}
    urlName = urlparse(content["url"])
    #baseName = urlName.netloc.replace('www.', '') + ".".join(urlName.path.split(".")[0:-1])
    baseName = urlName.netloc.replace('www.', '') + urlName.path
    
    preExistingUrl = False
    
    with open('urls.txt', 'r') as f:
        urlList = f.read()
        urlList = eval(urlList)
        urlList = sorted(urlList, key  = lambda x: x['url_id'])
        f.close()
        
    for idx, el in enumerate(urlList):
        if el['url'] == content["url"]:
            preExistingUrl = True
            id = el['url_id']
            resp['id'] = id 
            resp['status'] = 1
            path = el['path']
            break
    
          
    if id==0:
        status = 0
        id = (urlList[-1]["url_id"] + 1)        
        
        pathName = str(id) + "___" +  baseName
        obj = WebsiteParser(content["url"], 3, pathName)
        '''
        try:
            status = 1 
            obj.parseWebsite()
        except Exception:
            status = 0 
            pass
        '''
        
        if status == 0:
            id = 0
        
        elif preExistingUrl == False:
            path = pathName
            urlList.append({"id": id, "url": content["url"], "path" : path})
            with open('urls.txt', 'w') as f:           
                f.write(str(urlList))
                f.close()
                
        else:
            print("THis case")
            pass
     
        resp['id'] = id 
        resp['status'] = status
        

    #resp = "the response is " + str(content["url"])
    print(jsonify(resp))
    return(jsonify(resp))
    
    
@app.route("/data2", methods = ["POST"])
def fetchDetails():
    
    global path
    
    content = request.get_json()
    print(content)
    query = content["question"]
    url_id = content["url_id"]
    
    with open('urls.txt', 'r') as f:
        urlList = f.read()
        urlList = eval(urlList)
        urlList = sorted(urlList, key  = lambda x: x['url_id'])
        f.close()
        
    for idx, el in enumerate(urlList):
        if el['url_id'] == content["url_id"]:
            path = el['path']
            urlName = el["url"]
            break
    
    #path = r"C:\Users\prateek.sethi\Desktop\BERT\Website_QA\invest-data"
    print(path)
    
    obj = WebsiteQA(query, path)
    result = obj.process()
 
    print(jsonify(result))
    
    return jsonify(result)
    
    
    


if __name__ == "__main__":
    app.run(debug = True, use_reloader=False)