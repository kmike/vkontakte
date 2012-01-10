#!/usr/bin/env python
from distutils.core import setup

version='1.1.0'

setup(
    name='vkontakte',
    version=version,
    author='Mikhail Korobov',
    author_email='kmike84@gmail.com',

    packages=['vkontakte'],

    url='http://bitbucket.org/kmike/vkontakte/',
    download_url = 'http://bitbucket.org/kmike/vkontakte/get/tip.gz',
    license = 'MIT license',
    description = "vk.com (aka vkontakte.ru) API wrapper",

    long_description = open('README.rst').read(),

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
