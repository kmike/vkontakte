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
SECURE_API_URL = 'https://api.vkontakte.ru/method/'
DEFAULT_TIMEOUT = 1


# See full list of VK API methods here:
# http://vkontakte.ru/developers.php?o=-1&p=%D0%A0%D0%B0%D1%81%D1%88%D0%B8%D1%80%D0%B5%D0%BD%D0%BD%D1%8B%D0%B5_%D0%BC%D0%B5%D1%82%D0%BE%D0%B4%D1%8B_API&s=0
COMPLEX_METHODS = ['secure', 'ads', 'messages', 'likes', 'friends',
    'groups', 'photos', 'wall', 'newsfeed', 'notifications', 'audio',
    'video', 'docs', 'places', 'storage', 'notes', 'pages',
    'activity', 'offers', 'questions', 'subscriptions']


class VKError(Exception):
    __slots__ = ["code", "description", "params"]
    def __init__(self, code, description, params):
        self.code, self.description, self.params = (code, description, params)
        Exception.__init__(self, str(self))
    def __str__(self):
        return "Error(code = '%s', description = '%s', params = '%s')" % (self.code, self.description, self.params)

def _to_utf8(s):
    if isinstance(s, unicode):
        return s.encode('utf8')
    return s # this can be number, etc.

def signature(api_secret, params):
    keys = sorted(params.keys())
    param_str = "".join(["%s=%s" % (str(key), _to_utf8(params[key])) for key in keys])
    return md5(param_str + str(api_secret)).hexdigest()

# We have to support this:
#
#   >>> vk = API(key, secret)
#   >>> vk.get('getServerTime')  # "get" is a method of API class
#   >>> vk.friends.get(uid=123)  # "get" is a part of vkontakte method name
#
# It works this way: API class has 'get' method but _API class doesn't.

class _API(object):
    def __init__(self, api_id=None, api_secret=None, token=None, **defaults):

        if not (api_id and api_secret or token):
            raise ValueError("Arguments api_id and api_secret or token are required")

        self.api_id = api_id
        self.api_secret = api_secret
        self.token = token
        self.defaults = defaults
        self.method_prefix = ''

    def _get(self, method, timeout=DEFAULT_TIMEOUT, **kwargs):
        status, response = self._request(method, timeout=timeout, **kwargs)
        if not (200 <= status <= 299):
            raise VKError(status, "HTTP error", kwargs)

        data = json.loads(response)
        if "error" in data:
            raise VKError(data["error"]["error_code"], data["error"]["error_msg"], data["error"]["request_params"])
        return data['response']

    def __getattr__(self, name):
        '''
        Support for api.<method>.<methodName> syntax
        '''
        if name in COMPLEX_METHODS:
            api = _API(api_id=self.api_id, api_secret=self.api_secret, token=self.token, **self.defaults)
            api.method_prefix = name + '.'
            return api

        # the magic to convert instance attributes into method names
        return partial(self, method=name)

    def __call__(self, **kwargs):
        method = kwargs.pop('method')
        params = self.defaults.copy()
        params.update(kwargs)
        return self._get(self.method_prefix + method, **params)

    def _signature(self, params):
        return signature(self.api_secret, params)

    def _request(self, method, timeout=DEFAULT_TIMEOUT, **kwargs):

        if self.token:
            # http://vkontakte.ru/developers.php?oid=-1&p=Выполнение_запросов_к_API
            params = dict(
                access_token=self.token,
            )
            params.update(kwargs)
            params['timestamp'] = int(time.time())
            url = SECURE_API_URL + method
            secure = True
        else:
            # http://vkontakte.ru/developers.php?oid=-1&p=Взаимодействие_приложения_с_API
            params = dict(
                api_id=str(self.api_id),
                method=method,
                format='JSON',
                v='3.0',
                random=random.randint(0, 2 ** 30),
            )
            params.update(kwargs)
            params['timestamp'] = int(time.time())
            params['sig'] = self._signature(params)
            url = API_URL
            secure = False
        data = urllib.urlencode(params)
        headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}

        # urllib2 doesn't support timeouts for python 2.5 so
        # custom function is used for making http requests
        return http.post(url, data, headers, timeout, secure=secure)


class API(_API):

    def get(self, method, timeout=DEFAULT_TIMEOUT, **kwargs):
        return self._get(method, timeout, **kwargs)