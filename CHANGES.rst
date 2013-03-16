
Changes
=======

dev (TBA)
---------

* bugfix for breaking vkontakte API updates.

``simplejson`` is now required under python 2.6 (it was previously
required only under python 2.5).

1.3.2 (2012-05-19)
------------------

* more COMPLEX_METHODS are suported.

1.3.1 (2012-04-09)
------------------

* don't raise an exception on json with control characters from vkontakte;
* properly encode request parameters after dumping them to json format.

1.3 (2012-03-27)
----------------

* dict, list and tuple arguments are now properly serialized;
* more info is preserved in VKError.

1.2.1 (2012-02-15)
------------------

* properly encode unicode for API calls;
* tox test running.

1.2 (2012-01-20)
----------------

* 'get' API calls are fixed;
* tests are added.

1.1.0 (2012-01-11)
------------------

* more magic methods are supported;
* proper timestamp calculation.

1.0.0 (2011-12-29)
------------------

* OAuth2 support;
* api.ads support;


0.9.5 (2010-10-30)
------------------

* syntax sugar for 'secure' methods;
* make vkontakte.signature public;
* unicode param names are fixed;

0.9.3 (2010-09-02)
------------------

* timeout support

0.9.1 (2010-08-25)
------------------
Initial release.
