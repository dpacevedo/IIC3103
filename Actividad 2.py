from flask import *
import json,requests

app = Flask(__name__)

@app.route('/status',methods =['GET'])
def home_page():
	status_code = Response(status=204)
	return status_code

@app.route('/info',methods =['GET'])
def info_page():
    url = "https://hola"
    data_set = {'url': url }
    json_dump = json.dumps(data_set)
    return json_dump

@app.route('/security',methods =['DELETE'])
def security_page():
    status_code = Response(status=401)
    return status_code

if __name__== '__main__':
    app.run(port=7776)
