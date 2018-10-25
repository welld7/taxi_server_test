#!/usr/local/bin/python
# -*- coding: utf-8 -*-

MAX_LIMIT = 100

HOST = 'http://127.0.0.1:8888/{0}'

MAX_ORDERS_PER_USER=2
CHANGE_STATUS_TIME=60 #FIXME
DRAFT_LIFETIME = 30 
UPDATE_ORDERS_INTERVAL=5

ENDPOINTS = {
    'orders': HOST.format('orders'),
    'signup': HOST.format('signup'),
    'edit': HOST.format('user/edit?username={0}'),
    'draft': HOST.format('order/draft?username={0}'),
    'commit': HOST.format('order/commit?username={0}&order_id={1}'),
    'list': HOST.format('orders?username={0}&show={1}'),
    'cancel': HOST.format('order/cancel?username={0}&order_id={1}')

}

performers =    {u'Маша', u'Петя', u'Вася', u'Таня'}


class CustomAuth:
    """Attaches HTTP Custom Authentication to the given Request object."""

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __eq__(self, other):
        return all([
            self.username == getattr(other, 'username', None),
            self.password == getattr(other, 'password', None)
        ])

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers['Authorization'] = "Custom " + self.password
        return r
