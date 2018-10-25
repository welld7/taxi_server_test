#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#long test cases
#TODO: 'expired' status still to be covered + COMPLETION_RATE

import pytest
import requests
import json
import uuid
from test_variables import ENDPOINTS, MAX_LIMIT, CustomAuth, CHANGE_STATUS_TIME, DRAFT_LIFETIME, performers, MAX_ORDERS_PER_USER, UPDATE_ORDERS_INTERVAL
import time

#returns order_id
def create_and_commit_order( uname, secret, uaddress):
    #uname = str(uuid.uuid4())[:8]
    new_user = { "name": "some_name", "username":uname, "secret":secret}
    requests.post(ENDPOINTS['signup'], json = new_user)

    r = requests.post(ENDPOINTS['draft'].format(uname),  json = new_user, auth = CustomAuth(uname, secret))
    order = json.loads(r.content)['order_id']
    address = {"address": uaddress}

    r = requests.post(ENDPOINTS['commit'].format(uname, order), json=address, auth = CustomAuth(uname,secret))
    return order


def all_same(items, val1, val2):
    return all(x == val1 or x==val2 for x in items)


@pytest.mark.long
@pytest.mark.taxi
def test_cancel_too_late():
    """ Test cancel after status changed from pending """
    uname = str(uuid.uuid4())[:8]
    order = create_and_commit_order(uname, "key1", "Моховая, 2")
    
    #CHANGE_STATUS_TIME+UPDATE_ORDERS_INTERVAL seconds is enough to find a driver
    time.sleep(CHANGE_STATUS_TIME+UPDATE_ORDERS_INTERVAL)
    r = requests.post(ENDPOINTS['cancel'].format(uname, order),  auth = CustomAuth(uname,'key1'))

    assert r.status_code == 406


@pytest.mark.long
@pytest.mark.taxi
def test_draft_lifetime():
    """ Test commit after draft_lifetime: the draft expirised and it's impossible to commit it """
    uname = str(uuid.uuid4())[:8]
    new_user = { "name": "some_name", "username":uname, "secret":"key1"}
    requests.post(ENDPOINTS['signup'], json = new_user)

    r = requests.post(ENDPOINTS['draft'].format(uname),  json = new_user, auth = CustomAuth(uname,'key1'))
    order = json.loads(r.content)['order_id']
    address = {"address": "Моховая, 2"}
    
    time.sleep(DRAFT_LIFETIME+35)#bug? why +35?
 
    r = requests.post(ENDPOINTS['commit'].format(uname, order), json=address, auth = CustomAuth(uname,'key1'))
    assert r.status_code == 404

@pytest.mark.parametrize("n", [2, 8])
@pytest.mark.long
@pytest.mark.taxi
@pytest.mark.param
def test_status_complete_for_n_users(n):
    """ Test that orders compete for multiple users simultaneously """

    name_list=[]
    for i in xrange(n):
        uname = str(uuid.uuid4())[:8]
        create_and_commit_order(uname, "key1", "someaddress")
        name_list.append(uname)

    time.sleep(2*CHANGE_STATUS_TIME + 2*UPDATE_ORDERS_INTERVAL+3)#wait for 'found' and 'complete'
    
    status_complete=[]
    for i in xrange(n):
        r = requests.get(ENDPOINTS['list'].format(name_list[i], 'all'), auth = CustomAuth(uname,'key1'))
        #print r.content
        status_complete.append(json.loads(r.content)['orders'][0]['status'])

    assert all_same(status_complete, 'complete', 'expired')

@pytest.mark.long
@pytest.mark.taxi
def test_cancel_when_status_found():
    """ Test that after CHANGE_STATUS_TIME status is 'found', and after another
        CHANGE_STATUS_TIME the status is 'complete """
    uname = str(uuid.uuid4())[:8]
    order = create_and_commit_order(uname, "key1", "Моховая, 2")

    time.sleep(CHANGE_STATUS_TIME+UPDATE_ORDERS_INTERVAL)#wait

    r = requests.get(ENDPOINTS['list'].format(uname, 'all'), auth = CustomAuth(uname,'key1'))

    r = requests.post(ENDPOINTS['cancel'].format(uname, order),  auth = CustomAuth(uname,'key1'))

    assert r.status_code == 406

    time.sleep(CHANGE_STATUS_TIME+UPDATE_ORDERS_INTERVAL)#wait

    r = requests.post(ENDPOINTS['cancel'].format(uname, order),  auth = CustomAuth(uname,'key1'))
    assert r.status_code == 406

@pytest.mark.long
@pytest.mark.taxi
def test_show_only_active():
    """ Test status after 'found' and 'complete' """
    uname = str(uuid.uuid4())[:8]
    order=create_and_commit_order(uname, "key1", "Моховая, 2")

    time.sleep(2*CHANGE_STATUS_TIME + 2*UPDATE_ORDERS_INTERVAL)#wait for 'found' and 'complete'

    #now the first order is inactive

    order2=create_and_commit_order(uname, "key1", "Моховая, 2")

    r = requests.get(ENDPOINTS['list'].format(uname, 'active'), auth = CustomAuth(uname,'key1'))
    json1 = json.loads(r.content)
    assert len(json1["orders"]) == 1 and json1['orders'][0]['status']=='pending'
    #TODO: check that 'cancelled', 'expired' not shown as active as well

@pytest.mark.taxi
@pytest.mark.negative
@pytest.mark.long
def test_max_orders_for_one_user():
    """ Positive test: MAX_ORDERS_PER_USER per user """
    uname = str(uuid.uuid4())[:8]
    new_user = { "name": "some_name", "username":uname, "secret":"key1"}
    requests.post(ENDPOINTS['signup'], json = new_user)
    
    for i in xrange(MAX_ORDERS_PER_USER):
        r = requests.post(ENDPOINTS['draft'].format(uname),  json = new_user, auth= CustomAuth(uname,'key1'))

        order = json.loads(r.content)['order_id']
        address = {"address": "Малая Бронная, 12"}
        r = requests.post(ENDPOINTS['commit'].format(uname, order),  json = address, auth = CustomAuth(uname,'key1'))

    time.sleep(2*CHANGE_STATUS_TIME+2*UPDATE_ORDERS_INTERVAL)#wait

    r = requests.get(ENDPOINTS['list'].format(uname, 'all'), auth = CustomAuth(uname,'key1'))

    status_complete = [json.loads(r.content)['orders'][i]['status'] for i in xrange(MAX_ORDERS_PER_USER) ] 
    #print status_complete
    assert all_same(status_complete, 'complete', 'expired')



@pytest.mark.long
@pytest.mark.taxi
def test_status_found_complete():
    """ Test status after 'found' and 'complete' """
    uname = str(uuid.uuid4())[:8]
    order=create_and_commit_order(uname, "key1", "Моховая, 2")

    time.sleep(CHANGE_STATUS_TIME+UPDATE_ORDERS_INTERVAL)#wait

    r = requests.get(ENDPOINTS['list'].format(uname, 'all'), auth = CustomAuth(uname,'key1'))
    status_found = json.loads(r.content)['orders'][0]['status']

    #Move up the first check to find the problem faster. We can save 60 seconds. 
    assert status_found == 'found' or status_found == 'expired'

    if status_found == 'expired':
        return

    time.sleep(CHANGE_STATUS_TIME+UPDATE_ORDERS_INTERVAL)#wait

    r = requests.get(ENDPOINTS['list'].format(uname, 'all'), auth = CustomAuth(uname,'key1'))
    status_complete = json.loads(r.content)['orders'][0]['status']
    performer_name = json.loads(r.content)['orders'][0]['performer']['name']

    # More than one checks in one test is not good. Using it only for time optimization
    assert status_complete == 'complete'
    assert performer_name in performers

    #TODO: it's also possible to check if the status won't change from 'complete' after
    # another CHANGE_STATUS_TIME seconds. Now skip it to save the time.

    #time.sleep(CHANGE_STATUS_TIME+UPDATE_ORDERS_INTERVAL)#wait
    #r = requests.get(ENDPOINTS['list'].format(uname, 'all'), auth = CustomAuth(uname,'key1'))
    #status_complete = json.loads(r.content)['orders'][0]['status']
    #assert status_complete == 'complete'

