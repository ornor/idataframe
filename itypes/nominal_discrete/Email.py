import pandas as pd

from idataframe.itypes.nominal_discrete.Text import Text
from idataframe.fields.StrField import StrField

__all__ = ['Email']


# -----------------------------------------------------------------------------


class Email(Text):
    """
    Email address. Subclass of Text.
    """

    RE_USERNAME = r"[a-zA-Z][a-zA-Z0-9._%+\-]*"
    RE_DOMAIN = r"[a-zA-Z][a-zA-Z.\-]+\.[a-zA-Z]{2,}"

    def __init__(self, series:pd.Series, fields=None):
        if fields is None:  # Email type called directly
            Text.__init__(self, series, (
                ('email', StrField()),
                ('username', StrField( lambda value: value.lower() )),
                ('domain', StrField( lambda value: value.lower() )),
            ))
        else:   # subtype of Email called
            Text.__init__(self, series, fields)

        if fields is None:
            self.add_match(name = 'username@domain',
                       regexp = r"^(?P<username>{})@(?P<domain>{})$".format(self.RE_USERNAME, self.RE_DOMAIN),
                       str_format = '{username}@{domain}')

    @classmethod
    def from_test_data(cls, *args, **kwargs):
        return cls(pd.Series([value.strip() for value in """
            foo@bar.com
            foo23@BLA.org
            asdfASDF@foo-bar.nl
            user@no-top-domain
            ornor@subdomain.ornor.org
        """.strip().split('\n')]), *args, **kwargs)