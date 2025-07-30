#!/usr/bin/env --split-string=python -m pytest --verbose

import pytest

from requiresthat import requires, RequirementNotFulfilledError, APRIORI, POSTMORTEM, BEFOREANDAFTER

class TestCase_requiresthat_01:

    def test_trivial(self):

        class Spam:

            @requires(that='True is not False')
            @requires(that='self is not None')
            def run(self): ...

        S = Spam()
        S.run()

    def test_tbd_is_more_than_none(self):

        class Spam:

            # Ok, we suggest that "not" is "more than", but the idea should be clear...
            @requires(that='... is not None')
            def run(self): ...

        S = Spam()
        S.run()

    def test_good(self):

        class Spam:

            def __init__(self):
                self.foo = 66
                self.bar = None

            @requires(that='self.foo == 66')
            @requires(that='self.bar is None')
            def run(self): ...

        S = Spam()
        S.run()

    def test_bad(self):

        class Spam:
            def __init__(self):
                self.foo = 66
                self.bar = ... # To be continued, not None

            @requires(that='self.foo == 66')
            @requires(that='self.bar is None')
            def run(self): ...

        S = Spam()
        with pytest.raises(RequirementNotFulfilledError):
            S.run()

    @pytest.mark.filterwarnings("ignore::SyntaxWarning")
    def test_ugly(self):

        class Spam:
            def __init__(self):
                pass

            @requires(that=b"'24' is not 'the answer'")
            def run(self): ...

        S = Spam()
        S.run()

    def test_too_soon_is_bad(self):

        class Spam:

            @requires(that='self.spam == "ham"')
            def __init__(self):
                self.spam = 'ham'

            def run(self): ...

        # We break the constructor
        with pytest.raises(RequirementNotFulfilledError):
            S = Spam()

        # Remember, the constructor just failed...
        with pytest.raises(UnboundLocalError):
            S.run()

    def test_docu(self):

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

    @pytest.mark.filterwarnings("ignore::SyntaxWarning")
    def test_the_impossible(self):
        """Make the evaluation itself a problem"""

        # In algebraic wheels, div by zero is meaningful: https://en.wikipedia.org/wiki/Wheel_theory
        # In Python wheels, it is not!
        the_impossible = '1 / 0 is not None'
        class C:

            def __init__(self, data=None):
                self.data = data

            @requires(the_impossible)
            def method(self):
                self.data = 'ham'

        X = C(data='spam')
        with pytest.raises(RequirementNotFulfilledError):
            X.method()
