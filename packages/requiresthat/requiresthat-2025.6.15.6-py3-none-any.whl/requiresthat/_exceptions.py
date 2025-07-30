"""Raise this when a requirement is found wanting"""

import textwrap

class RequirementNotFulfilledError(Exception):

    def __init__(self, that, when, msg=None):
        """Show a default or a user-provided message indicating that some condition is unmet"""

        self.default_msg = textwrap.dedent(f"""
            {that!r} ({when.name!r}) does not hold
        """).strip()

        # Call the base class' constructor to init the exception class
        super().__init__(msg or self.default_msg)
