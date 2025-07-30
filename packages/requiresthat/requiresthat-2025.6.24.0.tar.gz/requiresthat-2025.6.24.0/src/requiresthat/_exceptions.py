import textwrap

class RequirementError(Exception):
    """Base class for all exceptions that follow here"""
    pass

class RequirementNotFulfilledError(RequirementError):
    """Raise this when a requirement is found wanting"""

    def __init__(self, that, when, subwhen: str = str(), msg=None):
        """Show a default or a user-provided message indicating that some condition is unmet"""

        if subwhen:
            subwhen = f' ({subwhen.name!r})'
        self.default_msg = textwrap.dedent(f"""
            {that!r} ({when.name!r}{subwhen}) does not hold
        """).strip()

        # Call the base class' constructor to init the exception class
        super().__init__(msg or self.default_msg)

class NoCallableConstructError(RequirementError):
    """Raise this when a construct is not callable"""

    def __init__(self, construct, msg=None):
        """Show a default or a user-provided message"""

        self.default_msg = textwrap.dedent(f"""
            {construct!r} does not seem to be callable

            You have managed to place the decorator before a construct that is not callable
            *without* tripping the Python interpreter.  Maybe you are a wizard?

            But, no, we can't carry on like that.  Sorry!
        """).strip()

        # Call the base class' constructor to init the exception class
        super().__init__(msg or self.default_msg)
