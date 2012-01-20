#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for vkontakte package.
Requires mock >= 0.7.2.
"""

import os
import sys
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


if __name__ == '__main__':
    unittest.main()