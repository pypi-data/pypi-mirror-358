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
success.  Then details should be observed `here
<https://gitlab.com/bedhanger/mwe/-/blob/master/python/requiresthat/src/requiresthat/_requires.py>`_.

The parameter ``when`` decides if the condition is
`a-priori, post-mortem, or before-and-after
<https://gitlab.com/bedhanger/mwe/-/blob/master/python/requiresthat/src/requiresthat/_when.py>`_.
The default is a-priori, meaning a precondition.  Note that before-and-after does *not* mean during;
you cannot mandate an invariant this way!

``RequirementNotFulfilledError`` is the exception you have to deal with in case a condition is not
met.  ``NoCallableConstructError`` gets raised should you apply the decorator to a construct that is
not callable.  Both of these derive from the `base class
<https://gitlab.com/bedhanger/mwe/-/blob/master/python/requiresthat/src/requiresthat/_exceptions.py>`_
``RequirementError``.

Installation
------------

**Currently**, use ``pip`` with `test PyPi <https://test.pypi.org>`_:

.. code-block:: bash

    python -m pip install --index-url=https://test.pypi.org/simple/ requiresthat

If you want to cook it on your own, do this:

.. code-block:: bash

    git clone https://gitlab.com/bedhanger/mwe.git
    cd mwe/python/requiresthat
    python -m venv --system-site-packages venv
    source venv/bin/activate
    python -m build
    python -m pip install .
    deactivate

It is recommended to carry out the build and install steps in a `venv
<https://docs.python.org/3/library/venv.html>`_.  This is shown in an exemplary manner in the
snipped above that deals with building from scratch.

Running the tests
-----------------

Build the package from scratch like shown above, but do not leave the ``venv`` (i.e., don't call
``deactivate``).  Then

.. code-block:: bash

    python -m pytest --verbose
