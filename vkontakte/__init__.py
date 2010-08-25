# coding: utf-8
import random
import time
import urllib
from hashlib import md5
from functools import partial
try:
    import json
except ImportError:
    import simplejson as json
from vkontakte import http

API_URL = 'http://api.vk.com/api.php'

class VKError(Exception):
    __slots__ = ["code", "description", "params"]
    def __init__(self, code, description, params):
        self.code, self.description, self.params = (code, description, params)
        Exception.__init__(self, str(self))
    def __str__(self):
        return "Error(code = '%s', description = '%s', params = '%s')" % (self.code, self.description, self.params)

def _sig(api_secret, **kwargs):
    keys = sorted(kwargs.keys())
    params = "".join(["%s=%s" % (key, kwargs[key]) for key in keys])
    return md5(params+str(api_secret)).hexdigest()

def request(api_id, api_secret, method, timestamp=None, timeout = 1, **kwargs):
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

    # urllib2 doesn't support timeouts for python 2.5 so
    # custom function is used for making http requests
    headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
    return http.post(API_URL, data, headers, timeout)


class API(object):
    def __init__(self, api_id, api_secret, **defaults):
        self.api_id = api_id
        self.api_secret = api_secret
        self.defaults = defaults

    def get(self, method, timeout = 1, **kwargs):
        status, response = request(self.api_id, self.api_secret, method, timeout = timeout, **kwargs)
        if not (status >= 200 and status <= 299):
            raise VKError(status, "HTTP error", kwargs)

        data = json.loads(response)
        if "error" in data:
            raise VKError(data["error"]["error_code"], data["error"]["error_msg"], data["error"]["request_params"])
        return data['response']

    # some magic to convert instance attributes into method names
    def __getattr__(self, name):
        return partial(self, method=name)

    def __call__(self, **kwargs):
        method = kwargs.pop('method')
        params = self.defaults.copy()
        params.update(kwargs)
        return self.get(method, **params)
