import csv
import datetime
from datetime import datetime
import json
import requests
from requests.auth import HTTPBasicAuth
import time

headers = {'Content-type': 'application/json'}
data = '{"count":1,"ackmode":"ack_requeue_false","encoding":"auto","truncate":50000}'

while True:
    response = requests.post('http://debian:15672/api/queues/glances/glances.cpu/get', headers=headers, data=data, auth=HTTPBasicAuth('glances', 'glances'))
    queuedMessage = '{"data":' + response.text + '}'
    queuedMessage = json.loads(queuedMessage)
    with open('cpuData.csv', 'a+', newline='') as f:
        fnames = ['dateinfo', 'user']
        writer = csv.DictWriter(f, fieldnames=fnames)
        for i in queuedMessage["data"]:
            statsdata = (i["payload"])
            stats = statsdata.split(', ')
            statpairs = dict(s.split('=',1) for s in stats)
            writer.writerow({'dateinfo' : datetime.fromisoformat(statpairs['dateinfo']), 'user' : statpairs['user']})
    time.sleep(1)
