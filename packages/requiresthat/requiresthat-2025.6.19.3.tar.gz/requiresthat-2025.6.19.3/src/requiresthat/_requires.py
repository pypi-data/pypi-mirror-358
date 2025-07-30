"""See the `README
<https://gitlab.com/bedhanger/mwe/-/blob/master/python/requiresthat/README.rst>`_ file
"""
from typing import Optional, Callable
from functools import wraps

from ._when import When, APRIORI, POSTMORTEM, BEFOREANDAFTER
from ._exceptions import RequirementNotFulfilledError, NoCallableConstructError

def requires(that, when: When = APRIORI) -> Optional[Callable]:
    """Require <that> of the decoratee, and require it <when>"""

    def func_wrapper(func: Callable) -> Optional[Callable]:
        """First-level wrap the decoratee"""

        @wraps(func)
        def inner_wrapper(self, *pargs, **kwargs) -> Optional[Callable]:
            """Wrap the first-level wrapper

            The wrapping stops here...
            """
            try:
                assert callable(func)
            except AssertionError as exc:
                raise NoCallableConstructError(func) from exc
            else:
                # Since we want to give detailed sub-failure diax in case of BEFOREANDAFTER,
                # economisng on the ifs below is tricky.
                if when == APRIORI:
                    try:
                        assert eval(that)
                    except AssertionError as exc:
                        raise RequirementNotFulfilledError(that, when) from exc
                    else:
                        func(self, *pargs, **kwargs)

                elif when == POSTMORTEM:
                    func(self, *pargs, **kwargs)
                    try:
                        assert eval(that)
                    except AssertionError as exc:
                        raise RequirementNotFulfilledError(that, when) from exc

                elif when == BEFOREANDAFTER:
                    try:
                        assert eval(that)
                    except AssertionError as exc:
                        raise RequirementNotFulfilledError(that, when, APRIORI) from exc
                    else:
                        func(self, *pargs, **kwargs)
                    try:
                        assert eval(that)
                    except AssertionError as exc:
                        raise RequirementNotFulfilledError(that, when, POSTMORTEM) from exc

                # We don't need an else clause; trying to enlist something that's not in the enum
                # will be penalised with an AttributeError, and small typos will be healed with a
                # suggestion as to what you might have meant.

        return inner_wrapper

    return func_wrapper
