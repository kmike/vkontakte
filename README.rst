=========
vkontakte
=========

``vkontakte`` is an vk.com (aka vkontakte.ru, largest Russian social network)
python API wrapper. The goal is to support all API methods (current and future)
that can be accessed from server.

Installation
============

::

    $ pip install vkontakte

Usage
=====

::
    >>> import vkontakte
    >>> vk = vkontakte.API('my_api_id', 'my_api_secret')
    >>> print vk.getServerTime()
    1282689362

    >>> profiles = vk.getProfiles(uids='1,2', fields='education')
    >>> pavel = profiles[0]
    >>> print pavel['last_name'], pavel['university_name']
    Дуров СПбГУ

All API methods should be supported.

See http://vkontakte.ru/developers.php?o=-1&p=Описание+методов+API for detailed
API help.
