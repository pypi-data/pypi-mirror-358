"""See the README file"""

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

            try:
                if when == APRIORI:
                    assert eval(that)
                    # We can use a return here :-)
                    return func(self, *pargs, **kwargs)
                elif when == POSTMORTEM:
                    func(self, *pargs, **kwargs)
                    assert eval(that)
                elif when == BEFOREANDAFTER:
                    assert eval(that)
                    func(self, *pargs, **kwargs)
                    assert eval(that)
                # We don't need an else clause; trying to enlist something that's not in the enum
                # will be penalised with an AttributeError, and small typos will be healed with a
                # suggestion as to what you might have meant.
            except AssertionError as exc:
                raise RequirementNotFulfilledError(that, when) from exc
        return inner_wrapper

    return func_wrapper
