# coding: utf-8
import random
import time
import urllib
import urllib2
from hashlib import md5
from functools import partial
try:
    import json
except ImportError:
    import simplejson as json

class VKError(Exception):
    pass

API_URL = 'http://api.vk.com/api.php'

def _sig(api_secret, **kwargs):
    keys = sorted(kwargs.keys())
    params = "".join(["%s=%s" % (key, kwargs[key]) for key in keys])
    return md5(params+str(api_secret)).hexdigest()

def request(api_id, api_secret, method, timestamp=None, **kwargs):
    params = dict(
        api_id = str(api_id),
        method = method,
        format = 'JSON',
        v = '3.0',
        random = random.randint(0, 2**30),
        timestamp = timestamp or int(time.time())
    )
    params.update(kwargs)
    params['sig'] = _sig(api_secret, **params)
    data = urllib.urlencode(params)
    return urllib2.urlopen(API_URL, data).read()


class API(object):
    def __init__(self, api_id, api_secret, **defaults):
        self.api_id = api_id
        self.api_secret = api_secret
        self.defaults = defaults

    def get(self, method, **kwargs):
        assert kwargs.get('format', 'JSON') == 'JSON', 'Only JSON in supported'
        response = request(self.api_id, self.api_secret, method, **kwargs)
        data = json.loads(response)
        if 'error' in data:
            raise VKError(data['error'])
        return data['response']

    # some magic to convert instance attributes into method names
    def __getattr__(self, name):
        return partial(self, method=name)

    def __call__(self, **kwargs):
        method = kwargs.pop('method')
        params = self.defaults.copy()
        params.update(kwargs)
        return self.get(method, **params)
