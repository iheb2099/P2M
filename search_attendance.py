
from elasticsearch import Elasticsearch
import pandas as pd
es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])
def searchAttendance(cameras,date,timefrom,timeto):
    query = {
        "query": {
            "bool": {
                "must": [{"match_phrase": {"cameraId": f"{cameras}"}}, {"match": {"datedetected": f"{date}"}},
                         {"range": {"timedetected": {"gte": f"{timefrom}"}}},
                         {"range": {"timedetected": {"lte": f"{timeto}"}}}],

            }}
    }
    response = es.search(index="attendance", body=query, size=10000)
    l = {}

    for hit in response['hits']['hits']:

        if l == {}:
            l['fname'] = [hit['_source']['fname']]
            l['lname'] = [hit['_source']['lname']]
            l['classgroup'] = [hit['_source']['classgroup']]
            l['classlevel'] = [hit['_source']['classlevel']]
            l['dateadded'] = [hit['_source']['dateadded']]
            l['email'] = [hit['_source']['email']]
            l['usertype'] = [hit['_source']['usertype']]
            l['datedetected'] = [hit['_source']['datedetected']]
            l['timedetected'] = [hit['_source']['timedetected']]

        else:
            l['fname'].append(hit['_source']['fname'])
            l['lname'].append(hit['_source']['lname'])
            l['classgroup'].append(hit['_source']['classgroup'])
            l['classlevel'].append(hit['_source']['classlevel'])
            l['dateadded'].append(hit['_source']['dateadded'])
            l['email'].append(hit['_source']['email'])
            l['usertype'].append(hit['_source']['usertype'])
            l['datedetected'].append(hit['_source']['datedetected'])
            l['timedetected'].append(hit['_source']['timedetected'])

    df = pd.DataFrame(l)
    return df