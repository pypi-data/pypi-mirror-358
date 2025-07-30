requiresthat
============

Decorate an instance method with pre- and/or postconditions that must be fulfilled

Example usage
-------------

.. code-block:: python

    from requiresthat import requires, RequirementNotFulfilledError, APRIORI, POSTMORTEM, BEFOREANDAFTER

    class C:

        def __init__(self, data=None):
            self.data = data

        @requires(that='self.data is not None')
        @requires(that='self.data == "spam"', when=APRIORI)
        @requires(that='True is not False')
        @requires(that='self.data != "spam"', when=POSTMORTEM)
        @requires(that='len(self.data) >= 3', when=BEFOREANDAFTER)
        def method(self):
            self.data = 'ham'

    X = C(data='spam')
    X.method()

See the `tests <https://gitlab.com/bedhanger/mwe/-/blob/master/python/requiresthat/tests/test_requiresthat.py>`_
for more.

The ``that`` can be almost any valid Python statement which can be evaluated and whose veracity can
be asserted, and the result thereof will decide whether or not the method fires/will be considered a
success.

The parameter ``when`` decides if the condition is
`a-priori, post-mortem, or before-and-after
<https://gitlab.com/bedhanger/mwe/-/blob/master/python/requiresthat/src/_when.py>`_.
The default is a-priori, meaning a precondition.  Note that before-and-after does *not* mean during;
you cannot mandate an invariant this way!

``RequirementNotFulfilledError`` is the exception you have to deal with in case a condition is not
met.  ``NoCallableConstructError`` gets raised should you apply the decorator to a construct that is
not callable.
