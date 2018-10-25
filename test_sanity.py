#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import pytest
import requests
import json
import uuid
from test_variables import ENDPOINTS, MAX_LIMIT, CustomAuth, MAX_ORDERS_PER_USER

@pytest.mark.sanity
@pytest.mark.taxi
def test_get_empty_orders():
    """ Test checks default error code 503. """

    r = requests.get(ENDPOINTS['orders'])

    assert r.status_code == 403

@pytest.mark.sanity
@pytest.mark.taxi
def test_signup():
    """ Test signup """
    uname = str(uuid.uuid4())[:8]
    new_user = { "name": "some_name", "username": uname, "secret":"key1"}
    r = requests.post(ENDPOINTS['signup'], json = new_user)

    assert r.status_code == 200

@pytest.mark.sanity
@pytest.mark.taxi
@pytest.mark.negative
def test_signup_negative():
    """ Test signup """
    uname = str(uuid.uuid4())[:8]
    new_user = { "name": "john", "username":uname, "secret":"key2"}
    r = requests.post(ENDPOINTS['signup'], json = new_user)

    new_user2 = { "name": "john", "username":uname, "secret":"key3"}
    r = requests.post(ENDPOINTS['signup'], json = new_user2)

    assert r.status_code == 406

@pytest.mark.sanity
@pytest.mark.taxi
def test_edit():
    """ Test edit user """
    
    uname = str(uuid.uuid4())[:8]
    new_user = { "name": "some_name", "username":uname, "secret":"key1"}
    requests.post(ENDPOINTS['signup'], json = new_user)

    new_secret = { "new_secret":"key2"}
    r = requests.post(ENDPOINTS['edit'].format(uname), json = new_secret, \
                      auth =CustomAuth(uname,'key1')) 

    assert r.status_code == 200

    new_secret = { "new_secret":"key1"}
    r = requests.post(ENDPOINTS['edit'].format(uname), json = new_secret, \
                      auth =CustomAuth(uname,'key2'))

@pytest.mark.sanity
@pytest.mark.taxi
@pytest.mark.negative
def test_edit_wrong_secret():
    """ Test edit user with wrong secret """
    uname = str(uuid.uuid4())[:8]

    new_user = { "name": "some_name", "username":uname, "secret":"key1"}
    requests.post(ENDPOINTS['signup'], json = new_user)

    new_secret = { "new_secret":"key2"}
    r = requests.post(ENDPOINTS['edit'].format(uname), json = new_secret, \
                      auth =CustomAuth(uname,'key0000000')) #using wrong secret 
    assert r.status_code == 403


@pytest.mark.sanity
@pytest.mark.taxi
#BUG: draft sometimes returns wrong json
def test_draft():
    """ Test draft """

    uname = str(uuid.uuid4())[:8]

    new_user = { "name": "some_name", "username":uname, "secret":"key1"}
    r = requests.post(ENDPOINTS['signup'], json = new_user)

    new_secret = { "new_secret":"key2"}
    r = requests.post(ENDPOINTS['draft'].format(uname),  json = new_secret, auth =CustomAuth(uname,'key1'))

    assert r.status_code == 200


@pytest.mark.sanity
@pytest.mark.taxi
@pytest.mark.negative
def test_draft_wrong_secret():
    """ Test draft: wrong secret """
    uname = str(uuid.uuid4())[:8]

    new_user = { "name": "some_name", "username":uname, "secret":"key1"}
    r = requests.post(ENDPOINTS['signup'], json = new_user)

    new_secret = { "new_secret":"key2"}
    r = requests.post(ENDPOINTS['draft'].format(uname),  json = new_secret, auth =CustomAuth(uname,'key2'))

    assert r.status_code == 403


@pytest.mark.sanity
@pytest.mark.taxi
def test_commit():
    """ Test commit """
    uname = str(uuid.uuid4())[:8]

    new_user = { "name": "some_name", "username":uname, "secret":"key1"}
    requests.post(ENDPOINTS['signup'], json = new_user)

    r = requests.post(ENDPOINTS['draft'].format(uname),  json = new_user, auth= CustomAuth(uname,'key1'))

    order = json.loads(r.content)['order_id']
    address = {"address": "Малая Бронная, 12"}

    r = requests.post(ENDPOINTS['commit'].format(uname, order),  json = address, auth = CustomAuth(uname,'key1'))

    assert r.status_code == 200


@pytest.mark.sanity
@pytest.mark.taxi
@pytest.mark.negative
def test_commit_wrong_secret():
    """ Test commit: wrong secret """

    uname = str(uuid.uuid4())[:8]

    new_user = { "name": "some_name", "username":uname, "secret":"key1"}
    requests.post(ENDPOINTS['signup'], json = new_user)

    requests.post(ENDPOINTS['draft'].format(uname),  json = new_user, auth= CustomAuth(uname,'key1'))

    r = requests.post(ENDPOINTS['commit'].format(uname, "0"),  json = {}, auth = CustomAuth(uname,'key2'))

    assert r.status_code == 403


@pytest.mark.sanity
@pytest.mark.taxi
@pytest.mark.negative
def test_commit_wrong_order():
    """ Test commit: wrong order """
 
    uname = str(uuid.uuid4())[:8]
    new_user = { "name": "some_name", "username":uname, "secret":"key1"}
    requests.post(ENDPOINTS['signup'], json = new_user)

    r = requests.post(ENDPOINTS['draft'].format(uname),  json = new_user, auth= CustomAuth(uname,'key1'))

    order = json.loads(r.content)['order_id']
    address = {"address": "Малая Бронная, 12"}
    r = requests.post(ENDPOINTS['commit'].format(uname, "0"),  json = address, auth = CustomAuth(uname,'key1'))

    assert r.status_code == 404


@pytest.mark.sanity
@pytest.mark.taxi
@pytest.mark.negative
def test_commit_too_fast():
    """ Test commit too fast"""
    uname = str(uuid.uuid4())[:8]
    new_user = { "name": "some_name", "username":uname, "secret":"key1"}
    requests.post(ENDPOINTS['signup'], json = new_user)
    
    #last iteration must return 429 code
    for i in xrange(MAX_ORDERS_PER_USER+1):
        r = requests.post(ENDPOINTS['draft'].format(uname),  json = new_user, auth= CustomAuth(uname,'key1'))

        order = json.loads(r.content)['order_id']
        address = {"address": "Малая Бронная, 12"}
        r = requests.post(ENDPOINTS['commit'].format(uname, order),  json = address, auth = CustomAuth(uname,'key1'))

    assert r.status_code == 429


@pytest.mark.sanity
@pytest.mark.taxi
#BUG: list sometimes (rarely) returns wrong json
def test_list():
    """ Test list for 1 order contains the list of 1 element """

    uname = str(uuid.uuid4())[:8]

    new_user = { "name": "some_name", "username":uname, "secret":"key1"}
    requests.post(ENDPOINTS['signup'], json = new_user)

    r = requests.post(ENDPOINTS['draft'].format(uname),  json = new_user, auth =CustomAuth(uname,'key1'))

    json2 = json.loads(r.content)
    order = json2['order_id']
    address = {"address": "Малая Бронная, 12"}

    requests.post(ENDPOINTS['commit'].format(uname, order), json = address, auth =CustomAuth(uname,'key1'))

    r = requests.get(ENDPOINTS['list'].format(uname, 'all'), auth = CustomAuth(uname,'key1'))
    json3 = json.loads(r.content)
    
    #expect 1 element in the "orders" list
    assert len(json3["orders"]) == 1

@pytest.mark.sanity
@pytest.mark.taxi
@pytest.mark.negative
def test_list_wrong_secret():
    """ Test list: wrong secret """
    uname = str(uuid.uuid4())[:8]

    new_user = { "name": "some_name", "username":uname, "secret":"key1"}
    requests.post(ENDPOINTS['signup'], json = new_user)

    r = requests.get(ENDPOINTS['list'].format(uname, 'all'), auth = CustomAuth(uname,'key2'))

    assert r.status_code == 403

@pytest.mark.sanity
@pytest.mark.taxi
def test_cancel():
    """ Test cancel """
    uname = str(uuid.uuid4())[:8]
    new_user = { "name": "some_name", "username":uname, "secret":"key1"}
    requests.post(ENDPOINTS['signup'], json = new_user)

    r = requests.post(ENDPOINTS['draft'].format(uname),  json = new_user, auth = CustomAuth(uname,'key1'))
    order = json.loads(r.content)['order_id']
    address = {"address": "Моховая, 2"}

    requests.post(ENDPOINTS['commit'].format(uname, order), json=address, auth = CustomAuth(uname,'key1'))

    r = requests.post(ENDPOINTS['cancel'].format(uname, order),  auth = CustomAuth(uname,'key1'))

    assert r.status_code == 200


@pytest.mark.sanity
@pytest.mark.taxi
@pytest.mark.negative
def test_cancel_wrong_secret():
    """ Test cancel: wrong secret """
    uname = str(uuid.uuid4())[:8]

    new_user = { "name": "some_name", "username":uname, "secret":"key1"}
    requests.post(ENDPOINTS['signup'], json = new_user)
    r = requests.post(ENDPOINTS['cancel'].format(uname, 0),  auth =CustomAuth(uname,'key2'))

    assert r.status_code == 403

@pytest.mark.sanity
@pytest.mark.taxi
@pytest.mark.negative
def test_cancel_wrong_order():
    """ Test cancel: wrong order """
    uname = str(uuid.uuid4())[:8]
    new_user = { "name": "some_name", "username":uname, "secret":"key1"}
    requests.post(ENDPOINTS['signup'], json = new_user)

    r = requests.post(ENDPOINTS['draft'].format(uname),  json = new_user, auth = CustomAuth(uname,'key1'))

    order = json.loads(r.content)['order_id']
    address = {"address": "Моховая, 2"}

    requests.post(ENDPOINTS['commit'].format(uname, order), json=address, auth = CustomAuth(uname,'key1'))

    r = requests.post(ENDPOINTS['cancel'].format(uname, "0"),  auth = CustomAuth(uname,'key1'))

    assert r.status_code == 404


# +We check 406 (cancel) in long cases module

@pytest.mark.sanity
@pytest.mark.taxi
@pytest.mark.negative
def test_commit_other_user():
    """ Test commit by an other user (security) """

    uname = str(uuid.uuid4())[:8]

    new_user = { "name": "some_name", "username":uname, "secret":"key1"}
    requests.post(ENDPOINTS['signup'], json = new_user)

    r = requests.post(ENDPOINTS['draft'].format(uname),  json = new_user, auth =CustomAuth(uname,'key1'))

    json2 = json.loads(r.content)
    order = json2['order_id']
    address = {"address": "Малая Бронная, 12"}

    uname2 = str(uuid.uuid4())[:8]

    new_user2 = { "name": "some_name", "username":uname, "secret":"key2"}
    requests.post(ENDPOINTS['signup'], json = new_user2)
   
    r=requests.post(ENDPOINTS['commit'].format(uname2, order), json = address, auth =CustomAuth(uname,'key1'))
    assert r.status_code == 403










