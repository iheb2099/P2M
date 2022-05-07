#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# import the Elasticsearch low-level client
from elasticsearch import Elasticsearch

# import the Image and TAGS classes from Pillow (PIL)
from PIL import Image
from PIL.ExifTags import TAGS

import uuid # for image meta data ID
import base64 # convert image to b64 for indexing
import datetime # for image meta data timestamp
import numpy as np

# create a client instance of Elasticsearch
elastic_client = Elasticsearch([{'host': 'localhost', 'port': 9200}])

"""
Function that uses PIL's TAGS class to get an image's EXIF
meta data and returns it all in a dict
"""
def get_image_exif(img):
    # use PIL to verify image is not corrupted
    img.verify()

    try:
        # call the img's getexif() method and return EXIF data
        exif = img._getexif()
        exif_data = {}

        # iterate over the exif items
        for (meta, value) in exif.items():
            try:
                # put the exif data into the dict obj
                exif_data[TAGS.get(meta)] = value
            except AttributeError as error:
                print ('get_image_meta AttributeError for:', '--', error)
    except AttributeError:
        # if img file doesn't have _getexif, then give empty dict
        exif_data = {}
    return exif_data

"""
Function to create new meta data for the Elasticsearch
document. If certain meta data is missing from the orginal,
then this script will "fill in the gaps" for the new documents
to be indexed.
"""
def create_exif_data(img,):

    # create a new dict obj for the Elasticsearch doc
    es_doc = {}
    es_doc["size"] = img.size

    # put PIL Image conversion in a try-except indent block


    # call the method to have PIL return exif data
    exif_data = get_image_exif(img)

    # get the PIL img's format and MIME
    es_doc["image_format"] = img.format
    es_doc["image_mime"] = Image.MIME[img.format]

    # get datetime meta data from one of these keys if possible
    if 'DateTimeOriginal' in exif_data:
        es_doc['datetime'] = exif_data['DateTimeOriginal']

    elif 'DateTime' in exif_data:
        es_doc['datetime'] = exif_data['DateTime']

    elif 'DateTimeDigitized' in exif_data:
        es_doc['datetime'] = exif_data['DateTimeDigitized']

    # if none of these exist, then use current timestamp
    else:
        es_doc['datetime'] = str( datetime.datetime.now() )

    # create a UUID for the image if none exists
    if 'ImageUniqueID' in exif_data:
        es_doc['uuid'] = exif_data['ImageUniqueID']
    else:
        # create a UUID converted to string
        es_doc['uuid'] = str( uuid.uuid4() )

    # make and model of the camera that took the image
    if 'Make' in exif_data:
        es_doc['make'] = exif_data['Make']
    else:
        es_doc['make'] = "Camera Unknown"

    # camera unknown if none exists
    if 'Model' in exif_data:
        es_doc['model'] = exif_data['Model']
    else:
        es_doc['model'] = "Camera Unknown"



    # get the X and Y res of image
    if 'XResolution' in exif_data:
        es_doc['x_res'] = exif_data['XResolution']
    else:
        es_doc['x_res'] = None

    if 'YResolution' in exif_data:
        es_doc['y_res'] = exif_data['YResolution']
    else:
        es_doc['y_res'] = None
    # return the dict
    return es_doc

# create an Image instance of photo
def storeImageElastic(img,_index,camera='camera 1'):

    # img = Image.open(open(_file, 'rb'))

    # get the _source dict for Elasticsearch doc
    _source={}
    # store the file name in the Elasticsearch index
    _source['name'] = 'unknown'
    _source['datedetected'] = datetime.datetime.today().strftime('%Y-%m-%d')
    _source['timedetected'] = datetime.datetime.today().strftime('%H:%M:%S')
    _source['camera']=f'{camera}'
    # covert NumPy of PIL image to simple Python list obj
    img_array = np.asarray(img).tolist()

    # convert the nested Python array to a str
    img_str = img_array

    # put the encoded string into the _source dict
    _source["raw_data"] = img_str



    # call the Elasticsearch client's index() method
    resp = elastic_client.index(
        index=_index,
        doc_type='_doc',
        document=_source,
        request_timeout=60
    )
    print("\nElasticsearch index() response -->", resp)
def searchUnkowns(timefrom,timeto,datefrom,dateto,cameras):
    query = {
        "query": {
            "bool": {
                "must": [{"match_phrase": {"camera": f"{cameras}"}},
                         {"range": {"datedetected": {"gte": f"{datefrom}"}}},
                         {"range": {"datedetected": {"lte": f"{dateto}"}}},
                         {"range": {"timedetected": {"gte": f"{timefrom}"}}},
                         {"range": {"timedetected": {"lte": f"{timeto}"}}}]

            }}
    }
    response = elastic_client.search(index="unknowns", body=query, size=10000)
    l = {}

    for hit in response['hits']['hits']:

        if l == {}:
            l['name'] = [hit['_source']['name']]
            l['datedetected'] = [hit['_source']['datedetected']]
            l['raw_data'] = [hit['_source']['raw_data']]
            l['timedetected']=[hit['_source']['timedetected']]
            l['camera']=[hit['_source']['camera']]

        else:
            l['name'].append(hit['_source']['name'])
            l['datedetected'].append(hit['_source']['datedetected'])
            l['raw_data'].append(hit['_source']['raw_data'])
            l['timedetected'].append(hit['_source']['timedetected'])
            l['camera'].append(hit['_source']['camera'])


    return l

