#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for vkontakte package.
Requires mock >= 0.7.2.
"""

import os
import sys
import urllib
sys.path.insert(0, os.path.abspath('..'))

import unittest
import mock
import vkontakte
import vkontakte.api

API_ID = 'api_id'
API_SECRET = 'api_secret'

class VkontakteTest(unittest.TestCase):
    def test_api_creation_error(self):
        self.assertRaises(ValueError, lambda: vkontakte.API())

class SignatureTest(unittest.TestCase):
    def test_signature_supports_unicode(self):
        params = {'foo': u'клен'}
        self.assertEqual(
            vkontakte.signature(API_SECRET, params),
            '560b3f1e09ff65167b8dc211604fed2b'
        )

class IterparseTest(unittest.TestCase):
    def test_iterparse(self):
        data = '{"error":{"error_code":8,"error_msg":"Invalid request: this auth method is obsolete, please use oauth. vk.com\/developers","request_params":[{"key":"sig","value":"97aasff03cc81d5db25de67893e207"},{"key":"uids","value":"1,2"},{"key":"timestamp","value":"1355095295"},{"key":"v","value":"3.0"},{"key":"fields","value":"education"},{"key":"format","value":"JSON"},{"key":"random","value":"937530097"},{"key":"method","value":"getProfiles"},{"key":"api_id","value":"3267523"}]}}{"error":{"error_code":8,"error_msg":"Invalid request: this auth method is obsolete, please use oauth. vk.com\/developers","request_params":[{"key":"sig","value":"97aasff03cc81d5db25de67893e207"},{"key":"uids","value":"1,2"},{"key":"timestamp","value":"1355095295"},{"key":"v","value":"3.0"},{"key":"fields","value":"education"},{"key":"format","value":"JSON"},{"key":"random","value":"937530097"},{"key":"method","value":"getProfiles"},{"key":"api_id","value":"3267523"}]}}{"response":[{"uid":1,"first_name":"Павел","last_name":"Дуров","university":1,"university_name":"СПбГУ","faculty":15,"faculty_name":"Филологический","graduation":2006},{"uid":2,"first_name":"Александра","last_name":"Владимирова"}]}'
        parses = list(vkontakte.api._json_iterparse(data))
        self.assertEqual(len(parses),  3)
        assert "error" in parses[0]
        assert "error" in parses[1]
        self.assertEqual(parses[2]["response"][0]["first_name"], u"Павел")

    def test_iterparse_edge(self):
        data = '{"error": {"}{": "foo"}}{"foo":"bar"}'
        parses = list(vkontakte.api._json_iterparse(data))
        self.assertEqual(parses[0]["error"]["}{"], "foo")
        self.assertEqual(parses[1]["foo"], "bar")



class VkontakteMagicTest(unittest.TestCase):

    def setUp(self):
        self.api = vkontakte.API(API_ID, API_SECRET)

    @mock.patch('vkontakte.api._API._get')
    def test_basic(self, _get):
        _get.return_value = '123'
        time = self.api.getServerTime()
        self.assertEqual(time, '123')
        _get.assert_called_once_with('getServerTime')

    @mock.patch('vkontakte.api._API._get')
    def test_with_arguments(self, _get):
        _get.return_value = [{'last_name': u'Дуров'}]
        res = self.api.getProfiles(uids='1,2', fields='education')
        self.assertEqual(res, _get.return_value)
        _get.assert_called_once_with('getProfiles', uids='1,2', fields='education')

    @mock.patch('vkontakte.api._API._get')
    def test_with_arguments_get(self, _get):
        _get.return_value = [{'last_name': u'Дуров'}]
        res = self.api.get('getProfiles', uids='1,2', fields='education')
        self.assertEqual(res, _get.return_value)
        _get.assert_called_once_with('getProfiles', vkontakte.api.DEFAULT_TIMEOUT, uids='1,2', fields='education')

    @mock.patch('vkontakte.http.post')
    def test_timeout(self, post):
        post.return_value = 200, '{"response":123}'
        api = vkontakte.API(API_ID, API_SECRET, timeout=5)
        res = api.getServerTime()
        self.assertEqual(res, 123)
        self.assertEqual(post.call_args[0][3], 5)

    @mock.patch('vkontakte.api._API._get')
    def test_magic(self, _get):
        for method in vkontakte.api.COMPLEX_METHODS:
            _get.return_value = None
            res = getattr(self.api, method).test()
            self.assertEqual(res, None)
            _get.assert_called_once_with('%s.test' % method)
            _get.reset_mock()

    @mock.patch('vkontakte.api._API._get')
    def test_magic_get(self, _get):
        _get.return_value = 'foo'
        res = self.api.friends.get(uid=642177)
        self.assertEqual(res, 'foo')
        _get.assert_called_once_with('friends.get', uid=642177)

    @mock.patch('vkontakte.http.post')
    def test_urlencode_bug(self, post):
        post.return_value = 200, '{"response":123}'
        res = self.api.search(q=u'клен')
        self.assertEqual(res, 123)

    @mock.patch('vkontakte.http.post')
    def test_valid_quoted_json(self, post):
        post.return_value = 200, '{"response": 123}'
        self.api.ads.getStat(data={'type': '1', 'id': 1})
        posted_data = urllib.unquote(post.call_args[0][1])
        self.assertTrue('data={"type":+"1",+"id":+1}' in posted_data, posted_data)

if __name__ == '__main__':
    unittest.main()