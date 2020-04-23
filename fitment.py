import os
import xml.etree.ElementTree as ET
import tempfile

import requests
from flask import Flask
from flask import render_template
from flask import request

from secrets import get_secret

app = Flask(__name__)

GET_ITEM = """<?xml version="1.0" encoding="utf-8"?>
<GetSingleItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
 <IncludeSelector>Compatibility,ItemSpecifics</IncludeSelector>
 <ItemID>{source}</ItemID>
</GetSingleItemRequest>
"""
GET_ITEM_HEADERS = {
    "Content-Type": "text/xml",
    "X-EBAY-API-APP-ID": "bogus",
    "X-EBAY-API-CALL-NAME": "GetSingleItem",
    "X-EBAY-API-REQUEST-ENCODING": "XML",
    "X-EBAY-API-VERSION": "967",
    "X-EBAY-API-SITE-ID": "100",
}

REVISE_ITEM = """<?xml version="1.0" encoding="utf-8"?>
<ReviseItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
 <RequesterCredentials>
  <eBayAuthToken>{ebay_auth_token}</eBayAuthToken>
 </RequesterCredentials>
 <WarningLevel>High</WarningLevel>
 <Item>
  <ItemID>{destination}</ItemID>
 </Item>
</ReviseItemRequest>
"""
REVISE_ITEM_HEADERS = {
    "Content-Type": "text/xml",
    "X-EBAY-API-CALL-NAME": "ReviseItem",
    "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
    "X-EBAY-API-REQUEST-ENCODING": "XML",
    "X-EBAY-API-SITEID": "100",
}

def post_get_item(input_data):
    ET.register_namespace("", "urn:ebay:apis:eBLBaseComponents")
    get_item_headers = dict(GET_ITEM_HEADERS)
    get_item_headers['X-EBAY-API-APP-ID'] = input_data['ebay_api_app_id']
    request_txt = GET_ITEM.format(**input_data)
    # with open('get_request.txt', 'w') as file:
    #     file.write(request_txt)
    r = requests.post('https://open.api.ebay.com/shopping', data=request_txt, headers=get_item_headers)
    # with open('get_response.txt', 'w') as file:
    #     file.write(r.text)
    return r.ok, ET.fromstring(r.text)


def get_compatibility(get_item_response):
    ns = {"ns0": "urn:ebay:apis:eBLBaseComponents"}
    item = get_item_response.find("ns0:Item", ns)
    return item.find("ns0:ItemCompatibilityList", ns)


def post_revise_item(input_data, compatibility):
    ns = {"ns0": "urn:ebay:apis:eBLBaseComponents"}
    revise_item_txt = REVISE_ITEM.format(**input_data)
    revise_item_xml = ET.fromstring(revise_item_txt)
    item = revise_item_xml.find("ns0:Item", ns)
    item.append(compatibility)
    tree = ET.ElementTree(revise_item_xml)
    fd, tmpfile = tempfile.mkstemp()
    tree.write(tmpfile, xml_declaration=True, encoding='UTF-8')
    with open(tmpfile) as file:
        contents = file.read()
    os.close(fd)
    os.unlink(tmpfile)
    r = requests.post("https://api.ebay.com/ws/api.dll", data=contents, headers=REVISE_ITEM_HEADERS)
    # with open('revise_response.xml', 'w') as file:
    #     file.write(r.text)
    return r.text


@app.route('/', methods=['GET', 'POST'])
def getitem():
    if request.method == 'POST':
        input_data = {
            'source': request.form['source'],
            'destination': request.form['destination'],
        }
        input_data.update(get_secret())
        is_ok, get_item_response = post_get_item(input_data)
        if not is_ok:
            return render_template('index.html', result=get_item_response)
        compatibility = get_compatibility(get_item_response)
        result = post_revise_item(input_data, compatibility)
        return render_template('index.html', result=result)
    return render_template('index.html', result='')