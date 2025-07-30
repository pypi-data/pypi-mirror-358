"""See the `README
<https://gitlab.com/bedhanger/mwe/-/blob/master/python/requiresthat/README.rst>`_ file
"""
from typing import Optional, Callable
from functools import wraps

from ._when import When, APRIORI, POSTMORTEM, BEFOREANDAFTER
from ._exceptions import RequirementNotFulfilledError, NoCallableConstructError

def requires(that, when: When = APRIORI) -> Optional[Callable]:
    """Require ``that`` of the decoratee, and require it ``when``

    Fail if the associated construct is not callable.

    Fail if the condition is not met: do not invoke the callable or prevent the operation from being
    considered a success.

    Needs the callable to be an instance method of a class, like so:

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

    Try adding

        the_impossible = '1 / 0'
    and
        @requires(the_impossible)

    to the list of decorators above and watch what happens.
    """
    def func_wrapper(__func: Callable) -> Optional[Callable]:
        """First-level wrap the decoratee"""

        @wraps(__func)
        def inner_wrapper(self, *pargs, **kwargs) -> Optional[Callable]:
            """Wrap the first-level wrapper

            The wrapping stops here...
            """
            if not callable(__func):
                raise NoCallableConstructError(__func)
            else:
                if when == APRIORI:
                    __assert(self, that, when)
                    __func(self, *pargs, **kwargs)

                elif when == POSTMORTEM:
                    __func(self, *pargs, **kwargs)
                    __assert(self, that, when)

                elif when == BEFOREANDAFTER:
                    __assert(self, that, when, APRIORI)
                    __func(self, *pargs, **kwargs)
                    __assert(self, that, when, POSTMORTEM)

                # We don't need an else clause; trying to enlist something that's not in the enum
                # will be penalised with an AttributeError, and small typos will be healed with a
                # suggestion as to what you might have meant.

        return inner_wrapper

    return func_wrapper

def __assert(self, that, when: When, subwhen: str = str()):
    """Do the actual testing and raise the proper exceptions

    The reason we don't use assert here is to avoid the Knuthian dilemma of premature optimisation;
    namely, that it nukes this useful tool, :-[
    """
    # We map everything that can go wrong to one exception; that way, the user has to deal with only
    # one catagory of exceptions.
    failure = RequirementNotFulfilledError(that, when, subwhen)
    try:
        if not eval(that):
            raise failure from None
    except Exception:
        raise failure from None
    else:
        # Success!
        pass
