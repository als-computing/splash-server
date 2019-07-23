import requests

url = 'http://localhost:5000/api/experiments'
headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}
r = requests.post(url, data=open('./splash-server/schema/fake_experiments/project0.json', 'rb'), headers=headers)
print (r)